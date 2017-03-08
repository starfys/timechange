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
import shutil
import numpy as np
import pandas
from PIL import Image
from . import transform

#Keras includes
from keras.preprocessing.image import ImageDataGenerator


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
        #Create the project parent folder if necessary
        #If not, assume the project already exists
        if not os.path.exists(self.project_path):
            #New project
            os.makedirs(self.project_path)
            #Make project skeleton
            os.mkdir(os.path.join(self.project_path, "csv"))
            os.mkdir(os.path.join(self.project_path, "images"))
            os.mkdir(os.path.join(self.project_path, "models"))
        else:
            #Existing project
            #Check if csv directory exists
            if os.path.exists(os.path.join(self.project_path, "csv")):
                #Check if all files in that folder are csv files
                for label in os.scandir(os.path.join(self.project_path, "csv")):
                    for entry in os.scandir(os.path.join(self.project_path, "csv", label.name)):
                        if not entry.name.endswith("csv"):
                            raise RuntimeError("{} is not a csv file".format(os.path.join(self.project_path, "csv", entry.name)))
            else:
                #CSV directory does not exist
                raise RuntimeError("{} cannot be a timechange project because {} does not exist".format(
                    self.project_path,
                    os.path.join(self.project_path, "csv")))
            #Check if images directory exists
            if os.path.exists(os.path.join(self.project_path, "images")):
                #Check if all files in that folder are csv files
                for label in os.scandir(os.path.join(self.project_path, "images")):
                    for entry in os.scandir(os.path.join(self.project_path, "images", label.name)):
                        #TODO: allow other extensions
                        if not entry.name.endswith("png"):
                            raise RuntimeError("{} is not a png file".format(os.path.join(self.project_path, "images", entry.name)))
            else:
                #Image directory does not exist
                raise RuntimeError("{} cannot be a timechange project because {} does not exist".format(
                    self.project_path,
                    os.path.join(self.project_path, "images")))
            #Check if images directory exists
            if os.path.exists(os.path.join(self.project_path, "models")):
                #Check if all files in that folder are csv files
                for label in os.scandir(os.path.join(self.project_path, "models")):
                    for entry in os.scandir(os.path.join(self.project_path, "models", label.name)):
                        if not entry.name.endswith("h5"):
                            raise RuntimeError("{} is not an h5 file".format(os.path.join(self.project_path, "models", entry.name)))
            else:
                #Image directory does not exist
                raise RuntimeError("{} cannot be a timechange project because {} does not exist".format(
                    self.project_path,
                    os.path.join(self.project_path, "models")))
        #Stores what csv columns to use
        #TODO: store this value in a file instead of as a private member
        self.columns = None #Default values
        #Stores the default conversion method
        #TODO: store this value in a file instead of as a private member
        self.default_method = "fft"
        #Stores the keras model used for training
        #TODO: store this in a configuration file
        self.model = None

    def add_training_file(self, label, file_path):
        """Adds a training file to the dataset under a specific label
        Keyword arguments:
        label -- the label to store the filename under
        filename -- the filename to add to the database
        """
        #If the folder for the label doesn't exist, create it
        if not os.path.exists(os.path.join(self.project_path, "csv", label)):
            os.mkdir(os.path.join(self.project_path, "csv", label))
        #Copy the csv file into the project
        #Uses the name of the original file.
        #TODO: generate better name
        shutil.copyfile(file_path, os.path.join(self.project_path, "csv", label, os.path.split(file_path)[1]))

    def remove_training_file(self, label, filename):
        """Removes a training file from a label
        Keyword arguments:
        label -- the label to store the filename under
        filename -- the filename to add to the project
        """
        #Removes the file with the given name from the label's directory
        os.remove(file_path, os.path.join(self.project_path, "csv", label, os.path.split(file_path)[1]))
    def get_labels(self):
        """Gets a list of labels based on the csv data set"""
        return [entry.name for entry in os.scandir(os.path.join(self.project_path, "csv"))]
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
        data = transform.extract(data, method=method)
        # Generate an image from the resulting feature representation
        img = Image.fromarray(data * 255, "L")
        #Save the image to the desired file path
        img.save(output_file_path)
        #Return the image's size
        return img.size
        data = transform.extract(data, method, data_size=chunk_size)
        # Generate an image from the resulting feature representation
        return Image.fromarray(data * 255, "L").save(output_file_path)
    def convert_all_csv(self, method=None, chunk_size=32):
        """Iterates over the training files set and generates corresponding images
        using the feature extraction method
        Keyword arguments:
        method -- Method used by extract_features to generate image data. Default: fft"""
        #TODO: implement this

        #Set a default method if none is set
        if method is None:
            method = self.default_method
        #Clear contents of image folder without deleting folder
        for label in os.scandir(os.path.join(self.project_path, "images")):
            #Get file path from direntry
            label = os.path.abspath(label.path)
            try:
                shutil.rmtree(label)
            except FileNotFoundError as exc:
                pass
        #Store the number of data samples
        self.num_samples = 0
        #Generate new images
        #Iterate over labels
        for label in self.get_labels():
            #Make a folder for the label
            os.mkdir(os.path.join(self.project_path, "images", label))
            #Iterate over a label's csv files
            for csv_file in os.scandir(os.path.join(self.project_path, "csv", label)):
                #Double check files is a csv file
                if not csv_file.name.lower().endswith(".csv"):
                    pass
                #Generate an image name from the original file's name
                #Removes csv and adds png
                new_name = '.'.join(csv_file.name.split('.')[:-1] + ['png'])
                #TODO: make all images the same size
                #Generate the image file
                #Store the size of the image
                #TODO: Store this in a config file
                self.image_size = self.convert_csv(os.path.abspath(csv_file.path), method=method, chunk_size=chunk_size, output_file_path=os.path.join(self.project_path, "images", label, new_name))
                #Increment the number of samples
                self.num_samples += 1
    def train(self, num_epochs=1):
        """Trains a neural net model on the project's dataset
        Preconditions: A Keras model is stored to self.model,
                       convert_all_csv(...) has been run and has generated images for training
        """
        #Create a training data generator from the images folder
        train_generator = ImageDataGenerator(
                rescale = 1.0/255.0, #Scale the 0-255 pixel values down to 0.0-1.0
                dim_ordering = 'th' #samples, channels, width, height
                ).flow_from_directory(
                os.path.join(self.project_path, 'images'), #Read training data from the project's images dir
                target_size=self.image_size, #Resize must be set or the generator will automatically choose dimensions
                color_mode='grayscale', #TODO: take another look at this
                batch_size=64, #TODO: customize this
                shuffle=True, #Shuffle the data inputs. TODO: set a random seed
                class_mode="categorical") #TODO: consider binary mode for systems with only 2 labels
        #Invert the label dictionary and store it
        #TODO: Store this in a file
        self.labels = {label: index for index, label in train_generator.class_indices.items()}
        #Train the model
        self.model.fit_generator(train_generator,
                                 samples_per_epoch=self.num_samples, #TODO: better solution
                                 nb_epoch=num_epochs) #TODO: customize this
        #TODO: k-fold validation
    def load_model(self, input_filename):
        """Loads a neural net model from a file
        Keyword arguments:
        input_filename -- h5 file to load the model from
        """
        #TODO: implement
        print("DUMMY: LOADING MODEL FROM {}".format(input_filename))
    def save_model(self, output_filename=None):
        """Saves the current neural net model
        Keyword arguments:
        output_filename -- The place the model will be stored. None stores it in the profile"""
        #Handle default filenames
        if output_filename is None:
            output_filename = os.path.join(self.project_path, "models", "latest.h5")
            pass
        #save the model
        self.model.save_weights(output_filename)
    def get_statistics(self):
        """Gets statistics from the model
        Return value: dictionary of statistical values
        """
        return {'accuracy':'not accurate'}
