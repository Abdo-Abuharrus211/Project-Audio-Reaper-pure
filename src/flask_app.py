"""
This is the backend, built using flask with redis for server-side sessions
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
backup_secret_key = os.urandom(24)
app.secret_key = os.getenv('SECRET_KEY', backup_secret_key)
api = Api(app)
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
redis_client = redis.from_url(os.getenv('REDIS_HOST'))
app.config['SESSION_REDIS'] = redis_client

app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Ensure the cookie is sent with cross-site requests
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True if using HTTPS

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=120)

server_session = Session(app)

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
# CORS(app, resources={r"/*": {"origins": "http://myfrontend.com"}})
load_dotenv()

MY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
MY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
MY_REDIRECT_URI = 'http://localhost:5000/callback'
# cache_handler = spotipy.cache_handler.RedisCacheHandler(redis_client)
print('Redis Instance Running? ' + str(redis_client.ping()))


def update_user_data_in_session(user_id, data):
    session[f'user_{user_id}'] = data
    session.modified = True
    print('session data updated')


@app.route('/login', methods=['GET'])
def login():
    sp_oauth = spotipy.oauth2.SpotifyOAuth(
        client_id=MY_CLIENT_ID, client_secret=MY_CLIENT_SECRET, redirect_uri=MY_REDIRECT_URI,
        scope='user-read-private playlist-modify-public playlist-modify-private playlist-read-private',
        cache_handler=None, cache_path=None
    )
    auth_url = sp_oauth.get_authorize_url()
    return jsonify({"auth_url": auth_url})  # auth code is exchanged for a token, then redirects to callback URI


@app.route('/callback', methods=['GET'])
def callback():
    code = request.args.get('code')
    if not code:
        return 'Authorization failed', 401
    try:
        return redirect(f'http://localhost:9000/?code={code}')
    except spotipy.SpotifyOauthError as s:
        app.logger.error(f"Spotify OAuth error: {s}")
        return f'A Spotify OAuth error occurred: {s}', 401
    except Exception as e:
        app.logger.error(f"An error occurred: {e}")
        return f'An error occurred: {e}', 500


@app.route('/logout', methods=['POST'])
def logout():
    if session:
        try:
            session.clear()
            # session.pop(f'user_{username}', None)
            # session.pop('spotify_auth_state', None)
            return jsonify({'message': 'Logged out successfully'})
        except Exception as e:
            return f'An error occurred: {e}', 500
    else:
        return 'Session expired or user not logged in.', 403


@app.route('/exchangeCodeSession/<code>', methods=['POST'])
def add_user_data_to_session(code):
    if not code:
        return 'Authorization Failed', 401
    try:
        sp_oauth = spotipy.oauth2.SpotifyOAuth(
            client_id=MY_CLIENT_ID, client_secret=MY_CLIENT_SECRET, redirect_uri=MY_REDIRECT_URI,
            scope='user-read-private playlist-modify-public playlist-modify-private playlist-read-private',
            cache_handler=None, cache_path=None
        )
        token_info = sp_oauth.get_access_token(code, check_cache=False)
        access_token = token_info['access_token']
        sp = spotipy.Spotify(auth=access_token)
        user = sp.current_user()
        # Log session and token information
        app.logger.debug(f"Session ID: {session.sid}")
        app.logger.debug(f"Access Token: {access_token}")
        app.logger.debug(f"User: {user['display_name']}")

        session.clear()
        session['token'] = token_info
        session['username'] = user['display_name']
        session['user_id'] = user['id']
        session['playlist_name'] = None
        session['added_songs'] = None
        session['failed_songs'] = None
        # session[f"user_{user['id']}"] = user_data
        return jsonify({'username': user['display_name']})
    except spotipy.SpotifyOauthError as s:
        app.logger.error(f"Spotify OAuth error: {s}")
        return f'A Spotify OAuth error occurred: {s}', 401


# TODO: Add exception handling here and beyond and test if actually work when multiple users logged in at once
@app.route('/setPlaylistName/<name>/', methods=['POST'])
def register_playlist(name):

    if session:
        if not name or not isinstance(name, str):
            return jsonify({"message": "Non valid value" + name}), 400
        session['playlist_name'] = name
        print("Playlist is called: " + name)
        return jsonify({"message": "Playlist name set to " + name})
    else:
        return 'Session expired or user not logged in.', 403


@app.route('/receiveMetadata', methods=['POST'])
def receive_metadata():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Data not valid"}), 400
    if session:
        try:
            token_info = session['token']
            sp = spotipy.Spotify(auth=token_info['access_token'])
            driver = Driver()
            driver.set_username(session['username'])
            driver.set_playlist_name(session['playlist_name'])
            driver.set_sp_object(sp)
            driver.harvest(data)
            session['failed_songs'] = driver.get_failed()
            # update_user_data_in_session(username, user_data)  # update user data in session
            return jsonify({"message": "Metadata received"})
        except Exception as e:
            return f'An error occurred: {e}', 500
    else:
        return 'Session expired or user not logged in', 403


@app.route('/getResults', methods=['GET'])
def send_results():
    if session:
        results = session['added_songs']
        return jsonify(results)
    else:
        return 'Session expired or user not logged in', 403


@app.route('/getFailed', methods=['GET'])
def send_failed():
    if session:
        failed = session['failed_songs']
        return jsonify(failed)
    else:
        return 'Session expired or user not logged in', 403


@app.route('/getDisplayName', methods=['GET'])
def send_display_name():
    if session:
        return jsonify(session['username'])
    else:
        return 'Session expired or user not logged in', 403


# Test routes ahead
@app.route('/debug/sessions', methods=['GET'])
def debug_sessions():
    if app.debug:
        all_sessions = {}
        for key in session.keys():
            try:
                value = session[key]
                if isinstance(value, (str, int, float, bool, list, dict)):
                    all_sessions[key] = value
                else:
                    all_sessions[key] = str(value)
            except Exception as e:
                all_sessions[key] = f"Error retrieving session data: {str(e)}"

        return jsonify({
            "current_sessions": all_sessions,
            "session_interface": str(type(app.session_interface)),
            "session_redis_url": str(app.config.get('SESSION_REDIS'))
        })
    else:
        return jsonify({"error": "This endpoint is only available in debug mode"}), 403


@app.route('/test_add', methods=['POST'])
def add_session():
    session['Citron'] = "Limon"
    return jsonify('Success')


@app.route('/test_get/<user_id>', methods=['GET'])
def get_session(user_id):
    data = session.get(user_id)
    return data


@app.route('/test_clear', methods=['POST'])
def clear_session():
    session.clear()
    return jsonify('Success')


if __name__ == '__main__':
    # remember to set debug to false when in prod
    app.run(debug=True, port=5000)
