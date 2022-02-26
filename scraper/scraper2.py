from bs4 import BeautifulSoup
import requests
import re
import os

"""This script allow to download all songs from specific genre from the midkar.com website
"""
genre_name = input(
    "type in genre name (lowercase, no space, no special characters): ")

# Just in case someone don't respect the rules.
genre_name = genre_name.lower()
genre_name = genre_name.strip()
genre_name = "".join(genre_name.split(" "))

URL = f"https://midkar.com/{genre_name}/{genre_name}_01.html" #Pages on that website has such structure

address_splitted = URL.split("/")
folder = os.path.join("genresDataset", genre_name, "midkar") #Unfortunately we do not have separate page here, so we treat midkar as separate artist
if not os.path.isdir(folder):
    os.mkdir(folder)


page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")
results = soup.find_all("a")

pages = []
for r in results:
    link = r["href"]
    #if hyperlink has this structure it lead to another page with midi of given genre
    if re.search(f"{genre_name}_\d\d.html", link):
        pages.append(link)

for URL in pages:
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find_all("a")
    for r in results:
        song_name = r["href"]
        if ".mid" in song_name:
            print(f"Downloading: {song_name}")
            if "http" in song_name:
                link = song_name
                song_name = song_name.split("/")[-1]
            else:
                address_splitted[-1] = song_name
                link = "/".join(address_splitted)
                
            song = requests.get(link) #This time sending get request will return us already midi song.
            #ofc it's in binary format so we just need to write it to the file.
            with open(os.path.join(folder, song_name), "wb") as f:
                f.write(song.content)
