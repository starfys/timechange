#!/usr/bin/env python3
from collections import defaultdict
import sys
import numpy as np
import pandas

class TimeChange:
    def __init__(self, model=None):
        """Constructor"""
        self.training_files = defaultdict(set)
        self.model = model
    def add_training_file(self, label, filename):
        """Adds a training file to the dataset under a specific label
        Keyword arguments:
        label -- the label to store the filename under
        filename -- the filename to add to the database
        """
        #TODO: check if file exists
        self.training_files[label].add(filename)
    def remove_training_file(self, label, filename):
        """Removes a training file from a label
        Keyword arguments:
        label -- the label to store the filename under
        filename -- the filename to add to the database
        """
        try:
            self.training_files[label].remove(filename)
        except KeyError:
            print("File {} not found under label {}".format(filename, label), file=sys.stderr)
    def extract_features(self, time_series, method="fft", data_size=None):
        """Extracts features from a time series or array of time series and outputs an image
        Keyword arguments:
        time_series -- A numpy array or array of numpy arrays representing the time series data
        """
        #Fix data size
        if data_size is None:
            data_size = time_series.shape[1]
        #TODO: implement this
        if method == "fft":
            features = np.abs(np.fft.rfft(time_series, n=data_size))
            return features / np.max(features)
        else:
            print("Feature extraction method {} invalid.".format(method), file=sys.stderr)
            return None
    def read_csv(self, filename, *args, **kwargs):
        """Reads a time-series data csv into a file
        Keyword arguments:
        filename -- filename to read into
        *args -- Extra args to pass the pandas parser
        """
        return pandas.read_csv(filename, *args, **kwargs).as_matrix().T
    def get_csv_columns(self, filename, *args, **kwargs):
        """Reads a csv file and returns the column names
        Keyword arguments:
        filename -- filename to read into
        *args -- Extra args to pass the pandas parser
        """
        return pandas.read_csv(filename, nrows=1, *args, **kwargs).columns

