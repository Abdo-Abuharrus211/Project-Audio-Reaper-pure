import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from src.ai_filename_process import process_response, invoke_prompt_to_ai
from src.fileIO import select_folder, media_file_finder, metadata_harvester, failed_csv_writer
from src.spotify_api_handler import get_or_create_playlist, search_songs_not_in_playlist, add_songs_to_playlist, \
    retry_failed_tracks


def main():
    load_dotenv()
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    redirect_uri = 'https://localhost:8888'

    # Authenticate with Spotify API and instantiate a Spotify object
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(client_id, client_secret, redirect_uri,
                                  scope='playlist-modify-public playlist-modify-private playlist-read-private',
                                  open_browser=True))

    # After auth then start calling the functions to execute program
    target_directory = ""
    while not target_directory:
        try:
            target_directory = select_folder()
        except FileNotFoundError:
            print("No folder selected")
        else:
            print("Harvesting audio files from " + target_directory + "...")
    playlist_name = input("Please enter the name of the playlist you would like to create:")
    library_size = len(os.listdir(target_directory))
    print(f"Harvesting %i audio files..." % library_size)

    audio_files = media_file_finder(target_directory)
    metadata, files_without_metadata = metadata_harvester(audio_files)
    print("The following files have no metadata:", files_without_metadata)
    filename_data = process_response(invoke_prompt_to_ai(files_without_metadata))
    # print(filename_data)
    metadata.extend(filename_data)
    playlist_id = get_or_create_playlist(sp, sp.current_user()['id'], playlist_name)

    new_songs, failed_tracks = search_songs_not_in_playlist(sp, playlist_id, metadata)
    failed_csv_writer(failed_tracks)
    added_tracks = add_songs_to_playlist(sp, playlist_id, new_songs)
    print("Second chance! Retrying failed tracks...")
    add_songs_to_playlist(sp, playlist_id, retry_failed_tracks())
    print("========================================")
    print(f"Added {len(added_tracks)} song(s) to the playlist.")
    print("========================================")
    print("AudioReaper has finished harvesting your audio files.")


if __name__ == "__main__":
    main()
