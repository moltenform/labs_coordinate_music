// wavcut
// Ben Fisher, 2015
// Released under the GNU General Public License version 3

#include "util.h"
#include <sys/stat.h>
#include <fstream>

const errormsg OK = 0;

bool fileExists(const char* path)
{
	FILE* f = fopen(path, "rb");
	if (f)
	{
		fclose(f);
		return true;
	}
	else
	{
		return false;
	}
}

bool getBoolFromUser(const char* prompt)
{
	printf("%s\n", prompt);
	printf("\ny/n?");
	while (true)
	{
		int c = getchar();
		if (c == 'y')
			return true;
		else if (c == 'n')
			return false;
	}
}

void assertEqualImpl(int a, int b, const char* msg, int line, const char* file)
{
	if (a != b)
	{
		std::ostringstream ss;
		ss << "Assertion failure on line " << line << 
			" of file " << file << " " << a << " != " << b;
		ss << (msg ? msg : "");
		fprintf(stderr, "%s\nPress enter to continue...\n", ss.str().c_str());
		std::cin.get();
		fflush(stderr);
		debugBreak();
	}
}

bool stringsEqual(const char *s1, const char *s2)
{
	return strcmp(s1, s2) == 0;
}

std::vector<std::string> splitString(const std::string & s, char delim)
{
	std::vector<std::string> elems;
	std::stringstream ss(s);
	std::string item;
	while (std::getline(ss, item, delim))
	{
		elems.push_back(item);
	}

	// add an empty element if the string ends with delim.
	if (s.length() > 0 && s[s.length() - 1] == delim)
	{
		elems.push_back(std::string());
	}

	return elems;
}

std::vector<int64> parseLengthsFile(const char* filename, uint64 sampleRate)
{
	std::vector<int64> result;
	if (!fileExists(filename))
	{
		printf("file does not exist.\n");
		return result;
	}

	std::ifstream t(filename, std::ifstream::in); // don't open as binary.
	std::stringstream buffer;
	buffer << t.rdbuf();
	std::vector<std::string> elems;
	std::string item;
	while (std::getline(buffer, item, '\n'))
	{
		if (item.size() > 0)
			elems.push_back(item);
	}

	if (elems.size() == 0)
		return std::vector<int64>();

	int expectedParts = 2;
	char delim = '|';
	bool cumulative = false;
	{
		std::vector<std::string> parts1 = splitString(elems[0], '|');
		std::vector<std::string> parts2 = splitString(elems[0], '\t');
		if (parts2.size() == 3 && parts1.size() == 1 && 
			getBoolFromUser("this looks like an audacity Label track. import as such?"))
		{
			expectedParts = 3;
			delim = '\t';
			cumulative = true;
		}
		else
		{
			elems.pop_back(); // the empty one
			if (elems.size() == 0)
				return std::vector<int64>();
		}
	}

	result.resize(elems.size());
	for (uint32 i = 0; i < size_t_to32(elems.size()); i++)
	{
		std::vector<std::string> parts = splitString(elems[i], delim);
		if (parts.size() != expectedParts)
		{
			printf("Error: expected one line of text per cut point,"
				"every line in the form seconds|trackname but got\n%s\n",
				elems[i].c_str());
			return std::vector<int64>();
		}

		int64 sampleAtWhichToCut = (int64)(sampleRate * atof(parts[0].c_str()));
		if (sampleAtWhichToCut <= 0 && i != 0)
		{
			printf("Error: length should not be <= 0\n%s\n", elems[i].c_str());
			return std::vector<int64>();
		}

		result[i] = sampleAtWhichToCut;
	}

	if (cumulative)
	{
		std::vector<int64> resultDifferences;
		resultDifferences.resize(result.size());
		resultDifferences[0] = result[0];
		for (uint32 i = 1; i < size_t_to32(result.size()); i++)
		{
			resultDifferences[i] = result[i] - result[i - 1];
		}
		return resultDifferences;
	}

	return result;
}



#ifndef _WIN32
#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>
#include <time.h>

PerfTimer::PerfTimer()
{
	_start = (int64)time(null);
}

double PerfTimer::stop()
{
	return (int64)time(null) - _start;
}

errormsg truncateFile(const char* path, int64 length)
{
	int ret = truncate(path, length);
	if (ret == 0)
		return OK;
	else
		return "failed to truncate file.";
}

int fseek64(FILE *stream, int64 offset, int type)
{
	return fseeko(stream, offset, type);
}

int64 ftell64(FILE *stream)
{
	return ftello(stream);
}

uint64 getFileSize(const char* path)
{
	struct stat64 st = { 0 };
	if (stat64(path, &st) == 0)
		return st.st_size;
	else
		return 0;
}

#else
#include <windows.h>

PerfTimer::PerfTimer()
{
	LARGE_INTEGER tmp = { 0 };
	QueryPerformanceCounter(&tmp);
	_start = tmp.QuadPart;
}

double PerfTimer::stop()
{
	assertTrue(_start != 0);
	LARGE_INTEGER nstop;
	QueryPerformanceCounter(&nstop);
	uint64 ndiff = nstop.QuadPart - _start;
	LARGE_INTEGER freq;
	QueryPerformanceFrequency(&freq);
	return (ndiff) / ((double)freq.QuadPart);
}

errormsg truncateFile(const char* path, int64 length)
{
	if (length >= fourgb)
	{
		return_err("currently only supports truncate if less than 4gb.");
	}

	uint32 length32 = u64_to32(length);
	HANDLE handle = CreateFileA(path, // file to be opened
		GENERIC_WRITE, // open for writing
		FILE_SHARE_READ, // share for reading
		NULL, // default security
		OPEN_EXISTING, // open existing file
		0, //the file is not read only
		NULL); // no attribute template

	if (handle == INVALID_HANDLE_VALUE)
		return_err("could not open file for truncate");

	DWORD ret = SetFilePointer(handle, length32, 0, FILE_BEGIN);
	if (ret == INVALID_SET_FILE_POINTER)
	{
		CloseHandle(handle);
		return_err("could not truncate file, seek failed.");
	}

	BOOL bret = SetEndOfFile(handle);
	if (!bret)
	{
		CloseHandle(handle);
		return_err("could not truncate file, SetEndOfFile failed.");
	}

	CloseHandle(handle);
	return OK;
}

int fseek64(FILE *stream, int64 offset, int type)
{
	return _fseeki64(stream, offset, type);
}

int64 ftell64(FILE *stream)
{
	return _ftelli64(stream);
}

uint64 getFileSize(const char* path)
{
	struct __stat64 buf;
	int result = _stat64(path, &buf);
	if (result != 0)
		return 0;
	else
		return buf.st_size;
}

#endif