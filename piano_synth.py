import os
from mingus.core import progressions, intervals
from mingus.core import chords as ch
from mingus.containers import NoteContainer, Note
from mingus.midi import fluidsynth
import time
import sys
from random import random
# from mingus.midi import MidiFileOut
# https://bspaans.github.io/python-mingus/doc/wiki/tutorialChords.html
SF2 = "piano.sf2"
PLAY_ENABLED = False
inversions = [ch.first_inversion, ch.second_inversion, ch.third_inversion]
# generate random permutation of inversions
options = (dir(ch))
major_options = [item for item in options if 'major' in item]
minor_options = [item for item in options if 'minor' in item]

def generate_accompaniment(net_output_chords):
    generated_chords = []
    chords = []
    for chord in net_output_chords:
        root, key = (chord.split(":"))
        print(root, key)
        if key == 'maj':
            chords.append(ch.major_triad(root))
        if key == 'min':
            chords.append(ch.minor_triad(root))      

    print(chords)  

    key = chords[0][0]
    print('key', key)
    if not fluidsynth.init(SF2):
        print("Couldn't load soundfont", SF2)
        sys.exit(1)

    print(dir(fluidsynth.midi))
    # fluidsynth.midi.start_audio_output()
    fluidsynth.midi.start_recording()
    phrase = 0
    while phrase == 0:
        i = 0
        for chord in chords:
            print("chord", chord)
            c = NoteContainer(chords[i])
            generated_chords.append([{'note':cc.name.replace("B#","B").replace("E#","E").replace("##","#"), 'octave':cc.octave} for cc in c])
            l = Note(c[0].name)
            p = c[1]
            l.octave_down()
            print(ch.determine(chords[i])[0])

            # Play chord and lowered first note
            # fluidsynth.midi.MidiFileOut.write_NoteContainer("test.mid", c)
            print("NEW CHORD = ", c)

            if PLAY_ENABLED:

                fluidsynth.play_NoteContainer(c)
                fluidsynth.play_Note(l)
                time.sleep(1.0)

                # Play highest note in chord
                fluidsynth.play_Note(c[-1])

                # 50% chance on a bass note

                if random() > 0.50:
                    p = Note(c[1].name)
                    p.octave_down()
                    fluidsynth.play_Note(p)
                time.sleep(0.50)

                # 50% chance on a ninth

                if random() > 0.50:
                    l = Note(intervals.second(c[0].name, key))
                    l.octave_up()
                    fluidsynth.play_Note(l)
                time.sleep(0.25)

                # 50% chance on the second highest note

                if random() > 0.50:
                    fluidsynth.play_Note(c[-2])
                time.sleep(0.25)
                fluidsynth.stop_NoteContainer(c)
                fluidsynth.stop_Note(l)
                fluidsynth.stop_Note(p)
            i += 1
        print("-" * 20)
        phrase = 1
        return generated_chords

def play_midi(chords):
    from EasyMIDI import EasyMIDI,Track,Note,Chord,RomanChord
    from random import choice
        
        
    easyMIDI = EasyMIDI()
    track1 = Track("acoustic grand piano")  # oops

    # print(chords)
    for chord_dict in chords:
        root = Note(chord_dict[0]['note'], chord_dict[0]['octave']-2)

        # MAKE THE TRIAD
        I = Note(chord_dict[0]['note'], chord_dict[0]['octave'], duration = 0.2)
        III = Note(chord_dict[1]['note'], chord_dict[1]['octave'], duration = 0.5)
        IV = Note(chord_dict[2]['note'], chord_dict[2]['octave'], duration = 0.01)

        chord = Chord([root, I,III,IV])  # a chord of notes C, E and G
        track1.addNotes(chord)

        # roman numeral chord, first inversion (defaults to key of C)
        # track1.addNotes(RomanChord('I*', octave = 5, duration = 1))

    easyMIDI.addTrack(track1)
    easyMIDI.writeMIDI("output.mid")
    os.system("timidity output.mid -Ow -o out.wav")
    os.system("open out.wav")



if __name__ == '__main__':
    net_output_chords = ['G#:min', 'F:maj', 'F:maj', 'G:maj', 'G#:maj', 'G:maj', 'D:maj', 'C:maj', 'D:min', 'C:maj', 'C:maj', 'C:maj', 'D:min', 'F:maj', 'B:maj', 'B:maj', 'E:maj', 'D#:min', 'C#:maj', 'C#:maj']
    chords = generate_accompaniment(net_output_chords)
    play_midi(chords)

