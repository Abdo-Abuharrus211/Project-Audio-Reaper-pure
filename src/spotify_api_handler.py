"""
    1. Prompt user to log in to Spotify
    2. Prompt user to enter the name of the playlist and check if it exists
        i. If it exists, return Playlist ID
        ii. If it does not exist, create a new playlist and return Playlist ID
    4. Search for the songs using the metadata
    5. Check if the song exists in the playlist (account for playlists with more than 100 songs)
        i. If it exists, skip
        ii. If it does not exist, add the song to the playlist

    """
import os

import requests
from fuzzywuzzy import fuzz
import Levenshtein

from src.fileIO import clean_metadata


def get_or_create_playlist(sp, user_id, playlist_name):
    """
    Retrieve user's Spotify playlist if it exists, otherwise create one.

    :param sp: authenticated Spotify object
    :param user_id: The user's Spotify ID
    :param playlist_name: the name of the playlist
    :precondition: user_id and playlist_name are valid strings
    :postcondition: either get the playlist's id or create a new one and get its id
    :return: the playlist's id
    """
    try:
        playlists = sp.current_user_playlists()
        for playlist in playlists['items']:
            if playlist['name'] == playlist_name:
                return playlist['id']

        new_playlist = sp.user_playlist_create(user_id, playlist_name, public=True)
        return new_playlist['id']
    except Exception as e:
        print(f"Spotify API error occurred while creating playlist: {e}")
        return None


def check_both_available(song_data) -> bool:
    """
    This function checks if a song's metadat includes both the title and artist.

    :param song_data: a dictionary containing song metadata
    :return: a boolean value, True if both are available, false otherwise
    """
    if song_data['Title'] != "" and song_data['Artist'] != "":
        return True
    else:
        return False


def search_songs_not_in_playlist(sp, playlist_id, metadata_list):
    """
    Search for songs in the list of song metadata dictionaries and return a list of songs not in the playlist
            and a list of songs not found on Spotify.

    :param sp: authenticated Spotify object
    :param playlist_id: a string representing the playlist's id
    :param metadata_list: a list of dictionaries containing songs' metadata
    :precondition: playlist_id and csv_file_path are valid strings
    :return: a tuple of lists, the first list contains the track ids of songs not in the playlist, and the second list
    contains the titles of songs that could not be found on Spotify
    """
    not_in_playlist = []
    existing_track_ids = set()
    failed_tracks = []
    results = sp.playlist_items(playlist_id)
    for item in results['items']:
        track = item['track']
        existing_track_ids.add(track['id'])

    for song in metadata_list:
        clean_title, clean_artist = clean_metadata(song['Title'], song['Artist'])
        both_artist_and_title = check_both_available(song)
        query = ""
        if both_artist_and_title:
            query = f"track:{clean_title} artist:{clean_artist}"
        else:
            query = f"track:{clean_title}"
        try:
            result = sp.search(query, type='track', limit=5)
            tracks = result['tracks']['items']
            if tracks:
                best_match = find_best_match(query, tracks)
                if best_match['id'] not in existing_track_ids:
                    not_in_playlist.append(best_match['id'])
            else:
                failed_tracks.append(f"{clean_title}, {clean_artist}")
                print(f"Could not find track on Spotify: {clean_title} by {clean_artist}")
        except requests.exceptions.ReadTimeout:
            print(f"Spotify API timeout occurred for track: {query}")
            failed_tracks.append(query)
        except Exception as e:
            print(f"Spotify API error occurred while searching for songs: {e}")
    return not_in_playlist, failed_tracks


def find_best_match(query, tracks):
    """
    Find the best match for a query in a list of tracks.
    :param query: A string representing the query containing the song's title and artist
    :param tracks: a list of dictionaries containing song metadata
    :return: a dictionary representing the best match for the query
    """
    similarities = [fuzz.token_sort_ratio(f"{track['name']} {track['artists'][0]['name']}", query) for track in tracks]
    best_match_index = similarities.index(max(similarities))
    best_match = tracks[best_match_index]
    return best_match


def add_songs_to_playlist(sp, playlist_id, track_ids):
    """
    Add songs to the Spotify playlist in batches of 100 songs at a time.

    :param sp: an authenticated Spotify object
    :param playlist_id: a string representing the playlist's IDs
    :param track_ids: a list of strings representing song IDs
    :precondition: playlist_id is a valid string
    :precondition: track_id is a valid non-empty list of strings
    :return: a list of songs added to the playlist
    """
    added_tracks = []
    batch_size = 100
    try:
        for i in range(0, len(track_ids), batch_size):
            batch = track_ids[i:i + batch_size]
            sp.playlist_add_items(playlist_id, batch)
            added_tracks.extend(batch)
    except Exception as e:
        print(f"Spotify API error occurred while adding songs to playlist: {e}")
    return added_tracks
