// wavcut
// Split a .wav file.
// By Ben Fisher, 2015.
// Released under the GPLv3 license.

#include "wavcut.h"

int main(int argc, char *argv[])
{
	const char *wavFile = null;
	const char *txtFile = null;
	bool preview = false;

	if (argc > 1)
	{
		wavFile = argv[1];
	}

	if (argc > 2)
	{
		if (stringsEqual("--preview", argv[2]))
			preview = true;
		else
			txtFile = argv[2];
	}

	if (argc > 3)
	{
		if (stringsEqual("--preview", argv[3]))
			preview = true;
		else
			txtFile = argv[3];
	}

	if (wavFile && !stringsEqual("/?", wavFile) && !stringsEqual("-h", wavFile))
	{
		runWavCut(wavFile, txtFile, preview);
	}
	else
	{
		printf("\nUsage: wavcut input.wav datalengths.txt\n");
		printf("or wavcut input.wav\n");
		printf("or wavcut input.wav --preview\n");
		printf("See readme for an explanation.\n");
	}

	return 0;
}
