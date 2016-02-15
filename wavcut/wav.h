#ifndef WAV_H
#define WAV_H

#include "util.h"

struct WavFileInfoT
{
	uint64 nRifflength, nExpectedSamples, nRawdatalength, nDataOffset;
	uint32 nAudioformat, nChannels, nSampleRate, nByteRate, nBlockAlign, nBitsPerSample, nRiffParts;
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

inline void ReadUint32(FILE* f, uint32 *dest)
{
	fread(dest, sizeof(uint32), 1, f);
}

inline void ReadUint16(FILE* f, uint16 *dest)
{
	fread(dest, sizeof(uint16), 1, f);
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
	const size_t bufsize = 1024 * 1024 * 16;
	size_t _pos;
	byte* _buffer;
	void flush()
	{
		::fwrite(_buffer, 1, _pos, _file);
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
	size_t fwrite(const void * ptr, size_t size, size_t count)
	{
		flush();
		return ::fwrite(ptr, size, count, _file);
	}
	int fseek64(int64 offset, int origin)
	{
		flush();
		return ::_fseeki64(_file, offset, origin);
	}
	int64 ftell64()
	{
		flush();
		return ::_ftelli64(_file);
	}
	int fputc(int character)
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
	size_t fwrite(const void * ptr, size_t size, size_t count)
	{
		return ::fwrite(ptr, size, count, _file);
	}
	int fseek64(int64 offset, int origin)
	{
		return ::_fseeki64(_file, offset, origin);
	}
	int fputc(int character)
	{
		return ::fputc(character, _file);
	}
	int64 ftell64()
	{
		return ::_ftelli64(_file);
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

errormsg readWavFileHeader(FILE* f, WavFileInfoT* info, uint64 addToLength);
errormsg writeWavHeader(FILE * f, int nLenInSamples, int bitsPerSample, int nSampleRate);



#endif /* WAV_H */
