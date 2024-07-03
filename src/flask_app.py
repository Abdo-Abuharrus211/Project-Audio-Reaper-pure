"""
This is the backend app, built using flask.
"""
import json
import os
import time

import redis
import spotipy
from dotenv import load_dotenv
from flask import Flask, request, jsonify, redirect, session
from flask_session import Session
from flask_cors import CORS
from flask_restful import Api

from driver import Driver

app = Flask(__name__)
app.secret_key = os.urandom(24)
api = Api(app)
app.config["SESSION_PERMANENT"] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)
# CORS(app, resources={r"/*": {"origins": "http://localhost:9000"}})
CORS(app, resources={r"/*": {"origins": "*"}})
load_dotenv()
# instantiating the driver
driver = Driver()

# Configure Redis
# try:
#     redis_client = redis.StrictRedis(
#         host=os.getenv('REDIS_HOST'),
#         port=int(os.getenv('REDIS_PORT')),
#         db=0,
#         decode_responses=True
#     )
#     redis_client.ping()  # Check if Redis server is reachable
# except redis.ConnectionError as e:
#     print(f"Could not connect to Redis: {e}")
#     redis_client = None

my_client_id = os.getenv('SPOTIFY_CLIENT_ID')
my_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
my_redirect_uri = 'https://project-audio-reaper-pure-4.onrender.com/callback'
# Set up Spotify OAuth
cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
sp_oauth = spotipy.oauth2.SpotifyOAuth(
    client_id=my_client_id, client_secret=my_client_secret, redirect_uri=my_redirect_uri,
    scope='playlist-modify-public playlist-modify-private playlist-read-private',
    cache_handler=cache_handler
)


@app.route('/login', methods=['GET'])
def login():
    auth_url = sp_oauth.get_authorize_url()
    return jsonify({"auth_url": auth_url})


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
        if token_info:
            session['token_info'] = token_info  # Store token info in session
        #     # Store the tokens in Redis with the user_id as the key
        #     user_id = token_info['id']  # Adjust based on actual token response structure
        #     redis_client.set(user_id, json.dumps(token_info))
        user = sp.current_user()
        driver.set_username(user["display_name"])
        return redirect(f'https://ar-web-app.onrender.com/?displayName={user["display_name"]}')
    except Exception as e:
        return f'An error occurred: {e}', 500


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('token_info', None)
    session.pop('auth_manager_state', None)
    session.clear()
    driver.clear_spotify_object()
    print(f"{driver.get_username()} is logged out.")
    return jsonify({'message': 'Logged out successfully'})
    # try:
    #     if session.get(['token_info']) is not None:
    #         session.pop('token_info', None)
    #         return jsonify({'message': 'Logged out successfully'})
    #     elif session.get(['token_info']) is None:
    #         return jsonify({'message': 'Error: User not logged in!'})
    # except Exception as e:
    #     return jsonify({'message': f"Error logging out: {e}"}), 500


@app.route('/setPlaylistName/<name>', methods=['POST'])
def register_playlist(name):
    if not name or type(name) is not str:
        return jsonify({"message": "Non valid value" + name}), 400
    print("Playlist is called: " + name)
    driver.set_playlist_name(name)
    return jsonify({"message": "Playlist name set to " + name})


@app.route('/receiveMetadata', methods=['POST'])
def receive_metadata():
    try:
        if driver.get_sp_object() is not None:
            data = request.get_json()
            if not data:
                return jsonify({"message": "Data not valid"}), 400
            driver.harvest(data)
            return jsonify({"message": "Metadata received"})
    except Exception as e:
        return f'An error occurred: {e}', 500


@app.route('/getResults', methods=['GET'])
def send_results():
    results = driver.get_added()
    return jsonify(results)


@app.route('/getFailed', methods=['GET'])
def send_failed():
    failed = driver.get_failed()
    return jsonify(failed)


@app.route('/getDisplayName', methods=['GET'])
def send_display_name():
    name = driver.get_username()
    return jsonify(name)


if __name__ == '__main__':
    # the debug set to true logs stuff to the console, so we can debug (only when developing)
    app.run(debug=False, port=5000)
