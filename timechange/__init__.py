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
from queue import Queue
from threading import Thread
import sys
import os
from os import path
import shutil
from configparser import ConfigParser
import numpy as np
import pandas
from PIL import Image
from . import worker

#Keras includes

#Default parameter config file. Included here due to tab issues
default_parameter_config = """
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

num_filters = 16,8,8

#Learning rate for training
learning_rate = 1e-2
"""
#Default transform config file. Included here due to tab issues
default_transform_config = """
[DEFAULT]
#CSV columns to read
columns=
#Type of transform to run
method=fft
#Size of the chunks
chunk_size=64
#Size of the fft output
fft_size=128
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
                config_file.write(default_parameter_config)
            #Create a transform file
            with open(path.join(self.project_path, "transform.conf"), "w") as config_file:
                config_file.write(default_transform_config)
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
        # Create a queue to communicate with the worker thread
        self.worker_queue = Queue()
        # Create a queue to recieve messages from the worker thread
        self.result_queue = Queue()
        # Start a worker thread, passing argument
        self.worker = Thread(target=worker.worker_thread, name="worker", args=(self.project_path, self.worker_queue, self.result_queue), daemon=True)
        self.worker.start()
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
    def set_columns(self, columns):
        """Sets the CSV columns to be used by the transform process"""
        #Load the config for transform parameters
        transform_config = ConfigParser()
        transform_config.read(path.join(self.project_path, "transform.conf"))
        transform_config["DEFAULT"]["columns"] = ",".join(map(str, columns))
        with open(path.join(self.project_path, "transform.conf"), "w") as transform_config_file:
            transform_config.write(transform_config_file)
    def set_transform_parameters(self, **kwargs):
        """Writes transform parameters to the transform configuration"""
        #Load the config for transform parameters
        transform_config = ConfigParser()
        transform_config.read(path.join(self.project_path, "transform.conf"))
        for parameter, value in kwargs.items():
            transform_config["DEFAULT"][parameter] = value
        with open(path.join(self.project_path, "transform.conf"), "w") as transform_config_file:
            transform_config.write(transform_config_file)
    def get_csv_columns(self, file_path):
        """Reads a csv file and returns the column names
        Keyword arguments:
        file_path -- path of file to read from
        Returns: A list of column names from the csv file
        """
        return list(pandas.read_csv(file_path, nrows=1).columns)
    def convert_all_csv(self):
        """Tells the worker thread to perform transformation on the csv data
        Preconditions
            CSV files have been added to the project with add_training_file
        """
        self.worker_queue.put({"command":"transform"})
    def build_model(self):
        """Tells the worker thread to build a keras model based on project_path/parameters.conf
        Preconditions
            A project_path/parameters.conf is a valid model parameter file
        """
        self.worker_queue.put({"command":"build_model"})
    def train(self):
        """Tells the worker thread to start training a keras model based on the image data
        Preconditions
            Data has been generated with convert_all_csv
            A valid model has been generated with build_model
        """
        self.worker_queue.put({"command":"train"})
        return {"acc":[0], "loss":[0]}
