### Introduction

This is a set of tools to keep a local music library "coordinated" and organized. Coordinate\_music can:

* check for, and automatically correct, consistency between filename, ID3 tag, and Spotify's metadata.
* check that every directory is structured correctly (by genre, artist, and album name).
* create .url files that play a specific song in Spotify Desktop.
* create links between local music and tracks on Spotify, stored in the "website" tag.
* create a utf-8 text file summary of all filenames and tags.

### Installation

1. Install Python, either Python 2.7+ or 3.5+
1. Install Mutagen (pip install mutagen)
1. Install Spotipy (pip install spotipy)
1. Copy coordmusicuserconfig.py.template to coordmusicuserconfig.py,
	* enter data
	* to enable linking to spotify, you will need a SpotifyClientID,
	* you can sign up for this at https://developer.spotify.com/my-applications/
1. Run \_\_main\_\_.py, it will interactively ask what to do next

Optional: the C++ program wavcut can split wav files based on a list of approximate song lengths in seconds.

Optional: on Windows, you can install pywinauto to enable the "type into Spotify window" feature.

Tests pass on Linux (latest Linux Mint) and Windows 7+.

### Other Features and Details

* add tracks to/remove tracks from Spotify playlist
* view Spotify playlist
* create Spotify playlist from directory of mp3s
* save a Spotify playlist to text file of song names and lengths.
* rename audio files in a directory based on a text file of song names.
* set tags automatically based on filename and path, see [directory structure](directory_structure.md)
* while running the Python script, type "BRK" to interrupt the current operation and view the current directory.
* save disk space by replacing audio files with .url files linking to Spotify (only if the user approves, and if Spotify's "popularity" data indicates high popularity for the song).

### Demo

Here's what it looks like to create a link between a local audio file and a track on Spotify:

![Demo search by track](http://2.bp.blogspot.com/-YeRX7dbJaeA/VtXodld_4lI/AAAAAAAABCc/_V-EHgqcn8Q/s1600/fromtracklgc.png)

Here's what it looks like to create links, an album at a time:

![Demo search by album](http://1.bp.blogspot.com/-ruydPiiYdE0/VtXnuf_bGOI/AAAAAAAABCU/rA9CvQoQ45o/s1600/fromalbumlgc.png)
