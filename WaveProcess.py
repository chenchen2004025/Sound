import wave

import numpy as np


def read_wave_data(file_path):
    # open a wave file, and return a Wave_read object
    f = wave.open(file_path, "rb")
    # read the wave's format information and return a tuple
    params = f.getparams()
    # get the info
    n_channels, sample_width, frame_rate, n_frames = params[:4]
    # Reads and returns n_frames of audio, as a string of bytes.
    str_data = f.readframes(n_frames)
    # close the stream
    f.close()
    # turn the wave's data to array
    wave_data = np.fromstring(str_data, dtype = np.short)
    # for the data is stereo,and format is LRLRLR...
    # shape the array to n*2(-1 means fit the y coordinate)
    wave_data.shape = -1, 2
    # transpose the data
    wave_data = wave_data.T
    # calculate the time bar
    time = np.arange(0, n_frames) * (1.0/frame_rate)
    return wave_data, time

def pre_process(wave_data, time):
    wave_data_mean = np.mean(wave_data, axis=1)
    wave_data = wave_data - wave_data_mean
    wave_data = wave_data - np.max(wave_data, axis=1)

def generate