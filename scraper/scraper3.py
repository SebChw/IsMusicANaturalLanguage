from bs4 import BeautifulSoup
import requests
import re
import os

genre_name = input(
    "type in genre name (lowercase, no space, no special characters): ")

# Just in case someone don't respect the rules.
genre_name = genre_name.lower()
genre_name = genre_name.strip()
genre_name = "".join(genre_name.split(" "))

folder = os.path.join("genresDataset", genre_name, "midiworld")
if not os.path.isdir(folder):
    os.mkdir(folder)

for i in range(1, 38):
    URL = f"https://www.midiworld.com/search/{i}/?q={genre_name}"
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find_all("li")
    for r in results:
        link = r.find("a")
        if link:
            if "download" in link:
                link = link['href']
                song_title = r.text.split("-")[0].strip()
                print(f"Downloading: {song_title}")
                song = requests.get(link)
                with open(os.path.join(folder, song_title + ".mid"), "wb") as f:
                    f.write(song.content)
