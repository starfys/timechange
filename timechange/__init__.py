#!/usr/bin/env python3

"""Copyright 2017
Steven Sheffey <stevensheffey4@gmail.com>,
John Ford,
Eyasu Asrat,
Jordan Flowers,
Joseph Volmer,
Luke Stanley,
Serenah Smith, and
Chandu Budati

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from collections import defaultdict
import sys
import os
import numpy as np
import pandas
from PIL import Image
from . import transform

class TimeChange:
    def __init__(self, project_name="default", parent_folder=None):
        """Constructor
        throws exception if failure to load occurs
        """
        #TODO:better default name to avoid collision 
        #Store the project's name
        self.project_name = project_name
        #Sets the project parent folder
        if parent_folder is None:
            parent_folder = os.path.expanduser("~/timechange")
        #Stores where the project profile will be kept
        self.project_path = os.path.join(parent_folder, project_name)
        #Stores what csv columns to use
        self.columns = None #Default values
    def add_training_file(self, label, file_path):
        """Adds a training file to the dataset under a specific label
        Keyword arguments:
        label -- the label to store the filename under
        filename -- the filename to add to the database
        """
        #TODO: implement this
        print("DUMMY: {} REMOVED FROM {}".format(file_path, label))
    def remove_training_file(self, label, filename):
        """Removes a training file from a label
        Keyword arguments:
        label -- the label to store the filename under
        filename -- the filename to add to the project
        """
        #TODO: implement this
        print("DUMMY: {} REMOVED FROM {}".format(filename, label))
    def get_csv_columns(self, file_path, *args, **kwargs):
        """Reads a csv file and returns the column names
        Keyword arguments:
        filename -- filename to read from
        *args -- Extra args to pass the pandas parser
        Returns: A list of column names from the csv file
        """
        return list(pandas.read_csv(file_path, nrows=1, *args, **kwargs).columns)
    def convert_csv(self, input_file_path, method="fft", chunk_size=32, output_file_path=None):
        """Reads a csv file and returns the column names
        Preconditions: self.columns is set or the user wants to use all csv columns 
        Keyword arguments:
        input_file_path -- CSV file_path to read from
        method -- feature extraction method to use. Default: fft
        chunk_size -- number of samples per chunk (used for FFT method)
        output_file_path -- png file to output to. Uses a standard scheme if None
        """
        # Set default columns if no argument specified
        if self.columns is None:
            self.columns = self.get_csv_columns(input_file_path)
        # Set default file_path if no argument specified
        if output_file_path is None:
            input_path = os.path.split(input_file_path)
            input_path[-1] = "converted_{}.png".format(input_path[-1])
            output_file_path = os.path.join(input_path)
        # Read the csv into a numpy array
        data = pandas.read_csv(input_file_path, usecols=self.columns).as_matrix().T
        # Extract features from the numpy array
        # Uses same variable name since data is not needed after feature extraction
        data = transform.extract(data, method, data_size=chunk_size)
        # Generate an image from the resulting feature representation
        return Image.fromarray(data * 255, "L").save(output_file_path)
    def convert_all_csv(self, method=None, chunk_size=32):
        """Iterates over the training files set and generates corresponding images
        using the feature extraction method
        Keyword arguments:
        method -- Method used by extract_features to generate image data. Default: fft"""
        #TODO: implement this
        print("DUMMY: CONVERTING ALL CSV FILES")
    def train(self):
        """Trains a neural net model on the project's dataset
        """
        #TODO: implement this
        print("DUMMY: TRAINING A NEURAL NET MODEL")
    def load_model(self, input_filename):
        """Loads a neural net model from a file
        Keyword arguments:
        input_filename -- h5 file to load the model from
        """
        #TODO: implement
        print("DUMMY: LOADING MODEL FROM {}".format(input_filename))
        pass
    def save_model(self, output_filename=None):
        """Saves the current neural net model
        Keyword arguments:
        output_filename -- The place the model will be stored. None stores it in the profile"""
        #Handle default filenames
        if output_filename is None:
            #TODO: implement
            output_filename = "model.h5"
            pass
        #TODO: implement
        print("DUMMY: outputting model to {}".format(output_filename))
    def get_statistics(self):
        """Gets statistics from the model
        Return value: dictionary of statistical values
        """
        return {'accuracy':'not accurate'}
