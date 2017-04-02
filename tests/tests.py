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

import random
import sys
import os
import shutil
import json
import numpy as np
from scipy import signal
#Set up the keras image backend
from keras.backend import common as K
K.set_image_dim_ordering('th')
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
NUM_TRAINING_SAMPLES = 2000
#Number of rows per training sample
MIN_ROWS = 100
MAX_ROWS = 1000
#Number of columns per training sample
NUM_COLUMNS = 3
#Bounds and parameters for sample waves
SAMPLE_LEFT_BOUND = 0.0
SAMPLE_RIGHT_BOUND = 100.0
SAMPLE_AMPLITUDE_MIN = -5.0
SAMPLE_AMPLITUDE_MAX = 5.0
SAMPLE_FREQUENCY_MIN = -100.0
SAMPLE_FREQUENCY_MAX = 100.0
SAMPLE_SHIFT_MIN = -10.0
SAMPLE_SHIFT_MAX = 10.0
#Number of samples to validate per category
NUM_VALIDATION_SAMPLES = 1000
#Types of waves to generate
WAVE_TYPES = ["sine", "square", "sawtooth"]
#Parameters for data conversion
CONVERT_CHUNK_SIZE=64
#Metaparameters for training
NUM_EPOCHS=20

#Seed the random number generator
random.seed(413)
np.random.seed(413);



#Delete the test project from previous iterations (if it exists)
try:
    shutil.rmtree(os.path.join(PROJECT_PARENT, PROJECT_NAME))
except FileNotFoundError as exc:
    pass
#Create a timechange object
#Store the timechange profile along with this script
time_change = timechange.TimeChange(PROJECT_NAME, PROJECT_PARENT)

"""
=======================================
Sample data generation
=======================================
"""
#Generate random data for a specific wave function
def random_wave(wave_type, length):
    #Generate random parameters
    amplitude = np.random.uniform(SAMPLE_AMPLITUDE_MIN,SAMPLE_AMPLITUDE_MAX)
    frequency = np.random.uniform(SAMPLE_FREQUENCY_MIN,SAMPLE_FREQUENCY_MAX)
    shift = np.random.uniform(SAMPLE_SHIFT_MIN,SAMPLE_SHIFT_MAX)
    #Generate the linear space
    wave_space = np.linspace(SAMPLE_LEFT_BOUND, SAMPLE_RIGHT_BOUND, length, endpoint=True, dtype=np.float32)
    #Apply the random changes to the wave
    wave_space = frequency * (wave_space - shift)
    #Generate the wave
    if wave_type == 'sine':
        return amplitude * np.sin(wave_space)
    elif wave_type == 'square':
        return amplitude * signal.square(wave_space)
    elif wave_type == 'sawtooth':
        return amplitude * signal.sawtooth(wave_space)
    else:
        raise Exception("Invalid wave type")
#Set data folder and schema
data_folder = SAMPLE_DATA_FOLDER
#Same as the csv header
column_names = list(map(str, range(NUM_COLUMNS)))
#Check if sample data already exists
if os.path.isdir(SAMPLE_DATA_FOLDER):
    print("Sample data already exists, continuing to training")
else:
    print("Generating sample training data")
    for wave_type in ("sine","square","sawtooth"):
        os.makedirs(os.path.join(SAMPLE_DATA_FOLDER, wave_type))
    #Used to display progress
    last_progress = 0
    progress_step = NUM_TRAINING_SAMPLES // 10
    #Generate the training data
    for sample_num in range(NUM_TRAINING_SAMPLES):
        #Generate a sample file name. Used for all waves because they"re sorted by folder
        sample_file_name = "SAMPLE_{0:05d}.csv".format(sample_num)
        #Generate a csv file for each wave type
        for wave_type in WAVE_TYPES:
            #Generate a bunch of wave rows
            sample_length = np.random.randint(MIN_ROWS, MAX_ROWS)
            wave_data = np.array([random_wave(wave_type,
                                sample_length)
                                for _ in range(NUM_COLUMNS)
                               ])
            np.savetxt(os.path.join(SAMPLE_DATA_FOLDER, wave_type, sample_file_name),
                       wave_data.T,
                       delimiter=",",
                       header=",".join(column_names),
                       comments="")
        #For printing progress
        if (sample_num - progress_step) >= last_progress:
            print("Generating samples: {}% done".format((sample_num / NUM_TRAINING_SAMPLES) * 100))
            last_progress = sample_num
    print("Finished generating training data")

"""
=======================================
File import
=======================================
"""
print("Importing files into timechange")
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
print("Finished importing files into timechange")

#Set the column schema by splitting the csv header into label names
time_change.columns = column_names
#Test the label list
print("The labels read in were: {}".format(','.join(time_change.get_csv_labels())))
#Generate the images
try:
    time_change.convert_all_csv(method="fft", chunk_size=CONVERT_CHUNK_SIZE)
    print("Converting CSV files into feature images: SUCCESS")
except:
    raise Exception("CSV conversion failed")
print("{} images generated".format(time_change.num_samples))

#Generate a model with the built in generator
time_change.build_model()
#Train the model
time_change.train(num_epochs=NUM_EPOCHS)
#Save the generated model
time_change.save_model()

#Generate a validation data set
#TODO: modularize this so it's not so copy-paste
print("Generating validation data")
for wave_type in ("sine","square","sawtooth"):
    try:
        os.makedirs(os.path.join(VALIDATION_DATA_FOLDER, wave_type))
    except FileExistsError:
        pass #Files already created, no problem. They are overwritten anyway

#Used to display progress
last_progress = 0
progress_step = NUM_VALIDATION_SAMPLES // 10
#Generate the training data
for sample_num in range(NUM_VALIDATION_SAMPLES):
    #Generate a sample file name. Used for all waves because they"re sorted by folder
    sample_file_name = "SAMPLE_{0:05d}.csv".format(sample_num)
    #Generate a csv file for each wave type
    for wave_type in WAVE_TYPES:
        #Generate a bunch of wave rows
        sample_length = np.random.randint(MIN_ROWS, MAX_ROWS)
        wave_data = np.array([random_wave(wave_type,
                            sample_length)
                            for _ in range(NUM_COLUMNS)
                           ])
        #Generate a csv file for the data
        np.savetxt(os.path.join(VALIDATION_DATA_FOLDER, wave_type, sample_file_name),
                   wave_data.T,
                   delimiter=",",
                   header=",".join(column_names),
                   comments="")
        #Generate a training image manually
        time_change.convert_csv(
                os.path.join(VALIDATION_DATA_FOLDER, wave_type, sample_file_name),
                chunk_size=CONVERT_CHUNK_SIZE,
                output_file_path=os.path.join(VALIDATION_DATA_FOLDER, wave_type, "{}.png".format(sample_file_name))) 
    #For printing progress
    if (sample_num - progress_step) >= last_progress:
        print("Generating samples: {}% done".format((sample_num / NUM_VALIDATION_SAMPLES) * 100))
        last_progress = sample_num
print("Finished generating validation data")

#Create a validation data generator
#TODO: move this inside timechange class
validation_generator = ImageDataGenerator(
        rescale = 1.0/255.0, #Scale the 0-255 pixel values down to 0.0-1.0
        dim_ordering = 'th' #samples, channels, width, height
        ).flow_from_directory(
        VALIDATION_DATA_FOLDER, #Read training data from generated validation data folder
        target_size=time_change.image_size, #Resize must be set or the generator will automatically choose dimensions
        color_mode='rgb', #TODO: take another look at this
        batch_size=32, #TODO: customize this
        shuffle=False, #No need to shuffle
        class_mode="categorical") #TODO: consider binary mode for systems with only 2 labels
#Validate the model against the training set
loss, accuracy = time_change.model.evaluate_generator(validation_generator, NUM_VALIDATION_SAMPLES * len(time_change.get_csv_labels()))
print("Model loss: {}".format(loss))
print("Model accuracy {}%".format(accuracy * 100))
