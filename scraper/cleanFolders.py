import os
import shutil
import re
#We want to leave only mid files and we do not want duplicates

genre_name = input(
    "type in genre name (lowercase, no space, no special characters): ")

# Just in case someone don't respect the rules.
genre_name = genre_name.lower()
genre_name = genre_name.strip()
genre_name = "".join(genre_name.split(" "))

working_path = os.path.join(os.getcwd(), genre_name)

#remove = True
not_downloaded = 0
for sub_folder in os.listdir(working_path):
    artist_folder = os.path.join(working_path, sub_folder)
    for file in os.listdir(artist_folder):
        if "crddownload" in file or "tmp" in file:
            os.remove(os.path.join(artist_folder, file))
            not_downloaded += 1
        elif re.search("(\d)", file) or ".crdownload" in file:
            #print(os.path.join(working_path, sub_folder, file))
            os.remove(os.path.join(artist_folder, file))
        elif not "mid" in file:
            os.remove(os.path.join(artist_folder, file))
    
    if len(os.listdir(artist_folder)) == 0:
        shutil.rmtree(artist_folder)
        
    #if not_downloaded > 5:
    #    print(artist_folder)
        
    not_downloaded = 0
        
    # if remove:
    #     shutil.rmtree(os.path.join(working_path, sub_folder))
    #     print(os.path.join(working_path, sub_folder))
        
    # remove = True
        
        
         
         