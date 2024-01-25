import unittest
from unittest.mock import Mock, patch
from arxiv import fetch_archive

class TestFetchArchive(unittest.TestCase):

    @patch('requests.get')
    def test_fetch_archive(self, mock_get):
        # Mock the requests.get function to return a custom response
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
            <entry>
                <title>Sample Title 2</title>
                <author>
                <name>Author 2</name>
                </author>
                <summary>Sample Summary 2</summary>
                <published>2022-01-26T10:00:00Z</published>
                <id>https://example.com/paper2</id>
            </entry>
            <!-- Add more entry elements for additional papers -->
            </feed>
            """
        mock_get.return_value = mock_response

        # Call the fetch_archive function
        result = fetch_archive(key_words='affective computing', max_results=20)

        # Define the expected result based on the mocked response
        expected_result = [
            {
                "title": "Sample Title 1",
                "authors": ["Author 1"],
                "summary": "Sample Summary 1",
                "published": "2022-01-25T10:00:00Z",
                "link": "https://example.com/paper1"
            },
            {
                "title": "Sample Title 2",
                "authors": ["Author 2"],
                "summary": "Sample Summary 2",
                "published": "2022-01-26T10:00:00Z",
                "link": "https://example.com/paper2"
            },
            # Add more expected results for other papers if needed
        ]

        # Assert that the result matches the expected result
        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()
