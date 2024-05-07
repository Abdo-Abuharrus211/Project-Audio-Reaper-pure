"""
This is the backend app, built using flask.
"""
from flask import Flask, request, jsonify

app = Flask(__name__)


# set up a basic flask backend API
@app.route('/api', methods=['POST'])
def api():
    data = request.get_json()
    return jsonify(data)
