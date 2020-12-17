from glob import glob
import time

from reader import ReadFile
from parser_module import Parse
from indexer import Indexer
from searcher import Searcher
import utils

import csv


def run_engine(corpus_path, output_path, stemming=False):
    """
    Builds the retrieval model.
    Preprocess, parse and index corpus.
    :return: a tuple of number_of_documents in the corpus and average_document_length
    """

    number_of_documents = 0
    total_document_length = 0

    reader = ReadFile(corpus_path)
    parser = Parse()
    indexer = Indexer(output_path)

    # read all parquet data files
    files = glob(corpus_path + "/**/*.parquet", recursive=True)

    # read, parse and index document in batches. Posting files are divided by english alphabet
    # a batch is defined as all the documents in a single parquet file
    # each batch is first written as many sub-batches indicated by an index and later merged into one coherent batch
    batch_index = 0
    file_index = 0
    while file_index < len(files):

        # batch two files at a time to reduce disk seek time penalty
        first_file = files[file_index]
        first_documents_list = reader.read_file(first_file)

        if file_index + 1 < len(files):
            second_file = files[file_index + 1]
            second_documents_list = reader.read_file(second_file)
            documents_list = first_documents_list + second_documents_list

        else:  # if only one batch left for the last batch
            documents_list = first_documents_list

        file_index += 2

        # Iterate over every document in the file

        # parse documents
        parsed_file = set()
        for document_as_list in documents_list:
            parsed_document = parser.parse_doc(document_as_list, stemming)
            parsed_file.add(parsed_document)
            total_document_length += parsed_document.doc_length
            number_of_documents += 1

        # index parsed documents
        indexer.index_batch(parsed_file, str(batch_index))

        batch_index += 1

    # calculate average document length
    average_document_length = float(total_document_length) / number_of_documents

    # after indexing all non-entity terms in the corpus, index legal entities
    indexer.index_entities()

    # save index dictionary to disk
    utils.save_obj(indexer.inverted_idx, output_path + "inverted_idx")

    # after indexing the whole corpus, consolidate all partial posting files
    indexer.consolidate_postings()

    return number_of_documents, average_document_length


def load_index(output_path):
    inverted_index = utils.load_obj(output_path + "\\inverted_idx")
    return inverted_index


def search_and_rank_query(queries, inverted_index, k, corpus_size, average_length, output_path):

    searcher = Searcher(inverted_index, corpus_size, average_length, output_path)

    # process queries
    if isinstance(queries, list):  # queries in a list format

        for i, query in enumerate(queries, 1):

            relevant_docs = searcher.relevant_docs_from_posting(query)  # retrieve all relevant documents
            ranked_docs = searcher.ranker.rank_relevant_doc(relevant_docs)  # rank documents by score
            top_relevant_documents = searcher.ranker.retrieve_top_k(ranked_docs, k)  # top k relevant documents

            for doc_id, score in top_relevant_documents:
                print("Tweet id: {id} Score: {score}".format(id=doc_id, score=score))

    elif isinstance(queries, str):  # queries in a file format

        with open(queries, encoding="utf-8") as queries_file:
            query_list = queries_file.readlines()
            empty_lines_number = 0
            for query_id, query_line in enumerate(query_list, 1):
                query = query_line.strip("\r\n")
                if query != "":
                    query_id -= empty_lines_number  # only count non empty lines

                    relevant_docs = searcher.relevant_docs_from_posting(query)  # retrieve all relevant documents
                    ranked_docs = searcher.ranker.rank_relevant_doc(relevant_docs)  # rank documents by score
                    top_relevant_documents = searcher.ranker.retrieve_top_k(ranked_docs, k)  # top k relevant documents

                    for doc_id, score in top_relevant_documents:
                        print("Tweet id: {id} Score: {score}".format(id=doc_id, score=score))
                else:
                    empty_lines_number += 1


def main(corpus_path, output_path, stemming, queries, num_doc_to_retrieve):

    if stemming:
        output_path += "\\WithStem\\"
    else:
        output_path += "\\WithoutStem\\"

    # build retrieval model
    corpus_size, average_document_length = run_engine(corpus_path, output_path, stemming)

    # load inverted index from disk
    inverted_index = load_index(output_path)

    search_and_rank_query(queries, inverted_index, num_doc_to_retrieve, corpus_size, average_document_length,
                          output_path)
