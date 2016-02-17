
import coordmusictools
import coordmusicuserconfig
import recurring_coordinate
import recurring_linkspotify
import sys

def showCmdOptions():
    trace('main.py'+
    '\n\tInteractive mode: organization and more.'+
    'main.py startspotify /path/to/song.mp3'+
    '\n\tStarts playing the Spotify track that this mp3\'s metadata points to.'+
    'main.py viewspotify /path/to/song.mp3'+
    '\n\tShow the Spotify track that this mp3\'s metadata points to.')

def main():
    choices = ['organize music', 
        'organize + save disk space (replace with Spotify shortcuts)',
        'Spotify playlist to song lengths',
        'Spotify playlist to filenames',
        'filenames to id3 tags',
        'save all filenames+metadata to text file',
        'show cmd-line options']
    choice = getInputFromChoices('', choices)
    if choice[0]==0:
        recurring_coordinate.mainCoordinate(isTopDown=True, enableSaveSpace=False)
    elif choice[0]==1:
        recurring_coordinate.mainCoordinate(isTopDown=True, enableSaveSpace=True)
    
    coordmusictools.tools_spotifyPlaylistToSongLengths
    
    coordmusicuserconfig.runAfterCoordinate()
    
if __name__=='__main__':
    if len(sys.argv)>1 and (sys.argv[1] == '-?' or sys.argv[1] == '-h' or sys.argv[1] == '/?'):
        showCmdOptions()
    elif len(sys.argv)>1 and sys.argv[1] == 'startspotify':
        recurring_linkspotify.startSpotifyFromM4aArgs(sys.argv)
    elif len(sys.argv)>2 and sys.argv[1] == 'viewspotify':
        recurring_linkspotify.viewTagsFromM4aOrDirectory(sys.argv[2])
    else if len(sys.argv)==1:
        main()
    else:
        showCmdOptions()
        

    

    