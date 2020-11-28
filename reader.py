import os
import pandas as pd

from glob import glob


class ReadFile:
    def __init__(self, corpus_path):
        self.corpus_path = corpus_path

    def read_file(self, file_name):
        """
        This function is reading a parquet file contains several tweets
        The file location is given as a string as an input to this function.
        :param file_name: string - indicates the path to the file we wish to read.
        :return: a dataframe contains tweets.
        """

        full_path = os.path.join(self.corpus_path, file_name)
        df = pd.read_parquet(full_path, engine="pyarrow")
        return df.values.tolist()

    def read_corpus(self):

        """
        Reads all corpus. The corpus location is given in the configuration file.
        Corpus is located in a directory named "Data"
        Each data file is a parquet file
        :return: a set of all the documents in the corpus as dataframes
        """

        corpus = []  # final document's set

        # collect all parquet data files
        files = glob(self.corpus_path + "/Data/**/*.parquet", recursive=True)

        for file in files:

            documents_list = self.read_file(file)
            # Iterate over every document in the file
            for document_as_list in documents_list:
                corpus.append(document_as_list)
                print(document_as_list[0])

        return corpus
