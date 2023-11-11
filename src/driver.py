import os


def folder_finder(target_directory):
    audio_files = []
    for file in os.listdir(target_directory):
        if file.endswith(".mp3") or file.endswith(".wav"):
            audio_files.append(file)
    return audio_files


def main():
    target_directory = input("Please enter the absoulte path of the directory you would like to harvest:")
    playlist_name = input("Please enter the name of the playlist you would like to create:")
    print("Harvester of Audio")
    print("Harvesting from " + target_directory)
    print("Creating playlist " + playlist_name)
    print("Harvesting audio files...")
    audio_files = folder_finder(target_directory)
    print("Harvested " + str(len(audio_files)) + " audio files.")


if __name__ == '__main__':
    main()
