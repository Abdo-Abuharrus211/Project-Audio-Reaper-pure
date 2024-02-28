import ntpath
import os
import re
import tinytag
import csv
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import tkinter as tk
from tkinter import filedialog, simpledialog


def csv_writer(playlist_name, metadata_list):
    """
    Write metadata to a CSV file that's named after the user's playlist.

    :param: playlist_name: a string representing the name of the playlist as entered by the user
    :param: metadata_list: a list of dictionaries containing the metadata of each audio file
    :precondition: playlist_name is a string, metadata_list is a list of dictionaries
    :postcondition: a CSV file is created in the 'metadata' directory
    :return: a string for the path of the CSV file
    """
    current_directory_path = os.path.dirname(os.path.abspath(__file__))
    parent_directory_path = os.path.dirname(current_directory_path)
    metadata_directory_path = os.path.join(parent_directory_path, 'metadata')
    if not os.path.exists(metadata_directory_path):
        os.makedirs(metadata_directory_path)
    csv_file_path = os.path.join(metadata_directory_path, playlist_name + '.csv')
    # Create/Open the CSV file
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # If you have headers like 'title', 'artist', 'album', you can write them here:
        # writer.writerow(['Title', 'Artist', 'Album'])
        for file in metadata_list:
            writer.writerow([file['title'], file['artist'], file['album']])
    return csv_file_path


# def parse_filename(file_name):
#     """
#     Parse the song file's name for relevant information to identify the song.
#
#     :param file_name: a string representing the file's name
#     :precondition: file_name must be a valid string
#     :postcondition: replace excess characters with spaces and split the string
#     :return: a substring containing only relevant information
#     """
#     # Remove the file extension
#     name, _ = os.path.splitext(file_name)
#     for delimiter in ['-', '_', '|', '(', ')', '[', ']', '&']:
#         name = name.replace(delimiter, ' ')
#     parts = [part for part in name.split(' ') if part]  # Filter out empty strings
#     return parts


def metadata_harvester(song_files):
    """
    Extract metadata (title, artist, & album) from song files.

    :param song_files: a list of MP3 and WAV files in the user specified directory
    :precondition: list must be non-empty and contain strings representing file paths
    :postcondition: extract necessary metadata from each file
    :return: a list of dictionaries of the songs' metadate, each song has a dictionary
    """
    metadata = []
    path_current_directory = os.path.dirname(os.path.abspath(__file__))
    path_parent_directory = os.path.dirname(path_current_directory)
    failure_directory = os.path.join(path_parent_directory, 'failure')
    failure_file_path = os.path.join(failure_directory, 'metadataFail.txt')
    if not song_files:
        print("No audio files found in directory.")
    else:
        if not os.path.exists(failure_directory):
            os.makedirs(failure_directory)

        with open(failure_file_path, 'w', encoding='utf-8') as fail_file:
            fail_file.truncate()
            for file in song_files:
                audio_file = tinytag.TinyTag.get(file)
                if audio_file.title or audio_file.artist or audio_file.album:
                    metadata.append({'title': audio_file.title, 'artist': audio_file.artist, 'album': audio_file.album})
                else:
                    # fail_file.write(file + '\n') # TODO: clean up and remove path from the file name
                    fail_file.write(ntpath.basename(file) + '\n')

    return metadata


def file_finder(target_directory):
    """
    Find all the MP3 and WAV files in a directory.

    :param target_directory: a string representing the path for the target folder
    :precondition: target_directory must be a valid path string
    :return: a list of strings, each being the path to a mp3 or wav file
    """
    audio_files = []
    for file in os.listdir(target_directory):
        if file.endswith(".mp3") or file.endswith(".wav"):
            full_path = os.path.join(target_directory, file)  # Add this line
            audio_files.append(full_path)
    return audio_files


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
    playlists = sp.current_user_playlists()
    for playlist in playlists['items']:
        if playlist['name'] == playlist_name:
            return playlist['id']

    new_playlist = sp.user_playlist_create(user_id, playlist_name, public=True)
    return new_playlist['id']


def clean_metadata(title, artist):
    """
    Remove excess unwanted characters from a song's metadata.

    :param title: a string representing the song's title
    :param artist: a string representing the song's artist
    :precondition: title and artist are valid strings
    :return: a tuple of strings representing the cleaned title and artist
    """
    # Remove common extraneous information from titles
    title = re.sub(r'\(.*\)|\[.*]|{.*}|-.*|ft\..*|feat\..*|official.*|video.*|\d+kbps.*', '', title,
                   flags=re.I).strip()
    # Refine artist name
    artist = artist.split(',')[0]  # Take the first artist if there are multiple
    artist = re.sub(r'\(.*\)|\[.*]|{.*}|official.*|video.*', '', artist, flags=re.I).strip()
    return title, artist


def search_songs_not_in_playlist(sp, playlist_id, csv_file_path):
    """
    Search for songs in the CSV file after checking they're not in the playlist.

    :param sp: authenticated Spotify object
    :param playlist_id: a string representing the playlist's id
    :param csv_file_path: a string representing the path to the CSV file
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

    with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            # Clean up metadata before search
            clean_title, clean_artist = clean_metadata(row[0], row[1])
            query = f"track:{clean_title} artist:{clean_artist}"
            result = sp.search(query, type='track', limit=1)
            tracks = result['tracks']['items']
            if tracks and tracks[0]['id'] not in existing_track_ids:
                not_in_playlist.append(tracks[0]['id'])
            elif not tracks:
                failed_tracks.append(f"{clean_title} by {clean_artist}")
                print(f"Could not find track on Spotify: {clean_title} by {clean_artist}")

    return not_in_playlist, failed_tracks


# TODO: move this part to a separate class and file
# def search_filename(sp, file_name):
#     """
#     Search for a song on Spotify using the file name.
#
#     :param sp: an authenticated Spotify object
#     :param file_name: a string representing the file's name
#     :precondition: file_name is a valid string
#     :return: a string representing the track's id0
#     """
#     parts = parse_filename(file_name)
#     best_match = None
#     max_popularity = -1
#
#     # Try all combinations of parts as artist and title
#     for i in range(1, len(parts)):
#         artist = ' '.join(parts[:i])
#         title = ' '.join(parts[i:])
#         query = f'track:{title} artist:{artist}'
#         result = sp.search(query, type='track', limit=1)
#         tracks = result['tracks']['items']
#         if tracks:
#             track = tracks[0]
#             # Select the track with the highest popularity
#             if track['popularity'] > max_popularity:
#                 best_match = track['id']
#                 max_popularity = track['popularity']
#
#     return best_match


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
    for i in range(0, len(track_ids), batch_size):
        batch = track_ids[i:i + batch_size]
        sp.playlist_add_items(playlist_id, batch)
        added_tracks.extend(batch)
    return added_tracks


def select_folder():
    """
    Prompt the user to select a folder.

    :return: a string representing the path of the selected folder
    """
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory()
    if not folder_path:
        raise FileNotFoundError
    return folder_path


def main():
    # Retrieve environment variables
    load_dotenv()
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    redirect_uri = 'https://localhost:8888'

    # Authenticate with Spotify API and instantiate a Spotify object
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(client_id, client_secret, redirect_uri,
                                  scope='playlist-modify-public playlist-modify-private playlist-read-private',
                                  open_browser=True))

    target_directory = ""
    while not target_directory:
        try:
            target_directory = select_folder()
        except FileNotFoundError:
            print("No folder selected")
        else:
            print("Harvesting audio files from " + target_directory + "...")

    # after selecting a directory I get prompted to copy & paste the URI response from the browser into the terminal
    # How can I automate that initial step so the user doesn't have to do it manually?

    playlist_name = input("Please enter the name of the playlist you would like to create:")
    library_size = len(os.listdir(target_directory))
    print("Harvesting audio files..." + str(library_size))

    audio_files = file_finder(target_directory)
    metadata_list = metadata_harvester(audio_files)
    csv_file_path = csv_writer(playlist_name, metadata_list)

    user_id = sp.current_user()['id']
    playlist_id = get_or_create_playlist(sp, user_id, playlist_name)

    track_ids_not_in_playlist = search_songs_not_in_playlist(sp, playlist_id, csv_file_path)
    added_tracks = add_songs_to_playlist(sp, playlist_id, track_ids_not_in_playlist[0])

    print("========================================")
    print(f"Added {len(added_tracks)} song(s) to the playlist.")
    print("========================================")
    print("AudioReaper has finished harvesting your audio files.")


if __name__ == '__main__':
    main()
