import wave
import sys
import glob
import os
import numpy as np
#import matplotlib.pyplot as plt


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
    wave_data = np.double(wave_data)
    # for the data is stereo,and format is LRLRLR...
    # shape the array to n*2(-1 means fit the y coordinate)
    wave_data.shape = -1, 2
    # transpose the data
    wave_data = wave_data.T
    # calculate the time bar
    time = np.arange(0, n_frames) * (1.0/frame_rate)
    return wave_data, time, frame_rate


def pre_process(wave_data, time):
    wave_data_shape = wave_data.shape
    wave_data_mean = np.mean(wave_data, axis=1)
    for i in range(0, wave_data_shape[1]):
        wave_data[:,i] = (wave_data[:,i] - wave_data_mean) #/ wave_data_max
    wave_data_max = np.max(np.abs(wave_data), axis=1)
    for i in range(0, wave_data_shape[1]):
        wave_data[0, i] = wave_data[0, i] / wave_data_max[0]
        wave_data[1, i] = wave_data[1, i] / wave_data_max[1]
    return wave_data


def enframe(x, win, inc, time):
    # Split signal up into frames: one per row
    x_shape = x.shape
    if len(x_shape) == 1:
        x_series_size = x_shape[0]
    else:
        x_series_size = x_shape[1]
    split_len = win
    f_size = int(np.fix((x_series_size - split_len + inc) / inc))
    f = np.zeros([f_size, split_len])
    frame_time = np.zeros([f_size])
    f_ind = inc * np.arange(f_size)
    # inds = np.arange(split_len)
    for i in range(f_size):
        f[i, :] = x[f_ind[i]:f_ind[i] + split_len]
        frame_time[i] = time[f_ind[i] + split_len / 2]
    return f, frame_time


def pitch_valid(frame, frame_number, T1, mini_L=10):
    frame_size = frame.shape[1]
    e_sum = np.zeros([frame_number])
    entropy_sum = np.zeros([frame_number])
    for i in range(0, frame_number):
        sp = np.abs(np.fft.fft(frame[i, :]))
        sp = sp[0:frame_size/2+1]
        e_sum[i] = np.sum(sp*sp)
        prob = sp/np.sum(sp)
        entropy_sum[i] = -np.sum(prob*np.log(prob+2**(-52)))
    h_index = np.argwhere(entropy_sum<0.1)
    entropy_sum[h_index] = np.max(entropy_sum)
    Ef = np.sqrt(1 + np.abs(e_sum/entropy_sum))
    Ef = Ef/np.max(Ef)
    z_index = np.argwhere(Ef>=T1)
    sound_segment_begin, sound_segment_end, sound_segment_duration = find_segement(z_index)
    # segment_number = len(sound_segment_begin)
    SF = np.zeros([frame_number])
    sound_segment_duration = np.array(sound_segment_duration)
    duration_long_than_miniL_index = np.argwhere(sound_segment_duration>mini_L)
    voice_segment = np.zeros([duration_long_than_miniL_index.shape[0], 3])
    voice_segment[:, 0] = [sound_segment_begin[i] for i in duration_long_than_miniL_index]
    voice_segment[:, 1] = [sound_segment_end[i] for i in duration_long_than_miniL_index]
    voice_segment[:, 2] = [sound_segment_duration[i] for i in duration_long_than_miniL_index]
    for i in duration_long_than_miniL_index:
        SF[sound_segment_begin[i]:sound_segment_end[i]+1] = 1
    return voice_segment, SF, Ef


def find_segement(express):
    if express[0] == 0:
        voice_index = np.argwhere(express == 1)
    else:
        voice_index = express
    sound_segment_begin = []
    sound_segment_end = []
    sound_segment_duration = []
    sound_segment_begin.append(voice_index[0][0])
    for i in range(0, len(voice_index)-1):
        if voice_index[i+1] - voice_index[i] > 1:
            sound_segment_end.append(voice_index[i][0])
            sound_segment_begin.append(voice_index[i+1][0])
    sound_segment_end.append(voice_index[-1][0])

    for i in range(0, len(sound_segment_begin)):
        sound_segment_duration.append(sound_segment_end[i] - sound_segment_begin[i] + 1)
    return sound_segment_begin, sound_segment_end, sound_segment_duration


def my_filter(b, a, x):
    import scipy.signal as signal
    seg_longs = range(10, 110, 10)
    seg_longs_mod = [y for y in seg_longs if x.shape[0] % y == 0]
    seg_long = max(seg_longs_mod)
    x2 = x.reshape((-1, seg_long))
    # the init state of the filter is 0
    z = np.zeros(max(len(a), len(b)) - 1, dtype=np.float)
    y2 = []  # output
    for tx in x2:
        ty, z = signal.lfilter(b, a, tx, zi=z)
        y2.append(ty)
    y2 = np.array(y2)
    y2 = y2.reshape((-1,))
    y2 = np.array(y2)
    y3 = signal.lfilter(b, a, x)
    return y2


def acf_coor(y, frame_number, vseg, pitch_max_cycle, pitch_min_cycle):
    vsl = vseg.shape[0]
    #y = y[0]
    part_number = y.shape[1]
    frame_size = y.shape[1]
    period = np.zeros([frame_number])
    for i in range(0, vsl):
        ixb = int(vseg[i,0])
        ixe = int(vseg[i,1])
        ixd = ixe - ixb + 1
        for k in range(0, ixd):
            u = y[k + ixb -1,:]
            ru = np.correlate(u, u, "full")
            ru = ru[frame_size-1:-1]
            tloc = np.argmax(ru[pitch_min_cycle:pitch_max_cycle])
            period[k + ixb -1] = pitch_min_cycle + tloc -1
    return period


def pitch_valid_main(path):
    suffix = "wav"
    files = glob.glob(path + '\\*.' + suffix)
    file_number = len(files)
    period_list = []
    span_list = []
    pitch_list = []
    energy_list = []
    ind = np.zeros([file_number,2])
    for ii in range(0, file_number):
        wave_data, time, frame_rate = read_wave_data(files[ii])
        wave_data = pre_process(wave_data, time)
        wave_data2, frame_time = enframe(wave_data[1, :], 1600, 400, time)
        frame_number = wave_data2.shape[0]
        voice_segment, SF, Ef = pitch_valid(wave_data2, frame_number, 0.05)
        b = np.array([0.012280, -0.039508, 0.042177, 0.000000, -0.042177, 0.039508, -0.012280])
        a = np.array([1.000000, -5.527146, 12.854342 - 16.110307, 11.479789, -4.410179, 0.713507])
        #xx = my_filter(b, a, wave_data[1, :])
        yy, frame_time = enframe(wave_data[1, :], 1600, 400, time)
        frame_number = yy.shape[0]
        energy = []
        for i in range(0, frame_number):
            temp = np.abs(yy[i, :])
            energy.append(10 * np.sum(np.log10(temp ** 2)))
        # draw the wave
        pitch_min_cycle = int(frame_rate / 500)
        pitch_max_cycle = int(frame_rate / 60)
        period = np.zeros([1, frame_number])
        T0 = acf_coor(yy, frame_number, voice_segment, pitch_max_cycle, pitch_min_cycle)
        ff = 12 * np.log2(T0 / 440) + 69
        vosl = voice_segment.shape[0]
        t_begin_eng = np.zeros([vosl, 2])
        time_span = []
        for k in range(0, vosl):
            nx1 = voice_segment[k, 0]
            nx2 = voice_segment[k, 1]
            nx1 = voice_segment[k, 2]
            t_begin_eng[k, 0:2] = np.array([frame_time[nx1], frame_time[nx2]])
            time_span.append(wave_data[0, nx1] - wave_data[0, nx2])
        result = np.zeros([2, frame_number])
        result[0, :] = frame_time
        result[1, :] = ff
        time_period = np.zeros([2, frame_number])
        time_period[0, :] = frame_time
        time_period[1, :] = T0
        period_list.append(result)
        span_list.append(time_span)
        pitch_list.append(time_period)
        energy_list.append(energy)
        ind[ii, 0] = voice_segment[0, 0]
        ind[ii, 1] = voice_segment[-1, 1]
    # plt.subplot(211)
    # # plt.plot(time, wave_data[0])
    # plt.plot(pitch_list[0][0, ind[0,0]:ind[0,1]], pitch_list[0][1, ind[0,0]:ind[0,1]], 'ob')
    # plt.plot(pitch_list[1][0, ind[0, 0]:ind[0, 1]], pitch_list[1][1, ind[0, 0]:ind[0, 1]], 'xr')
    # plt.title('compare of standard a correct')
    # plt.legend(('standard', 'correct'))
    # plt.subplot(212)
    # plt.plot(pitch_list[0][0, ind[0,0]:ind[0,1]], pitch_list[0][1, ind[0,0]:ind[0,1]], 'ob')
    # plt.plot(pitch_list[3][0, ind[0, 0]:ind[0, 1]], pitch_list[3][1, ind[0, 0]:ind[0, 1]], 'xr')
    # plt.title('compare of standard a wrong')
    # plt.legend(('standard', 'wrong'))
    # plt.show()