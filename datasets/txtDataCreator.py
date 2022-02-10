
from midiToTxt import converter as c
import pypianoroll
import os
from midiToTxt import compressor


class Creator():
    def __init__(self, data_path: str, categories={}, merged_file_name="merged.txt"):
        self.data_path = data_path
        self.categories = categories
        self.merged_file_name = merged_file_name

    def prepare_data(self, destination_folder: str, categorize=False, split_sections=False, compression_type=None, how_much_to_save=500, tokens_to_use=-1, songs_separator=" "):
        # Compression type can be None, lossy, lossles
        converter = c.MidiTxtConverter()
        saved = 0
        if categorize:
            pass
        else:
            with open(os.path.join(destination_folder, self.merged_file_name), 'w') as destination:
                for root, subdirs, files in os.walk(self.data_path):
                    for f in files:
                        path = os.path.join(root, f)
                        try:
                            # ! Some midi files may be invalid so we just skip them
                            multitrack = pypianoroll.read(path)
                        except (IOError, ValueError, EOFError) as e:
                            print(f"Invalid MIDI file at {path}: {str(e)}")
                            continue

                        converted = converter.multitrack_to_string(
                            multitrack, split_sections=split_sections, token_limit=tokens_to_use)

                        if compression_type == "lossy":
                            converted = compressor.lossy_compresion(converted)
                        elif compression_type == "lossless":
                            converted = compressor.lossless_compression(
                                converted)
                        #!Some files contains this character, allegedly some files exceed ASCII coding.
                        # if "\r" in converted:
                        #     print(path)
                        #     break
                        destination.write(converted)
                        destination.write(songs_separator)
                        saved += 1
                    if saved > how_much_to_save:
                        break


if __name__ == '__main__':
    creator = Creator("data/lmd_matched",
                      merged_file_name="lstm_dataset_compressed.txt")
    creator.prepare_data(".", compression_type="lossless",
                         tokens_to_use=200, songs_separator="\n", how_much_to_save=1)
