import search_engine
from os import getcwd as os_getcwd
from spellchecker import SpellChecker

if __name__ == '__main__':

    # corpus_path = os_getcwd()
    # output_path = os_getcwd() + "postings\\"
    # stemming = True
    # queries = None
    # num_doc_to_retrieve = 2000
    # search_engine.main(corpus_path, output_path, stemming, queries, num_doc_to_retrieve)

    spell = SpellChecker()
    text = "qalk Qalk QALK"
    for term in text.split():
        res = spell.candidates(term)
        for candid in res:
            print("Origin: {}".format(term))
            print("Result: {}".format(candid))
