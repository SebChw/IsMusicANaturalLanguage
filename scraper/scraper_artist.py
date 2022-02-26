from bs4 import BeautifulSoup
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
import os

"""Scraper written specifically for the page freemidi.org This is probably the best page with midi, as it has classification
    of artist based on ganres.
    
    With this scraper you can download all songs from specific artist if it is on the page. 
"""

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


artist_name = input(
    "type in artist name (lowercase, no space, no special characters): ")

# Just in case someone don't respect the rules.
artist_name = artist_name.lower()
artist_name = artist_name.strip()
artist_name = "".join(artist_name.split(" "))

URL = f"https://freemidi.org/artists-{artist_name[0]}" #We get page with all artists. As at first we need to check
#If this artist is even on the page

artists_page = requests.get(URL)
artists_soup = BeautifulSoup(artists_page.content, "html.parser")

artists = artists_soup.find_all(class_="genre-link-text") #here we have all objects with artists links

working_path = os.getcwd()


for artist in artists:
    artist_link = artist.find("a")["href"]
    artist_name_2 = "".join(artist_link.split("-")[2:]) #artist name of currently considered artist link
    if artist_name_2 == artist_name:
        #If we have a match we go to the artist page and download everything
        URL = f"https://freemidi.org/{artist_link}"
        artist_page = requests.get(URL)
        artist_soup = soup = BeautifulSoup(artist_page.content, "html.parser")

        working_path_artist = os.path.join(working_path, artist_name)

        if not os.path.isdir(working_path_artist):
            os.mkdir(working_path_artist)

        options = webdriver.ChromeOptions() # on freemidi page we need to fire click events

        prefs = {"download.default_directory": working_path_artist} #to download our files directly to folder of interest

        options.add_experimental_option("prefs", prefs)

        driver = webdriver.Chrome(
            executable_path='./chromedriver', chrome_options=options) #Not to puth chromedriver in the PATH

        #Now we iterate over all song pages of given artist
        for a_link in find_sublinks(artist_link):
            URL = f"https://freemidi.org/{a_link}"
            artist_page = requests.get(URL)
            artist_soup = soup = BeautifulSoup(
                artist_page.content, "html.parser")

            songs = artist_soup.find_all(class_="artist-song-cell") # get all songs

            for song in songs:
                print(song)
                link = song.find("a")["href"]
                #some links are unfortunately broken, that's why this is in try except block
                try:
                    driver.get(f"https://freemidi.org/{link}") # try to open page with given song

                    gotit = driver.find_element(By.ID, 'downloadmidi') #try to find clickable element that will download song

                    gotit.click() #download it
                except:
                    continue

        clean_dir(working_path_artist)
