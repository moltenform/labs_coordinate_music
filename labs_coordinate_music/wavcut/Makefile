
CC = g++
CFLAGS=-c -std=c++11 -Wall -Werror -Wno-unused-label -Wno-unused-function 

debug: CFLAGS += -DDEBUG -D_DEBUG -g
debug: all
ship: CFLAGS += -O3
ship: all

OBJECTS= main.o util.o wavcut.o wav.o
LIBS=

all: wavcut

wavcut: $(OBJECTS)
	$(CC) -o wavcut $(OBJECTS) $(LIBS)

main.o: main.cpp
	$(CC) $(CFLAGS) main.cpp

util.o: util.cpp
	$(CC) $(CFLAGS) util.cpp
	
wav.o: wav.cpp
	$(CC) $(CFLAGS) wav.cpp
	
wavcut.o: wavcut.cpp
	$(CC) $(CFLAGS) wavcut.cpp
	
clean:
	rm *.o
	rm wavcut

