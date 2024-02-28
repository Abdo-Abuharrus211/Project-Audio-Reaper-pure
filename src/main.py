import os
import spotipy
from spotipy import SpotifyOAuth


def main():
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    redirect_uri = 'https://localhost:8888'

    # Authenticate with Spotify API and instantiate a Spotify object
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(client_id, client_secret, redirect_uri,
                                  scope='playlist-modify-public playlist-modify-private playlist-read-private',
                                  open_browser=True))


if __name__ == "__main__":
    main()
