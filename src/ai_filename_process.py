"""
This file is mainly used to process the file name of songs without
metadata and is often convulted and messy. So AI will be used to extract
info from the file name and then search for it on Spotify.

"""
import os
from openai import OpenAI

# this authenticates by auto retrieving the API key
client = OpenAI()


def invoke_prompt_to_ai(file_names):
    """
        This function will invoke a prompt to the AI to extract the song's metadata from the filenames.

        :param: file_names: a list of strings representing the filenames of songs
        :return:
        """
    extracted_metadata = []
    for name in file_names:
        prompt = ("Given filename %s, provide only the metadata in the following format: "
                  "{ 'Title': <title>, 'Artist': <artist>, 'Album': <album> }. "
                  "Leave blank if not specified." % name)
    return extracted_metadata


def process_prompt_result():
    """
        This function will process the result from the prompt and format the result.
        :return:
        """
    pass

# TODO: Remove These old functions after testing only

# def search_filename(sp, file_name):
#     """
#     Search for a song on Spotify using the file name.
#
#     :param sp: an authenticated Spotify object
#     :param file_name: a string representing the file's name
#     :precondition: file_name is a valid string
#     :return: a string representing the track's id0
#     """
#     parts = parse_filename(file_name)
#     best_match = None
#     max_popularity = -1
#
#     # Try all combinations of parts as artist and title
#     for i in range(1, len(parts)):
#         artist = ' '.join(parts[:i])
#         title = ' '.join(parts[i:])
#         query = f'track:{title} artist:{artist}'
#         result = sp.search(query, type='track', limit=1)
#         tracks = result['tracks']['items']
#         if tracks:
#             track = tracks[0]
#             # Select the track with the highest popularity
#             if track['popularity'] > max_popularity:
#                 best_match = track['id']
#                 max_popularity = track['popularity']
#
#     return best_match

# def parse_filename(file_name):
#     """
#     Parse the song file's name for relevant information to identify the song.
#
#     :param file_name: a string representing the file's name
#     :precondition: file_name must be a valid string
#     :postcondition: replace excess characters with spaces and split the string
#     :return: a substring containing only relevant information
#     """
#     # Remove the file extension
#     name, _ = os.path.splitext(file_name)
#     for delimiter in ['-', '_', '|', '(', ')', '[', ']', '&']:
#         name = name.replace(delimiter, ' ')
#     parts = [part for part in name.split(' ') if part]  # Filter out empty strings
#     return parts
