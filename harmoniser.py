import pdb
import glob
import ntpath
import numpy as np
from os import listdir
from tensorflow.keras.models import model_from_json
from keras_preprocessing import sequence
import music21
from preprocess import one_hot_encoding

from music_dictionary import chord_dictionary, scale_dictionary, key_signature_calculator, root_list, chord_list, unused_note

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

for song in npy_files:
    
    
    note_seq2 = [['F', 'G', 'G#'], ['B', 'C', 'C', 'B', 'B', 'G#', 'G', 'E', 'F', 'G']]
    input_array = []
    for bar in note_seq2:
        print(bar)
        input_array.append([one_hot_encoding(note, root_list) for note in bar])
    note_sequence2 = sequence.pad_sequences(input_array, maxlen=32)
    # print(note_sequence2.shape)
    # print(note_sequence2)
    # predict
    prediction_list2 = []
    # network takes a note_sequence of size: (num_bars, 32, 12)
    net_output2 = model.predict(note_sequence2)
    for chord_index in net_output2.argmax(axis=1):
        prediction_list2.append(chord_dictionary[chord_index])
    print(ntpath.basename(song), prediction_list2)
    # break


    # a = np.load(song)[2,0] # get the second song in the first 'dataset/test.npy'
    # note_sequence = sequence.pad_sequences(a, maxlen=32)
    # # print(note_sequence.shape)
    # # print(note_sequence)

    # # predict
    # prediction_list = []
    # # network takes a note_sequence of size: (num_bars, 32, 12)
    # net_output = model.predict(note_sequence)
    # for chord_index in net_output.argmax(axis=1):
    #     prediction_list.append(chord_dictionary[chord_index])
    # print(ntpath.basename(song), prediction_list)
    break

# restore np.load for future normal usage
np.load = np_load_old    