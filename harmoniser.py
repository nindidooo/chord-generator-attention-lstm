import pdb
import glob
import ntpath
import numpy as np
from os import listdir
from tensorflow.keras.models import model_from_json
from keras_preprocessing import sequence
import music21
from preprocess import one_hot_encoding
from midi_helpers import *
from music_dictionary import chord_list, root_list
from yin import transcribe, plot_inputs
from piano_synth import generate_accompaniment, play_midi


def load_model():
    # load model file
    model_dir = 'model_json/'
    model_files = listdir(model_dir)
    for i, file in enumerate(model_files):
        print(str(i) + " : " + file)
    file_number_model = 0 # int(input('Choose the model:'))
    model_file = model_files[file_number_model]
    model_path = '%s%s' % (model_dir, model_file)
    # load weights file
    weights_dir = 'model_weights/'
    weights_files = listdir(weights_dir)
    for i, file in enumerate(weights_files):
        print(str(i) + " : " + file)
    file_number_weights = 0 #int(input('Choose the weights:'))
    weights_file = weights_files[file_number_weights]
    weights_path = '%s%s' % (weights_dir, weights_file)
    # load the model
    model = model_from_json(open(model_path).read())
    model.load_weights(weights_path)
    return model

def generate_harmony():
    model_path = '/Users/matthewbrown/chord-generator-attention-lstm/model_json/800epochs_20190405_15_52.json'
    model = model_from_json(open(model_path).read())

    weights_path = '/Users/matthewbrown/chord-generator-attention-lstm/model_weights/800epochs_20190405_15_52.h5'
    model.load_weights(weights_path)

    file_path = 'dataset/*.npy'
    npy_files = glob.glob(file_path)

    chord_dictionary = ['C:maj', 'C:min',
                        'C#:maj', 'C#:min',
                        'D:maj', 'D:min',
                        'D#:maj', 'D#:min',
                        'E:maj', 'E:min',
                        'F:maj', 'F:min',
                        'F#:maj', 'F#:min',
                        'G:maj', 'G:min',
                        'G#:maj', 'G#:min',
                        'A:maj', 'A:min',
                        'A#:maj', 'A#:min',
                        'B:maj', 'B:min']

    # save np.load
    np_load_old = np.load

    # modify the default parameters of np.load
    np.load = lambda *a,**k: np_load_old(*a, allow_pickle=True, **k)

    # midi_notes = get_midi_data('transcription.mid')
    midi_notes, plot_data = transcribe() 

    input_array = []
    for bar in midi_notes:
        print("processing bar: ", bar)
        input_array.append([one_hot_encoding(note, root_list) for note in bar])
    note_sequence = sequence.pad_sequences(input_array, maxlen=32)
    chord_prediction_list = []
    # network takes a note_sequence of size: (num_bars, 32, 12)
    net_output = model.predict(note_sequence)
    for chord_index in net_output.argmax(axis=1):
        chord_prediction_list.append(chord_dictionary[chord_index])

    print(chord_prediction_list)

    # restore np.load for future normal usage
    np.load = np_load_old    

    # make dictionary of chords and notes
    for notes, chord in zip(midi_notes, chord_prediction_list):
        print(notes, chord)

    PLOT_DATA = True
    if PLOT_DATA:
        plot_inputs(plot_data)

    generated_chords = generate_accompaniment(chord_prediction_list)
    return generated_chords

if __name__ == '__main__':
    chords = generate_harmony()
    play_midi(chords)