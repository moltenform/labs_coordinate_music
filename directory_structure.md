
### Directory structure

The general principle for filenames is that one can uniquely identify a song solely from its filename and directory. coordinate\_music includes logic for inferring artist, title, discnumber, tracknumber, and album from a filename. 

The directory structure is essentially genre/artist/album/tracks.

	For example, let's say that
	~/music
	is the root. (you can set this in coordmusicuserconfig.py, getMusicRoot()).

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
	
You can add allowed file extensions in the CheckFileExtensions class of recurring_coordinate.py. By default, url, mp3, m4a, and flac are supported (use the extension .m4a and not .mp4).
