import os
from unittest import TestCase, mock
from unittest.mock import patch, mock_open

import src.driver as driver


class Test(TestCase):

    # def test_metadata_harvester(self):
    #     self.fail()

    @patch('os.path.exists')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_csv_writer(self, mock_file, mock_makedirs, mock_exists):
        mock_exists.return_value = False
        playlist_name = 'test_playlist'
        metadata_list = [
            {'title': 'Song1', 'artist': 'Artist1', 'album': 'Album1'},
            {'title': 'Song2', 'artist': 'Artist2', 'album': 'Album2'}
        ]

        driver.csv_writer(playlist_name, metadata_list)

        mock_file.assert_called_with(
            os.path.join('/metadata', 'test_playlist.csv'),
            'w', newline='', encoding='utf-8')

        # Check each call to write
        calls = [call for call in mock_file().write.mock_calls]
        expected_calls = [
            mock.call(f'Song1,Artist1,Album1{os.linesep}'),
            mock.call(f'Song2,Artist2,Album2{os.linesep}')
        ]
        self.assertEqual(calls, expected_calls)

    def test_parse_filename(self):
        file_name = 'Artist1 - Song1.mp3'
        expected_output = ['Artist1', 'Song1']
        result = driver.parse_filename(file_name)
        self.assertEqual(result, expected_output)

    @patch('os.listdir')
    def test_file_finder(self, mock_listdir):
        mock_listdir.return_value = ['song1.mp3', 'song2.wav']
        target_directory = '/test/directory'  # This should be a path appropriate for your OS
        expected_output = [
            os.path.join(target_directory, 'song1.mp3'),
            os.path.join(target_directory, 'song2.wav')]
        result = driver.file_finder(target_directory)
        self.assertEqual(result, expected_output)
