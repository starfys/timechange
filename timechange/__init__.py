#!/usr/bin/env python3
from collections import defaultdict
import sys
import numpy as np
import pandas

class TimeChange:
    def __init__(self, model=None):
        """Constructor"""
        print("Constructor called")
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
    def time_series_to_image(time_series, method="fft"):
        """Extracts features from a time series or array of time series and outputs an image
        Keyword arguments:
        time_series -- A numpy array or array of numpy arrays representing the time series data
        """
        #TODO: implement this
        if method == "fft":
            return np.abs(np.fft.fft(time_series))
        else:
            print("Feature extraction method {} invalid.".format(method), file=sys.stderr)
            return None
