#!/usr/bin/env python3
from collections import defaultdict
import sys
import os
import numpy as np
import pandas
from PIL import Image

class TimeChange:
    def __init__(self, model=None):
        """Constructor
        """
        self.training_files = defaultdict(set)
        self.training_images = defaultdict(set)
        self.model = model
        self.data_schema = None
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
            # Perform a fourier transform on the data
            features = np.fft.rfft(time_series, n=data_size)
            #Extract real features
            real_features = np.real(features)
            #Normalize real features
            real_features /= np.max(real_features)
            #Extract imaginary features
            imag_features = np.imag(features)
            #Normalize imaginary features
            imag_features /= np.max(imag_features)
            #TODO: Extract complex features
            # Normalize the data against the maximum element
            return np.concatenate((real_features, imag_features))
        else:
            print("Feature extraction method {} invalid.".format(method), file=sys.stderr)
            return None
    def read_csv(self, filename, *args, **kwargs):
        """Reads a time-series data csv into a file
        Keyword arguments:
        filename -- filename to read from
        *args -- Extra args to pass the pandas parser
        """
        return pandas.read_csv(filename, *args, **kwargs).as_matrix().T
    def get_csv_columns(self, filename, *args, **kwargs):
        """Reads a csv file and returns the column names
        Keyword arguments:
        filename -- filename to read from
        *args -- Extra args to pass the pandas parser
        """
        return list(pandas.read_csv(filename, nrows=1, *args, **kwargs).columns)
    def convert_csv(self, input_filename, output_filename=None, method="fft", data_size=None):
        """Reads a csv file and returns the column names
        Keyword arguments:
        input_filename -- CSV filename to read from
        output_filename -- png file to output to. Uses a standard scheme if None
        columns -- columns to read. If this is set to None, use all
        method -- feature extraction method to use
        """
        # Set default columns if no argument specified
        if self.data_schema is None:
            self.data_schema = self.get_csv_columns(input_filename)
        # Set default filename if no argument specified
        if output_filename is None:
            input_path = os.path.split(input_filename)
            input_path[-1] = "converted_{}.png".format(input_path[-1])
            output_filename = os.path.join(input_path)
        # Read the csv into a numpy array
        data = self.read_csv(input_filename, usecols=self.data_schema)
        # Determine an FFT size
        if data_size is None:
            #Get the next nearest power of 2 to the data size
            data_size = int(2 ** np.ceil(np.log2(data.shape[1])))
        #TODO: chunking
        # Extract features from the numpy array
        # Uses same variable name since data is not needed after feature extraction
        data = self.extract_features(data, method="fft", data_size=data_size)
        # Generate an image from the resulting feature representation
        Image.fromarray(data * 255, "L").save(output_filename)
    def set_data_schema(new_data_schema):
        """Sets the list of columns that will be read when handling a data set
        Keyword arguments:
        new_data_schema -- The list of columns to be used when reading data
        """
        self.data_schema = new_data_schema
    def convert_all(self, method=None, data_size=1024):
        """Iterates over the training files set and generates corresponding images
        using the feature extraction method
        Keyword arguments:
        method -- Method used by extract_features to generate image data"""
        #Clear the image reference cache
        #TODO: DELETE OLD IMAGES OPTIONALLY
        self.training_images.clear()
        for label, filenames in self.training_files.items():
            for input_filename in filenames:
                #TODO: find file with most lines and use this to determine FFT pad size
                #Generate a new filename for the output image
                output_filename = list(os.path.split(input_filename)) #Splits the filename
                output_filename[-1] = "{}_{}.png".format(label, output_filename[-1])
                output_filename = os.path.join(*output_filename)
                #Convert the csv
                self.convert_csv(input_filename, output_filename, method=method, data_size=data_size)
                #Add image to dataset
                self.training_images[label].add(output_filename)
    def list_images(self):
        for label, images in self.training_images.items():
            print(label)
            for image in images:
                print("\t{}".format(image))
