import pickle
from os import makedirs as os_makedirs
from os.path import dirname as os_path_dirname


def save_obj(obj, name):
    """
    This function save an object as a pickle.
    :param obj: object to save
    :param name: name of the pickle file.
    :return: -
    """

    # if any directory on path doesn't exist - create it
    os_makedirs(os_path_dirname(name), exist_ok=True)

    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    """
    This function will load a pickle file
    :param name: name of the pickle file
    :return: loaded pickle file
    """
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)


def load_inverted_index(output_path=None):
    """
    This function loads the inverted index dictionary from disk
    :param output_path: path to inverted_idx.pkl
    :return: returns contents of inverted_idx file
    """

    with open(output_path + "\\inverted_idx.pkl", "rb") as f:
        return pickle.load(f)
