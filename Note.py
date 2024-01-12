#!/usr/bin/python3

import csv
import unittest
import math

A4 = 440
NOTE_NAMES = ["A","A#","B","C","C#","D","D#","E","F","F#","G","G#"]

"""
Encapsulate various information related to a musical note.

A major fact is that there are a few different ways to look at its value:
    - Index in the frequency-domain output of the FFT
    - Frequency of the note
    - Note name, as said frequency can map into the 12 TET system.

"""


class Note:

    def __init__(self, sample_rate, N, index, amplitude):
        """Construct a Note object

        @param sample_rate The # of samples/second of the audio, such as 44.1KHz

        @param N Number of samples in the time-domain audio

        @param index The index which represents this note in the FFT frequency-domain output.
        """
        self._sample_rate = sample_rate
        self._N = N
        self._index = index
        self._amplitude = amplitude
        self._freq = (index * sample_rate) / N

    def __str__(self):
        return self.name()

    def __repr__(self):
        return "{}: {} Hz; index={}".format(self.name(), self._freq, self._index)

    def freq(self):
        return self._freq

    def name(self):
        """Return the note name for humans to read, such as F# or B.

        This will only return sharps, not flats.
        Once again, this is entirely built upon 12 TET

        TODO: Incide the math in this comment, and check it

        TODO: Also include the extent to which the note is detuned, in cents.
        """
        # This note's position relative to A4 (440Hz)
        # A4 = 440Hz fundamentally defines the frequency of all other notes
        pos = self._freq / A4
        exp = math.log2(pos)
        # Now we have calculated the number of semitones away from A4
        # is the frequency of this note,
        # we can use it to figure out what note it IS.
        semitones = 12 * exp
        tones = round(semitones)
        # In Python, modulo of a negative number returns a positive number
        # which behaves in the same way as providing the same negative number
        # as a list index.
        note = NOTE_NAMES[tones % 12]
        # While frequency to note name is based around A,
        # octaves increment based on C, rather than A.
        semitones_from_c4 = tones + 9
        octave = math.floor(semitones_from_c4/12)
        if False:
            print("""NAME:
            freq {}
            pos {}
            exp {}
            semitones {}
            tones {}
            note {}
            semis_from_c4 {}
            octave {}
            """.format(self._freq, pos, exp, semitones,
                tones, note, semitones_from_c4, octave
            ))
        return "{}{}".format(note, 4+octave)

    def index(self):
        return self._index

    def amplitude(self):
        return self._amplitude



class TestNote(unittest.TestCase):

    # sample rate = 44.1kHz
    N = 441000

    def freq_to_index(self, freq):
        #return round(self.N * (freq / self.sample_rate))
        # ONLY WHEN N == sample_rate!!!
        return round(freq)

    def test_table(self):
        FREQ = 1
        NAME = 0
        # https://pages.mtu.edu/~suits/notefreqs.html
        with open("notes.csv") as csv_file:
            note_table = csv.reader(csv_file, delimiter=",")
            next(note_table) # Skip the header row
            for row in note_table:
                index = self.freq_to_index(float(row[FREQ]))
                note = Note(self.N, self.N, index, 0)
                self.assertEqual(index, note.index())
                exp = float(row[FREQ])
                act = note.freq()
                self.assertTrue(abs(exp-act) < 1, "Expected: {} Actual: {}".format(exp, note))
                self.assertEqual(row[NAME].strip(), note.name(), "Expected: {} Actual: {}".format(row[NAME], note))


if __name__ == "__main__":
    unittest.main()

