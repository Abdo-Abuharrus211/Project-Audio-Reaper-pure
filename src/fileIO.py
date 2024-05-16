"""
This file contains the functions for reading and writing to files.

    Functions:
    1. Grab folder from user using the popup
    2. Parse the folder for all relevant files (mp3 and wav)
    3. Collect metadata from the files
    4. Write the names of filenames with not metadata to a text file
    5. Clean the metadata of any unwanted characters
    6. Write metadata to a csv file
"""
import csv
import ntpath
import os
import re
import tkinter as tk
from tkinter import filedialog
from tinytag import tinytag


def select_folder():
    """
    Prompt the user to select a folder.

    :return: a string representing the path of the selected folder
    """
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory()
    if not folder_path:
        raise FileNotFoundError
    return folder_path


def media_file_finder(target_directory):
    """
    Find all the MP3 and WAV files in a directory.

    :param target_directory: a string representing the path for the target folder
    :precondition: target_directory must be a valid path string
    :return: a list of strings, each being the path to a mp3 or wav file
    """
    audio_files = []
    for file in os.listdir(target_directory):
        if file.endswith(".mp3") or file.endswith(".wav"):
            full_path = os.path.join(target_directory, file)  # Add this line
            audio_files.append(full_path)
    return audio_files


def metadata_harvester(song_files):
    """
    Extract metadata (title, artist, & album) from song files.

    :param song_files: a list of MP3 and WAV files in the user specified directory
    :precondition: list must be non-empty and contain strings representing file paths
    :postcondition: extract necessary metadata from each file
    :return: a list of dictionaries of the songs' metadata, each song has a dictionary containing title, artist,
             and album keys and their respective values
    """
    metadata = []
    file_names = []
    if not song_files:
        print("No audio files found in directory.")
    else:
        for file in song_files:
            audio_file = tinytag.TinyTag.get(file)
            if audio_file.title and audio_file.artist:
                metadata.append({'Title': audio_file.title, 'Artist': audio_file.artist, 'Album': audio_file.album})
            else:
                file_names.append(ntpath.basename(file))

    return metadata, file_names


def organize_harvest(bulk_metadata):
    """
    Organize the incoming metadata according to the abundance of metadata per song, and return relevant lists.

    This function is the alternative of metadata_harvester for when receiving data from the frontend via API.
    :param: bulk_metadata: a list of dictionaries representing song metadata and filenames
    :precondition: bulk_metadata must be a non-empty list of dictionaries containing strings
    :return: two separate lists, a list of songs with metadata and a list of file names for songs without
    """
    metadata_list = []
    file_names_list = []
    for item in bulk_metadata:
        print(item)
        if item['Title'] and item['Artist']:
            metadata_list.append(item)
        else:
            file_names_list.append(item['FileName'])
    return metadata_list, file_names_list


def clean_metadata(title, artist):
    """
    Remove excess unwanted characters from a song's metadata.

    :param title: a string representing the song's title
    :param artist: a string representing the song's artist
    :precondition: title and artist are valid strings
    :return: a tuple of strings representing the cleaned title and artist
    """
    # Remove common extraneous information from titles
    title = title.replace(" - Copy", "").replace(" (HD)", "").replace(" (Official Video)", "").strip()

    # Handle case where artist and title are combined in 'Title' field
    if " - " in title and not artist:
        artist, title = title.split(" - ", 1)

    title = re.sub(r'\(.*\)|\[.*]|{.*}|-.*|ft\..*|feat\..*|official.*|video.*|\d+kbps.*', '', title,
                   flags=re.I).strip()
    if artist is None:
        artist = ""
    else:
        artist = artist.split(',')[0]  # Take the first artist if there are multiple
    artist = re.sub(r'\(.*\)|\[.*]|{.*}|official.*|video.*', '', artist, flags=re.I).strip()

    return title, artist


def failed_csv_writer(items):
    """
    Write songs that failed to a CSV file.

    :param: items: a list of strings representing songs not failed to find on Spotify
    :postcondition: a CSV file is created in the 'metadata' directory
    :return: a string for the path of the CSV file
    """
    csv_filename = "failures"
    current_directory_path = os.path.dirname(os.path.abspath(__file__))
    parent_directory_path = os.path.dirname(current_directory_path)
    failures_directory_path = os.path.join(parent_directory_path, 'failures')
    if not os.path.exists(failures_directory_path):
        os.makedirs(failures_directory_path)
    csv_file_path = os.path.join(failures_directory_path, csv_filename + '.csv')

    with open(csv_file_path, 'w', newline='', encoding='utf-8') as f:
        # writer = csv.writer(f)
        writer = csv.writer(f, delimiter=',', quotechar='|', quoting=csv.QUOTE_NONE, escapechar='\\')
        for _ in items:
            writer.writerow([_])


def read_failed_tracks():
    """
    Retry searching for failed tracks in the failures CSV file.

    :return: A list of dictionaries containing the metadata of the failed tracks from the CSV file
    """
    current_directory_path = os.path.dirname(os.path.abspath(__file__))
    root_directory_path = os.path.dirname(current_directory_path)
    file_path = os.path.join(root_directory_path, 'failures', 'failures.CSV')

    failed_metadata = []
    try:
        with open(file_path, 'r') as file:
            failed_tracks = file.readlines()
        for track in failed_tracks:
            title, artist = track.split(", ")
            failed_metadata.append({'Title': title.replace('\\', ''), 'Artist': artist.replace('\n', '')})
    except FileNotFoundError:
        print("No failures.csv file found.")
    return failed_metadata

# TODO: Mull this one over as it can result in incorrect data being written
# def write_metadata_to_files(file_paths, metadata_list):
#     """
#     Write extracted metadata onto song file tags.
#
#     :param file_paths: a list of strings representing the file paths of songs
#     :param metadata_list: a list of dictionaries containing songs' metadata
#     """
#     for i in range(len(file_paths)):
#         audio = EasyID3(file_paths[i])
#         audio['title'] = metadata_list[i]['Title']
#         audio['artist'] = metadata_list[i]['Artist']
#         audio['album'] = metadata_list[i]['Album']
#         audio.save()

# stuff = metadata_harvester(media_file_finder(select_folder()))
# for x in stuff[0]: print(x)
# print("==========\nNo metadata songs:")
# for x in stuff[1]: print(x)
