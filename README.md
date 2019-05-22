### Introduction

This is a set of tools I made back in 2014, to keep a local music library "coordinated" and organized. Coordinate\_music can:

* check for, and automatically correct, consistency between filename, ID3 tag, and Spotify's metadata.
* check that every directory is structured correctly (by genre, artist, and album name).
* create .url files that play a specific song in Spotify Desktop.
* create links between local music and tracks on Spotify, stored in the "website" tag.
* create a text file summary of all your music's files and tags.

### Demo

Here's what it looks like to create a link between a local audio file and a track on Spotify:

<a href="#">![Demo search by track](https://moltenjs.com/page/labs-coordinate-music/fromtracklgc.png)</a>

Here's what it looks like to create links, an album at a time:

<a href="#">![Demo search by album](https://moltenjs.com/page/labs-coordinate-music/fromalbumlgc.png)</a>

### Other Features and Details

* add tracks to/remove tracks from a Spotify playlist
* view a Spotify playlist
* create Spotify playlist from directory of mp3s
* save a Spotify playlist to text file of song names and lengths.
* rename audio files in a directory based on a text file of song names.
* set tags automatically based on filename and path, see [directory structure](directory_structure.md)
* save disk space by replacing audio files with .url files linking to Spotify (if you've marked the file as "low quality" and Spotify's "popularity" data indicates high popularity for the song).

### Installation

1. Install Python, either Python 2.7+ or 3.5+
1. Install Mutagen (pip install mutagen)
1. Install Spotipy (pip install spotipy)
1. Install Pyperclip (pip install pyperclip)
1. Copy coordmusicuserconfig.py.template to coordmusicuserconfig.py,
	* fill in the missing information,
	* for example from `# return u'~/music'` to `return u'~/my/music/files'`
	* to enable linking to spotify, you will need a SpotifyClientID,
	* you can sign up for this at https://developer.spotify.com/my-applications/
1. Run \_\_main\_\_.py, it will interactively ask what you'd like it to do

Also: the C++ program wavcut can split wav files based on a list of approximate song lengths in seconds.

Also: on Windows, you can install pywinauto to enable the "type into Spotify window" feature.

Also: when the Python script is asking you a question, you can type "BRK" to pause, investigate the question, and then resume processing the directory from the start.

Tests pass on latest Linux Mint and Windows 7+.

