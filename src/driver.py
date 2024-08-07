"""
This module will kick the process in motion (substituting main.py from the standalone program)
"""

from ai_filename_process import process_response, invoke_prompt_to_ai
from fileIO import organize_harvest
from spotify_api_handler import get_or_create_playlist, search_songs_not_in_playlist, add_songs_to_playlist


class Driver:
    def __init__(self):
        self.sp = None
        self.playlist_name = None
        self.username = None
        self.metadata = None
        self.added = None
        self.failed = None

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

    def get_added(self):
        return self.added

    def get_failed(self):
        return self.failed

    # def get_sp_object(self):
    #     return self.sp

    def set_sp_object(self, spot_obj):
        self.sp = spot_obj

    def set_playlist_name(self, name):
        self.playlist_name = name

    def set_username(self, name):
        self.username = name

    def get_username(self):
        return self.username
