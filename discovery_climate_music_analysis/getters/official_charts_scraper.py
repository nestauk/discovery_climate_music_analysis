import csv
import requests
import bs4
import pandas as pd

# Credit: https://medium.com/@caineosborne/analysing-uk-chart-history-1956-to-2017-6fec0ecc991b - with changes made


def getsongs(url):
    """
    Scrapes UK Official Charts website.
    Cycling through the current week to the very first week available.
    """

    allsongs = []
    print("Getting Page %s" % url)
    req = requests.get(url)
    req.raise_for_status()

    # Exit loop if status code is not 200
    if req.status_code != 200:
        return None

    soup = bs4.BeautifulSoup(req.text, "lxml")

    # Retrieve chart dates and tidy the format
    sdate = soup.find_all("p", class_="article-date")
    date = sdate[0].text.split("-")[0]

    # retrieve album position, artist and album name
    positions = soup.find_all("span", class_="position")
    songs = soup.find_all("div", class_="title")
    artists = soup.find_all("div", class_="artist")

    # create a list of each album, tidying the format
    for i in range(0, len(positions)):
        song = []
        song.append(date.strip("\r").strip("\n").strip(" "))
        song.append(positions[i].text)
        song.append(artists[i].text.strip("\n").strip("\r"))
        song.append(songs[i].text.strip("\n").strip("\r"))
        # append each album list to the weeks list
        allsongs.append(song)

    # find previous weeks information and create link, exit loop if link can't be found
    prevlink = soup.find("a", text="prev")
    if prevlink == None:
        return None
    link = prevlink["href"]
    link = "http://www.officialcharts.com/" + link

    # write weekly albums to CSV, appending to existing file
    with open("output.csv", "a", newline="") as resultFile:
        wr = csv.writer(resultFile)
        wr.writerows(allsongs)
        resultFile.close()

    # clear out the weekly list and proceed to next weeks file
    allsongs = []
    getsongs(link)
