"""
This is the backend app, built using flask.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_restful import Api, Resource

from driver import Driver

app = Flask(__name__)
api = Api(app)
CORS(app)

# TODO:
# implement the auth
# kickstart the process
# prep response
# send back response

# instantiating the driver
driver = Driver()


@app.route('/loginSpotify', methods=['POST'])
def login_user(auth_key):
    # authenticate the user using the passed auth key to get the sp object thingy
    spotify_object = login_user(auth_key)
    return spotify_object


@app.route('/setPlaylistName', methods=['POST'])
def register_playlist(name_of_playlist):
    driver.set_playlist_name(name_of_playlist)


@app.route('/receiveMetadata', methods=['POST'])
def receive_metadata():
    data = request.get_json()
    print(data)
    # TODO: parse data and separate it...
    return jsonify({"message": "Bob!"})


def process_data(data):
    # Process your data here
    processed_data = driver.harvest(data)
    return processed_data


if __name__ == '__main__':
    # the debug set to true logs stuff to the console, so we can debug (only when developing)
    app.run(debug=True)
