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
        raises RuntimeError the project fails to either save or load
        """
        #TODO:better default name to avoid collision 
        #Store the project's name
        self.project_name = project_name
        #Sets the project parent folder
        if parent_folder is None:
            parent_folder = os.path.expanduser("~/timechange")
        #Stores where the project profile will be kept
        self.project_path = os.path.abspath(os.path.join(parent_folder, project_name))
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
            #Folder names and the file types within them
            folder_structure = {'csv':'csv', 'images':'png', 'models':'h5'}
            #Iterate over folder structure
            for folder_name, file_type in folder_structure.items():
                #Check if directory exists
                if os.path.exists(os.path.join(self.project_path, folder_name)):
                    #Check if all files in that folder are csv files
                    for label in os.scandir(os.path.join(self.project_path, folder_name)):
                        #So this works on 1 and 2-layer folders
                        try:
                            #Scan subdirectories
                            for entry in os.scandir(os.path.join(self.project_path, folder_name, label.name)):
                                #TODO: allow other extensions for ex: image
                                if not entry.name.endswith(file_type):
                                    raise RuntimeError("{} is not a {} file".format(
                                        os.path.join(self.project_path, folder_name, entry.name),
                                        file_type))
                        except NotADirectoryError:
                            #Scan subfiles
                            #TODO: allow other extensions for ex: image
                            if not label.name.endswith(file_type):
                                raise RuntimeError("{} is not a {} file".format(
                                    os.path.join(self.project_path, folder_name, label.name),
                                    file_type))

                else:
                    #directory does not exist
                    raise RuntimeError("{} cannot be a timechange project because {} does not exist".format(
                        self.project_path,
                        os.path.join(self.project_path, folder_name)))

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
    def convert_csv(self, input_file_path, method="fft", chunk_size=64, data_length=None, output_file_path=None):
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
        # TODO: fix this to be more in line with the rest of the project structure
        if output_file_path is None:
            input_path = os.path.split(input_file_path)
            input_path[-1] = "converted_{}.png".format(input_path[-1])
            output_file_path = os.path.join(input_path)
        # Read the csv into a numpy array
        data = pandas.read_csv(input_file_path, usecols=self.columns).as_matrix().T
        # Handle padding.
        if data_length is not None:
            pad_amount = data_length - data.shape[1]
            data = np.pad(data, ((0,0), (0, pad_amount)), 'constant', constant_values=0.0)
        # Extract features from the numpy array
        # Uses same variable name since data is not needed after feature extraction
        data = transform.extract(data, method=method, chunk_size=chunk_size)
        # Generate an image from the resulting feature representation
        img = Image.fromarray((data * 255).astype(np.uint8), "RGB")
        #Save the image to the desired file path
        img.save(output_file_path)
        #Return the image's size
        return img.size
    def convert_all_csv(self, method=None, chunk_size=64):
        """Iterates over the training files set and generates corresponding images
        using the feature extraction method
        Keyword arguments:
        method -- Method used by extract_features to generate image data. Default: fft"""
        #TODO: implement this

        #Set a default method if none is set
        if method is None:
            method = self.default_method
        #Clear subfolders in image folder without deleting images folder
        #TODO: caching
        for label in os.scandir(os.path.join(self.project_path, "images")):
            #Get file path from direntry
            label = os.path.abspath(label.path)
            try:
                shutil.rmtree(label)
            except FileNotFoundError as exc:
                pass
        #Store the number of data samples
        self.num_samples = 0
        #Get length of longest csv file
        self.csv_length = 0
        #Iterate over labels
        for label in self.get_labels():
            #Iterate over a label's csv files
            for csv_file in os.scandir(os.path.join(self.project_path, "csv", label)):
                with open(csv_file.path, 'r') as csv_file_handle:
                    #Get number of lines in file and keep track of longest file
                    self.csv_length = max(self.csv_length, len(csv_file_handle.readlines()))
        #Generate new images
        #Iterate over labels
        for label in self.get_labels():
            #Make a folder for the label
            os.mkdir(os.path.join(self.project_path, "images", label))
            #Iterate over a label's csv files
            for csv_file in os.scandir(os.path.join(self.project_path, "csv", label)):
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
                        data_length = self.csv_length,
                        output_file_path=os.path.join(self.project_path, "images", label, new_name))
                #Increment the number of samples
                self.num_samples += 1
    def train(self, num_epochs=10):
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
                color_mode='rgb', #TODO: take another look at this
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
