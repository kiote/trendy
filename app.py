# simple_api.py
from flask import Flask, jsonify
from flask_cors import CORS
from data_sources.trends import get_trending_repos
from data_sources.arxiv import fetch_archive

app = Flask(__name__)
CORS(app)

@app.route('/')
@app.route('/daily', methods=['GET'])
def home():
    return jsonify(get_trending_repos())

@app.route('/weekly', methods=['GET'])
def weekly():
    return jsonify(get_trending_repos(since='weekly'))

@app.route('/monthly', methods=['GET'])
def monthly():
    return jsonify(get_trending_repos(since='monthly'))

@app.route('/arxiv/affective_computing', methods=['GET'])
def arxiv_affective_computing():
    return jsonify(fetch_archive(key_words='affective computing'))

if __name__ == '__main__':
    app.run(debug=True)
