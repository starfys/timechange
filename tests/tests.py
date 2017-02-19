#!/usr/bin/env python3
import sys
import os
import json
import numpy as np
from scipy import signal
import timechange
"""DEBUG
"""
import traceback


#Where to store sample data
SAMPLE_DATA_FOLDER = "SAMPLE_DATA"

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



#Create a timechange object
time_change = timechange.TimeChange()

#Check arguments
if len(sys.argv) < 2:
    print("Usage: {} SAMPLE".format(__file__)) 
    print("or     {} [DATA_FOLDER] [SCHEMA]".format(__file__))
    print("Where [DATA_FOLDER] is a directory containing data sorted into labeled subdirectories")
    print("And [SCHEMA] is a comma-separated list of columns to use from the csv files")
    print("If [SCHEMA] is empty, the program will use all columns")
    print("Example: {} data x,y,z".format(__file__))
    exit()
if sys.argv[1] == "SAMPLE":
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
        progress_step = 100
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

else:
    data_folder = sys.argv[1]
    #Take the rest of the arguments as as a separated list and handle spaces
    schema = " ".join(sys.argv[2:]).strip("\"").split(",")
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
print("Number of training samples in database: {}".format(sum([len(data) for _, data in time_change.training_files.items()])))
#Set the schema
time_change.data_schema = schema.split(',')

#Try generating images for training dataset
try:
    #Generate images from dataset
    time_change.convert_all(method="fft", data_size=1024)
    #Store result
    result = "SUCCESS"
except Exception as e:
    #Print the error
    traceback.print_exc()
    #Store result
    result = "FAILURE"
print("Converting training data to images: {}".format(result))
print("Number of training images in database: {}".format(sum([len(data) for _, data in time_change.training_images.items()])))
