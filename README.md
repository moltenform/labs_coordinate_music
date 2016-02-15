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
