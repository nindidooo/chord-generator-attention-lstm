#@title Initialize Model
import tensorflow.compat.v1 as tf
import librosa
import numpy as np
# from google.colab import files
from magenta.common import tf_utils
from note_seq import audio_io
from magenta.models.onsets_frames_transcription import audio_label_data_utils
from magenta.models.onsets_frames_transcription import configs
from magenta.models.onsets_frames_transcription import constants
from magenta.models.onsets_frames_transcription import data
from magenta.models.onsets_frames_transcription import infer_util
from magenta.models.onsets_frames_transcription import train_util
import note_seq
from note_seq import midi_io
from note_seq import sequences_lib
from magenta.music.protobuf import music_pb2
tf.disable_v2_behavior()
## Define model and load checkpoint
## Only needs to be run once.
MAESTRO_CHECKPOINT_DIR = 'train'
model_type = "MAESTRO (Piano)" #@param ["MAESTRO (Piano)", "E-GMD (Drums)"]
if model_type.startswith('MAESTRO'):
  config = configs.CONFIG_MAP['onsets_frames']
  hparams = config.hparams
  hparams.use_cudnn = False
  hparams.batch_size = 1
  checkpoint_dir = MAESTRO_CHECKPOINT_DIR
elif model_type.startswith('E-GMD'):
  config = configs.CONFIG_MAP['drums']
  hparams = config.hparams
  hparams.batch_size = 1
  checkpoint_dir = EGMD_CHECKPOINT_DIR
else:
  raise ValueError('Unknown Model Type')
examples = tf.placeholder(tf.string, [None])
dataset = data.provide_batch(
    examples=examples,
    preprocess_examples=True,
    params=hparams,
    is_training=False,
    shuffle_examples=False,
    skip_n_initial_records=0)
estimator = train_util.create_estimator(
    config.model_fn, checkpoint_dir, hparams)
iterator = tf.data.make_initializable_iterator(dataset)
next_record = iterator.get_next()

def transcription_data(params):
    del params
    return tf.data.Dataset.from_tensors(sess.run(next_record))

"""# Upload Audio

Run the following cell to upload audio files.
"""
# pianoAudio = 'misty.wav'
pianoAudio = 'lalala.wav'
to_process = []

with open(pianoAudio, mode='rb') as file: 
    wav_data = file.read()

example_list = list(
      audio_label_data_utils.process_record(
          wav_data=wav_data,
          ns=music_pb2.NoteSequence(),
          example_id='accompaniment.wav',
          min_length=0,
          max_length=-1,
          allow_empty_notesequence=True))

to_process.append(example_list[0].SerializeToString())
sess = tf.Session()

sess.run([
    tf.initializers.global_variables(),
    tf.initializers.local_variables()
])

sess.run(iterator.initializer, {examples: to_process})

input_fn = infer_util.labels_to_features_wrapper(transcription_data)
"""# Inference

Run the following cell to transcribe the files you uploaded. Each time it runs it will transcribe one of the uploaded files.
"""
#@title Run inference
prediction_list = list(
    estimator.predict(
        input_fn,
        yield_single_examples=False))
assert len(prediction_list) == 1
sequence_prediction = note_seq.NoteSequence.FromString(
    prediction_list[0]['sequence_predictions'][0])

#@title Download MIDI
midi_filename = ('transcription.mid')
midi_io.sequence_proto_to_midi_file(sequence_prediction, midi_filename)
