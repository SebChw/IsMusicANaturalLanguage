from bs4 import BeautifulSoup
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
import os


#! the very same functions are in scraper_artist.py. I just didn't want to make any dependencies with such simple scripts
def find_sublinks(artist_link):
    """Some artists have that many songs so we have multiple pages for them. This functions finds all subpages for given artist

       e.g if we have page freemidi/queen_1 script go on that page and seek for all specific hyperlinks.
       as a return we could get [freemidi/queen_1, freemidi/queen_2, ...., freemidi/queen_n]
    Args:
        artist_link (str): link to the home page of the artist

    Returns:
        _type_: list of all pages with songs that can be reached from the artist_link 
    """
    links = [artist_link]

    URL = f"https://freemidi.org/{artist_link}" # as it's written it works only for freemidi page
    artist_page = requests.get(URL)
    artist_soup = BeautifulSoup(artist_page.content, "html.parser")

    #So we iterate over all specific hyperlinks, and add them to the list
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


genre_name = input(
    "type in genre name (lowercase, no space, no special characters): ")

# Just in case someone don't respect the rules.
genre_name = genre_name.lower()
genre_name = genre_name.strip()
genre_name = "".join(genre_name.split(" "))

URL = f"https://freemidi.org/genre-{genre_name}" 

genre_page = requests.get(URL) #we get the page containing all artist that are in that specific genre
genre_soup = BeautifulSoup(genre_page.content, "html.parser")

artists = genre_soup.find_all(class_="genre-link-text") # artist block has such class

working_path = os.path.join(os.getcwd(), genre_name)

if not os.path.isdir(working_path):
    os.mkdir(working_path)

already_in = set(os.listdir(working_path)) #If we have some artist we will not download it once again


for artist in artists:
    artist_link = artist.find("a")["href"]

    artist_name = "".join(artist_link.split("-")[2:])

    if artist_name in already_in:
        print(f"Skipping {artist_name}")
        continue

    URL = f"https://freemidi.org/{artist_link}"
    artist_page = requests.get(URL)
    artist_soup = soup = BeautifulSoup(artist_page.content, "html.parser")

    #! In that script I'm also making sure that artist is associated to only one genre. To omit situatoion when same song is in rock and country.
    #! Unfortunately tagging with genres is not good when artist has more than 2 tags.
    genres = artist_soup.find(class_="col-md-12").find_all("a")

    num_of_genres = 0

    for a in genres:
        if "genre" in a['href']:
            num_of_genres += 1

    if num_of_genres > 1:
        continue

    working_path_artist = os.path.join(working_path, artist_name)

    if not os.path.isdir(working_path_artist):
        os.mkdir(working_path_artist)

    options = webdriver.ChromeOptions()

    prefs = {"download.default_directory": working_path_artist}

    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(
        executable_path='../chromedriver', chrome_options=options)

    #Here we just iterate over all pages with songs of given artist and try to get all songs from there
    for a_link in find_sublinks(artist_link):
        URL = f"https://freemidi.org/{a_link}"
        artist_page = requests.get(URL)
        artist_soup = soup = BeautifulSoup(artist_page.content, "html.parser")

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
