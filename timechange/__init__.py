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
from os import path
from configparser import ConfigParser
import shutil
import numpy as np
import pandas
from PIL import Image
from . import transform
from . import models

#Keras includes
from keras.preprocessing.image import ImageDataGenerator

#Default config file. Included here due to tab issues
default_config = """
[DEFAULT]
#The type of neural net to generate
#Settings for the chosen type will be stored under a
#section of the same name
model_type = convolutional_basic

[convolutional_basic]
#The number of convolutional blocks to use for the model
num_blocks = 3
#The number of filters for these blocks (comma-separated list)
#If the size of this list is less than num_blocks, the last value
#will be used for the remaining values

num_filters = 64,32,32

#Learning rate for training
learning_rate = 1e-2
"""

class TimeChange:
    def __init__(self, project_name="default", parent_folder=None):
        """Constructor
        raises Exception the project fails to either save or load
        """
        #TODO:better default name to avoid collision 
        #Store the project's name
        self.project_name = project_name
        #Sets the project parent folder
        if parent_folder is None:
            parent_folder = path.expanduser("~/timechange")
        #Stores where the project profile will be kept
        self.project_path = path.abspath(path.join(parent_folder, project_name))
        #Create the project parent folder if necessary
        #If not, assume the project already exists
        if not path.exists(self.project_path):
            #New project
            os.makedirs(self.project_path)
            #Make project skeleton
            os.mkdir(path.join(self.project_path, "csv"))
            os.mkdir(path.join(self.project_path, "images"))
            os.mkdir(path.join(self.project_path, "models"))
            #Create a parameters file
            with open(path.join(self.project_path, "parameters.conf"), "w") as config_file:
                config_file.write(default_config)
        else:
            #Existing project
            #Folder names and the file types within them
            folder_structure = {'csv':'csv', 'images':'png', 'models':'h5'}
            #Iterate over folder structure
            for folder_name, file_type in folder_structure.items():
                #Check if directory exists
                if path.exists(path.join(self.project_path, folder_name)):
                    #Check if all files in that folder are csv files
                    for label in os.scandir(path.join(self.project_path, folder_name)):
                        #So this works on 1 and 2-layer folders
                        try:
                            #Scan subdirectories
                            for entry in os.scandir(path.join(self.project_path, folder_name, label.name)):
                                #TODO: allow other extensions for ex: image
                                if not entry.name.endswith(file_type):
                                    raise Exception("{} is not a {} file".format(
                                        path.join(self.project_path, folder_name, entry.name),
                                        file_type))
                        except NotADirectoryError:
                            #Scan subfiles
                            #TODO: allow other extensions for ex: image
                            if not label.name.endswith(file_type):
                                raise Exception("{} is not a {} file".format(
                                    path.join(self.project_path, folder_name, label.name),
                                    file_type))

                else:
                    #directory does not exist
                    raise Exception("{} cannot be a timechange project because {} does not exist".format(
                        self.project_path,
                        path.join(self.project_path, folder_name)))
            #Check for the config file
            if not path.exists(path.join(self.project_path, "parameters.conf")):
                raise Exception("{} cannot be a timechange project because {} does not exist".format(
                    self.project_path,
                    path.join(self.project_path, "parameters.conf")))


        #Stores what csv columns to use
        #TODO: store this value in a file instead of as a private member
        self.columns = None #Default values
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
        if not path.exists(path.join(self.project_path, "csv", label)):
            os.mkdir(path.join(self.project_path, "csv", label))
        #Copy the csv file into the project
        #Uses the name of the original file.
        #TODO: generate better name
        shutil.copyfile(file_path, path.join(self.project_path, "csv", label, path.split(file_path)[1]))

    def remove_training_file(self, label, filename):
        """Removes a training file from a label
        Keyword arguments:
        label -- the label to store the filename under
        filename -- the filename to add to the project
        """
        #Removes the file with the given name from the label's directory
        os.remove(file_path, path.join(self.project_path, "csv", label, path.split(file_path)[1]))
        #Check to see if this was the last entry for a label
        if len(os.scandir(path.join(self.project_path, "csv", label))) == 0:
            #If this was the last entry, delete the label
            shutil.rmtree(path.join(self.project_path, "csv", label))
    def get_csv_labels(self):
        """Gets a list of labels based on the csv data set. Labels are always in alphabetical order"""
        return sorted([entry.name for entry in os.scandir(path.join(self.project_path, "csv"))])
    def get_image_labels(self):
        """Gets a list of labels based on the csv data set. Labels are always in alphabetical order"""
        return sorted([entry.name for entry in os.scandir(path.join(self.project_path, "images"))])
    def get_csv_columns(self, file_path):
        """Reads a csv file and returns the column names
        Keyword arguments:
        file_path -- path of file to read from
        Returns: A list of column names from the csv file
        """
        return list(pandas.read_csv(file_path, nrows=1).columns)
    def convert_csv(self, input_file_path, method="fft", chunk_size=64, fft_size=128, data_length=None, output_file_path=None):
        """Reads a csv file and returns the column names
        Preconditions: self.columns is set or the user wants to use all csv columns 
        Keyword arguments:
        input_file_path -- CSV file_path to read from
        method -- feature extraction method to use. Default: fft
        chunk_size -- number of samples per chunk (used for FFT method)
        output_file_path -- png file to output to. Uses a standard scheme if None
        """

        # Set default file_path if no argument specified
        # TODO: fix this to be more in line with the rest of the project structure
        if output_file_path is None:
            input_path = path.split(input_file_path)
            input_path[-1] = "converted_{}.png".format(input_path[-1])
            output_file_path = path.join(input_path)
        # Read the csv into a numpy array
        data = pandas.read_csv(input_file_path, usecols=self.columns).as_matrix().T
        # Handle padding.
        if data_length is not None:
            pad_amount = data_length - data.shape[1]
            data = np.pad(data, ((0,0), (0, pad_amount)), 'constant', constant_values=0.0)
        # Extract features from the numpy array
        # Uses same variable name since data is not needed after feature extraction
        data = transform.extract(data, method=method, chunk_size=chunk_size, fft_size=fft_size)
        # Generate an image from the resulting feature representation
        img = Image.fromarray((data * 255).astype(np.uint8), "RGB")
        #Save the image to the desired file path
        img.save(output_file_path)
        #Return the image's size
        return img.size
    def convert_all_csv(self, method="fft", chunk_size=64, fft_size=128):
        """Iterates over the training files set and generates corresponding images
        using the feature extraction method
        Keyword arguments:
        method -- Method used by extract_features to generate image data. Default: fft"""
        # Set default columns if no argument specified
        if self.columns is None:
            self.columns = self.get_csv_columns(input_file_path)
        #Clear subfolders in image folder without deleting images folder
        #This is to make sure old images don't stick around
        #In case a file has been removed
        #TODO: caching
        for label in os.scandir(path.join(self.project_path, "images")):
            #Get file path from direntry
            label = path.abspath(label.path)
            #Delete the folder
            try:
                shutil.rmtree(label)
            #TODO: Handle exceptions better
            except FileNotFoundError as _:
                pass
        #Store the number of data samples
        self.num_samples = 0
        #Get length of longest csv file
        self.csv_length = 0
        #Iterate over labels
        for label in self.get_csv_labels():
            #Iterate over a label's csv files
            for csv_file in os.scandir(path.join(self.project_path, "csv", label)):
                with open(csv_file.path, 'r') as csv_file_handle:
                    #Get number of lines in file and keep track of longest file
                    self.csv_length = max(self.csv_length, len(csv_file_handle.readlines()))
        #Generate new images
        #Iterate over labels
        for label in self.get_csv_labels():
            #Make a folder for the label
            os.mkdir(path.join(self.project_path, "images", label))
            #Iterate over a label's csv files
            for csv_file in os.scandir(path.join(self.project_path, "csv", label)):
                #Generate an image name from the original file's name
                #Removes csv and adds png
                new_name = '.'.join(csv_file.name.split('.')[:-1] + ['png'])
                #TODO: make all csv files the same size by padding 0s to the smaller files
                #Generate the image file
                #Store the size of the image
                #TODO: Store this in a config file
                self.image_size = self.convert_csv(
                        csv_file.path,
                        method=method,
                        chunk_size=chunk_size,
                        fft_size=fft_size,
                        data_length = self.csv_length,
                        output_file_path=path.join(self.project_path, "images", label, new_name))
                #Increment the number of samples
                self.num_samples += 1
    def build_model(self):
        """Generates a neural net model based on the image size, the parameters set in parameters.conf,
        and the number of output classes
        Prerequisites: convert_all has been run"""
        #Generate input shape from image parameters generated by input
        if self.image_size is None:
            raise Exception("Conversion process must occur before generating model")
        input_shape = (3, *self.image_size)
        #Load the configuration file
        config = ConfigParser()
        config.read(path.join(self.project_path, "parameters.conf"))
        #Generate the model and store it
        try:
            #Try to generate a model
            self.model = models.generate_model(len(self.get_image_labels()), input_shape, config)
        except Exception as exc:
            #Something went wrong.
            raise exc
    def train(self, num_epochs=10):
        """Trains a neural net model on the project's dataset
        Preconditions: A Keras model is stored to self.model,
                       convert_all_csv(...) has been run and has generated images for training
        """
        #Check to see if a model has been generated
        if self.model is None:
            raise Exception("There is no model stored. Please generate a model before training")
        #Create a training data generator from the images folder
        train_generator = ImageDataGenerator(
                rescale = 1.0/255.0, #Scale the 0-255 pixel values down to 0.0-1.0
                dim_ordering = 'th' #samples, channels, width, height
                ).flow_from_directory(
                path.join(self.project_path, 'images'), #Read training data from the project's images dir
                target_size=self.image_size, #Resize must be set or the generator will automatically choose dimensions
                color_mode='rgb', #TODO: take another look at this
                batch_size=64, #TODO: customize this
                shuffle=True, #Shuffle the data inputs. TODO: set a random seed
                class_mode="categorical") #TODO: consider binary mode for systems with only 2 labels
        #Invert the label dictionary and store it
        #TODO: Store this in a file
        self.labels = {label: index for index, label in train_generator.class_indices.items()}
        #Train the model
        #TODO: k-fold validation
        try:
            self.model.fit_generator(train_generator,
                                    samples_per_epoch=self.num_samples, #TODO: better solution
                                    nb_epoch=num_epochs) #TODO: customize this
        except Exception as err:
            #TODO: Handle error better
            raise Exception("Something went wrong with the training process")
    def load_model(self, input_filename):
        """Loads a neural net model from a file
        Keyword arguments:
        input_filename -- h5 file to load the model from
        """
        self.model.load_weights(input_filename)
    def save_model(self, output_filename=None):
        """Saves the current neural net model
        Keyword arguments:
        output_filename -- The place the model will be stored. None stores it in the profile"""
        #Handle default filenames
        if output_filename is None:
            output_filename = path.join(self.project_path, "models", "latest.h5")
            pass
        #Save the model
        self.model.save_weights(output_filename)
    def get_statistics(self):
        """Gets statistics from the model
        Return value: dictionary of statistical values
        """
        return {'accuracy':'not accurate'}
