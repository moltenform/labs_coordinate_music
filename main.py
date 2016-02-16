import recurring_coordinate
    
def utils_clearPlaylist(playlist_id):
    import time
    sp = spotipyconnect()
    tracks = getTracksFromPlaylist(sp, playlist_id)
    trace('removing %d tracks.'%len(tracks))
    urisToRemove = [track[u'uri'] for track in tracks]
    
    for res in takeBatch(urisToRemove, 10):
        sp.user_playlist_remove_all_occurrences_of_tracks(getSpotifyUsername(), playlist_id, res)
        time.sleep(0.2)

def utils_lookForMp3AndAddToPlaylist(dir, bitrateThreshold, playlistId = None):
    results = []
    lib = os.sep+'lib'+os.sep
    for short, fullpath in files.recursefiles(dir):
        if lib not in fullpath:
            if fullpath.endswith('.mp3') and not fullpath.endswith('.3.mp3') and not fullpath.endswith('.sv.mp3'):
                obj = CoordMusicAudioMetadata(fullpath)
                if 'spotify:track:' in obj.getLink() and get_empirical_bitrate(fullpath, obj) >= bitrateThreshold:
                    trace('found file', fullpath)
                    results.append((fullpath, obj.getLink()))
                    
    if playlistId:
        for batch in takeBatch(results, 10):
            trace('adding to playlist', '\n'.join((item[0] for item in batch)))
            sp.user_playlist_add_tracks(getSpotifyUsername(), playlistId, [item[1] for item in batch])
            time.sleep(0.2)
        

def main(root, scope=None, startingpoint=None):
    choices = ['organize music', 
        'organize + save disk space (replace with Spotify shortcuts)',
        'view a song\'s Spotify link',
        'Spotify playlist to song lengths',
        'Spotify playlist to filenames',
        'filenames to id3 tags',
        'save all filenames+metadata to text file']
    choice = getInputFromChoices('', choices)
    getInout('scope?')
    getInout('startingpoint?')
    getInputBool('run create sync for sv.mp3?')
    
    
if __name__=='__main__':
    #~ if len(sys.argv)>1 and sys.argv[1] == 'startspotify':
        #~ startSpotifyFromM4aArgs(sys.argv)
    #~ else:
        #~ tests()
    #~ main(r'C:\music', r'C:\music\00s Indie Rock\Tune-yards, Micachu\2009, Micachu - Jewellery')
    #~ main(ur'C:\music', ur'C:\music')
    files.run([r'C:\data\local\devsoftware\FisherAppsFull\Utils\Create Synchronicity6.0\Create Synchronicity.exe', '/preview','/run', 'svmp3'])

    