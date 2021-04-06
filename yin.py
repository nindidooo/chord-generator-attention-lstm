import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display

def format_notes(notes, num_bars):

    formatted_notes = np.array_split(notes, num_bars)
    
    # bar_len=5
    # formatted_notes = []
    # i = 0
    # for note in notes:
    #     items_left = len(notes) - i
    #     if items_left < 1:
    #         break
    #     if items_left < bar_len:
    #         formatted_notes.append(notes[i:])
    #         break
    #     else:
    #         formatted_notes.append(notes[i:i+bar_len])
    #     i += bar_len
      
    return formatted_notes

def get_num_bars(y, sr, tempo):
    song_duration_s = len(y) / sr  # secs = samples * (samples/sec)
    print("tempo =", tempo)
    print("song_duration_s = ", song_duration_s)
    one_min = 60.
    beats_per_bar = 4.
    secs_per_bar = (one_min * beats_per_bar) / tempo
    num_bars = int(np.ceil(song_duration_s / secs_per_bar))    
    print("secs_per_bar =", secs_per_bar)
    print("detected %s bars" % num_bars)
    return num_bars

def sort_bars(y, sr, f0, tempo):
    actual_notes = []
    for f in f0:
        if not np.isnan(f):
            note = librosa.hz_to_note(f)[:-1].replace("♯","#") # strip off octave digit and fix formatting
            actual_notes.append(note)
            # actual_notes.append(librosa.hz_to_note(f))
            # midi_notes = librosa.hz_to_midi(f0)
        # else:
            # actual_notes.append('')
    num_chords = get_num_bars(y, sr,tempo)
    formatted_notes = format_notes(actual_notes, num_chords)  
    return formatted_notes  

def wav2f0(y, sr):
    f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), 
        fmax=librosa.note_to_hz('C6'))
    # f0 = np.nan_to_num(f0) # get rid of nans
    f0_times = librosa.times_like(f0)
    # D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
    return f0, voiced_flag, voiced_probs, f0_times    

def get_tempo(y, sr):
    onset_env = librosa.onset.onset_strength(y, sr=sr, aggregate=np.median)
    tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
    return tempo, beats, onset_env


def transcribe(filename="lalala.wav", plot=False):
    y, sr = librosa.load(filename)

    # TRANSCRIPTION
    f0, voiced_flag, voiced_probs, f0_times = wav2f0(y, sr)

    # BEAT TRACKING
    tempo, beats, onset_env = get_tempo(y, sr)
    # print(tempo)

    # MAKE CHORD TIMINGS
    notes = sort_bars(y, sr, f0, tempo)
    # print(notes)

    plot_data = [y, sr, f0, f0_times, voiced_probs, beats, onset_env]
    if plot:
        plot_inputs(plot_data)

    return notes, plot_data

def plot_inputs(plot_data):
    y, sr, f0, f0_times, voiced_probs, beats, onset_env = plot_data

    hop_length = 512
    fig, ax = plt.subplots(nrows=2, sharex=True)        
    M = librosa.feature.melspectrogram(y=y, sr=sr, hop_length=hop_length)
    librosa.display.specshow(librosa.power_to_db(M, ref=np.max),
                             y_axis='mel', x_axis='time', hop_length=hop_length,
                             ax=ax[0])
    ax[0].set(title='Fundamental Frequency Estimation: Mel spectrogram')
    ax[0].set_ylim(0, 2048)
    ax[0].plot(f0_times, f0, label='f0', color='cyan', linewidth=5)
    ax[0].plot(f0_times, 2000*voiced_probs, label='Voice Activity', color='yellow', linewidth=2)
    ax[0].legend(loc='upper right')

    # ax[0].label_outer()
    ax[0].set(title='Beats detected')
    beat_times = librosa.times_like(onset_env, sr=sr, hop_length=hop_length)
    ax[1].plot(beat_times, librosa.util.normalize(onset_env),
             label='Onset strength')
    ax[1].vlines(beat_times[beats], 0, 1, alpha=0.5, color='r',
               linestyle='--', label='Beats')
    ax[1].legend()    
    plt.show()

if __name__ == '__main__':
    notes, plot_data = transcribe()    
    print(notes)
    plot_inputs(plot_data)
    # get_tempo()
    # plt.show()
