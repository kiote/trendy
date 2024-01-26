# test_arxiv.py
import unittest
from unittest.mock import Mock, patch
from arxiv import fetch_archive, cache
from datetime import datetime

class TestFetchArchive(unittest.TestCase):

    def setUp(self):
        # Clear the cache before each test
        cache.clear()

    @patch('arxiv.requests.get')
    def test_fetch_archive_xml_parsing(self, mock_get):
        # Setup mock response for XML parsing test
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = """
            <feed xmlns="http://www.w3.org/2005/Atom">
            <entry>
                <title>Sample Title 1</title>
                <author>
                <name>Author 1</name>
                </author>
                <summary>Sample Summary 1</summary>
                <published>2022-01-25T10:00:00Z</published>
                <id>https://example.com/paper1</id>
            </entry>
            </feed>
            """
        mock_get.return_value = mock_response

        # Test XML parsing
        result = fetch_archive(key_words='affective computing', max_results=1)
        expected_result = [
            {
                "title": "Sample Title 1",
                "authors": ["Author 1"],
                "summary": "Sample Summary 1",
                "published": "2022-01-25T10:00:00Z",
                "link": "https://example.com/paper1"
            }
        ]
        self.assertEqual(result, expected_result)

    @patch('arxiv.fetch_from_arxiv')
    def test_fetch_archive_with_cache_miss(self, mock_fetch_from_arxiv):
        # Setup mock response for cache miss
        mock_response = [
            {
                "title": "Sample Title 1",
                "authors": ["Author 1"],
                "summary": "Sample Summary 1",
                "published": "2022-01-25T10:00:00Z",
                "link": "https://example.com/paper1"
            }
        ]
        mock_fetch_from_arxiv.return_value = mock_response

        # Test cache miss
        result = fetch_archive(key_words='affective computing', max_results=1)
        self.assertEqual(result, mock_response)
        mock_fetch_from_arxiv.assert_called_once()

        # Ensure the result is cached
        cache_key = (datetime.now().strftime("%Y-%m-%d"), 'affective computing', 1)
        self.assertIn(cache_key, cache)
        self.assertEqual(cache[cache_key], mock_response)

    @patch('arxiv.fetch_from_arxiv')
    def test_fetch_archive_with_cache_hit(self, mock_fetch_from_arxiv):
        # Setup mock response and prefill the cache
        mock_response = [
            {
                "title": "Sample Title 2",
                "authors": ["Author 2"],
                "summary": "Sample Summary 2",
                "published": "2022-01-26T10:00:00Z",
                "link": "https://example.com/paper2"
            }
        ]
        cache_key = (datetime.now().strftime("%Y-%m-%d"), 'affective computing', 1)
        cache[cache_key] = mock_response

        # Test cache hit
        result = fetch_archive(key_words='affective computing', max_results=1)
        self.assertEqual(result, mock_response)
        mock_fetch_from_arxiv.assert_not_called()

if __name__ == '__main__':
    unittest.main()
