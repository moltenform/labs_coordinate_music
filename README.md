### Introduction

This is a set of tools to keep a local music library "coordinated", having perfect consistency between filename, id3 tag, and Spotify's metadata. You can store your local music library in formats like .mp3, or, since streaming music is becoming prevalent, .url files that will play a song online or in Spotify Desktop. Coordinate\_music can:

* check for consistency between filename, id3 tag, and Spotify's metadata. set tags from filename, or filename from tags.
* check that every directory is structured correctly (by genre, artist, and album name).
* create .url files that open directly to Spotify Desktop.
* create links between local music and tracks on Spotify, stored in the "website" tag.
* create a utf-8 text file summary of all filenames and tags.

Other features include, if enabled:

* double-clicking a .mp3 plays the corresponding song online in Spotify.
* interact with Spotify playlists (view tracks, remove tracks, create playlist from directory of mp3s).
* filenames in the format .sv.mp3 can be synced to an external directory for backup.
* save a Spotify playlist to text file of song names and lengths.
* rename audio files in a directory based on a text file of song names and lengths.
* in the Python script, type "BRK" to interrupt the current operation and view the current directory.
* set tags based on filename and path, see ![Directory Structure](directory_structure.md)
* save disk space: loop through each song and,
	* if file is low bitrate, and Spotify's 'popularity' data indicates high popularity, and user confirms,
	* replace the file with a .url linking to Spotify.

### Installation

To run coordinate\_music,

1. Install Python, either Python 2.7+ or 3.5+
1. Install Mutagen (pip install mutagen)
1. Install Spotipy (pip install spotipy)
1. Copy coordmusicuserconfig.py.template to coordmusicuserconfig.py,
	* enter data
	* to enable linking to spotify, you will need a SpotifyClientID,
	* you can sign up for this at https://developer.spotify.com/my-applications/
1. Run __main__.py, it will interactively ask what to do next

Optional: the c++ program wavcut can split wav files based on a list of approximate song lengths in seconds, which can be useful for splitting a long mixtape into tracks.

Optional: on Windows, you can install pywinauto to enable the "type into Spotify window" feature.

Tests pass on Linux (latest Linux Mint) and Windows 7+.

### Demo

Here's what it looks like to create a link between a local audio file and a track on Spotify:

![Demo search by track](http://2.bp.blogspot.com/-YeRX7dbJaeA/VtXodld_4lI/AAAAAAAABCc/_V-EHgqcn8Q/s1600/fromtracklgc.png)

Here's what it looks like to create links, an album at a time:

![Demo search by album](http://1.bp.blogspot.com/-ruydPiiYdE0/VtXnuf_bGOI/AAAAAAAABCU/rA9CvQoQ45o/s1600/fromalbumlgc.png)
