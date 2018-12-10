// wavcut
// Ben Fisher, 2015
// Released under the GNU General Public License version 3

#ifndef WAV_H
#define WAV_H

#include "util.h"

struct WavFileInfoT
{
	uint64 nRifflength, nExpectedSamples, nRawdatalength, nDataOffset;
	uint32 nAudioformat, nChannels, nSampleRate, nByteRate;
	uint32 nBlockAlign, nBitsPerSample, nRiffParts;
	WavFileInfoT() { memset(this, 0, sizeof(*this)); }
};

inline void WavFileInfoTPrint(const WavFileInfoT& s)
{
	std::ostringstream ss;
	ss << " nRifflength=" << s.nRifflength;
	ss << " nAudioformat=" << s.nAudioformat;
	ss << " nChannels=" << s.nChannels;
	ss << " nSampleRate=" << s.nSampleRate;
	ss << " nByteRate=" << s.nByteRate;
	ss << " nBlockAlign=" << s.nBlockAlign;
	ss << " nBitsPerSample=" << s.nBitsPerSample;
	ss << " nRiffParts=" << s.nRiffParts;
	ss << " nExpectedSamples=" << s.nExpectedSamples;
	ss << " nRawdatalength=" << s.nRawdatalength;
	ss << " nDataOffset=" << s.nDataOffset;
	printf("%s ", ss.str().c_str());
}

inline void readUint32(FILE* f, uint32 *dest)
{
	*dest = 0;
	size_t read = fread(dest, sizeof(uint32), 1, f);
	assertTrue(read == 1);
}

inline void readUint16(FILE* f, uint16 *dest)
{
	*dest = 0;
	size_t read = fread(dest, sizeof(uint16), 1, f);
	assertTrue(read == 1);
}

inline void printADuration(uint64 nSamples, uint64 nSampleRate)
{
	double seconds = nSamples / ((double)nSampleRate);
	int nSeconds = (int)seconds;
	printf("%02d:%02d", nSeconds / 60, nSeconds % 60);
}

class FileWriteWrapper
{
	FILE* _file;
	const uint32 bufsize = 1024 * 1024 * 16;
	uint32 _pos;
	byte* _buffer;
	void flush()
	{
		fwrite(_buffer, 1, _pos, _file);
		_pos = 0;
	}

public:
	FileWriteWrapper(const char* path, const char* spec)
	{
		_pos = 0;
		_buffer = new byte[bufsize];
		_file = fopen(path, spec);
		assertTrue(_file != 0);
	}
	~FileWriteWrapper()
	{
		close();
	}
	uint32 write(const void * ptr, uint32 size, uint32 count)
	{
		flush();
		return size_t_to32(fwrite(ptr, size, count, _file));
	}
	int seek64(int64 offset, int origin)
	{
		flush();
		return fseek64(_file, offset, origin);
	}
	int64 tell64()
	{
		flush();
		return ftell64(_file);
	}
	int putchar(int character)
	{
		_buffer[_pos] = character;
		_pos++;
		if (_pos >= bufsize)
		{
			flush();
		}
		return character;
	}
	void close()
	{
		flush();
		if (_file)
		{
			fclose(_file);
		}
		delete[] _buffer;
		_buffer = 0;
		_file = 0;
	}
	FILE* detach() // caller is now responsible for fclosing the file.
	{
		flush();
		FILE* ret = _file;
		_file = 0;
		delete[] _buffer;
		_buffer = 0;
		return ret;
	}
};

class FileWriteThinWrapper
{
	FILE* _file;

public:
	FileWriteThinWrapper(char* path, char* spec)
	{
		_file = fopen(path, spec);
		assertTrue(_file != 0);
	}
	~FileWriteThinWrapper()
	{
		close();
	}
	uint32 write(const void * ptr, uint32 size, uint32 count)
	{
		return size_t_to32(fwrite(ptr, size, count, _file));
	}
	int seek64(int64 offset, int origin)
	{
		return fseek64(_file, offset, origin);
	}
	int putchar(int character)
	{
		return fputc(character, _file);
	}
	int64 tell64()
	{
		return ftell64(_file);
	}
	void close()
	{
		if (_file)
		{
			fclose(_file);
		}
		_file = 0;
	}
	FILE* detach() // caller is now responsible for fclosing the file.
	{
		FILE* ret = _file;
		_file = 0;
		return ret;
	}
};

errormsg readWavFileHeader(
	FILE* f, WavFileInfoT* info, uint64 addToLength);

errormsg writeWavHeader(
	FILE * f, int nLenInSamples, int bitsPerSample, int nSampleRate);

#endif /* WAV_H */
