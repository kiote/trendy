import requests
import xml.etree.ElementTree as ET

BASE_ARXIV_URL = 'http://export.arxiv.org/api/query?'

def fetch_archive(key_words='affective computing', max_results=20):
    formatted_search_term = f'"{key_words}"'

    # Define the query parameters with the formatted search term
    query_params = {
        "search_query": f'cat:cs.* AND (ti:{formatted_search_term} OR abs:{formatted_search_term})',
        "start": 0,
        "max_results": max_results
    }

    response = requests.get(BASE_ARXIV_URL, params=query_params)

    if response.status_code != 200:
        print("Error fetching data from ArXiv")
        return []

    # Parse the XML response
    root = ET.fromstring(response.content)

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