#Set universal dimension ordering
from keras.backend import common as K
K.set_image_dim_ordering('th')
#Imports for keras
from keras.models import Sequential
from keras.layers import Convolution2D, MaxPooling2D
from keras.layers import Input, Dense, Flatten, Dropout
from keras.optimizers import SGD

#Generates a compiled keras model for use in timechange training
#Parameters:
#num_classes -- number of classes this model is trained to distinguish
#input_shape -- The shape of image
def generate_model(num_classes, input_shape, config):
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
        model.add(Convolution2D(8, 3, 3,  activation='relu', input_shape=input_shape, dim_ordering='th'))
        model.add(MaxPooling2D(pool_size=(2,2), dim_ordering='th'))
        #Add convolutional blocks. n-1 because the first was added already
        for _ in range(num_blocks - 1):
            #TODO: Allow configuring the parameters on these
            model.add(Convolution2D(8, 3, 3,  activation='relu', input_shape=input_shape, dim_ordering='th'))
            model.add(MaxPooling2D(pool_size=(2,2), dim_ordering='th'))
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
