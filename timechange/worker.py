#For reading config files
from configparser import ConfigParser
#For navigating filesystems
import os
from os import path
#For deleting directories
import shutil
#For padding data
import numpy as np
#For creating images from numpy arrays
from PIL import Image
#For reading csv files
import pandas
#For performing transformations
from . import transform

def convert_all_csv(project_path):
    """Iterates over the training files set and generates corresponding images
    using the feature extraction method
    Keyword arguments:
    method -- Method used by extract_features to generate image data. Default: fft"""
    # Extract parameters from project path
    transform_config = ConfigParser()
    transform_config.read(path.join(project_path, "transform.conf"))
    #Columns to read from the csv
    columns = transform_config["DEFAULT"].get("columns", "").split(",")
    #Default to reading all columns if this fails 
    if columns == [""]:
        columns = None
    #Type of transformation to apply 
    method = transform_config["DEFAULT"].get("method", "fft").strip("\"").strip("\'")
    #Size of chunks
    chunk_size = int(transform_config["DEFAULT"].get("chunk_size", "64").strip("\"").strip("\'"))
    #Size of fft output
    fft_size = int(transform_config["DEFAULT"].get("fft_size", "128").strip("\"").strip("\'"))
    #Clear subfolders in image folder without deleting images folder
    #This is to make sure old images don't stick around
    #In case a file has been removed
    for label in os.scandir(path.join(project_path, "images")):
        #Delete the folder
        try:
            shutil.rmtree(label.path)
        except FileNotFoundError as _:
            #Do nothing
            pass
    #Get length of longest csv file
    max_length = -1
    #Iterate over labels
    for label in os.scandir(path.join(project_path, "csv")):
        #Iterate over a label's csv files
        for csv_file in os.scandir(label.path):
            with open(csv_file.path, 'r') as csv_file_handle:
                #Get number of lines in file and keep track of longest file
                max_length = max(max_length, len(csv_file_handle.readlines()) - 1)
    #Generate new images
    #Iterate over labels
    for label in os.scandir(path.join(project_path, "csv")):
        #Make a folder for the label
        os.mkdir(path.join(project_path, "images", label.name))
        #Iterate over a label's csv files
        for csv_file in os.scandir(label.path):
            # Read the csv into a numpy array
            data = pandas.read_csv(csv_file.path, usecols=columns).as_matrix().T
            # Pad the csv
            data = np.pad(data, ((0,0), (0, max_length - data.shape[1])), 'constant', constant_values=0.0)
            # Extract features from the numpy array
            # Uses same variable name since data is not needed after feature extraction
            data = transform.extract(data, "fft", chunk_size=chunk_size, fft_size=fft_size)
            # TODO: normalize and imageize here
            # TODO: Don't imagize at all
            # Generate an image from the resulting feature representation
            img = Image.fromarray((data * 255).astype(np.uint8), "RGB")
            # Save the image to the desired file path
            # project/csv/example/1.csv becomes
            # project/images/example/1.png
            img.save(path.join(project_path, "images", label.name, "{}.png".format(path.splitext(csv_file.name)[0])))
def build_model(project_path):
    """Generates a compiled keras model for use in timechange training
    Parameters: 
    project_path -- path to a timechange project"""
    #Load keras
    from keras.models import Sequential
    from keras.layers import Convolution2D, MaxPooling2D
    from keras.layers import Input, Dense, Flatten, Dropout
    from keras.optimizers import SGD
    #Set dimension ordering
    from keras.backend import common as K
    K.set_image_dim_ordering('th')
    # Extract parameters from project folder
    image_folder = path.join(project_path, "images")
    # Extract number of classes from project by finding image folders
    num_classes = len(list(os.scandir(image_folder)))
    # Extract height and width of image
    image_height, image_width = Image.open(os.scandir(os.scandir(image_folder).__next__().path).__next__().path).size
    # Extract configuration
    config = ConfigParser()
    config.read(path.join(project_path,'parameters.conf'))
    #Extract model type from configuration
    model_type = config['DEFAULT'].get('model_type', 'convolutional_basic').strip('\"').strip('\'')
    #Initialize a model object
    model = Sequential()
    #Determine the block type for the model
    if model_type == 'convolutional_basic':
        #Extract and set parameters
        #Load number of blocks, with a default of 3
        num_blocks = int(config['convolutional_basic'].get('num_blocks', 3))
        #Load a filter size list, with a default
        num_filters = config['convolutional_basic'].get('num_filters', '8,8,8')
        #Parse the filter list into useful values
        num_filters = [int(f) for f in num_filters.split(',')]
        #Extend the filter list to make sure it accounts for all blocks
        if len(num_filters) < num_blocks:
            #Pad the filter sizes with the last element
            num_filters.extend(num_filters[-1] * (num_blocks - len(num_filters)))
        #Extract the learning rate
        learning_rate = float(config['convolutional_basic'].get('learning_rate', 1e-2))
        #Dynamically determine final layer's activation based
        #on the number of classes
        if num_classes == 2:
            final_activation = 'sigmoid'
            loss_measure = 'binary_crossentropy'
        else:
            final_activation = 'softmax'
            loss_measure = 'categorical_crossentropy'
        #Add the initial blocks
        model.add(Convolution2D(num_filters[0], 3, 3,
                                activation='relu',
                                input_shape=(3, image_height, image_width),
                                dim_ordering='th'))
        model.add(MaxPooling2D(pool_size=(2,2), dim_ordering='th'))
        #Add convolutional blocks. n-1 because the first was added already
        for layer in range(1, num_blocks):
            #TODO: Allow configuring the parameters on these
            model.add(Convolution2D(num_filters[layer], 3, 3,
                                    activation='relu',
                                    dim_ordering='th'))
            model.add(MaxPooling2D(pool_size=(2,2),
                                   dim_ordering='th'))
        #Create the final layers
        model.add(Flatten())
        #TODO: Allow configuring the parameters and existence of these
        model.add(Dense(64, activation='relu'))
        model.add(Dropout(0.3))
        model.add(Dense(num_classes, activation=final_activation))
    else:
        raise Exception("Invalid neural net type")
    #Compile the model
    optimizer = SGD(lr=learning_rate)
    #Compile the model
    model.compile(loss=loss_measure,
                  optimizer=optimizer,
                  metrics=['accuracy'])
    #Output the model
    return model

def train(project_path, model, output_queue):
    """Trains a neural net model on the project's dataset
    Parameters:
    project_path -- 
    """
    #Load keras
    from keras.preprocessing.image import ImageDataGenerator
    #Set dimension ordering
    from keras.backend import common as K
    K.set_image_dim_ordering('th')
    #Load the image size
    image_size = Image.open(os.scandir(os.scandir(path.join(project_path, "images")).__next__().path).__next__().path).size
    #Check to see if a model has been generated
    if model is None:
        raise Exception("There is no model stored. Please generate a model before training")
    #Determine class mode based on folder structure
    num_classes = len(list(os.scandir(path.join(project_path, "images"))))
    if num_classes == 1:
        raise Exception("The training data only contains one class")
    else:
        class_mode = "categorical"
    #Create a training data generator from the images folder
    train_generator = ImageDataGenerator(
            rescale = 1.0/255.0, #Scale the 0-255 pixel values down to 0.0-1.0
            dim_ordering = 'th' #samples, channels, width, height
            ).flow_from_directory(
            path.join(project_path, 'images'), #Read training data from the project's images dir
            target_size=image_size, #Resize must be set or the generator will automatically choose dimensions
            color_mode='rgb', #TODO: take another look at this
            batch_size=64, #TODO: customize this
            shuffle=True, #Shuffle the data inputs. TODO: set a random seed
            class_mode=class_mode) #TODO: consider binary mode for systems with only 2 labels
    #Design a callback to store training progress
    import keras
    class ProgressBarCallback(keras.callbacks.Callback):
        def on_train_begin(self, logs={}):
            return
        def on_train_end(self, logs={}):
            return
        def on_epoch_begin(self, epoch, logs={}):
            return
        def on_epoch_end(self, epoch, logs={}):
            print("Training epoch {} ended".format(epoch))
            return
        def on_batch_begin(self, batch, logs={}):
            return
    #Train the model
    #TODO: k-fold validation
    try:
        return model.fit_generator(
            train_generator,
            samples_per_epoch=len(train_generator.filenames), #TODO: better solution
            nb_epoch=20,
            callbacks=[ProgressBarCallback()]).history #TODO: customize this
    except Exception as err:
        #TODO: Handle error better
        raise Exception("Something went wrong with the training process: {}".format(str(err)))
def worker_thread(project_path, input_queue, output_queue):
    try:
        model = generate_model(project_path)
    except:
        model = None
    while True:
        job = input_queue.get()
        #Transform the data
        if job["command"] == "transform":
            #Attempt to transform data
            try:
                #Run the conversion process
                convert_all_csv(project_path)
                #Inform the main thread that transformation is finished
                output_queue.put({"type":"success", "job":"transform"})
            except Exception as err:
                output_queue.put({"type":"error", "job":"transform", "message": str(err)})
        #Build the keras model
        elif job["command"] == "build_model":
            #Attempt to generate the model
            try:
                #Build the model
                model = build_model(project_path)
                #Inform the main thread that model generated properly
                output_queue.put({"type":"success", "job":"build_model"})
            except Exception as err:
                output_queue.put({"type":"error", "job":"build_model", "message": str(err)})
        #Train the keras model
        elif job["command"] == "train":
            #Attempt to train the model
            try:
                #Run training
                results = train(project_path, model, output_queue)
                #Save the model's most recent weights
                model.save_weights(path.join(project_path, "models", "latest.h5"))
                #Inform the main thread that the model trained properly
                output_queue.put({"type":"success", "job":"train", "message": results})
            except Exception as err:
                output_queue.put({"type":"error", "job":"train", "message": str(err)})
        elif job["command"] == "shutdown":
            break
