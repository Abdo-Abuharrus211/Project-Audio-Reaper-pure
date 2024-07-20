"""
This is the backend app, built using flask.
"""
import json
import os
import time
from datetime import timedelta

import redis
import spotipy
from dotenv import load_dotenv
from flask import Flask, request, jsonify, redirect, session
from flask_session import Session
from flask_cors import CORS
from flask_restful import Api
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required

from driver import Driver

app = Flask(__name__)
app.secret_key = os.urandom(24)
api = Api(app)
app.config['JWT_SECRET_KEY'] = os.urandom(24)
jwt = JWTManager(app)
app.config["SESSION_PERMANENT"] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)
Session(app)

# CORS(app, resources={r"/*": {"origins": "http://localhost:9000"}})
CORS(app, resources={r"/*": {"origins": "*"}})
load_dotenv()

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
my_redirect_uri = 'http://localhost:5000/callback'
# Set up Spotify OAuth
cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)


# TODO: set the following:
#  Move the instantiation of driver and sp out of the global scope
#   session['spotify_object'] = sp
#   session['username'] = user["display_name"
#  Remove username and sp from the driver
#  Review the login flow, may need to 'check' if user is remembered and then instantiate...

@app.route('/login', methods=['GET'])
def login():
    sp_oauth = spotipy.oauth2.SpotifyOAuth(
        client_id=my_client_id, client_secret=my_client_secret, redirect_uri=my_redirect_uri,
        scope='playlist-modify-public playlist-modify-private playlist-read-private',
        cache_handler=cache_handler
    )
    auth_url = sp_oauth.get_authorize_url()
    session['sp_oauth'] = sp_oauth
    return jsonify({"auth_url": auth_url})


@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return 'Authorization failed', 401
    try:
        sp_oauth = session.get('spotify_object')
        if not sp_oauth:
            return 'Session Expired', 401
        token_info = sp_oauth.get_access_token(code)
        access_token = token_info['access_token']
        sp = spotipy.Spotify(auth=access_token)
        user = sp.current_user()
        username = user['display_name']

        # Create user dictionary in session
        user_session_dictionary = {'display_name': username, 'sp_obj': sp, 'driver': Driver()}
        #     # Store the tokens in Redis with the user_id as the key
        #     user_id = token_info['id']  # Adjust based on actual token response structure
        #     redis_client.set(user_id, json.dumps(token_info))
        print(session[user]['display_name'] + "IS ALIVE!")
        session[username] = user_session_dictionary
        session[username]['driver'].set_username(username)
        return redirect(f'http://localhost:9000/?displayName={username}')
    except Exception as e:
        return f'An error occurred: {e}', 500


@app.route('/logout/<username>', methods=['POST'])
def logout(username):
    # name = request.args.get('username')
    if session.get(username):
        try:
            session.pop(username, None)
            # session.pop('token_info', None)
            # session.pop('auth_manager_state', None)
            session.clear()
            for key in list(session.keys()):
                session.pop(key)
            # TODO: inform frontend to clear local session and storage
            return jsonify({'message': 'Logged out successfully'})
        except Exception as e:
            return f'An error occurred: {e}', 401
    else:
        return 'Session expired or user not logged in...'
    # try:
    #     if session.get(['token_info']) is not None:
    #         session.pop('token_info', None)
    #         return jsonify({'message': 'Logged out successfully'})
    #     elif session.get(['token_info']) is None:
    #         return jsonify({'message': 'Error: User not logged in!'})
    # except Exception as e:
    #     return jsonify({'message': f"Error logging out: {e}"}), 500


@app.route('/setPlaylistName/<username>/<name>', methods=['POST'])
def register_playlist(name, username):
    if session.get(username):
        if not name or type(name) is not str:
            return jsonify({"message": "Non valid value" + name}), 400
        print("Playlist is called: " + name)
        session[username]['driver'].set_playlist_name(name)
        return jsonify({"message": "Playlist name set to " + name})
    else:
        return 'Session expired or user not logged in'


@app.route('/<username>/receiveMetadata', methods=['POST'])
def receive_metadata(username):
    if session[username]:
        try:
            if session[username]['driver'].get_sp_object() is not None:
                data = request.get_json()
                if not data:
                    return jsonify({"message": "Data not valid"}), 400
                session[username]['driver'].harvest(data)
                return jsonify({"message": "Metadata received"})
        except Exception as e:
            return f'An error occurred: {e}', 500
    else:
        return 'Session expired or user not logged in'


# TODO: add user checks for the following functions
@app.route('/<username>/getResults', methods=['GET'])
def send_results(username):
    results = session[username]['driver'].get_added()
    return jsonify(results)


@app.route('/<username>/getFailed', methods=['GET'])
def send_failed(username):
    failed = session[username]['driver'].get_failed()
    return jsonify(failed)


@app.route('/getDisplayName', methods=['GET'])
def send_display_name(username):
    name = session[username]['driver'].get_username()
    return jsonify(name)


if __name__ == '__main__':
    # the debug set to true logs stuff to the console, so we can debug (only when developing)
    app.run(debug=True, port=5000)
