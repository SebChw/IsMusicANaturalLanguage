from bs4 import BeautifulSoup
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
import os


def find_sublinks(artist_link):
    links = [artist_link]

    URL = f"https://freemidi.org/{artist_link}"
    artist_page = requests.get(URL)
    artist_soup = soup = BeautifulSoup(artist_page.content, "html.parser")

    for a in artist_soup.find(class_="pagination").find_all("a"):
        link = a["href"]
        if link != "#":
            links.append(link)

    return links


def clean_dir(path):
    # it will remove all duplicates
    for file in os.listdir(path):
        if "(" in file:
            os.remove(os.path.join(path, file))


artist_name = input(
    "type in genre name (lowercase, no space, no special characters): ")

# Just in case someone don't respect the rules.
artist_name = artist_name.lower()
artist_name = artist_name.strip()
artist_name = "".join(artist_name.split(" "))

URL = f"https://freemidi.org/artists-{artist_name[0]}"

artists_page = requests.get(URL)
artists_soup = BeautifulSoup(artists_page.content, "html.parser")

artists = artists_soup.find_all(class_="genre-link-text")

working_path = os.getcwd()


for artist in artists:
    artist_link = artist.find("a")["href"]
    artist_name_2 = "".join(artist_link.split("-")[2:])
    if artist_name_2 == artist_name:
        URL = f"https://freemidi.org/{artist_link}"
        artist_page = requests.get(URL)
        artist_soup = soup = BeautifulSoup(artist_page.content, "html.parser")

        working_path_artist = os.path.join(working_path, artist_name)

        if not os.path.isdir(working_path_artist):
            os.mkdir(working_path_artist)

        options = webdriver.ChromeOptions()

        prefs = {"download.default_directory": working_path_artist}

        options.add_experimental_option("prefs", prefs)

        driver = webdriver.Chrome(
            executable_path='./chromedriver', chrome_options=options)

        # driver.get("https://freemidi.org")

        for a_link in find_sublinks(artist_link):
            URL = f"https://freemidi.org/{a_link}"
            artist_page = requests.get(URL)
            artist_soup = soup = BeautifulSoup(
                artist_page.content, "html.parser")

            songs = artist_soup.find_all(class_="artist-song-cell")

            for song in songs:
                print(song)
                link = song.find("a")["href"]

                try:
                    driver.get(f"https://freemidi.org/{link}")

                    gotit = driver.find_element(By.ID, 'downloadmidi')

                    gotit.click()
                except:
                    continue

        clean_dir(working_path_artist)
