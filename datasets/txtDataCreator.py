
from midiToTxt import converter as c
from midiToTxt import converter2 as c2
import pypianoroll
import os
from midiToTxt import compressor
from mido.midifiles.meta import KeySignatureError


class Creator():
    """I've used that class to convert folders with midi files into txt files with that musical language.
       This could by just a function, but at the very begining I thought I'll need something more from that class.
    """
    def __init__(self, data_path: str, merged_file_name="merged.txt"):
        """
        Args:
            data_path (str): path to the midi_files
            merged_file_name (str, optional): path to the outcome file. Defaults to "merged.txt".
        """
        self.data_path = data_path
        self.merged_file_name = merged_file_name

    def prepare_data(self, destination_folder: str, split_sections=False, compression_type=None, songs_separator=" ", with_drums=True, method = 1, resolution = 8):
        """Function which parses all midi files in self.data_path and saves them to given destination_folder

        Args:
            destination_folder (str): folder to save txt file
            split_sections (bool, optional): Whether to encode drums, guitar, piano, bass separately or just merge all tracks into one. Defaults to False.
            compression_type (_type_, optional): lossy or lossles compression. Defaults to None.
            songs_separator (str, optional): how to separate two songs within one file. Defaults to " ".
            with_drums (bool, optional): whether to parse drums or to neglect them. Defaults to True.
            method (int, optional): method 1 or 2. These are just 2 different representations. Defaults to 1.
            resolution (int, optional): the bigger resolution the more detailed representation, but also much longer. Defaults to 8.
        """
        #create appropriate converter
        if method == 1:
            converter = c.MidiTxtConverter()
        else:
            converter = c2.BetterMidiToTxtConverter()
        saved = 0
        with open(os.path.join(destination_folder, self.merged_file_name), 'w') as destination:
            #walk over all folders with midi 
            for root, subdirs, files in os.walk(self.data_path):
                for f in files:
                    path = os.path.join(root, f)
                    if method == 1:
                        #some midi files seemed to be invalid, and these are exceptions raised
                        #only method one can be compressed 
                        try:
                            multitrack = pypianoroll.read(path, resolution = resolution)
                        except (IOError, ValueError, EOFError, KeySignatureError, IndexError) as e:
                            print(
                                f"Invalid MIDI file at {path}: {str(e)}.")
                            #os.remove(path)
                            continue
                    
                        converted = converter.multitrack_to_string(
                            multitrack, split_sections=split_sections, with_drums=with_drums)

                        if converted is None:
                            print("Empty track!")
                            continue
                        if compression_type == "lossy":
                            converted = compressor.lossy_compresion(converted)
                        elif compression_type == "lossless":
                            converted = compressor.lossless_compression(
                                converted)
                    else:
                        #that representation can't be further compressed
                        try:
                            converted = converter.midi_to_str(path, with_drums=with_drums)
                        except:
                            print(f"Invalid midi file: {path}")
                    
                    #we write song representation and song separator to the file         
                    destination.write(converted)
                    destination.write(songs_separator)
                    saved += 1

if __name__ == '__main__':
    creator = Creator("scraper/genresDataset/jazz",
                      merged_file_name="Presentation Data/lossless_compression.txt")
    creator.prepare_data(".", compression_type="lossless", songs_separator="\n", with_drums=False, method=1)
