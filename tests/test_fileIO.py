import io
from unittest import TestCase
from unittest.mock import patch, MagicMock
from src import fileIO


class FolderTest(TestCase):

    @patch('tkinter.filedialog.askdirectory')
    def test_select_folder_found(self, mock_askdirectory):
        mock_askdirectory.return_value = 'path/to/folder'
        result = fileIO.select_folder()
        self.assertEqual(mock_askdirectory.return_value, result)

    @patch('tkinter.filedialog.askdirectory')
    def test_select_folder_not_found(self, mock_askdirectory):
        mock_askdirectory.return_value = ''
        with self.assertRaises(FileNotFoundError):
            fileIO.select_folder()


class MetadataHarvestTest(TestCase):
    @patch('tinytag.TinyTag.get')
    def test_metadata_harvester_files_found_harvested(self, mock_get):
        mock_audio_file = MagicMock()
        mock_audio_file.title = 'Test Title'
        mock_audio_file.artist = 'Test Artist'
        mock_audio_file.album = 'Test Album'
        mock_get.return_value = mock_audio_file

        metadata, filenames = fileIO.metadata_harvester(['test_file.mp3'])
        self.assertEqual(metadata, [{'Title': 'Test Title', 'Artist': 'Test Artist', 'Album': 'Test Album'}])
        self.assertEqual(filenames, [])

    @patch('tinytag.TinyTag.get')
    def test_metadata_harvester_no_metadata(self, mock_get):
        mock_audio_file = MagicMock()
        mock_audio_file.title = None
        mock_audio_file.artist = None
        mock_get.return_value = mock_audio_file

        metadata, filenames = fileIO.metadata_harvester(['test_file.mp3'])
        self.assertEqual(metadata, [])
        self.assertEqual(filenames, ['test_file.mp3'])

    @patch('tinytag.TinyTag.get')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_metadata_harvester_no_files_found(self, mock_get, mock_output):
        mock_audio_file = MagicMock()
        mock_audio_file.title = 'Test Title'
        mock_audio_file.artist = 'Test Artist'
        mock_audio_file.album = 'Test Album'
        mock_get.return_value = mock_audio_file

        mock_output.getvalue = "No audio files found in directory."
        metadata, filenames = fileIO.metadata_harvester([])
        self.assertEqual(metadata, [])
        self.assertEqual(filenames, [])
        self.assertEqual(mock_output.getvalue, "No audio files found in directory.")


class Test(TestCase):
    def test_clean_metadata_clean_title(self):
        dummy_title = "Super Duper -**_/ Official Video ft. BOB"
        dummy_artist = "Best 3vr Singer /.feat"

        expected_title = "Super Duper"
        clean_title, clean_artist = fileIO.clean_metadata(dummy_title, dummy_artist)
        self.assertEqual(expected_title, clean_title)

    def test_clean_metadata_clean_artist(self):
        dummy_title = "Super Duper -**_/ Official Video ft. BOB"
        dummy_artist = "Best 3vr Singer (video)"

        expected_artist = "Best 3vr Singer"
        clean_title, clean_artist = fileIO.clean_metadata(dummy_title, dummy_artist)
        self.assertEqual(expected_artist, clean_artist)
