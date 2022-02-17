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

URL = f"https://midkar.com/{genre_name}/{genre_name}_01.html"

address_splitted = URL.split("/")
folder = os.path.join("genresDataset", genre_name, "midkar")
if not os.path.isdir(folder):
    os.mkdir(folder)


page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")
results = soup.find_all("a")

pages = []
for r in results:
    link = r["href"]
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
                
            song = requests.get(link)
            with open(os.path.join(folder, song_name), "wb") as f:
                f.write(song.content)
