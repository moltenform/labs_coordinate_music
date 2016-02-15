// wavcut
// Split a .wav file.
// By Ben Fisher, 2015.
// Released under the GPLv3 license.

#include "wavcut.h"

int main(int argc, char *argv[])
{
	if (argc == 2)
	{
		return runWavCut(argv[1], NULL);
	}
	else if (argc == 3)
	{
		return runWavCut(argv[1], argv[2]);
	}
	else
	{
		printf("\nUsage: wavcut input.wav datalengths.txt\n");
		printf("or wavcut input.wav\n");
		printf("See readme for an explanation.\n");
	}

	return 0;
}
