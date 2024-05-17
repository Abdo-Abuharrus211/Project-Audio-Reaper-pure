"""
This is the backend app, built using flask.
"""
import os

import spotipy
from dotenv import load_dotenv
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
from flask_restful import Api, Resource

from driver import Driver

app = Flask(__name__)
api = Api(app)
CORS(app)

# instantiating the driver
driver = Driver()

load_dotenv()
my_client_id = os.getenv('SPOTIFY_CLIENT_ID')
my_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
my_redirect_uri = 'http://localhost:5000/callback'
# Set up Spotify OAuth
sp_oauth = spotipy.oauth2.SpotifyOAuth(
    client_id=my_client_id, client_secret=my_client_secret, redirect_uri=my_redirect_uri,
    scope='playlist-modify-public playlist-modify-private playlist-read-private'
)


@app.route('/login', methods=['GET'])
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return 'Authorization failed', 401
    try:
        token_info = sp_oauth.get_access_token(code)
        access_token = token_info['access_token']
        sp = spotipy.Spotify(auth=access_token)
        driver.set_sp_object(sp)

        # Access user data using the Spotify object
        user = sp.current_user()
        return f'Logged in as {user["display_name"]}'
    except Exception as e:
        return f'An error occurred: {e}', 500


# @app.route('/authCode', methods=['POST'])
# def login_user():
#     # authenticate the user using the passed auth key to get the sp object thingy
#     code = request.json.get('code')
#     if not code:
#         return jsonify({"message": "Not an authentication code"}), 400
#     print("auth code:" + code)
#     spotify_object = driver.instantiate_sp_object(code)
#     if spotify_object:
#         return jsonify({"message": "Authenticated successfully"})
#     else:
#         return jsonify({"message": "Unsuccessful authentication"})


@app.route('/setPlaylistName/<name>', methods=['POST'])
def register_playlist(name):
    if not name or type(name) is not str:
        return jsonify({"message": "Non valid value" + name}), 400
    print("Playlist is called: " + name)
    driver.set_playlist_name(name)
    return jsonify({"message": "Playlist name set to " + name})


@app.route('/receiveMetadata', methods=['POST'])
def receive_metadata():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Data not valid"}), 400
    begin_process(data)
    return jsonify({"message": "Metadata received"})


@app.route('/getResults', methods=['GET'])
def send_results():
    results = driver.get_added()
    return jsonify(results)


@app.route('/getFailed', methods=['GET'])
def send_failed():
    failed = driver.get_failed()
    return jsonify(failed)


def begin_process(goodies):
    driver.harvest(goodies)


if __name__ == '__main__':
    # the debug set to true logs stuff to the console, so we can debug (only when developing)
    app.run(debug=True, port=5000)
