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

import sys
import os
import shutil
import json
import numpy as np
from scipy import signal
#Add one level up to timechange
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import timechange
"""DEBUG
"""
import traceback
#Keras includes
from keras.preprocessing.image import ImageDataGenerator

#Where to store the timechange project
PROJECT_PARENT = os.path.dirname(os.path.abspath(__file__)) #Same folder as script
#Name of the timechange project
PROJECT_NAME = "TEST_PROJECT"
#Where to store sample data
SAMPLE_DATA_FOLDER = os.path.join(PROJECT_PARENT, "SAMPLE_DATA")
VALIDATION_DATA_FOLDER = os.path.join(PROJECT_PARENT, "VALIDATION_DATA")
"""Sample dataset parameters
"""
#Number of training samples per category
NUM_TRAINING_SAMPLES = 1000
#Number of rows per training sample
NUM_TRAINING_ROWS = 1000
#Number of columns per training sample
NUM_TRAINING_COLUMNS = 3
#Bounds and parameters for sample waves
SAMPLE_LEFT_BOUND = 0
SAMPLE_RIGHT_BOUND = 100
SAMPLE_AMPLITUDE_MIN = -5
SAMPLE_AMPLITUDE_MAX = 5
SAMPLE_FREQUENCY_MIN = -10
SAMPLE_FREQUENCY_MAX = 10
SAMPLE_SHIFT_MIN = -10
SAMPLE_SHIFT_MAX = 10
#Number of samples to validate per category
NUM_VALIDATION_SAMPLES = 100

#Delete the test project from previous iterations (if it exists)
try:
    shutil.rmtree(os.path.join(PROJECT_PARENT, PROJECT_NAME))
except FileNotFoundError as exc:
    pass
#Create a timechange object
#Store the timechange profile along with this script
time_change = timechange.TimeChange(PROJECT_NAME, PROJECT_PARENT)
#Set data folder and schema
data_folder = SAMPLE_DATA_FOLDER
#Same as the csv header
schema = ",".join(map(str, range(NUM_TRAINING_COLUMNS)))
#Check if sample data already exists
if os.path.isdir(SAMPLE_DATA_FOLDER):
    print("Sample data already exists, continuing to training")
else:
    print("Generating sample training data")
    for wave_type in ("sine","square","sawtooth"):
        os.makedirs(os.path.join(SAMPLE_DATA_FOLDER, wave_type))
    #CSV header. Columns named by numbers (very creative)
    #Space to create the waves over
    wave_space = np.linspace(SAMPLE_LEFT_BOUND, SAMPLE_RIGHT_BOUND, NUM_TRAINING_ROWS, endpoint=True, dtype=np.float32)
    #Used to display progress
    last_progress = 0
    progress_step = NUM_TRAINING_SAMPLES // 10
    #Generate the training data
    for sample_num in range(NUM_TRAINING_SAMPLES):
        #Generate a sample file name. Used for all waves because they"re sorted by folder
        sample_file_name = "SAMPLE_{0:05d}.csv".format(sample_num)
        """
            GENERATE SINE WAVE
        """
        columns = []
        for _ in range(NUM_TRAINING_COLUMNS):
            columns.append(np.random.uniform(SAMPLE_AMPLITUDE_MIN, SAMPLE_AMPLITUDE_MAX) *
                    np.sin(np.random.uniform(SAMPLE_FREQUENCY_MIN, SAMPLE_FREQUENCY_MAX) * (wave_space - 
                        np.random.uniform(SAMPLE_SHIFT_MIN, SAMPLE_SHIFT_MAX))))
        #Convert list to numpy array, transpose it, and save to file
        columns = np.array(columns).T 
        np.savetxt(os.path.join(SAMPLE_DATA_FOLDER, "sine", sample_file_name), columns, delimiter=",", header=schema, comments="")
        """
            GENERATE SQUARE WAVE
        """
        columns = []
        for _ in range(NUM_TRAINING_COLUMNS):
            columns.append(np.random.uniform(SAMPLE_AMPLITUDE_MIN, SAMPLE_AMPLITUDE_MAX) *
                    signal.square(np.random.uniform(SAMPLE_FREQUENCY_MIN, SAMPLE_FREQUENCY_MAX) * (wave_space - 
                        np.random.uniform(SAMPLE_SHIFT_MIN, SAMPLE_SHIFT_MAX))))
        #Convert list to numpy array, transpose it, and save to file
        columns = np.array(columns).T 
        np.savetxt(os.path.join(SAMPLE_DATA_FOLDER, "square", sample_file_name), columns, delimiter=",", header=schema, comments="")
        """
            GENERATE SAWTOOTH WAVE
        """
        columns = []
        for _ in range(NUM_TRAINING_COLUMNS):
            columns.append(np.random.uniform(SAMPLE_AMPLITUDE_MIN, SAMPLE_AMPLITUDE_MAX) *
                    signal.sawtooth(np.random.uniform(SAMPLE_FREQUENCY_MIN, SAMPLE_FREQUENCY_MAX) * (wave_space - 
                        np.random.uniform(SAMPLE_SHIFT_MIN, SAMPLE_SHIFT_MAX))))
        #Convert list to numpy array, transpose it, and save to file
        columns = np.array(columns).T 
        np.savetxt(os.path.join(SAMPLE_DATA_FOLDER, "sawtooth", sample_file_name), columns, delimiter=",", header=schema, comments="")
        #Print progress
        if (sample_num - progress_step) >= last_progress:
            print("Generating samples: {}% done".format((sample_num / NUM_TRAINING_SAMPLES) * 100))
            last_progress = sample_num
    print("Finished generating training data")
#Try reading a file database into timechange
try:
    #Read data into timechange object
    for label in os.scandir(data_folder):
        #Extract name from direntry object
        label = label.name
        label_path = os.path.join(data_folder, label)
        #Iterate over csv files for a label
        for data_filename in os.scandir(label_path):
            #Extract name from direntry object
            data_filename = data_filename.name
            #Ensure file is a csv file
            if data_filename.endswith(".csv"):
                #Add the file to the timechange dataset
                time_change.add_training_file(label, os.path.join(label_path, data_filename))
    #Store result
    result = "SUCCESS"
except Exception as e:
    #Print the error
    traceback.print_exc()
    #Store result
    result = "FAILURE"
#Show test results
print("Reading filenames into training database: {}".format(result))
#Set the column schema by splitting the csv header into label names
time_change.column = schema.split(',')
#Test the label list
print("The labels read in were: {}".format(','.join(time_change.get_labels())))
#Generate the images
try:
    time_change.convert_all_csv()
    result = "SUCCESS"
except:
    result = "FAILURE"
print("Converting CSV files into feature images: {}".format(result))
print("{} images generated".format(time_change.num_samples))
#Set up a neural net and train the model
#Basic convnet
from keras.models import Sequential
from keras.layers import Convolution2D, MaxPooling2D
from keras.layers import Activation, Dropout, Flatten, Dense
#First layer
model = Sequential()
model.add(Convolution2D(32, 3, 3, input_shape=(1, *time_change.image_size)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
#Second layer
model.add(Convolution2D(32, 3, 3))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
#Flattening layer
model.add(Flatten())  # this converts our 3D feature maps to 1D feature vectors
model.add(Dense(64))
model.add(Activation('relu'))
model.add(Dropout(0.5)) #Dropout layers help to reduce overfitting
model.add(Dense(len(time_change.get_labels()))) #Number of outputs corresponds to number of labels
model.add(Activation('softmax'))
model.compile(loss='categorical_crossentropy',
              optimizer='rmsprop',
              metrics=['accuracy'])
time_change.model = model
time_change.train(num_epochs=10)
#Save the generated model
time_change.save_model()

#Generate a small test set
#TODO: modularize this so it's not so copy-paste
print("Generating sample validatoin data")
for wave_type in ("sine","square","sawtooth"):
    try:
        os.makedirs(os.path.join(VALIDATION_DATA_FOLDER, wave_type))
    except FileExistsError as exc:
        pass
#CSV header. Columns named by numbers (very creative)
#Space to create the waves over
wave_space = np.linspace(SAMPLE_LEFT_BOUND, SAMPLE_RIGHT_BOUND, NUM_TRAINING_ROWS, endpoint=True, dtype=np.float32)
#Used to display progress
last_progress = 0
progress_step = NUM_VALIDATION_SAMPLES // 10
#Generate the training data
for sample_num in range(NUM_VALIDATION_SAMPLES):
    #Generate a sample file name. Used for all waves because they"re sorted by folder
    sample_file_name = "SAMPLE_{0:05d}.csv".format(sample_num)
    """
        GENERATE SINE WAVE
    """
    columns = []
    for _ in range(NUM_TRAINING_COLUMNS):
        columns.append(np.random.uniform(SAMPLE_AMPLITUDE_MIN, SAMPLE_AMPLITUDE_MAX) *
                np.sin(np.random.uniform(SAMPLE_FREQUENCY_MIN, SAMPLE_FREQUENCY_MAX) * (wave_space - 
                    np.random.uniform(SAMPLE_SHIFT_MIN, SAMPLE_SHIFT_MAX))))
    #Convert list to numpy array, transpose it, and save to file
    columns = np.array(columns).T 
    np.savetxt(os.path.join(VALIDATION_DATA_FOLDER, "sine", sample_file_name), columns, delimiter=",", header=schema, comments="")
    time_change.convert_csv(os.path.join(VALIDATION_DATA_FOLDER, "sine", sample_file_name), output_file_path=os.path.join(VALIDATION_DATA_FOLDER, "sine", "{}.png".format(sample_file_name))) 
    """
        GENERATE SQUARE WAVE
    """
    columns = []
    for _ in range(NUM_TRAINING_COLUMNS):
        columns.append(np.random.uniform(SAMPLE_AMPLITUDE_MIN, SAMPLE_AMPLITUDE_MAX) *
                signal.square(np.random.uniform(SAMPLE_FREQUENCY_MIN, SAMPLE_FREQUENCY_MAX) * (wave_space - 
                    np.random.uniform(SAMPLE_SHIFT_MIN, SAMPLE_SHIFT_MAX))))
    #Convert list to numpy array, transpose it, and save to file
    columns = np.array(columns).T 
    np.savetxt(os.path.join(VALIDATION_DATA_FOLDER, "square", sample_file_name), columns, delimiter=",", header=schema, comments="")
    time_change.convert_csv(os.path.join(VALIDATION_DATA_FOLDER, "square", sample_file_name), output_file_path=os.path.join(VALIDATION_DATA_FOLDER, "square", "{}.png".format(sample_file_name))) 
    """
        GENERATE SAWTOOTH WAVE
    """
    columns = []
    for _ in range(NUM_TRAINING_COLUMNS):
        columns.append(np.random.uniform(SAMPLE_AMPLITUDE_MIN, SAMPLE_AMPLITUDE_MAX) *
                signal.sawtooth(np.random.uniform(SAMPLE_FREQUENCY_MIN, SAMPLE_FREQUENCY_MAX) * (wave_space - 
                    np.random.uniform(SAMPLE_SHIFT_MIN, SAMPLE_SHIFT_MAX))))
    #Convert list to numpy array, transpose it, and save to file
    columns = np.array(columns).T 
    np.savetxt(os.path.join(VALIDATION_DATA_FOLDER, "sawtooth", sample_file_name), columns, delimiter=",", header=schema, comments="")
    #Convert the csv file to an image
    time_change.convert_csv(os.path.join(VALIDATION_DATA_FOLDER, "sawtooth", sample_file_name), output_file_path=os.path.join(VALIDATION_DATA_FOLDER, "sawtooth", "{}.png".format(sample_file_name))) 
    #Print progress
    if (sample_num - progress_step) >= last_progress:
        print("Generating validation samples: {}% done".format((sample_num / NUM_VALIDATION_SAMPLES) * 100))
        last_progress = sample_num
print("Finished generating test data")
#Create a validation data generator
#TODO: move this inside timechange class
validation_generator = ImageDataGenerator(
        rescale = 1.0/255.0, #Scale the 0-255 pixel values down to 0.0-1.0
        dim_ordering = 'th' #samples, channels, width, height
        ).flow_from_directory(
        VALIDATION_DATA_FOLDER, #Read training data from generated validation data folder
        target_size=time_change.image_size, #Resize must be set or the generator will automatically choose dimensions
        color_mode='grayscale', #TODO: take another look at this
        batch_size=32, #TODO: customize this
        shuffle=False, #No need to shuffle
        class_mode="categorical") #TODO: consider binary mode for systems with only 2 labels
#Validate the model against the training set
loss, accuracy = time_change.model.evaluate_generator(validation_generator, NUM_VALIDATION_SAMPLES * len(time_change.get_labels()))
print("Model loss: {}".format(loss))
print("Model accuracy {}%".format(accuracy * 100))
