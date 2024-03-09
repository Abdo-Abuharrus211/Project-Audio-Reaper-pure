import ntpath
import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from src.fileIO import select_folder, media_file_finder, metadata_harvester


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

    """
    1. pass the playlist name to check for it on spotify
    2. Read the metadata from the audio files
    3. Prompt the AI to read the filename and extract the metadata
    4. add them to the list of metadata tooo
    5. Search for the songs on Spotify
    6. Add the songs to the playlist (if they're not already on there)
    7. Organise how everything is called and setup the control flow
    """
    audio_files = media_file_finder(target_directory)
    metadata, files_without_metadata = metadata_harvester(audio_files)


if __name__ == "__main__":
    main()
