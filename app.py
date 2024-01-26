# simple_api.py
import os.path
from flask import Flask, jsonify, Response
from flask_cors import CORS
from data_sources.trends import get_trending_repos
from data_sources.arxiv import fetch_archive

app = Flask(__name__)
CORS(app)

def root_dir():  # pragma: no cover
    return os.path.abspath(os.path.dirname(__file__))


def get_file(filename):  # pragma: no cover
    try:
        src = os.path.join(root_dir(), filename)
        # Figure out how flask returns static files
        # Tried:
        # - render_template
        # - send_file
        # This should not be so non-obvious
        return open(src).read()
    except IOError as exc:
        return str(exc)

@app.route('/daily', methods=['GET'])
def home():
    return jsonify(get_trending_repos())

@app.route('/weekly', methods=['GET'])
def weekly():
    return jsonify(get_trending_repos(since='weekly'))

@app.route('/monthly', methods=['GET'])
def monthly():
    return jsonify(get_trending_repos(since='monthly'))

@app.route('/')
def metrics():  # pragma: no cover
    content = get_file('frontends/arxiv/index.html')
    return Response(content, mimetype="text/html")

@app.route('/output.css')
def output_css():
    content = get_file('frontends/arxiv/src/output.css')
    return Response(content, mimetype="text/css")

@app.route('/arxiv/affective_computing', methods=['GET'])
def arxiv_affective_computing():
    return jsonify(fetch_archive(key_words='affective computing'))

if __name__ == '__main__':
    app.run(debug=True)
