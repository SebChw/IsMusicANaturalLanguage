import os
import shutil
import re
"""Script that removes all not midi files that our scraper has downloaded. If eventually folder is empty.
    Then it is removed.
"""

genre_name = input(
    "type in genre name (lowercase, no space, no special characters): ")

# Just in case someone don't respect the rules.
genre_name = genre_name.lower()
genre_name = genre_name.strip()
genre_name = "".join(genre_name.split(" "))

working_path = os.path.join(os.getcwd(), genre_name)

for sub_folder in os.listdir(working_path):
    artist_folder = os.path.join(working_path, sub_folder)
    for file in os.listdir(artist_folder):
        if "crddownload" in file or "tmp" in file:
            os.remove(os.path.join(artist_folder, file))
        elif re.search("(\d)", file):
            os.remove(os.path.join(artist_folder, file))
        elif not "mid" in file:
            os.remove(os.path.join(artist_folder, file))
    
    if len(os.listdir(artist_folder)) == 0:
        shutil.rmtree(artist_folder)
        
        
         
         