from parser_module import Parse
from ranker import Ranker
import utils
from spellchecker import SpellChecker

class Searcher:

    def __init__(self, inverted_index):
        """
        :param inverted_index: dictionary of inverted index
        """
        self.parser = Parse()
        self.ranker = Ranker()
        self.inverted_index = inverted_index

    def relevant_docs_from_posting(self, query):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query: query
        :return: dictionary of relevant documents.
        """

        spell = SpellChecker()

        posting = utils.load_obj("posting")
        relevant_docs = {}
        parsed_query = self.parser.parse_sentence(query)

        spell = SpellChecker()
        i = 0
        while i < len(parsed_query):
            corrected_token = spell.correction(parsed_query[i])
            if corrected_token in self.inverted_index:
                parsed_query.insert(i + 1, corrected_token)
            i += 1

        for term in parsed_query:
            try:  # an example of checks that you have to do
                posting_doc = posting[term]
                for doc_tuple in posting_doc:
                    doc = doc_tuple[0]
                    if doc not in relevant_docs.keys():
                        relevant_docs[doc] = 1
                    else:
                        relevant_docs[doc] += 1
            except:
                print('term {} not found in posting'.format(term))

        return relevant_docs
