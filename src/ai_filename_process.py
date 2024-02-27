"""
This file is mainly used to process the file name of songs without
metadata and is often convulted and messy. So AI will be used to extract
info from the file name and then search for it on Spotify.

"""


def filename_parse():
    """
    This function will parse the file name and extract the song name, artist, and album name.
    :return:
    """
    pass


def process_filename():
    """
    This function will process the file name and remove any unnecessary characters.
    :return:
    """
    pass


def invoke_prompt_to_ai():
    """
    This function will invoke a prompt to the AI to extract the song's metadata.
    :return:
    """
    pass


def process_prompt_result():
    """
    This function will process the result from the prompt and format the result.
    :return:
    """
    pass

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
