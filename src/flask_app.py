"""
This is the backend app, built using flask.
"""
import os
from datetime import timedelta

import spotipy
from dotenv import load_dotenv
from flask import Flask, request, jsonify, redirect, session
from flask_session import Session
import redis
from flask_cors import CORS
from flask_restful import Api

from driver import Driver

app = Flask(__name__)
app.secret_key = os.urandom(24)
# TODO: get a secret key generated
# app.secret_key = os.getenv('SECRET_KEY', default='BAD_SECRET_KEY')
api = Api(app)
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.Redis(host='localhost', port=6379)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=120)
Session(app)

CORS(app, resources={r"/*": {"origins": "*"}})
# CORS(app, resources={r"/*": {"origins": "http://myfrontend.com"}})
load_dotenv()

my_client_id = os.getenv('SPOTIFY_CLIENT_ID')
my_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
my_redirect_uri = 'http://localhost:5000/callback'
cache_handler = spotipy.cache_handler.RedisCacheHandler(session)  # TODO: Double check this


@app.route('/login', methods=['GET'])
def login():
    sp_oauth = spotipy.oauth2.SpotifyOAuth(
        client_id=my_client_id, client_secret=my_client_secret, redirect_uri=my_redirect_uri,
        scope='playlist-modify-public playlist-modify-private playlist-read-private',
        cache_handler=cache_handler
    )
    auth_url = sp_oauth.get_authorize_url()
    session['spotify_auth_state'] = sp_oauth.state
    return jsonify({"auth_url": auth_url})


@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return 'Authorization failed', 401
    try:
        sp_oauth = spotipy.oauth2.SpotifyOAuth(
            client_id=my_client_id, client_secret=my_client_secret, redirect_uri=my_redirect_uri,
            scope='playlist-modify-public playlist-modify-private playlist-read-private',
            cache_handler=cache_handler
        )
        token_info = sp_oauth.get_access_token(code)
        access_token = token_info['access_token']
        sp = spotipy.Spotify(auth=access_token)
        user = sp.current_user()
        username = user['display_name']
        # Create user dictionary in session
        user_data = {'token': token_info, 'username': username,
                     'playlist_name': None, 'added_songs': None, 'failed_songs': None}
        print(session[user]['display_name'] + "IS ALIVE!")
        session[username] = user_data
        return redirect(f'http://localhost:9000/?displayName={username}')
    except spotipy.SpotifyOauthError as s:
        return f'A Spotify Oauth error occurred: {s}', 401
    except Exception as e:
        return f'An error occurred: {e}', 500


@app.route('/logout/<username>', methods=['POST'])
def logout(username):
    if session[username]:
        try:
            session.pop(username)
            session.pop('user_data', None)
            return jsonify({'message': 'Logged out successfully'})
        except Exception as e:
            return f'An error occurred: {e}', 500
    else:
        return 'Session expired or user not logged in.', 403


@app.route('/setPlaylistName/<username>/<name>', methods=['POST'])
def register_playlist(name, username):
    if session[username]:
        if not name or type(name) is not str:
            return jsonify({"message": "Non valid value" + name}), 400
        session.get('user_data')['playlist_name'] = name
        print("Playlist is called: " + name)
        return jsonify({"message": "Playlist name set to " + name})
    else:
        return 'Session expired or user not logged in.', 403


@app.route('/<username>/receiveMetadata', methods=['POST'])
def receive_metadata(username):
    if session[username]:
        try:
            user_session = session['user_data']
            print(user_session)
            token_info = user_session['token_info']
            sp = spotipy.Spotify(auth=token_info['access_token'])
            driver = Driver()
            driver.set_username(session['username'])
            driver.set_playlist_name(user_session['playlist_name'])
            driver.set_sp_object(sp)
            data = request.get_json()
            if not data:
                return jsonify({"message": "Data not valid"}), 400
            # Todo: start process here
            driver.harvest(data)
            session['failed_songs'] = driver.get_failed()
            return jsonify({"message": "Metadata received"})
        except Exception as e:
            return f'An error occurred: {e}', 500
    else:
        return 'Session expired or user not logged in', 403


@app.route('/<username>/getResults', methods=['GET'])
def send_results(username):
    if session[username]:
        results = session.get('added_songs')
        return jsonify(results)
    else:
        return 'Session expired or user not logged in', 403


@app.route('/<username>/getFailed', methods=['GET'])
def send_failed(username):
    if session[username]:
        failed = session.get('failed_songs')
        return jsonify(failed)
    else:
        return 'Session expired or user not logged in', 403


@app.route('/getDisplayName', methods=['GET'])
def send_display_name():
    if session['user_data']:
        return jsonify(session.get('user_data')['username'])
    else:
        return 'Session expired or user not logged in', 403


if __name__ == '__main__':
    # the debug set to true logs stuff to the console, so we can debug (only when developing)
    app.run(debug=True, port=5000)
