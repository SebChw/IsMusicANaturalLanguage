import pypianoroll
import numpy as np
from collections import defaultdict


class BetterMidiToTxtConverter:
    def __init__(self,resolution=8):
        self.biggest_roll = (0,0) # biggest shape of the roll encountered. (timesteps, notes). To know how big array to do
        self.NOTE_PREFIX = "n"
        self.DURATION_PREFIX = "t"
        self.PAUSE_PREFIX = "w"
        self.PAUSE_TOKEN = -1 #Special note event
        self.resolution = resolution
    
    def midi_to_txt(self, midi_path: str, txt_path: str, with_drums=False, save_last_pause=False):
        with open(txt_path, 'w') as f:
            f.write(self.midi_to_str(midi_path, with_drums, save_last_pause))
            
    def midi_to_str(self, midi_path,  with_drums=False, save_last_pause=False) -> str:
        multitrack = pypianoroll.read(midi_path, resolution = self.resolution)
        
        duration_roll = self.track_to_duration_roll(multitrack, with_drums)
        events_array = self.duration_roll_to_events_array(duration_roll,save_last_pause)
        converted = self.events_to_str(events_array)
        
        return converted
    
    def set_biggest_roll(self, biggest_roll):
        self.biggest_roll = biggest_roll
        
    def txt_to_midi(self, txt_path: str, midi_path: str):
        with open(txt_path, 'r') as f:
            self.str_to_midi(f.read(), midi_path)
        
    def str_to_midi(self, text, midi_path, power=100):
        roll = self.str_to_piano_roll(text, power=power)
        multitrack = pypianoroll.Multitrack(resolution=self.resolution)
        multitrack.append(pypianoroll.StandardTrack(pianoroll=roll))
        
        pypianoroll.write(midi_path, multitrack)
    
    def track_to_duration_roll(self, multitrack, with_drums=False):
        roll = multitrack.blend()
        if roll.shape[0] > self.biggest_roll[0]:
            self.biggest_roll = roll.shape
            
        duration_roll = np.zeros(roll.shape)
        
        durations = defaultdict(lambda: set())
        for track in multitrack.tracks:
            if not track.is_drum or with_drums: # If track is no drum then we always convert it, or if we force to converts drums
                roll = track.pianoroll
                for time, note in zip(*roll.nonzero()):
                    durations[note].add(time)
            
        for note, trigerred in durations.items():
            trigerred = sorted(list(trigerred))
            curr = trigerred[0]
            duration = 0
            for next in trigerred[1:]:
                if curr - next == -1:
                    curr +=1
                    duration +=1
                else:
                    duration_roll[curr-duration, note] = duration + 1
                    duration = 0
                    curr = next
            
            duration_roll[curr-duration, note] = duration + 1
        #print(np.sum(duration_roll))
        return duration_roll
            
    def duration_roll_to_events_array(self, duration_roll, save_last_pause=False):
        events = [] #each is 2 element array [note_played, duration_of_note]
        wait_for = 0 #how long our pause will be before playing next notes
        for idx, timestep in enumerate(duration_roll):
            timestep_events = [[note_played, duration_roll[idx, note_played]] for note_played in timestep.nonzero()[0]]
            if len(timestep_events) == 0:
                wait_for += 1
            else:
                if wait_for > 0: 
                    events.append([self.PAUSE_TOKEN, wait_for])
                events.extend(timestep_events)
                wait_for = 1
        if wait_for > 0 and save_last_pause:
            #For generation purposes its not necesarry but if we want mapping 1 to 1 to original_piano_roll we must save it too 
            events.append([self.PAUSE_TOKEN, wait_for])
        return events    
    
    def events_to_str(self,events: list) -> str:
        """Very simple and straightforward approach
           each note played has prefix n
           each time duration has prefix t
           each pause has prefix w as wait

        Args:
            events (liast): list of all events

        Returns:
            str: _description_
        """
        #Think about adding velocity here!
        #Think about adding instruments information here too
        text = []
        for note, duration in events:
            if note != -1:
                text.append(f"{self.NOTE_PREFIX}{note}")
            else:
                text.append(self.PAUSE_PREFIX)
                
            text.append(f"{self.DURATION_PREFIX}{int(duration)}")
                
        return " ".join(text)
    
    def str_to_piano_roll(self, txt, power=1):
        piano_roll = np.zeros(self.biggest_roll)
        tokens = txt.split(" ")
        #print(tokens)
        current_timestep = 0
        for i in range(0, len(tokens),2):
            note, time = tokens[i:i+2]
            time_value = int(time[1:])
            if note == self.PAUSE_PREFIX:
                current_timestep += time_value
            else:
                note_value = int(note[1:])
                piano_roll[current_timestep: current_timestep + time_value, note_value] = power
                
        current_timestep += time_value

        return piano_roll[:current_timestep,:]
    
if __name__ == "__main__":
    converter = BetterMidiToTxtConverter(resolution=4)
    midi_path = "scraper/genresDataset/jazz/billevans/AutumnLeaves.mid"
    multitrack = pypianoroll.read(midi_path, resolution=4)
    #print(multitrack.tempo)
    roll = multitrack.blend()
    binarized_roll = roll > 1
    
    # duration_roll = converter.track_to_duration_roll(multitrack, with_drums=True)
    # events_array = converter.duration_roll_to_events_array(duration_roll, save_last_pause=True)
    # converted = converter.events_to_str(events_array)
    
    converted = converter.midi_to_str(midi_path, with_drums=True, save_last_pause=True)
    converted_piano_roll = converter.str_to_piano_roll(converted)
    
    assert np.all(binarized_roll == converted_piano_roll)