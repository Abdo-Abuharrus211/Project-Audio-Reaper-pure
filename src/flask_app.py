"""
This is the backend app, built using flask.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_restful import Api, Resource

from src.driver import harvest

app = Flask(__name__)
api = Api(app)
CORS(app)


@app.route('/loginSpotify', methods=['POST'])
def login_user(auth_key):
    # authenticate the user using the passed auth key to get the sp object thingy
    spotify_object = login_user(auth_key)
    return "Bob!"


@app.route('/receiveMetadata', methods=['POST'])
def receive_metadata():
    data = request.get_json()
    print(data)
    # parse data and separate it
    return jsonify(data)


def process_data(data):
    # Process your data here
    processed_data = harvest(data)
    return data


if __name__ == '__main__':
    # the debug set to true logs stuff to the console, so we can debug (only when developing)
    app.run(debug=True)
