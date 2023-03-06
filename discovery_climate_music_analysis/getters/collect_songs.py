import numpy as np
import pandas as pd
import spotipy as spy
from discovery_climate_music_analysis.utils.io import import_config
from dateutil.parser import parse

PARAMS = import_config("credentials.yaml")

from spotipy.oauth2 import SpotifyClientCredentials

sp = spy.Spotify(
    auth_manager=SpotifyClientCredentials(PARAMS["client_id"], PARAMS["client_secret"])
)
sp.trace = True


# Credit - https://github.com/spotipy-dev/spotipy/issues/322
def show_tracks(results, uriArray):
    for i, item in enumerate(results["items"]):
        track = item["track"]
        #         print(track)
        uriArray.append(track["id"])


def get_playlist_tracks(username, playlist_id):
    tracksId = []
    results = sp.user_playlist(username, playlist_id)
    tracks = results["tracks"]
    show_tracks(tracks, tracksId)
    #     print(tracks)
    while tracks["next"]:
        tracks = sp.next(tracks)
        show_tracks(tracks, tracksId)
    #         tracks.extend(results['items'])
    return tracksId


def get_track_info(song_id):
    track_info = sp.track(song_id)
    track_features = sp.audio_features(song_id)

    artist_uri = track_info["artists"][0]["uri"]
    artist_info = sp.artist(artist_uri)

    name = track_info["name"]
    artist = track_info["album"]["artists"][0]["name"]
    release_date = track_info["album"]["release_date"]
    length = track_info["duration_ms"]
    popularity = track_info["popularity"]
    artist_genres = artist_info["genres"]

    # listens, ranking of song (e.g. top 40),
    danceability = track_features[0]["danceability"]
    energy = track_features[0]["energy"]
    tempo = track_features[0]["tempo"]
    key = track_features[0]["key"]
    time_signature = track_features[0]["time_signature"]
    valence = track_features[0]["valence"]
    track_href = track_features[0]["track_href"]

    track = [
        name,
        artist,
        release_date,
        artist_genres,
        length,
        popularity,
        danceability,
        energy,
        tempo,
        key,
        time_signature,
        valence,
        track_href,
    ]

    return track


def get_songs(username, playlist_id):
    tracks = get_playlist_tracks(username, playlist_id)
    songs = []
    for item in tracks:
        songs.append(get_track_info(item))

    return songs


def create_dataframe(username, playlist_id):
    songs = get_songs(username, playlist_id)
    dataframe = pd.DataFrame(
        songs,
        columns=[
            "name",
            "artist",
            "release_date",
            "artist_genres",
            "length",
            "popularity",
            "danceability",
            "energy",
            "tempo",
            "key",
            "time_signature",
            "valence",
            "track_href",
        ],
    )
    dataframe["artist"] = dataframe["artist"].apply(lambda x: x.upper())
    dataframe["name"] = dataframe["name"].apply(lambda x: x.upper())
    dataframe = dataframe.drop_duplicates(["name", "artist"]).reset_index(drop=True)
    dataframe["release_year"] = dataframe["release_date"].apply(
        lambda x: parse(x, fuzzy=True).year
    )
    dataframe["release_year"] = pd.to_datetime(dataframe["release_year"], format="%Y")
    dataframe["release_year_"] = dataframe["release_year"].apply(lambda x: x.year)
    dataframe["release_decade"] = dataframe["release_year"].apply(
        lambda x: x.year - (x.year % 10)
    )

    return dataframe


def create_multi_playlist_dataframe(playlist_dict):
    full_list = []
    for id, username in playlist_dict.items():
        songs = get_songs(username, id)
        full_list.extend(songs)
    # print(full_list)

    dataframe = pd.DataFrame(
        full_list,
        columns=[
            "name",
            "artist",
            "release_date",
            "artist_genres",
            "length",
            "popularity",
            "danceability",
            "energy",
            "tempo",
            "key",
            "time_signature",
            "valence",
            "track_href",
        ],
    )

    dataframe["artist"] = dataframe["artist"].apply(lambda x: x.upper())
    dataframe["name"] = dataframe["name"].apply(lambda x: x.upper())
    dataframe = dataframe.drop_duplicates(["name", "artist"]).reset_index(drop=True)
    dataframe["release_year"] = dataframe["release_date"].apply(
        lambda x: parse(x, fuzzy=True).year
    )
    dataframe["release_year"] = pd.to_datetime(dataframe["release_year"], format="%Y")
    dataframe["release_year_"] = dataframe["release_year"].apply(lambda x: x.year)
    dataframe["release_decade"] = dataframe["release_year"].apply(
        lambda x: x.year - (x.year % 10)
    )

    return dataframe
