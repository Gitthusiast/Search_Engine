from parser_module import Parse
from ranker import Ranker
from configuration import ConfigClass
import utils
from spellchecker import SpellChecker
from math import log

# Constants for accessing data lists
IDF_INDEX = 0
POSTING_POINTER_INDEX = 2

DOCUMENT_ID_INDEX = 0
FREQUENCY_INDEX = 1
LENGTH_INDEX = 4  # document length

# Constants for BM25+ calculation
K1 = 1.2
B = 0.75
DELTA = 1


class Searcher:

    def __init__(self, inverted_index, corpus_size, average_length):
        """
        :param inverted_index: dictionary of inverted index
        """
        self.parser = Parse()
        self.ranker = Ranker()
        self.config = ConfigClass()
        self.inverted_index = inverted_index
        self.corpus_size = corpus_size
        self.average_length = average_length

    def calculate_doc_scores(self, term, relevant_docs, posting_pointer, posting_file):

        """
        Retrieves term's posting file and calculates score for each relevant document.
        Adds the relevant documents to relevant_docs dictionary
        :param term: query term for retrieval
        :param relevant_docs: dictionary of relevant documents
        :param posting_pointer: pointer (name) of relevant posting file
        :param posting_file: relevant posting file
        :return: returns a tuple of the current relevant posting pointer and posting file
        """
        # retrieve term's posting file
        if posting_pointer is None or term[0].lower() != posting_pointer or posting_file is None:
            posting_pointer = self.inverted_index[term][POSTING_POINTER_INDEX]
            posting_file = utils.load_obj(
                self.config.corpusPath + self.config.savedFileMainFolder + posting_pointer)

        inverted_document_frequency = log(self.corpus_size / self.inverted_index[term][IDF_INDEX])

        documents = posting_file[term]
        for document in documents:

            # calculate score
            document_id = document[DOCUMENT_ID_INDEX]
            doc_weight = document[FREQUENCY_INDEX]
            normalized_length = document[LENGTH_INDEX] / self.average_length

            if document_id not in relevant_docs:
                relevant_docs[document_id] = 0

            # calculate score according to BM25+ weighting formula
            relevant_docs[document_id] += inverted_document_frequency * (
                    float((doc_weight * (K1 + 1))) / (
                                                        doc_weight + K1 * (1 - B + B * normalized_length)) + DELTA)

        return posting_pointer, posting_file

    def relevant_docs_from_posting(self, query):

        """
        Search and retrieve relevant documents for the query. Calculate the similarity score for each document.
        :param query: query
        :return: dictionary of relevant documents and their scores
        """

        # parse query according to the same parsing rules of the corpus
        entities = dict()
        term_dict = dict()
        parsed_query = self.parser.parse_sentence(query, entities)
        self.parser.parse_capital_letters(parsed_query, term_dict)

        # perform spell correction
        spell_checker = SpellChecker()
        corrected_terms = []
        misspelled_terms = spell_checker.unknown(*term_dict.keys())
        for term in misspelled_terms:

            # only correct terms that aren't in the inverted dictionary
            # terms in the dictionary are considered correct for retrieval
            if term not in self.inverted_index:
                candidates = spell_checker.candidates(term)
                if term in candidates:  # remove duplicate originally correct terms
                    candidates.remove(term)
                corrected_terms.extend(candidates)

        # sort the parsed query alphabetically for optimal posting files retrieval
        # always hold at most one posting file in memory
        sorted_query = [*term_dict.keys()] + [*entities.keys()] + corrected_terms
        sorted_query.sort()

        # dictionary for holding all relevant documents (at least one query term appeared in the document)
        # format: {document_id: score}
        relevant_docs = dict()
        posting_file = None  # currently used posting file from disk
        posting_pointer = None  # current posting's pointer
        for term in sorted_query:

            # check if term exists in inverted dictionary in either lower or upper form
            if term in self.inverted_index:
                posting_pointer, posting_file = self.calculate_doc_scores(term, relevant_docs, posting_pointer,
                                                                          posting_file)
            elif term.islower() and term.upper() in self.inverted_index:
                posting_pointer, posting_file = self.calculate_doc_scores(term.upper(), relevant_docs, posting_pointer,
                                                                          posting_file)
            elif term.isupper() and term.lower() in self.inverted_index:
                posting_pointer, posting_file = self.calculate_doc_scores(term.lower(), relevant_docs, posting_pointer,
                                                                          posting_file)

        return relevant_docs
