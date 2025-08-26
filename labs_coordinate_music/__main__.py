# labs_coordinate_music
# Ben Fisher, 2016
# Released under the GNU General Public License version 3

import sys
import os

# let this file be started as either a script or as part of the package.
if __package__ is None and not hasattr(sys, 'frozen'):
    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(path)))

from labs_coordinate_music import \
    coordmusictools, coordmusicuserconfig, \
    recurring_coordinate, recurring_linkspotify

def showCmdOptions():
    coordmusictools.trace('\nmain.py' +
    '\n\tInteractive mode: organization and more.' +
    '\n\nmain.py startspotify /path/to/song.mp3' +
    '\n\tStarts playing the Spotify track that this mp3\'s metadata points to.' +
    '\n\nmain.py viewspotify /path/to/song.mp3' +
    '\n\tShow the Spotify track that this mp3\'s metadata points to.')

def main():
    choices = ['organize music',
        'organize + save disk space (replace with Spotify shortcuts)',
        'Spotify playlist to text',
        'Spotify playlist to song lengths',
        'Spotify playlist to filenames',
        'filenames to id3 tags, remove low bitrate',
        'save all filenames+metadata to text file',
        'show cmd-line options']
        
    choice, s = coordmusictools.getInputFromChoices('', choices)
    if choice == 0:
        recurring_coordinate.mainCoordinate(isTopDown=True, enableSaveSpace=False)
        coordmusicuserconfig.runAfterCoordinate()
    elif choice == 1:
        recurring_coordinate.mainCoordinate(isTopDown=True, enableSaveSpace=True)
        coordmusicuserconfig.runAfterCoordinate()
    elif choice == 2:
        coordmusictools.tools_viewSpotifyPlaylist()
    elif choice == 3:
        coordmusictools.tools_spotifyPlaylistToSongLengths()
    elif choice == 4:
        coordmusictools.tools_spotifyPlaylistToFilenames()
    elif choice == 5:
        coordmusictools.tools_filenamesToMetadataAndRemoveLowBitrate()
    elif choice == 6:
        coordmusictools.tools_saveFilenamesMetadataToText()
    elif choice == 7:
        showCmdOptions()
    
def checkForMetadataTags(dir):
    import coordmusicutil
    import sys
    from shinerainsevenlib.standard import files

    assert files.exists(dir)
    countWithTags = 0
    countWithoutTags = 0
    for file, short in files.listFiles(dir):
        if coordmusicutil.getFieldForFile(file, False):
            obj = coordmusicutil.CoordMusicAudioMetadata(file)
            if obj.get_or_default('artist', None) and obj.get_or_default('title', None):
                countWithTags += 1
            else:
                countWithoutTags += 1
                
    sys.stderr.write('saw %d audio files with tags and %d audio files without tags'%(countWithTags, countWithoutTags))


if __name__ == '__main__':
    if len(sys.argv) > 1 and (sys.argv[1] == '-?' or sys.argv[1] == '-h' or sys.argv[1] == '/?'):
        showCmdOptions()
    elif len(sys.argv) > 1 and sys.argv[1] == 'startspotify':
        recurring_linkspotify.startSpotifyFromM4aArgs(sys.argv)
    elif len(sys.argv) > 2 and sys.argv[1] == 'viewspotify':
        recurring_linkspotify.viewTagsFromM4aOrDirectory(sys.argv[2])
    elif len(sys.argv) > 2 and sys.argv[1] == 'checkformetadatatags':
        checkForMetadataTags(sys.argv[2])
    elif len(sys.argv) == 1:
        main()
    else:
        showCmdOptions()
