**Timechange**

**Description**

The purpose of the Timechange project is to design an open source software tool that simplifies as much as possible the task of sophisticated ML analysis of time series data. Moreover, Timechange will be unique in that it will serve as a one stop shop solution for data input, pre-processing, and transformation, as well as training and evaluation of state-of-the-art deep learning methods. The focus with regards to the design of this system during the Spring 2017 Software Engineering course, will be on the implementation of features that will allow the system to generate images from transformed time series data (Fig. 1), and then to use these images to train a deep learning model such as a convolutional neural network.

**Usage instructions**

In the repository root, type

.. code-block:: bash

  python3 -m virtualenv env
  
  source ./env/bin/activate
  
  pip install -e .

To run the test suite with the sample dataset

.. code-block:: bash

  cd tests
  
  ./tests.py SAMPLE
  
