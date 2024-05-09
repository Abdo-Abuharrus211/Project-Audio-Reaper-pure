"""
This module will kick the process in motion (substituting main.py from the standalone program)
"""

import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from ai_filename_process import process_response, invoke_prompt_to_ai
from fileIO import select_folder, media_file_finder, metadata_harvester, failed_csv_writer, read_failed_tracks, \
    organize_harvest
from spotify_api_handler import get_or_create_playlist, search_songs_not_in_playlist, add_songs_to_playlist


# TODO: get the credentials for the Auth
#       get the name of the Playlist
#       get the metadata
#       return the stuff that needs to be conveyed(Songs added, songs failed...etc)
#       Consider making this a Class to have fields...

class Driver:
    def __init__(self):
        self.sp = None
        self.playlist_name = None
        self.metadata = None

    def login_user(self, auth_key):
        load_dotenv()
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        redirect_uri = 'http://localhost:8888'

        # Authenticate with Spotify API and instantiate a Spotify object
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(client_id, client_secret, redirect_uri,
                                      scope='playlist-modify-public playlist-modify-private playlist-read-private',
                                      open_browser=True))
        return self.sp

    def harvest(self, metadata):
        # TODO:  separate the  metadate from the blanks ('Unknown') that are sent from the frontend
        # so replace
        metadata, files_without_metadata = organize_harvest(metadata)
        filename_data = process_response(invoke_prompt_to_ai(files_without_metadata))
        metadata.extend(filename_data)
        playlist_id = get_or_create_playlist(self.sp, self.sp.current_user()['id'], self.playlist_name)
        new_songs, failed_tracks = search_songs_not_in_playlist(self.sp, playlist_id, metadata)
        # failed_csv_writer(failed_tracks)
        added_tracks = add_songs_to_playlist(self.sp, playlist_id, new_songs)
        return added_tracks, failed_tracks

    def set_playlist_name(self, name):
        self.playlist_name = name
