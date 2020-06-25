#!/usr/bin/python3

import math
import numpy as np
from scipy.fft import dct
from scipy.io import wavfile
import sys

def main():
    filename = sys.argv[1]
    sample_rate, data = wavfile.read(filename)
    print("Sample rate:", sample_rate)
    data = normalize_to_mono(data)
    data = group_track(data, sample_rate/10) # 100 ms groups
    print("Grouped into", len(data), "groups")
    data = frequency_domain(data)
    data = remove_dc_bias(data)
    data = find_dominant_frequencies(data, sample_rate)
    print(data)

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
    res = np.empty(data.shape, dtype=np.float64)
    for i, group in enumerate(data):
        res[i] = np.abs(dct(group, norm='ortho'))
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


