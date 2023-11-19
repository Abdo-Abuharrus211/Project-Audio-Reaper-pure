import os
import tinytag
import csv
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth


def csv_writer(playlist_name, metadata_list):
    # Get the directory of the current script
    current_directory = os.path.dirname(os.path.abspath(__file__))
    # Get the parent directory (project root)
    parent_directory = os.path.dirname(current_directory)
    # Path to the 'metadata' directory in the project root
    metadata_directory = os.path.join(parent_directory, 'metadata')
    # Check if the 'metadata' directory exists, if not, create it
    if not os.path.exists(metadata_directory):
        os.makedirs(metadata_directory)

    # Path to the CSV file in the 'metadata' directory
    csv_file_path = os.path.join(metadata_directory, playlist_name + '.csv')

    # Create/Open the CSV file
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # If you have headers like 'title', 'artist', 'album', you can write them here
        # writer.writerow(['Title', 'Artist', 'Album'])
        for file in metadata_list:
            writer.writerow([file['title'], file['artist'], file['album']])
    return csv_file_path


def metadata_harvester(audio_files):
    metadata = []
    current_directory = os.path.dirname(os.path.abspath(__file__))
    parent_directory = os.path.dirname(current_directory)
    # Path to the 'metadata' directory in the project root
    failure_directory = os.path.join(parent_directory, 'failure')
    failure_file_path = os.path.join(failure_directory, 'metadataFail.txt')
    if not audio_files:
        print("No audio files found in directory.")
    else:
        # Ensure the 'failure' directory exists
        if not os.path.exists(failure_directory):
            os.makedirs(failure_directory)

        with open(failure_file_path, 'a') as fail_file:
            for file in audio_files:
                audio_file = tinytag.TinyTag.get(file)
                if audio_file.title or audio_file.artist or audio_file.album:
                    metadata.append({'title': audio_file.title, 'artist': audio_file.artist, 'album': audio_file.album})
                else:
                    # Write the file name to metadataFail.txt
                    fail_file.write(file + '\n')

    return metadata


def folder_finder(target_directory):
    audio_files = []
    for file in os.listdir(target_directory):
        if file.endswith(".mp3") or file.endswith(".wav"):
            full_path = os.path.join(target_directory, file)  # Add this line
            audio_files.append(full_path)
    return audio_files


def get_or_create_playlist(sp, user_id, playlist_name):
    playlists = sp.current_user_playlists()
    for playlist in playlists['items']:
        if playlist['name'] == playlist_name:
            return playlist['id']  # Playlist exists, return its ID

    # Playlist not found, create a new one
    new_playlist = sp.user_playlist_create(user_id, playlist_name, public=True)
    return new_playlist['id']


def search_songs_not_in_playlist(sp, playlist_id, csv_file_path):
    not_in_playlist = []
    existing_track_ids = set()

    # Retrieve current tracks in the playlist
    results = sp.playlist_items(playlist_id)
    for item in results['items']:
        track = item['track']
        existing_track_ids.add(track['id'])

    with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            query = f"track:{row[0]} artist:{row[1]}"
            result = sp.search(query, type='track', limit=1)
            tracks = result['tracks']['items']
            if tracks and tracks[0]['id'] not in existing_track_ids:
                not_in_playlist.append(tracks[0]['id'])
            elif not tracks:
                print(f"Could not find track: {row[0]} by {row[1]}")

    return not_in_playlist


def add_songs_to_playlist(sp, playlist_id, track_ids):
    added_tracks = []
    if track_ids:
        sp.playlist_add_items(playlist_id, track_ids)
        added_tracks = track_ids
    return added_tracks


def main():
    # Retrieve environment variables
    load_dotenv()
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

    # Authenticate with Spotify API and instantiate a Spotify object
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(client_id, client_secret, redirect_uri='https://localhost:8080/callback'
                                  , scope='playlist-modify-public playlist-read-private'))

    target_directory = input("Please enter the absolute path of the directory you would like to harvest:")
    playlist_name = input("Please enter the name of the playlist you would like to create:")
    print("Harvesting audio files...")
    audio_files = folder_finder(target_directory)
    metadata_harvester(audio_files)
    csv_file_path = csv_writer(playlist_name, metadata_harvester(audio_files))

    # with open(os.path.join('../metadata', playlist_name + '.csv'), 'r', encoding='utf-8') as csv_file:
    #     print(csv_file.read())

    user_id = sp.current_user()['id']
    playlist_id = get_or_create_playlist(sp, user_id, playlist_name)

    track_ids_not_in_playlist = search_songs_not_in_playlist(sp, playlist_id, csv_file_path)
    added_tracks = add_songs_to_playlist(sp, playlist_id, track_ids_not_in_playlist)
    print("========================================")
    print(f"Added {len(added_tracks)} songs to the playlist.")


if __name__ == '__main__':
    main()
