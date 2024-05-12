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


class Driver:
    def __init__(self):
        self.sp = None
        self.playlist_name = None
        self.metadata = None
        self.added = None
        self.failed = None

    def instantiate_sp_object(self, auth_code):
        load_dotenv()
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        redirect_uri = 'http://localhost:8888'
        try:
            sp_oauth = SpotifyOAuth(client_id, client_secret, redirect_uri,
                                    scope='playlist-modify-public playlist-modify-private playlist-read-private')
            auth_token = sp_oauth.get_access_token(code=auth_code)
            self.sp = spotipy.Spotify(auth=auth_token)

            return self.sp
        except Exception as e:
            print(f"Error occurred while instantiating Spotify object: {e}")
            return None

    def harvest(self, unrefined_data):
        try:
            metadata, files_without_metadata = organize_harvest(unrefined_data)
            filename_data = process_response(invoke_prompt_to_ai(files_without_metadata))
            metadata.extend(filename_data)
            playlist_id = get_or_create_playlist(self.sp, self.sp.current_user()['id'], self.playlist_name)
            new_songs, failed_tracks = search_songs_not_in_playlist(self.sp, playlist_id, metadata)
            added_tracks = add_songs_to_playlist(self.sp, playlist_id, new_songs)
            self.added = added_tracks
            self.failed = failed_tracks
            return self.added, self.failed
        except Exception as e:
            print(f"Error occurred while harvesting: {e}")
            return None, None

    def set_playlist_name(self, name):
        self.playlist_name = name

    def set_metadata(self, data):
        self.metadata = data
