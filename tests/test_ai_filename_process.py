import unittest
from unittest import TestCase
from unittest.mock import patch, MagicMock

from src import ai_filename_process


class TestInvokePromptToAI(unittest.TestCase):
    @patch('src.ai_filename_process.client.chat.completions.create')
    def test_invoke_prompt_to_ai(self, mock_create):
        # Mock the API response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = 'Test Title, Test Artist, Test Album'
        mock_create.return_value = mock_response

        file_names = ['test_file.mp3']
        result = ai_filename_process.invoke_prompt_to_ai(file_names)
        self.assertEqual(result, ['Test Title, Test Artist, Test Album'])

        # Assert the mock was called with the correct arguments
        mock_create.assert_called_once_with(
            model="gpt-4-0125-preview",
            messages=[
                {"role": "system", "content": "You are a metadata extractor assistant."},
                {"role": "user",
                 "content": "Given the filename 'test_file.mp3', provide the metadata in plain text, separating Title,"
                            " Artist, and Album with commas, such that they return match when searched on Spotify, "
                            "and leave blank if not specified, remove excess words. Don't label fields "
                            "and Say nothing else."}
            ],
            max_tokens=60,
        )


class TestProcessResponse(TestCase):
    def test_process_response(self):
        real_songs = ['Come my way,BOB,Emerald Lake',
                      'He who waits,Sharleze,Austin',
                      'Amogus,Bigus,Monty']
        expected_outcome = [{'Title': 'Come my way', 'Artist': 'BOB', 'Album': 'Emerald Lake'},
                            {'Title': 'He who waits', 'Artist': 'Sharleze', 'Album': 'Austin'},
                            {'Title': 'Amogus', 'Artist': 'Bigus', 'Album': 'Monty'}]
        results = ai_filename_process.process_response(real_songs)
        self.assertEqual(expected_outcome, results)

    def test_process_response_empty_list(self):
        song_list = []
        expected = []
        results = ai_filename_process.process_response(song_list)
        self.assertEqual(expected, results)
        self.assertTrue(len(results) == 0)


if __name__ == "__main__":
    unittest.main()
