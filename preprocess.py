import glob
import csv
import json


class Measure:
    def __init__(self, measure, chord, note):
        self.measure = measure
        self.chord = chord
        self.note = note


def convert_chord_type(chord):
    """Change all the chord to the major or minor."""
    return {'maj': 'maj',
            'major': 'maj',
            'major-sixth': 'maj',
            'major-seventh': 'maj',
            'maj7': 'maj',
            'major-ninth': 'maj',
            'maj69': 'maj',
            'maj9': 'maj',
            'major-minor': 'maj',
            'minor': 'min',
            'min': 'min',
            'minor-sixth': 'min',
            'minor-seventh': 'min',
            'min7': 'min',
            'min9': 'min',
            'minor-ninth': 'min',
            'minor-11th': 'min',
            'minor-13th': 'min',
            'minor-major': 'min',
            'minMaj7': 'min',
            '6': 'maj',
            '7': 'maj',
            '9': 'maj',
            'dominant': 'maj',
            'dominant-seventh': 'maj',
            'dominant-ninth': 'maj',
            'dominant-11th': 'maj',
            'dominant-13th': 'maj',
            'augmented': 'maj',
            'aug': 'maj',
            'augmented-seventh': 'maj',
            'augmented-ninth': 'maj',
            'dim': 'min',
            'diminished': 'min',
            'diminished-seventh': 'min',
            'half-diminished': 'min',
            'm7b5': 'min',
            'dim7': 'min',
            ' dim7': 'min',
            'suspended-second': 'maj',
            'suspended-fourth': 'maj',
            'sus47': 'maj',
            'power': 'maj'}.get(chord, None)


def scale_to_integer(scale):
    """Convert the scale to integer."""
    return {'B#': 0, 'C0': 0, 'C2': 0,
            'Db': 1, 'C#': 1,
            'D0': 2, 'D-2': 2,
            'Eb': 3, 'D#': 3,
            'E0': 4, 'Fb': 4,
            'F0': 5, 'E#': 5, 'F2': 5,
            'Gb': 6, 'F#': 6,
            'G0': 7,
            'Ab': 8, 'G#': 8,
            'A0': 9, 'A2': 9,
            'Bb': 10, 'A#': 10,
            'Cb': 11, 'B0': 11, 'B-2': 11}.get(scale, None)


def transpose(root, key):
    """Transpose the key of the chords."""
    root_integer = scale_to_integer(root)  # result : 0 ~ 11
    transpose_interval = get_transpose_interval(key)

    # transpose
    transposed_index = root_integer + transpose_interval
    if transposed_index >= 12:
        transposed_index = transposed_index - 12

    return transposed_index


def get_transpose_interval(key):
    """Get the interval to transpose from key signature."""
    return {'-6': 6,
            '-5': -1,
            '-4': 4,
            '-3': -3,
            '-2': 2,
            '-1': -5,
            '0': 0,
            '1': 5,
            '2': -2,
            '3': 3,
            '4': -4,
            '5': 1,
            '6': -6,
            '7': -1}.get(key, None)


def preprocess(files):
    for csv_path in glob.glob(files):
        csv_ins = open(csv_path, 'r', encoding='utf-8')
        next(csv_ins)  # skip first line
        reader = csv.reader(csv_ins)

        song = []

        # get all rows from csv file
        for line in reader:
            measure = line[1]
            key_fifths = line[2]
            chord_root = line[4]
            chord_type = line[5]
            note_root = line[6]

            # ignore rest note or None
            if chord_type in skip_data or note_root in skip_data:
                continue

            # convert all the chord to major or minor
            result_chord_type = convert_chord_type(chord_type)

            # transpose
            transposed_chord = transpose(chord_root, key_fifths)
            transposed_note = transpose(note_root, key_fifths)

            chord = root_dict[transposed_chord] + ':' + result_chord_type
            note = root_dict[transposed_note]

            song.append(Measure(measure, chord, note))
        yield song


if __name__ == '__main__':
    skip_data = ['rest', '[]', '', 'pedal']
    root_dict = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    with open('config.json') as f:
        config = json.load(f)

    train = preprocess(config['train_path'])
    test = preprocess(config['test_path'])
