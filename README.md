## Project Audio Reaper

#### Author: Abdulqadir Abuharrus

#### Date: 2023-11-10

#### Version: 0.1

____

### Description:

A lightweight script to extract metadata from songs in a local library on a PC and format it to call the Spotify API
To create a playlist of these songs on Spotify.

## To-Do List:

- [X] Connect to spotify API and authenticate tokens
- [X] Figure out how to handle user login credentials and authentication
- [X] Connect to spotify API and authenticate user login
- [ ] Deal with the songs that have no metadata or are not found on spotify
- [ ] Check if user has playlist with specified name, if not create the playlist
- [ ] Search for songs on spotify, if found add to playlist, if not found, add to list of songs not found
- [ ] Create new txt file of songs not found, and print list to the user
- [ ] Implement error handling for all possible errors(try-except)
- [ ] Consider CSV headers for the txt file metadata collection
- [ ] Add Docstrings and doctests (where applicable)
- [ ] implement unit testing
- [ ] Write documentation and instructions for use in the README.md file
- [ ] Consider wiping the CSV file after each use