import numpy as np
from scipy import signal

def extract(time_series, method="fft", data_size=None):
    """Extracts features from a time series or array of time series and outputs an image
    Keyword arguments:
    time_series -- A numpy array or array of numpy arrays representing the time series data
    method -- the type of feature extraction to use
    data_size -- Used for some feature extraction methods. Pads or truncates data
    """
    #Switches on method
    if method == "fft":
        return simple_fourier(time_series, data_size)
    elif method == "spectrogram":
        return spectrogram(time_series)
    else:
        raise ValueError("Invalid feature extraction method")

#Possible enhancements
#TODO: separate real and imaginary components so as not to lose data
#TODO: split time series into chunks
#TODO: ignoring values with little information
def simple_fourier(time_series, data_size = None):
    """Performs a basic fourier transform across the entire time series. The imaginary results are normalized.
    Keyword arguments:
    time_series -- The time series analyse as a numpy array. Can also be a 2d array.
                   In the case of a 2d array, the operation is performed on each subarray and returned
                   as an array of results.
    data_size -- The size value to be passed to numpy's FFT. Values higher than the data size will pad zeroes.
                 Values lower than the data size will remove elements.
                 With FFT, it is recommended to use powers of 2 here
    """
    #If default value is left for data size, use the data's actual size 
    if data_size is None:
        data_size = time_series.shape[1]
    # Perform a fourier transform on the data
    return np.abs(np.fft.rfft(time_series, n=data_size))

def spectrogram(time_series):
    """Performs a basic fourier transform across the entire time series. The imaginary results are normalized.
    Keyword arguments:
    time_series -- The time series analyse as a numpy array. Can also be a 2d array.
                   In the case of a 2d array, the operation is performed on each subarray and returned
                   as an array of results.
    """
    #TODO: Implement scipy's spectrogram
    #Look here https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.spectrogram.html


    #Replace this with actual output
    return time_series
