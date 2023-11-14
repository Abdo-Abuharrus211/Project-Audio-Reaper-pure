import os
import tinytag
import csv


def csv_writer(playlist_name, metadate_list):
    with open('metadata/' + playlist_name + '.csv', 'w') as f:
        for file in metadate_list:
            writer = csv.writer(f)
            writer.writerow(file)


def metadata_harvester(audio_files):
    metadata = []
    if not audio_files:
        # TODO: Add error handling
        print("No audio files found in directory.")
    else:
        for file in audio_files:
            audio_file = tinytag.TinyTag.get(file)
            metadata.append({'title': audio_file.title, 'artist': audio_file.artist, 'album': audio_file.album})
    return metadata


def folder_finder(target_directory):
    # TODO: Add error handling
    audio_files = []
    for file in os.listdir(target_directory):
        if file.endswith(".mp3") or file.endswith(".wav"):
            audio_files.append(file)
    return audio_files


def main():
    target_directory = input("Please enter the absolute path of the directory you would like to harvest:")
    playlist_name = input("Please enter the name of the playlist you would like to create:")
    print("Harvesting from " + target_directory)
    print("Harvesting audio files...")
    audio_files = folder_finder(target_directory)
    metadata_harvester(audio_files)
    csv_writer(playlist_name, metadata_harvester(audio_files))
    csv_file = open('metadata/' + playlist_name + '.csv', 'r')


if __name__ == '__main__':
    main()
