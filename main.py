import search_engine
from os import getcwd as os_getcwd
from glob import glob
import utils
import matplotlib.pyplot as plt
from os.path import splitext as os_path_splitext


def reconstruct_from_postings(output_path, stemming):
    postings = glob(output_path + "\\{}\\*.pkl".format("WithStem" if stemming else "WithoutStem"), recursive=True)

    reconstructed = set()
    corpus_size = 0
    total_length = 0
    for posting in postings:

        if "inverted_idx" not in posting:

            splited_path = os_path_splitext(posting)
            print(splited_path)
            file = utils.load_obj(splited_path[0])

            for doc_list in file.values():

                for doc in doc_list:

                    doc_id = doc[0]
                    doc_length = doc[4]

                    if doc_id not in reconstructed:
                        reconstructed.add(doc_id)
                        total_length += doc_length
                        corpus_size += 1

    return corpus_size, float(total_length) / corpus_size


def report_analysis(output_path, stemming):
    with open("log.txt", "a") as log:
        log.write("with stemming:\n" if stemming else "without stemming:\n")

        # number of unique terms in the index
        if stemming:
            output_path += "\\WithStem\\"
        else:
            output_path += "\\WithoutStem\\"
        inverted_idx = search_engine.load_index(output_path)
        term_number = len(inverted_idx.keys())
        log.write("Numbers of terms in the index {ifStem} is: {num}\n".format(
            num=term_number, ifStem="with stemming" if stemming else "without stemming"))

        # top 10 max, min by total frequency
        sorted_index = [[entry[0], entry[1][2]] for entry in inverted_idx.items()]
        sorted_index.sort(key=lambda entry: entry[1], reverse=True)
        ranked_index = [[entry[0], entry[1], i] for i, entry in enumerate(sorted_index, 1)]

        log.write(" top 10 max: {}\n".format(ranked_index[:10]))
        log.write(" bottom 10 min: {}\n".format(ranked_index[-10:]))

        # zipf
        rank = [entry[2] for entry in ranked_index]  # x
        frequency = [entry[1] for entry in ranked_index]  # y

        plt.plot(rank, frequency, "-ok")
        plt.xlabel("rank")
        plt.ylabel("frequency")
        plt.title("Zipf law in twitter corpus")
        plt.savefig("Zipf law in twitter corpus.png")


def main():
    corpus_path = os_getcwd() + "\\Data"
    output_path = os_getcwd() + "\\postings"
    stemming = True
    queries = os_getcwd() + "\\queries.txt"
    num_doc_to_retrieve = 2000
    corpus_size, average_length = reconstruct_from_postings(output_path, stemming)

    # with open("log.txt", "a") as log:
    #     log.write("Corpus size {ifStem}: {num}\n".format(
    #         num=corpus_size, ifStem="with stemming" if stemming else "without stemming"))
    #
    #     log.write("Avrgdl size {ifStem}: {num}\n".format(
    #         num=average_length, ifStem="with stemming" if stemming else "without stemming"))

    # search_engine.main(corpus_path, output_path, stemming, queries, num_doc_to_retrieve, 9980027, 22.454247769069163)

    # report_analysis(output_path, stemming)


if __name__ == '__main__':
    main()
