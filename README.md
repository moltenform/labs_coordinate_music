# coordinate_music
Tools to keep a music library and ID3 tags tidy, using metadata from Spotify. 

Setup:
1) Install Python 2.7.x
2) Install Mutagen, for example by running
	pip install mutagen
	Tested with Mutagen 1.31.
3) Install Spotipy, for example by running
	pip install spotipy
	Tested with Spotipy 2.3.7
4) Copy coordmusicuserconfig.py.template to coordmusicuserconfig.py,
	fill out the values here, especially getMusicRoot()
	
	to enable linking to spotify, you will need a SpotifyClientID,
	you can sign up for this at https://developer.spotify.com/my-applications/
5) Run main.py

Optional: build the c++ program wavcut to enable splitting wav files based on length metadata.
Optional: install pywinauto to enable the "type into Spotify window" feature.


File naming
----------------

The general principle for file naming is: sufficient information to simply and uniquely identify a song should be available solely from directory names and file names. If in an album, an audio file's artist, title, discnumber, tracknumber, and album name must be either specified in the filename or inferred from the directory name.

The directory structure is first genre, then artist, then album.
For example, let's say that
~/music
is the root. (As set in coordmusicuserconfig.py, getMusicRoot()).

~/music/00s Indie Folk
is a genre directory, because it is directly below root.

~/music/00s Indie Folk/Fleet Foxes
is an artist directory, because it is directly below a genre.
any files within this directory will now by default have the artist 'Fleet Foxes'

~/music/00s Indie Folk/Fleet Foxes/English House.flac
this is a non-album track, as it is outside an album and does not have a tracknumber.
we can override the artist, if we included a Robin Pecknold solo track here we could name it
Robin Pecknold - Where Is My Wild Rose.flac

~/music/00s Indie Folk/Fleet Foxes/2008, Sun Giant
this is an album directory, because it is directly below an artist. named in the format year, title.
we can override the artist, for example 
2009, White Antelope - Recorded Live in Seattle

~/music/00s Indie Folk/Fleet Foxes/2008, Sun Giant/01 Sun Giant.m4a
this is an album track. to specify another artist or disc number, the following variations are allowed:
01 Sun Giant.m4a
01 Fleet Foxes - Sun Giant.m4a
01 01 Sun Giant.m4a
01 01 Fleet Foxes - Sun Giant.m4a

This structure is maintained by main.py's checkFilenamesMain, which will ensure valid structure and also set corresponding ID3/metadata tags based on the file and directory names. 
