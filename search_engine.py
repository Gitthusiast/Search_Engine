from glob import glob
import time

from reader import ReadFile
from configuration import ConfigClass
from parser_module import Parse
from indexer import Indexer
from searcher import Searcher
import utils


def run_engine():
    """

    :return:
    """
    number_of_documents = 0

    config = ConfigClass()
    reader = ReadFile(corpus_path=config.get__corpusPath())
    parser = Parse()
    indexer = Indexer(config)

    total_tic = time.perf_counter()
    tic = time.perf_counter()
    # read all parquet data files
    files = glob(config.get__corpusPath() + "/Data/**/*.parquet", recursive=True)
    toc = time.perf_counter()
    print("Took {} seconds to fetch all files".format(toc-tic))

    # read, parse and index document in batches. Posting files are divided by english alphabet
    # a batch is defined as all the documents in a single parquet file
    # each batch is first written as many sub-batches indicated by an index and later merged into one coherent batch
    batch_index = 0
    file_index = 0
    while file_index < len(files):

        # batch two files at a time to reduce disk seek time penalty
        first_file = files[file_index]
        first_documents_list = reader.read_file(first_file)

        print("Currently in batch #{} are files:".format(batch_index))
        print(first_file)

        if file_index + 1 < len(files):
            second_file = files[file_index + 1]
            second_documents_list = reader.read_file(second_file)
            documents_list = first_documents_list + second_documents_list
            print(second_file)
        else:  # if only one batch left for the last batch
            documents_list = first_documents_list

        file_index += 2

        # Iterate over every document in the file

        tic = time.perf_counter()
        # parse documents
        parsed_file = set()
        for document_as_list in documents_list:
            parsed_documents = parser.parse_doc(document_as_list)
            parsed_file.add(parsed_documents)
            number_of_documents += 1
        toc = time.perf_counter()
        print("Took {} seconds to parse batch number #{}".format(toc-tic, batch_index))

        tic = time.perf_counter()
        # index parsed documents
        indexer.index_batch(parsed_file, str(batch_index))
        toc = time.perf_counter()
        print("Took {} seconds to index batch number #{}".format(toc-tic, batch_index))

        batch_index += 1

    tic = time.perf_counter()
    # after indexing all non-entity terms in the corpus, index legal entities
    indexer.index_entities()
    toc = time.perf_counter()
    print("Took {} seconds to index all entities in the corpus".format(toc-tic))

    tic = time.perf_counter()
    # after indexing the whole corpus, consolidate all partial posting files
    indexer.consolidate_postings()
    toc = time.perf_counter()
    print("Finished creating inverted index")
    print("Took {} seconds to consolidate all postings".format(toc-tic))
    total_toc = time.perf_counter()
    print("In total, took {} seconds to parse all corpus and build inverted index".format(total_toc-total_tic))

# -----------------
#     batch_index = 0
#     # Iterate over every document in the file
#     documents_list = reader.read_file("sample3.parquet")
#
#     # parse documents
#     parsed_file = set()
#     for document_as_list in documents_list:
#         parsed_documents = parser.parse_doc(document_as_list)
#         parsed_file.add(parsed_documents)
#         number_of_documents += 1
#
#     # index parsed documents and write to disk current batch's posting file
#     indexer.index_batch(parsed_file, str(batch_index))
#
#     # after indexing all non-entity terms in the corpus, index legal entities
#     indexer.index_entities()
#
#     # after indexing all documents, consolidate all partial posting files
#     indexer.consolidate_postings()
#     print("Finished creating inverted index")

def load_index():
    print('Load inverted index')
    inverted_index = utils.load_obj("inverted_idx")
    return inverted_index


def search_and_rank_query(query, inverted_index, k):
    p = Parse()
    query_as_list = p.parse_sentence(query)
    searcher = Searcher(inverted_index)
    relevant_docs = searcher.relevant_docs_from_posting(query_as_list)
    ranked_docs = searcher.ranker.rank_relevant_doc(relevant_docs)
    return searcher.ranker.retrieve_top_k(ranked_docs, k)


# def main(corpus_path, output_path, stemming, queries, num_doc_to_retrieve):
def main():
    run_engine()
    query = input("Please enter a query: ")
    k = int(input("Please enter number of docs to retrieve: "))
    inverted_index = load_index()
    for doc_tuple in search_and_rank_query(query, inverted_index, k):
        print('tweet id: {}, score (unique common words with query): {}'.format(doc_tuple[0], doc_tuple[1]))
