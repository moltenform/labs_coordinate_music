# wavcut
Split a .wav file.
By Ben Fisher, 2015.
Released under the GPLv3 license.

There are three methods for splitting a wav file. 

* wavcut input.wav datalengths.txt
	* where datalengths.txt is a text file. one line of text per cut point, every line in the form seconds|trackname.
	* for example,
		* 140.045|song1
		* 201.543|song2
		* 180.132|song3
	* this uses the given times as guidelines, and will seek for the best split point based on silence.
	* it will even automatically add fade-ins and fade-outs if the transition would be too abrupt. 

* wavcut input.wav
	* you will be asked if you used audiomark. if you say yes, this program will search for occurrences
	* of audiomark.mp3 inside the audio, and split at these points (audiomark.mp3 is located in the wavcut directory).

* wavcut input.wav
	* you will be asked if you used audiomark. if you say no, this program will attempt to find
	* silences in the audio on which to split. this is experimental and results may vary.

Output will be saved to the current directory. 

Supports input wav files that are larger than 4 gigabytes, as saved by Audacity.
