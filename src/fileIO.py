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
            if audio_file.title or audio_file.artist or audio_file.album:
                metadata.append({'Title': audio_file.title, 'Artist': audio_file.artist, 'Album': audio_file.album})
            else:
                file_names.append(ntpath.basename(file))

    return metadata, file_names


def clean_metadata(title, artist):
    """
    Remove excess unwanted characters from a song's metadata.

    :param title: a string representing the song's title
    :param artist: a string representing the song's artist
    :precondition: title and artist are valid strings
    :return: a tuple of strings representing the cleaned title and artist
    """
    # Remove common extraneous information from titles
    title = re.sub(r'\(.*\)|\[.*]|{.*}|-.*|ft\..*|feat\..*|official.*|video.*|\d+kbps.*', '', title,
                   flags=re.I).strip()
    # Refine artist name
    if artist is None:
        artist = 'Unknown Artist'
    else:
        artist = artist.split(',')[0]  # Take the first artist if there are multiple
    artist = re.sub(r'\(.*\)|\[.*]|{.*}|official.*|video.*', '', artist, flags=re.I).strip()
    return title, artist


# TODO: this is now redundant, remove later after testing only!
def csv_writer(metadata_list):
    """
    Write metadata to a CSV file that's named after the user's playlist.

    :param: playlist_name: a string representing the name of the playlist as entered by the user
    :param: metadata_list: a list of dictionaries containing the metadata of each audio file
    :precondition: playlist_name is a string, metadata_list is a list of dictionaries
    :postcondition: a CSV file is created in the 'metadata' directory
    :return: a string for the path of the CSV file
    """
    csv_filename = "metadata"
    current_directory_path = os.path.dirname(os.path.abspath(__file__))
    parent_directory_path = os.path.dirname(current_directory_path)
    metadata_directory_path = os.path.join(parent_directory_path, 'metadata')
    if not os.path.exists(metadata_directory_path):
        os.makedirs(metadata_directory_path)
    csv_file_path = os.path.join(metadata_directory_path, csv_filename + '.csv')
    # Create/Open the CSV file
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # If you have headers like 'title', 'artist', 'album', you can write them here:
        # writer.writerow(['Title', 'Artist', 'Album'])
        for file in metadata_list:
            writer.writerow([file['Title'], file['Artist'], file['Album']])
    return csv_file_path

# stuff = metadata_harvester(media_file_finder(select_folder()))
# for x in stuff[0]: print(x)
# print("==========\nNo metadata songs:")
# for x in stuff[1]: print(x)
