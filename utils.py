# pylint: disable = C0103, C0111, C0301, R0913, R0903, R0914

"""Some common utility functions"""

import os
import cPickle as pickle


def run_cmds(cmds):
    for cmd in cmds:
        # print cmd
        os.system(cmd)


def save_to_pickle(log, pkl_filepath):
    with open(pkl_filepath, 'wb') as pkl_file:
        pickle.dump(log, pkl_file)


def load_if_pickled(pkl_filepath):
    """Load if the pickle file exists. Else return empty list"""
    if os.path.isfile(pkl_filepath):
        with open(pkl_filepath, 'rb') as pkl_file:
            log = pickle.load(pkl_file)
    else:
        log = []
    return log
