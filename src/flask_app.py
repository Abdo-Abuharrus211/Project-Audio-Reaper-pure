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

# TODO: Determine if these configs are needed
# app.config['SESSION_USE_SIGNER'] = True
# app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Ensure the cookie is sent with cross-site requests
# app.config['SESSION_COOKIE_SECURE'] = False  # Set to True if using HTTPS

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=120)

server_session = Session(app)

CORS(app, resources={r"/*": {"origins": "*"}})
# CORS(app, resources={r"/*": {"origins": "http://myfrontend.com"}})
load_dotenv()

MY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
MY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
MY_REDIRECT_URI = 'http://localhost:5000/callback'
cache_handler = spotipy.cache_handler.RedisCacheHandler(redis_client)
print('Redis Instance Running? ' + str(redis_client.ping()))


def get_user_data_from_session(user_id):
    # redundant but whatever, it's atomic...
    data = session.get(f'user_{user_id}')
    if data:
        return dict(data)
    else:
        return None


def update_user_data_in_session(user_id, data):
    session[f'user_{user_id}'] = data
    session.modified = True
    print(f'session data updated:\n{session.get(user_id)}')


@app.route('/login', methods=['GET'])
def login():
    sp_oauth = spotipy.oauth2.SpotifyOAuth(
        client_id=MY_CLIENT_ID, client_secret=MY_CLIENT_SECRET, redirect_uri=MY_REDIRECT_URI,
        scope='playlist-modify-public playlist-modify-private playlist-read-private',
        cache_handler=cache_handler
    )
    auth_url = sp_oauth.get_authorize_url()
    session['spotify_auth_state'] = sp_oauth.state  # This persists as it's before the callback route

    return jsonify({"auth_url": auth_url})  # auth code is exchanged for a token, then redirects to callback URI


@app.route('/exchangeCodeSession/<code>', methods=['POST'])
def big_weiner(code):
    if not code:
        return 'Authorization Failed', 401
    try:
        sp_oauth = spotipy.oauth2.SpotifyOAuth(
            client_id=MY_CLIENT_ID, client_secret=MY_CLIENT_SECRET, redirect_uri=MY_REDIRECT_URI,
            scope='playlist-modify-public playlist-modify-private playlist-read-private',
            cache_handler=cache_handler
        )
        token_info = sp_oauth.get_access_token(code)
        access_token = token_info['access_token']
        sp = spotipy.Spotify(auth=access_token)
        user = sp.current_user()
        user_data = {'token': token_info, 'username': user['display_name'],
                     'playlist_name': None, 'added_songs': None, 'failed_songs': None}
        session[f"user_{user['id']}"] = user_data
        return jsonify('Successfully exchanged token for user data'), 200
    except spotipy.SpotifyOauthError as s:
        app.logger.error(f"Spotify OAuth error: {s}")
        return f'A Spotify OAuth error occurred: {s}', 401


@app.route('/callback', methods=['GET'])
def callback():
    code = request.args.get('code')
    if not code:
        return 'Authorization failed', 401
    try:
        return jsonify(f'http://localhost:9000/?code={code}')
    except spotipy.SpotifyOauthError as s:
        app.logger.error(f"Spotify OAuth error: {s}")
        return f'A Spotify OAuth error occurred: {s}', 401
    except Exception as e:
        app.logger.error(f"An error occurred: {e}")
        return f'An error occurred: {e}', 500


@app.route('/logout/<user_id>', methods=['POST'])
def logout(user_id):
    user_data = session.get(f'user_{user_id}')
    if user_data:
        try:
            session.pop(f'user_{user_id}', None)
            session.pop('spotify_auth_state', None)
            return jsonify({'message': 'Logged out successfully'})
        except Exception as e:
            return f'An error occurred: {e}', 500
    else:
        return 'Session expired or user not logged in.', 403


# TODO: Add exception handling here and beyond and test if actually work when multiple users logged in at once
@app.route('/setPlaylistName/<name>/<user_id>', methods=['POST'])
def register_playlist(name, user_id):
    user_data = get_user_data_from_session(user_id)
    if user_data:
        if not name or not isinstance(name, str):
            return jsonify({"message": "Non valid value" + name}), 400
        user_data['playlist_name'] = name
        print("Playlist is called: " + name)
        return jsonify({"message": "Playlist name set to " + name})
    else:
        return 'Session expired or user not logged in.', 403


@app.route('/receiveMetadata/<user_id>', methods=['POST'])
def receive_metadata(user_id):
    user_data = get_user_data_from_session(user_id)
    data = request.get_json()
    if not data:
        return jsonify({"message": "Data not valid"}), 400
    if user_data:
        try:
            token_info = user_data['token']
            sp = spotipy.Spotify(auth=token_info['access_token'])
            driver = Driver()
            driver.set_username(user_data['username'])
            driver.set_playlist_name(user_data['playlist_name'])
            driver.set_sp_object(sp)
            driver.harvest(data)
            user_data['failed_songs'] = driver.get_failed()
            update_user_data_in_session(user_id, user_data)  # update user data in session
            return jsonify({"message": "Metadata received"})
        except Exception as e:
            return f'An error occurred: {e}', 500
    else:
        return 'Session expired or user not logged in', 403


@app.route('/<user_id>/getResults', methods=['GET'])
def send_results(user_id):
    user_data = get_user_data_from_session(user_id)
    if user_data:
        results = user_data.get('added_songs')
        return jsonify(results)
    else:
        return 'Session expired or user not logged in', 403


@app.route('/getFailed/<user_id>', methods=['GET'])
def send_failed(user_id):
    user_data = get_user_data_from_session(user_id)
    if user_data:
        failed = user_data.get('failed_songs')
        return jsonify(failed)
    else:
        return 'Session expired or user not logged in', 403


@app.route('/getDisplayName/<user_id>', methods=['GET'])
def send_display_name(user_id):
    user_data = get_user_data_from_session(user_id)
    if user_data:
        return jsonify(user_data['username'])
    else:
        return 'Session expired or user not logged in', 403


@app.route('/debug/sessions', methods=['GET'])
def debug_sessions():
    if app.debug:
        all_sessions = {}
        for key in session.keys():
            print(key)
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
    return jsonify(data)


@app.route('/test_clear', methods=['POST'])
def clear_session():
    session.clear()
    return jsonify('Success')


@app.route('/test_edit', methods=['PUT'])
def small_weiner():
    session[f"user_{'216duqlyymfjzxf2pirmwc7kq'}"]['token'] = 'Tugma'
    return jsonify('Success')


if __name__ == '__main__':
    # remember to set debug to false when in prod
    app.run(debug=True, port=5000)
