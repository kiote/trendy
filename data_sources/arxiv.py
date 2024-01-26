# fetch_archive_refactored.py
import requests
import xml.etree.ElementTree as ET
import os
import logging
import http.client as http_client
from datetime import datetime

BASE_ARXIV_URL = 'http://export.arxiv.org/api/query?'
OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions'
API_KEY = os.getenv('OPENAI_API_KEY')

# Cache for storing results
cache = {}

def enable_requests_logging():
    """ Enable detailed logging for requests made using `requests` library. """
    # Enable logging at the DEBUG level
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)

    # Enable HTTP client logging to capture HTTP requests
    http_client.HTTPConnection.debuglevel = 1

    # Set up logging for the requests module
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

def is_cached(cache_key):
    """ Check if the result is in the cache. """
    return cache_key in cache

def cache_result(cache_key, result):
    """ Cache the result. """
    cache[cache_key] = result

def get_cache_key(key_words, max_results):
    """ Generate a cache key based on the current date, keywords, and max results. """
    current_date = datetime.now().strftime("%Y-%m-%d")
    return (current_date, key_words, max_results)

def fetch_from_arxiv(key_words, max_results):
    """ Fetch data from ArXiv and parse XML. """
    formatted_search_term = f'"{key_words}"'
    query_params = {
        "search_query": f'cat:cs.* AND (ti:{formatted_search_term} OR abs:{formatted_search_term})',
        "start": 0,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": max_results
    }

    response = requests.get(BASE_ARXIV_URL, params=query_params)

    if response.status_code != 200:
        print("Error fetching data from ArXiv")
        return []

    root = ET.fromstring(response.content)
    return parse_xml(root)

def parse_xml(root):
    """ Parse the XML response from ArXiv to extract paper details. """
    papers = []
    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
        paper = {
            "title": entry.find('{http://www.w3.org/2005/Atom}title').text,
            "authors": [author.find('{http://www.w3.org/2005/Atom}name').text for author in entry.findall('{http://www.w3.org/2005/Atom}author')],
            "summary": extract_goals_and_results(entry.find('{http://www.w3.org/2005/Atom}summary').text),
            "published": entry.find('{http://www.w3.org/2005/Atom}published').text,
            "link": entry.find('{http://www.w3.org/2005/Atom}id').text
        }
        papers.append(paper)
    return papers

def extract_goals_and_results(summary):
    """ Communicate with ChatGPT API to extract goals and results from the summary. """
    enable_requests_logging()

    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": (
                    "Extract goals and results from the summary: " + summary + "\n\n"
                    "Provide a result in html format with goals and results in bold, "
                    "every goal and result from a new line."
                    "For example:"
                    "<b>Goals:</b><br/>"
                    "1. Goal 1<br/><br/>"
                    "2. Goal 2<br/><br/>"
                    "<hr><b>Results:</b><br/>"
                    "1. Result 1<br/><br/>"
                    "2. Result 2<br/><br/>"
                    "DO NOT skip <br/><br/> tags."
                )
            }
        ],
        "temperature": 0
    }

    response = requests.post(OPENAI_API_URL, headers=headers, json=data)

    if response.status_code == 200:
        api_response = response.json()
        print("ChatGPT API response:")
        print(api_response)
        return api_response.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
    else:
        print("Error communicating with ChatGPT API")
        return "Goals and results extraction failed."
    
def fetch_archive(key_words='affective computing', max_results=20):
    """ Main function to fetch archives, either from cache or from ArXiv. """
    if API_KEY is None or API_KEY == '':
        print("OPENAI_API_KEY environment variable not set.")
        return []
    cache_key = get_cache_key(key_words, max_results)

    if is_cached(cache_key):
        return cache[cache_key]

    papers = fetch_from_arxiv(key_words, max_results)
    cache_result(cache_key, papers)

    return papers
