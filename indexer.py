import utils
from os import remove as os_remove
from os import getcwd as os_getcwd
from os.path import exists as os_path_exists
from os import rename as os_rename


class Indexer:

    def __init__(self, config):
        self.inverted_idx = {}  # dictionary format {term: [document_frequency, posting_pointer] }

        # dictionary holds posting files for current ongoing batch
        # dictionary format {posting_batch_pointer : { term: [[docId, term_frequency]] } }
        self.postingDict = dict()

        self.config = config

        # entity_dict is a partial inverted_idx dictionary containing only entities
        # entity_dict is of the format {entity: document_frequency}
        self.entity_dict = dict()

        # a dictionary of all currently existing postings (partial or merged)
        # to be used after clearing the postingDict between batches
        # key - final merged posting file's alphabet pointer; value - partial posting files' pointers
        # for example: {a : [a0, a1, a2]} ; {b: [b]}
        self.posting_pointers = dict()

    def collect_possible_entities(self, document_entities):

        """
        Collect all possible entities from the possible entities in a document and add them to entity_dict
        A possible entity is defined as every sequence of tokens starting in a capital letter
        An entity is defined as a possible entity that appears in at least 2 different documents
        :param document_entities: dictionary of all entities in the document
        """

        for entity in document_entities.keys():

            if entity not in self.entity_dict:
                self.entity_dict[entity] = 1
            else:
                self.entity_dict[entity] += 1

    def index_uniform_terms(self, document_dictionary):

        """
        Index terms according to capital letters rule.
        Ensures a uniform appearance of terms across all corpus
        If a term only appears in capital form - record as upper case. Else, record in lower case
        Documents are indexed in batches
        :param document_dictionary - per document uniform term dictionary
        """

        for term in document_dictionary.keys():

            # Add term to inverted_idx dictionary
            # In the dictionary keep the term_frequency
            # term_frequency - how many times the term appeared in the document
            # key indicates if term is capital or lower case

            # Any posting file gets a name (pointer) to identify it
            # Pointer of a fully merged legal posting file is a string posting_pointer that equals to posting_prefix
            # where posting_prefix is the alphabet letter the token starts with
            posting_prefix = term[0].lower()

            # Check if term form is a upper case
            if term.isupper():

                term_lower_form = term.lower()
                # check in which form the token appears in dictionary and update it accordingly
                if term not in self.inverted_idx and term_lower_form not in self.inverted_idx:
                    self.inverted_idx[term] = [1, posting_prefix]
                elif term in self.inverted_idx:
                    self.inverted_idx[term][0] += 1
                else:  # term appears in lower case in dictionary
                    self.inverted_idx[term_lower_form][0] += 1

            # If current term is lower case change key to lower case
            else:

                term_upper_form = term.upper()
                # check in which form the token appears in dictionary and update it accordingly
                if term_upper_form not in self.inverted_idx and term not in self.inverted_idx:
                    self.inverted_idx[term] = [1, posting_prefix]
                elif term_upper_form in self.inverted_idx:  # replace term in dictionary from upper case to lower case
                    self.inverted_idx[term] = [self.inverted_idx[term_upper_form][0] + 1,
                                               self.inverted_idx[term_upper_form][1]]
                    if term.islower() or term.isupper():  # term is neither a number nor a punctuation
                        self.inverted_idx.pop(term_upper_form, None)  # remove upper case form from the dictionary
                else:  # term appears in lower case in dictionary
                    self.inverted_idx[term][0] += 1

    def add_document_to_posting_batch(self, doc_id, document_dictionary, document_entities, batch_index):

        """
        Creates an initial batch posting file
        This file doesn't promise integrity of lower/upper letter rule or entities rule
        Integrity of these rules should be enforced by merging of corresponding batch posting files
        Posting dictionary format is {posting_batch_pointer : { term: [[docId, term_frequency]] } }
        :param doc_id: current document id to be added
        :param document_dictionary: document's uniform term dictionary
        :param document_entities: document's entities dictionary
        :param batch_index: current batch index to create partial posting file
        """

        # unpack dict_items object into a list before applying operand +
        for term, frequency in [*document_dictionary.items()] + [*document_entities.items()]:

            # Any partial posting file gets a name (pointer) to identify it
            # Pointer is a string posting_prefix+batch_index
            # where posting_prefix is the alphabet letter the token starts with and batch_index is current batch number
            posting_prefix = term[0].lower()
            posting_batch_pointer = posting_prefix + batch_index

            if posting_batch_pointer not in self.postingDict:
                self.postingDict[posting_batch_pointer] = dict()
                self.postingDict[posting_batch_pointer][term] = [[doc_id, frequency]]

                # update pointer in posting files pointer dictionary
                if posting_prefix not in self.posting_pointers:
                    self.posting_pointers[posting_prefix] = [posting_batch_pointer]
                else:
                    if posting_batch_pointer not in self.posting_pointers[posting_prefix]:
                        self.posting_pointers[posting_prefix].append(posting_batch_pointer)
            else:
                partial_posting = self.postingDict[posting_batch_pointer]
                if term not in partial_posting:
                    partial_posting[term] = [[doc_id, frequency]]
                else:
                    partial_posting[term].append([doc_id, frequency])

    def index_batch(self, batch, batch_index):

        """
        Index all non-entity terms and collect all possible entities in the entire batch then creates partial
        posting file for current batch
        :param batch: list(Document) - list of all documents in batch to be indexed
        :param batch_index: str - current batch index
        """

        # index all terms and possible entities in the document
        for document in batch:

            document_dictionary = document.term_doc_dictionary
            document_entities_dictionary = document.entities

            self.index_uniform_terms(document_dictionary)
            self.collect_possible_entities(document_entities_dictionary)

        # create posting file for current batch
        for document in batch:
            doc_id = document.tweet_id
            document_dictionary = document.term_doc_dictionary
            document_entities_dictionary = document.entities

            self.add_document_to_posting_batch(doc_id, document_dictionary, document_entities_dictionary, batch_index)

        print('Finished parsing and indexing batch #{}. Starting to export files'.format(batch_index))
        self.write_batch_postings()

        # after finished indexing all batch, clean posting dictionary for next batch
        self.postingDict.clear()

    def index_entities(self):

        """
        Index all legal entities recorded in the indexer's entity dictionary after processing all the corpus
        """

        for entity, document_frequency in self.entity_dict.items():

            # Any posting file gets a name (pointer) to identify it
            # Pointer of a fully merged legal posting file is a string posting_pointer that equals to posting_prefix
            # where posting_prefix is the alphabet letter the token starts with
            posting_prefix = entity[0].lower()

            # check if possible entity is a legal entity and and index it
            if entity not in self.inverted_idx and document_frequency >= 2:
                self.inverted_idx[entity] = [document_frequency, posting_prefix]

    def write_batch_postings(self):

        """
        Writes all partial posting files in current batch to disk in .pkl form
        """

        for posting_batch_pointer, posting_batch in self.postingDict.items():
            utils.save_obj(posting_batch, os_getcwd() + "/postings/{}".format(posting_batch_pointer))

    def read_batch_postings(self, posting_prefix):

        """
        Read all partial posting files according to posting prefix across all batches
        :param posting_prefix: string - the alphabet letter the token starts with
        :return: (list(dict), list(str)) - returns a tuple of a list of posting files and a list of the corresponding
                 file names
        """

        # Any partial posting file gets a name (pointer) to identify it
        # Pointer is a string posting_prefix+batch_index
        # where posting_prefix is the alphabet letter the token starts with and batch_index is current batch number

        posting_names = []
        posting_files = []
        for posting_pointer in self.posting_pointers[posting_prefix]:
            posting_file = utils.load_obj(os_getcwd() + "/postings/{}".format(posting_pointer))
            posting_files.append(posting_file)
            posting_names.append(posting_pointer)

        return posting_files, posting_names

    def merge_document_lists(self, document_list1, document_list2, merged_posting, term):

        """
        Merges two internal document lists of two different posting files.
        Lists are merged into the internal document list of the corresponding term in the final merged posting file
        :param document_list1: document list of first posting file
        :param document_list2: document list of second posting file
        :param merged_posting: final merged posting file dictionary
        :param term: current term to merge posting file according to
        """

        i, j = 0, 0
        while i < len(document_list1) and j < len(document_list2):

            if document_list1[i][0] <= document_list2[j][0]:
                merged_posting[term].append(document_list1[i])
                i += 1
            else:
                merged_posting[term].append(document_list2[j])
                j += 1

        # check if any documents left in either posting file
        while i < len(document_list1):
            merged_posting[term].append(document_list1[i])
            i += 1
        while j < len(document_list2):
            merged_posting[term].append(document_list2[j])
            j += 1

    def merge_postings(self, posting1, posting2=None):

        """
        Merges two sorted posting files. Each file is sorted internally by sorting the documents by the document id
        If posting2 not given returns posting1 as is
        When performing merge, only include terms that abide entities and lower/upper rules
        :param posting1: first posting to merge
        :param posting2: second posting to merge
        :return: returns a merged posting file
        """

        # if posting2 not given returns posting1 as is
        if posting2 is None:
            return posting1

        merged_posting = {}  # result merged posting file

        # merge posting by term corresponding document lists
        # iterate first on terms from posting1 and check for intersection with posting2
        for term in posting1.keys():

            if term in posting2.keys():

                if term not in merged_posting:  # initialize merged_posting
                    merged_posting[term] = []

                # merge internal document lists by document id
                document_list1 = posting1[term]
                document_list2 = posting2[term]

                self.merge_document_lists(document_list1, document_list2, merged_posting, term)

                # remove merged term from posting2
                posting2.pop(term, None)
            else:  # term appears only in posting1
                merged_posting[term] = posting1[term]

        # check if any term left in posting2 to be merged
        for term, document_list in posting2.items():
            merged_posting[term] = document_list

        return merged_posting

    def merge_posting_pairs(self, posting_files, posting_names):

        """
        Merges every two consecutive posting file pairs in the posting files list
        Deletes already merged and un-needed posting files from disk
        :param posting_files: list of posting files to be merged internally
        :param posting_names: list of posting file names
        :return: returns a new list containing merged posting files
        """

        # merge posting files into one complete and legal posting file

        i, j = 0, 1
        merged_postings = []
        while i < len(posting_files):

            if j < len(posting_files):
                merged_postings.append(self.merge_postings(posting_files[i], posting_files[j]))
            else:  # if second element in pair doesn't exist add first element as is
                merged_postings.append(posting_files[i])

            i += 2
            j += 2

        # delete already merged posting files from disk
        for posting in posting_names:
            if os_path_exists(os_getcwd() + "/postings/{}".format(posting) + ".pkl"):
                os_remove(os_getcwd() + "/postings/{}".format(posting) + ".pkl")

        return merged_postings

    def consolidate_postings(self):

        """
        Reads from disk partial posting files and merges them into new sorted legal posting files divided by their
        alphabet partition. Deletes old postings and writes the new ones to the disk.
        Merge is performed in batches by alphabet partition.
        """

        # collect all postings by their posting_prefix
        for posting_prefix in self.posting_pointers.keys():

            # read all partial posting files
            posting_files, posting_names = self.read_batch_postings(posting_prefix)

            # sort each posting_file by document id
            for posting_file in posting_files:
                for term in list(posting_file.keys()):

                    # verify legality of the term

                    # if term is an entity and it doesn't appear in at least two different document
                    # remove from posting file
                    if term in self.entity_dict and self.entity_dict[term] == 1:
                        posting_file.pop(term, None)
                        continue

                    # if term is upper case and there has been a term in lower form in the corpus
                    # change the term in the posting to lower form
                    elif term.isupper() and term not in self.inverted_idx:
                        posting_file[term.lower()] = posting_file.pop(term)

                        # sort internal document list according to document id
                        posting_file[term.lower()].sort(key=lambda doc_list: doc_list[0])
                    else:
                        # sort internal document list according to document id
                        posting_file[term].sort(key=lambda doc_list: doc_list[0])

            # if current alphabetical partition has only one batch posting file
            if len(posting_files) == 1 and posting_names[0] != posting_prefix:
                posting_files = self.merge_posting_pairs(posting_files, posting_names)
            else:
                # merge posting files into one complete and legal posting file
                while len(posting_files) != 1:
                    posting_files = self.merge_posting_pairs(posting_files, posting_names)

            # write to disk merged posting file
            utils.save_obj(posting_files[0], os_getcwd() + "/postings/{}".format(posting_prefix))

            # update posting files pointer dictionary
            self.posting_pointers[posting_prefix] = [posting_prefix]
