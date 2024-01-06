#!/usr/bin/python3

import math
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from scipy.fft import dct
from scipy.fft import fft
from scipy.io import wavfile
from scipy.signal.windows import blackman
import sys

A4 = 440
NOTE_NAMES = ["A","A#","B","C","C#","D","D#","E","F","F#","G","G#"]
NOTE_THRESH = 30000 # Open to change

def main():
    filename = sys.argv[1]
    sample_rate, data = wavfile.read(filename)
    print("Sample rate:", sample_rate)
    data = normalize_to_mono(data)
    #data = group_track(data, sample_rate/10) # 100 ms groups
    #print("Grouped into", len(data), "groups")
    window = blackman(len(data))
    data = data * window
    data = frequency_domain(data)
    print("Frequency Domain shape", data.shape)
    indicies = indicies_gt_thresh(data, NOTE_THRESH)[1:]
    # We need the X-axis to be freq, Y to be amplitude
    freqs = list(map(lambda indx : index_to_freq(indx, len(data), sample_rate), indicies))
    #freqs = indicies
    notes = set()
    for freq in freqs:
        notes.add(freq_to_note_name(freq))
    print("Significant notes: {} over thresh {}".format(notes, NOTE_THRESH))
    print("Made of frequencies: {}".format(freqs))
    print("Data shape: {}; window shape: {}".format(data.shape, window.shape))
    display(data[:1000]) #, 10*NOTE_THRESH*window[:1000])
    #data = find_dominant_frequencies(data, sample_rate)
    print(data)

def index_to_freq(index, N, sample_rate):
    # Yeah, I'm just not using the sine (complex) side
    assert index <= N, "N={} given index={}".format(N, index)
    factor = index / N
    return sample_rate * factor

# TODO: Let's test these functions using the data at
# https://www.phys.unsw.edu.au/jw/notes.html

def semitones_from_a4_to_freq(semitones):
    return A4 * (2 ** (semitones/12))

def freq_to_semitones_from_a4(freq):
    assert type(freq) in (float, int), "Freq invalid type: {}".format(type(freq))
    if type(freq) is float:
        #assert not freq.isnan(), "Freq is NaN"
        pass
    assert freq > 0, "Freq not positive: {}".format(freq)
    pos = freq / A4
    print("Attempting freq_to_semi with {} {}...".format(type(freq), freq))
    exp = math.log2(pos)
    return 12 * exp

def freq_to_note_name(freq):
    semitones = freq_to_semitones_from_a4(freq)
    tones = round(semitones)
    note = NOTE_NAMES[tones % 12]
    octave = math.floor(semitones/12)
    return "{}{}".format(note, 4+octave)

def indicies_gt_thresh(array, threshold):
    return list(map(int, np.argwhere(array >= threshold).flatten()))

def display(*args):
    figure, ax = plt.subplots()
    for data in args:
        ax.plot(data)
    plt.grid()
    plt.show()

def n2hz(n, N, sampling_freq=44100):
    # Tell me the actual audio frequency
    # represented by the frequency sample
    return (n * sampling_freq) / N

def find_dominant_frequencies(data, sample_rate):
    # Take groups of frequency-domain signals,
    # Find the maximum frequency of each group,
    # and return a vector of the dominant frequency
    # per group.
    num_groups, group_size = data.shape
    # This finds the max element per row
    max_indicies = np.argmax(data, 1)
    res = np.empty((num_groups,), dtype=np.float64)
    for i, group in enumerate(max_indicies):
        # Map the index from the DCT into
        # a real audio frequency
        res[i] = n2hz(group, group_size, sample_rate)
    return res

def remove_dc_bias(data):
    # Perform 1/n correction.
    # Subtract a weighted factor from the vector
    res = np.empty(data.shape, dtype=data.dtype)
    factor = np.empty((data.shape[1],), dtype=data.dtype)
    for i in range(len(factor)):
        factor[i] = 1 / (i+1)
    for num, group in enumerate(data):
        res[num] = group - (group * factor)
    return res

def frequency_domain(data):
    # Map the individual groups of the track
    # from the time domain into the frequency space.
    #res = np.empty(data.shape, dtype=np.float64)
    #res = np.abs(dct(data, norm="ortho"))
    res = dct(data, norm="ortho")
    res = np.abs(fft(data, norm="ortho"))
    #for i, group in enumerate(data):
    #    res[i] = np.abs(dct(group, norm='ortho'))
    return res

def normalize_to_mono(data):
    # If the track was recorded in stereo,
    # only take one of the tracks
    if len(data.shape) != 1:
        return data[:,0]
    else:
        return data

def group_track(data, group_size):
    group_size = int(group_size)
    num_samples = data.shape[0]
    # We want each group to have the same
    # number of samples. Drop the rest.
    num_samples -= int(num_samples % group_size)
    assert num_samples % group_size == 0
    data = data[:num_samples]
    num_groups = num_samples // group_size
    # Each group is now a row in the ouptut matrix
    return np.reshape(data, (num_groups, group_size))

if __name__ == '__main__':
    main()


