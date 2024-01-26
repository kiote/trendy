# fetch_archive_refactored.py
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

BASE_ARXIV_URL = 'http://export.arxiv.org/api/query?'

# Cache for storing results
cache = {}

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
            "summary": entry.find('{http://www.w3.org/2005/Atom}summary').text,
            "published": entry.find('{http://www.w3.org/2005/Atom}published').text,
            "link": entry.find('{http://www.w3.org/2005/Atom}id').text
        }
        papers.append(paper)
    return papers

def fetch_archive(key_words='affective computing', max_results=2):
    """ Main function to fetch archives, either from cache or from ArXiv. """
    cache_key = get_cache_key(key_words, max_results)

    if is_cached(cache_key):
        return cache[cache_key]

    papers = fetch_from_arxiv(key_words, max_results)
    cache_result(cache_key, papers)

    return papers
