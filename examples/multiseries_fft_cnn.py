#!/usr/bin/env python3
"""
    Copyright 2017 Steven Sheffey
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import random
import sys
import os
import csv
import numpy as np
from scipy import signal
from sklearn.utils import shuffle

from keras.models import Sequential
from keras.layers import Convolution2D, MaxPooling2D
from keras.layers import Activation, Dropout, Flatten, Dense

CHUNK_SIZE = 100


#Runs a basic numpy FFT on a time series in chunks
def extract_features(time_series, chunk_size):
    time_series = time_series.reshape(-1, chunk_size)
    #Normalize the complex FFT output, convert the results into a properly shaped array
    return np.array([np.abs(np.fft.fft(time_series))])

#Get the folder name to read from
if len(sys.argv) < 2:
    print("Usage: multiseries_fft_cnn.py [folder]")
    exit()
data_folder = sys.argv[1]
#Define labels
labels = {}
#Stores training inputs
training_inputs = []
#Stores training outputs
training_outputs = []
#Read in data
for label in os.listdir(data_folder):
    labels[label] = len(labels)
    cur_path = os.path.join(data_folder, label)
    for data_filename in os.listdir(cur_path):
        with open(os.path.join(cur_path, data_filename), 'r') as data_file:
            print(data_filename, file=sys.stderr)
            data = [list(map(float, row[1:])) for row in list(csv.reader(data_file))[1:]]
            print(len(data))

"""
#Set up a fixed space for the waves
t = np.linspace(-10, 10, NUM_SAMPLES)

train_input = []
train_output = []
#Generate a training data set
for _ in range(TRAIN_SIZE):
    #Add a random square wave
    train_input.append(extract_features(signal.square(random.uniform(-10, 10) * np.pi * t)))
    train_output.append(np.array([1,0,0]))
    #Add a random square wave
    train_input.append(extract_features(signal.sawtooth(random.uniform(-10, 10) * np.pi * t)))
    train_output.append(np.array([0,1,0]))
    #Add a random sine wave
    train_input.append(extract_features(np.sin(random.uniform(-10, 10) * np.pi * t)))
    train_output.append(np.array([0,0,1]))
#Convert the training data to np arrays and shuffle
train_input, train_output = shuffle(np.array(train_input), np.array(train_output))

test_input = []
test_output = []
#Generate a testing data set
for _ in range(TEST_SIZE):
    #Add a random square wave
    test_input.append(extract_features(signal.square(random.uniform(-10, 10) * np.pi * t)))
    test_output.append(np.array([1,0,0]))
    #Add a random square wave
    test_input.append(extract_features(signal.sawtooth(random.uniform(-10, 10) * np.pi * t)))
    test_output.append(np.array([0,1,0]))
    #Add a random sine wave
    test_input.append(extract_features(np.sin(random.uniform(-10, 10) * np.pi * t)))
    test_output.append(np.array([0,0,1]))
#Convert the testing data to np arrays and shuffle
test_input, test_output = shuffle(np.array(test_input), np.array(test_output))

#Set up a very basic keras CNN.
#Based roughly on https://blog.keras.io/building-powerful-image-classification-models-using-very-little-data.html
model = Sequential()
model.add(Convolution2D(32, 3, 3, input_shape=(1, NUM_CHUNKS, CHUNK_SIZE)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Convolution2D(32, 3, 3))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Flatten())  # this converts our 3D feature maps to 1D feature vectors
model.add(Dense(64))
model.add(Activation('relu'))
model.add(Dropout(0.5))
model.add(Dense(3))
model.add(Activation('softmax'))

model.compile(loss='categorical_crossentropy',
              optimizer='rmsprop',
              metrics=['accuracy'])

#Train the model
model.fit(train_input,
          train_output,
          nb_epoch=NUM_EPOCH)

#Evaluate the model
train_results = model.evaluate(test_input, test_output)

#Print results
print("Accuracy of model: {}%".format(train_results[1] * 100))
"""
