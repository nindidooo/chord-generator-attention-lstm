import glob
import csv
import json

from music_dictionary import chord_dictionary, scale_dictionary, key_signature_calculator, root_dictionary, unused_note


class Measure:
    def __init__(self, measure, chord, note):
        self.measure = measure
        self.chord = chord
        self.note = note


def convert_chord_type(chord):
    """Change all the chord to the major or minor."""
    return chord_dictionary.get(chord, None)


def scale_to_integer(scale):
    """Convert the scale to integer."""
    return scale_dictionary.get(scale, None)


def get_transpose_interval(key):
    """Get the interval to transpose from key signature."""
    return key_signature_calculator.get(key, None)


def transpose(root, key):
    """Transpose the key of the chords."""
    root_integer = scale_to_integer(root)  # result : 0 ~ 11
    transpose_interval = get_transpose_interval(key)

    # transpose
    transposed_index = root_integer + transpose_interval
    if transposed_index >= 12:
        transposed_index = transposed_index - 12

    return transposed_index


def preprocess(paths):
    for path in glob.glob(paths):
        csv_file = open(path, 'r', encoding='utf-8')
        reader = csv.reader(csv_file)
        next(reader)  # skip first line

        song = []
        for line in reader:
            measure = line[1]
            key_fifths = line[2]
            chord_root = line[4]
            chord_type = line[5]
            note_root = line[6]

            # ignore unused note
            if chord_type in unused_note or note_root in unused_note:
                continue

            # convert all the chord to major or minor
            result_chord_type = convert_chord_type(chord_type)

            # transpose
            transposed_chord = transpose(chord_root, key_fifths)
            transposed_note = transpose(note_root, key_fifths)

            chord = root_dictionary[transposed_chord] + ':' + result_chord_type
            note = root_dictionary[transposed_note]

            song.append(Measure(measure, chord, note))
        csv_file.close()
        yield song


if __name__ == '__main__':
    with open('config.json') as f:
        config = json.load(f)

    train = preprocess(config['train_path'])
    test = preprocess(config['test_path'])
