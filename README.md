## Project Audio Reaper

#### Author: Abdulqadir Abuharrus

#### Date: 2023-11-10

#### Version: 1.0

____

### Description:

A lightweight script to extract metadata from songs in a local library on a PC and format it to call the Spotify API
To create a playlist of these songs on Spotify.

## To-Do List:

- [X] Connect to spotify API and authenticate tokens
- [X] Figure out how to handle user login credentials and authentication
- [X] Connect to spotify API and authenticate user login
- [X] Deal with the songs that have no metadata or are not found on spotify (Tried to extract info from file name)
- [X] Check if user has playlist with specified name, if not create the playlist
- [X] Search for songs on spotify, if found add to playlist, if not found, add to list of songs not found
- [X] Create new txt file of songs not found, and print list to the user
- [X] Implement error handling for all possible errors(try-except)
- [X] Consider CSV headers for the txt file metadata collection
- [X] Add Docstrings and doctests (where applicable)
- [ ] implement unit testing
- [X] File browser??
- [ ] ~~Consider using a database instead of a CSV file~~
- [X] Decompose into separate classes to maintain Separation of Concerns and Single Responsibility Principle
- [ ] ~~Ensure wiping the failure file before each run~~
- [ ] ~~delete the metadata CSV file after each run~~
- [ ] OpenAI API rate limit handling
- [ ] Write a function to retry again with the songs that were not found (aka the failures)
- 
- [ ] Docstrings for all classes and methods
- [ ] Write documentation and instructions for use in the README.md file
