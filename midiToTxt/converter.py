import pypianoroll
import numpy as np


class MidiTxtConverter:
    def __init__(self,):
        pass

    def midi_to_txt(self, midi_path: str, txt_path: str, split_sections=True):
        multitrack = pypianoroll.read(midi_path)

        converted = self.multitrack_to_string(
            multitrack, split_sections=split_sections)

        with open(txt_path, 'w') as f:
            f.write(converted)

    def txt_to_midi(self, txt_path: str, midi_path: str):
        with open(txt_path, 'r') as f:
            multitrack = self.string_to_multitrack(f.read())

        pypianoroll.write(midi_path, multitrack)

    def categorize(self, multitrack: pypianoroll.Multitrack, first_note=21, last_note=108, with_drums=True) -> dict:
        """There are 5 categories of instruments distinguished:
            1. Piano: MIDI programs in ranges: [1, 24] U [49,56] U [81,06]
            2. Guitar: MIDI programs in range: [25,32]
            3. Bass: in range: [33,40]
            4. Strings + Horns: [41, 48] U [57, 80]
            5. Drums if flag is_drum is set to True

            This function basically takes a multitrack, separate it w.r.t instruments
            merge tracks within scope of 1 type of instrument into 1 track. Returns array of tracks
        Args:
            multitrack (pypianoroll.Multitrack): [Track to be categorized]
        Returns:
            dict of cardinality 5 [piano_track, guitar_track, bass_track, strings_horns_track, drums_track]
        """
        categories = ["piano", "guitar", "bass", "other", "drums"]
        categorized = {t: pypianoroll.Multitrack() for t in categories}

        for track in multitrack.tracks:
            program = track.program
            if program >= 25 and program <= 32:
                categorized["guitar"].append(track)
            elif program >= 33 and program <= 40:
                categorized["bass"].append(track)
            elif (program >= 41 and program <= 48) or (program >= 57 and program <= 80):
                categorized["other"].append(track)
            elif track.is_drum and with_drums:
                categorized["drums"].append(track)
            elif program < 97:
                # Programs higher than 97 are some effects which we do not neceserily want here
                categorized["piano"].append(track)

        if not with_drums:
            categorized.pop("drums", None)

        for category in categorized.keys():
            # Merging entire Multitrack into one pianoroll
            #print(category)
            if len(categorized[category].tracks) > 0:
                categorized[category] = categorized[category].blend()[
                    :, first_note:last_note+1]

        return categorized

    def blend(self,multitrack, first_note, last_note, with_drums=True):
        if with_drums:
            return multitrack.blend()[:, first_note:last_note+1]
        else:
            blended = pypianoroll.Multitrack()
            
            for track in multitrack.tracks:
                if not track.is_drum:
                    blended.append(track)
                    
            if len(blended.tracks) > 0:       
                return blended.blend()[:, first_note:last_note+1]
            
    
    def multitrack_to_string(self, multitrack: pypianoroll.Multitrack,  split_sections=True, first_note=21, last_note=108, token_limit=-1, with_drums=True):
        #! Maybe some categorization is needed: sections_separately = False or True
        """Function given a multitrack maps it into plain ASCII text. By default we map notes from A0 to C8. We do not map 
        it 1:1 to ASCII we do it with ofset equal to 13. We do it to be able to use space and exclamation mark as a special
        characters. Space corresponds to next unit of time and ! means change of the section.


        Args:
            multitrack (pypianoroll.Multitrack): midi song to be mapped
            destination (str): path for saving the file 
            first_note (int, optional): [from which midi note start 21 is A0]. Defaults to 21.
            last_note (int, optional): [on which midi note end. 108 is C8]. Defaults to 109.
        """
        offset = 13 + first_note  # Since we want quite nice interpretation. WE set some offset and since we cut from 0-21 we must add first_note
        time_separator = " "
        section_separator = "!" if split_sections else ""
        if split_sections:
            categorized = self.categorize(multitrack, first_note, last_note,with_drums=with_drums)
        else:
            categorized = {'everything': self.blend(multitrack, first_note, last_note, with_drums=with_drums)}
            if categorized['everything'] is None:
                return None
        
        instrument_piano_rolls = list(categorized.values())
        instrument_notes_played = [np.transpose(np.nonzero(
            instrument)) for instrument in instrument_piano_rolls]
        # To now in which cell in particular instrument we are
        pointers = [0 for instrument in instrument_piano_rolls]

        # Set time_step to the first non silent place
        starting_point = self.find_starting_point(
            instrument_piano_rolls[0].shape[0], pointers, instrument_notes_played)

        length_of_song = instrument_piano_rolls[0].shape[0] if token_limit < 1 else (
            token_limit + 1 + starting_point)

        converted = ""
        for time_step in range(starting_point, length_of_song):
            for index, notes_played in enumerate(instrument_notes_played):
                while(pointers[index] < len(notes_played) and notes_played[pointers[index]][0] == time_step):
                    converted += chr(notes_played[pointers[index]]
                                     [1] + offset)

                    pointers[index] += 1
                # Now the deal is if we want to put section separator only
                converted += section_separator
            converted += time_separator

        converted = converted.strip()
        return converted

    def string_to_multitrack(self, text: str, programs=[1, 26, 34, 65, 0]) -> pypianoroll.Multitrack:
        offset = 13
        time_separator = " "
        section_separator = "!"

        length_of_song = text.count(time_separator)
        timesteps = text.split(time_separator)
        pianorolls = [np.zeros((length_of_song, 128)) for i in range(5)]

        for t in range(length_of_song):
            step = timesteps[t]
            for index, section in enumerate(step.split(section_separator)):
                for note in section:
                    # Some random velocity at this moment
                    pianorolls[index][t, ord(note) - offset] = 100

        multitrack = pypianoroll.Multitrack()

        for i, pianoroll in enumerate(pianorolls):
            multitrack.append(pypianoroll.StandardTrack(
                pianoroll=pianoroll, program=programs[i], is_drum=False if i != 4 else True))

        return multitrack

    def find_starting_point(self, length_of_song, pointers, instrument_notes_played):
        for time_step in range(length_of_song):
            for index, notes_played in enumerate(instrument_notes_played):
                if notes_played[pointers[index]][0] == time_step:
                    return time_step
