
#include "wav.h"

bool readFourChars(FILE* f, char c1, char c2, char c3, char c4)
{
	// we read 4 characters regardless.
	char cc1 = fgetc(f), cc2 = fgetc(f), cc3 = fgetc(f), cc4 = fgetc(f);
	bool b1 = (cc1 == c1);
	bool b2 = (cc2 == c2);
	bool b3 = (cc3 == c3);
	bool b4 = (cc4 == c4);
	return (b1 && b2 && b3 && b4);
}

errormsg readWavFileHeader(FILE* f, WavFileInfoT* info, uint64 addToLength)
{
	uint32 size;
	uint32 length32bit;
	uint16 nChannels;
	uint32 nSampleRate;
	uint32 nByteRate;
	uint16 nBlockAlignUnused;
	uint16 nBitsPerSample;
	uint16 nAudioformat;

	memset(info, 0, sizeof(*info));
	if (!readFourChars(f, 'R', 'I', 'F', 'F'))
		return_err("No RIFF tag, probably invalid wav file.");

	ReadUint32(f, &length32bit); // (length of file in bytes) - 8
	info->nRifflength = length32bit;
	if (!readFourChars(f, 'W', 'A', 'V', 'E'))
		return_err("No WAVE tag, probably invalid wav file.");

	if (!readFourChars(f, 'f', 'm', 't', ' '))
		return_err("No fmt  tag.");

	ReadUint32(f, &size); // header size
	if (size != 16)
		return_err("Size of fmt header != 16.");

	// audio format. 1 refers to uncompressed PCM
	ReadUint16(f, &nAudioformat);
	info->nAudioformat = nAudioformat;
	if (nAudioformat != 1)
		return_err("Only audio format 1 is supported");

	ReadUint16(f, &nChannels);
	ReadUint32(f, &nSampleRate);
	ReadUint32(f, &nByteRate); 
	ReadUint16(f, &nBlockAlignUnused);
	ReadUint16(f, &nBitsPerSample); 
	
	info->nChannels = nChannels;
	info->nSampleRate = nSampleRate;
	info->nByteRate = nByteRate;
	info->nBlockAlign = nBlockAlignUnused;
	info->nBitsPerSample = nBitsPerSample;

	if (nChannels != 1 && nChannels != 2)
		return_err("Currently only supports # of channels = 1 or 2.");

	if (nBitsPerSample != 8 && nBitsPerSample != 16)
		return_err("Currently only supports 8bit or 16 bit audio.");

	uint32 dataSize = 0;
	const int maxTries = 100;
	bool found = false;
	info->nRiffParts = 0;
	for (int i = 0; i < maxTries; i++)
	{
		info->nRiffParts++;
		bool rightTag = readFourChars(f, 'd', 'a', 't', 'a');
		ReadUint32(f, &dataSize);
		if (!rightTag && dataSize > INT_MAX)
			return_err("Data size too large.");

		if (rightTag)
		{
			found = true;
			break;
		}
		else
		{
			// look ahead by dataSize bytes, skipping over the current chunk
			int seekres = fseek64(f, dataSize, SEEK_CUR);
			if (seekres != 0) return "seek failed";
		}
	}
	if (!found)
		return_err("Could not find data tag");

	info->nRawdatalength = dataSize + addToLength;
	info->nDataOffset = ftell64(f);

	uint64 nSamples = ((info->nRawdatalength) /
		((info->nBitsPerSample / 8) * info->nChannels));
	info->nExpectedSamples = nSamples;

	if (nBitsPerSample != 16)
		return_err("Only 16 bit supported currently.");

	if (nChannels != 2)
		return_err("Only stereo, not mono supported currently.");

	return OK;
}

errormsg writeWavHeader(
	FILE * f, int nLenInSamples, int bitsPerSample, int nSampleRate)
{
	if (bitsPerSample != 16)
		return_err("NotSupported: Only 8 bit and 16 bit supported.");

	if (nLenInSamples == 0)
		return_err("Error: Tried to save empty wave file.");

	int nChannels = 2;
	uint32 datasize = (uint32)(nLenInSamples * (bitsPerSample / 8) * nChannels);
	uint32 filesize_minus8 = 4 /*header*/ + (8 + 16) /*fmt chunk*/ + 
		8 /*data chunk*/ + datasize;

	fputc('R', f);
	fputc('I', f);
	fputc('F', f);
	fputc('F', f);
	fwrite(&filesize_minus8, sizeof(uint32), 1, f);

	fputc('W', f);
	fputc('A', f);
	fputc('V', f);
	fputc('E', f);
	fputc('f', f);
	fputc('m', f);
	fputc('t', f);
	fputc(' ', f);
	uint32 tmpuint = 16;
	fwrite(&tmpuint, sizeof(uint32), 1, f); //size is 16 bytes
	uint16 tmpushort = 1;
	fwrite(&tmpushort, sizeof(uint16), 1, f); //format 1
	tmpushort = (uint16)nChannels;
	fwrite(&tmpushort, sizeof(uint16), 1, f);
	tmpuint = (uint32)nSampleRate;
	fwrite(&tmpuint, sizeof(uint32), 1, f);

	uint32 nByteRate = (uint32)
		((nChannels * bitsPerSample * nSampleRate) / 8);
	fwrite(&nByteRate, sizeof(uint32), 1, f);

	uint16 blockAlign = (uint16)((nChannels * bitsPerSample) / 8);
	fwrite(&blockAlign, sizeof(uint16), 1, f);

	tmpushort = (uint16)bitsPerSample;
	fwrite(&tmpushort, sizeof(uint16), 1, f);

	fputc('d', f);
	fputc('a', f);
	fputc('t', f);
	fputc('a', f);
	fwrite(&datasize, sizeof(uint32), 1, f);
	return OK;
}
