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


@app.route('/authCode', methods=['POST'])
def login_user():
    # authenticate the user using the passed auth key to get the sp object thingy
    code = request.json.get('code')
    if not code:
        return jsonify({"message": "Not an authentication code"}), 400
    print("auth code:" + code)
    spotify_object = driver.instantiate_sp_object(code)
    if spotify_object:
        return jsonify({"message": "Authenticated successfully"})
    else:
        return jsonify({"message": "Unsuccessful authentication"})


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
    if not data or type(data) is not dict:
        return jsonify({"message": "Data not valid"}), 400
    #  TODO: Do something here to pass it on or proceed process
    print("Metadata:\n", data)
    return jsonify({"message": "Metadata received"})


@app.route('/getResults', methods=['GET'])
def send_results():
    results = driver.added
    return jsonify(results)


@app.route('/getFailed', methods=['GET'])
def send_failed():
    failed = driver.failed
    return jsonify(failed)


def process_data(data):
    # Process your data here
    processed_data = driver.harvest(data)
    return processed_data


if __name__ == '__main__':
    # the debug set to true logs stuff to the console, so we can debug (only when developing)
    app.run(debug=True, port=5000)
