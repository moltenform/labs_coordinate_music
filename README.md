### Introduction

This is a set of tools to keep a local music library "coordinated", to have perfect consistency between filename, id3 tag, and Spotify's metadata. Audio files like .mp3 are kept in a specific directory structure. As streaming music is becoming prevalent, coordinate\_music also supports .url files that link to a song online, or link directly to Spotify Desktop. Coordinate\_music can:

* check that every directory and filename is formatted correctly.
* check for consistency between filename, id3 tag, and Spotify's metadata. set tags from name and vice versa.
* create .url files that open directly to Spotify Desktop.
* search Spotify interactively by artist, title, album to find a corresponding Spotify track.
* save all metadata to a utf-8 text file, which can be useful for backup.

When importing music, coordinate\_music will walk through audio files and use the Spotify API to search for the associated track. This can either be done one album at a time, or on a track by track basis. It will present you with a list of candidates, then you can then confirm, or type "hear0" to hear the original, or type "hear1" to hear the first candidate. Here's what it looks like when searching by track:

![Demo search by track](http://2.bp.blogspot.com/-YeRX7dbJaeA/VtXodld_4lI/AAAAAAAABCc/_V-EHgqcn8Q/s1600/fromtracklgc.png)

Here's what it looks like when searching by album:

![Demo search by album](http://1.bp.blogspot.com/-ruydPiiYdE0/VtXnuf_bGOI/AAAAAAAABCU/rA9CvQoQ45o/s1600/fromalbumlgc.png)

This association is saved in the website ID3 tag in the audio file (mp3, m4a, or flac).

Other features include, if enabled:

* opening a .mp3 redirects to the associated track to play in Spotify desktop, which often has higher audio quality.
* typing "BRK" into any interactive text prompt to view the current directory in UI and retry the current operation.
* filenames in the format .sv.mp3 are synced to an external directory for backup.
* working with Spotify playlists (viewing tracks, removing tracks, creating playlist from directory of mp3s).
* saving a Spotify playlist to text file of song lengths and names.
* renaming files in a directory based on Spotify playlist.
* indicating a song's subjective "rating" by its bitrate.
* saving disk space, by interactively walking through directories, and
	* if low bitrate and Spotify's 'popularity' data indicates high popularity,
	* replace the file with a .url linking to Spotify, after asking the user.


### Installation

To run coordinate\_music,

1. Install Python 2.7.x
1. Install Mutagen, for example by running
	* pip install mutagen
	* Tested with Mutagen 1.31.
1. Install Spotipy, for example by running
	* pip install spotipy
	* Tested with Spotipy 2.3.7
1. Copy coordmusicuserconfig.py.template to coordmusicuserconfig.py,
	* fill in missing values, especially getMusicRoot()
	* to enable linking to spotify, you will need a SpotifyClientID,
	* you can sign up for this at https://developer.spotify.com/my-applications/
1. Run main.py, it will run interactively.

Optional: the c++ program wavcut can split wav files based on length metadata, which can be useful for splitting a long mixtape into tracks.

Optional: install pywinauto to enable the "type into Spotify window" feature.


### Directory structure

The general principle for filenames is that one can uniquely identify a song solely from its filename and directory. coordinate\_music includes logic for inferring artist, title, discnumber, tracknumber, and album from a filename. 

The directory structure is essentially genre/artist/album/tracks.

	For example, let's say that
	~/music
	is the root. (specified in coordmusicuserconfig.py, getMusicRoot()).

	~/music/00s Indie Folk
	is a genre directory.

	~/music/00s Indie Folk/Fleet Foxes
	is an artist directory.

	~/music/00s Indie Folk/Fleet Foxes/2008, Sun Giant EP
	this is an album directory, because it is directly below an artist. 
	the format is (year), (album title).
	compilations with an irrelevent release date can use 0000 for a year.

	~/music/00s Indie Folk/Fleet Foxes/2008, Sun Giant EP/01 Sun Giant.flac
	the inferred artist is Fleet Foxes
	the inferred album is Sun Giant EP
	the inferred discnumber is 01 (default)
	the inferred tracknumber is 01
	the inferred title is Sun Giant
	all required fields are successfully inferred, so this is a valid name.

	~/music/00s Indie Folk/Fleet Foxes/Robin Pecknold - Where Is My Wild Rose.m4a
	the inferred artist is Fleet Foxes, overridden to be Robin Pecknold
	the inferred title is Where Is My Wild Rose
	since this is not in an album, tracknumber is not required.
	all required fields are successfully inferred, so this is a valid name.

	~/music/Blues/Compilations/0000, The Soul Of A Man/01 02 Eagle Eye - Down In Mississippi.mp3
	the inferred artist is Compilations, overridden to be Eagle Eye
	the inferred album is The Soul Of A Man
	the inferred discnumber is 01
	the inferred tracknumber is 02
	the inferred title is Down In Mississippi
	all required fields are successfully inferred, so this is a valid name.

	A directory name can also end with one of these keywords to change behavior:
	' Compilation': allow tracks to have id3 tag for a different album
	' Selections': allow tracks to have id3 tag for a different album, and do not require track numbers
	
You can add allowed file extensions in the CheckFileExtensions class of recurring_coordinate.py. By default, url, mp3, m4a, and flac are supported. (You will have to rename .mp4 and .aac files to .m4a). Enabling ogg is easily added with two lines of code to getFieldForFile() in coordmusicutil.py.

Tests pass on Linux (latest Linux Mint) and Windows (7 and later supported). 
