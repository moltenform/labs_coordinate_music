import recurring_linkspotify
import recurring_music_to_url
import codecs
from coordmusicutil import *
import time

def tools_getPlaylistId(playlistId=None):
    if not playlistId:
        playlistId = getDefaultSpotifyPlaylist()
        if not playlistId:
            warn('no default playlist, please edit coordmusicuserconfig.py '+
                'and implement getDefaultSpotifyPlaylist()')
    return playlistId
        
def tools_clearPlaylist(playlistId=None):
    playlistId = tools_getPlaylistId(playlistId)
    sp = spotipyconnect()
    tracks = getTracksFromPlaylist(sp, playlistId)
    trace('removing %d tracks.'%len(tracks))
    urisToRemove = [track[u'uri'] for track in tracks]
    
    for res in takeBatch(urisToRemove, 10):
        sp.user_playlist_remove_all_occurrences_of_tracks(getSpotifyUsername(), playlistId, res)
        time.sleep(0.2)

def tools_viewSpotifyPlaylist(playlistId=None):
    playlistId = tools_getPlaylistId(playlistId)
    tracks = getTracksFromPlaylist(spotipyconnect(), playlistId)
    for i, track in enumerate(tracks):
        info = ExtendedSongInfo(None, None)
        info.info['uri'] = track['uri'].replace('spotify:track:', '')
        info.addSpotifyInfo(track)
        trace(str(i+1), unicode(info).replace('None	00:00:000	0',''))

def tools_spotifyPlaylistToSongLengths(playlistId=None):
    playlistId = tools_getPlaylistId(playlistId)
    tracks = getTracksFromPlaylist(spotipyconnect(), playlistId)
    outpath = getDefaultDirectorySpotifyToFilenames()+'/data/lengths.txt'
    with open(outpath, 'w') as fout:
        for i, track in enumerate(tracks):
            fout.write('%f|%d %s'%(track['duration_ms']/1000.0, i+1, track['uri']))
            fout.write('\n')
    trace('wrote %d lengths to %s'%(len(tracks), outpath))
    
def tools_spotifyPlaylistToFilenames(playlistId=None):
    playlistId = tools_getPlaylistId(playlistId)
    tracks = getTracksFromPlaylist(spotipyconnect(), playlistId)
    startInPlaylist = getInputInt('start where in the playlist (default 1)?', 1, len(tracks))-1
    tracks = tracks[startInPlaylist:]
    
    potentialRenames = []
    localfiles = list(getScopedRecurseFiles(getDefaultDirectorySpotifyToFilenames()))
    for i, track in enumerate(tracks):
        if i>=len(localfiles):
            trace('reached end of available files, %d files needed but got %d'%(len(tracks), len(localfiles)))
            return
        trace('%d) %s %s\t->%s %s - %s'%(i+1, localfiles[i][1], getFormattedDuration(get_audio_duration(localfiles[i][0])),
            getFormattedDuration(track['duration_ms']/1000.0), 
            track['artists'][0]['name'], track['name']))
        newname = files.getparent(localfiles[i][0])+files.sep+getFilenameFromTrack(i+1, track)+'.'+files.getext(localfiles[i][0])
        potentialRenames.append((localfiles[i][0], newname))
    
    if getInputBool('begin renaming?'):
        for old, new in potentialRenames:
            trace('renaming "%s" to "%s"'%(files.getname(old), files.getname(new)))
            files.move(old, new, False)

def getFilenameFromTrack(number, track):
    newname = '$' + track['artists'][0]['name']+ '$'
    newname += '%02d'%(int(track['track_number'])) + \
        '$' + track['name'].split(u' - ')[0]+ '$'
    newname +=  track['uri'].replace('spotify:track:','')
    
    # add either the album name, or part of the album name if our name is too long
    if len(newname) > 160:
        warn('filename is too long '+newname)
    elif len(newname)+len(track[u'album'][u'name']) > 160:
        warn('truncating album name for too long '+newname)
        newname = track[u'album'][u'name'][0:5] + newname
    else:
        newname = track[u'album'][u'name'] + newname
    
    newname = '%04d '%number + newname
    return safefilename(newname)
    
def setMetadataFromFilename(fullpath):
    parts = files.getname(fullpath).split('$')
    if len(parts)!=5:
        trace('for file %s incorrect # of $'%(fullpath))
        return
    alb, artist, tracknum, title, spotifyUri = parts
    position, alb = alb.split(' ', 1)
    spotifyUri = spotifyUri.split('.')[0]
    obj = CoordMusicAudioMetadata(fullpath)
    obj.setLink('spotify:track:'+spotifyUri)
    obj.set('album', alb)
    obj.set('artist', artist)
    obj.set('title', title)
    obj.set('tracknumber', tracknum)
    obj.save()
    
def tools_filenamesToMetadataAndRemoveLowBitrate():
    localfiles = list(getScopedRecurseFiles(getDefaultDirectorySpotifyToFilenames()))
    for fullpath, short in localfiles:
        if short.endswith('.wav'): warn('why is there still a wav here? '+short)
        if '__MARKAS' in short: warn('why is there a file with MARKAS here? '+short)
    
    for fullpath, short in localfiles:
        if fullpath.endswith('.m4a'):
            setMetadataFromFilename(fullpath)
            if get_empirical_bitrate(fullpath) < 20:
                trace('auto-deleting low bitrate', short)
                softDeleteFile(fullpath)
            else:
                trace('saved tags for', short)
        

def tools_lookForMp3AndAddToPlaylist(dir, bitrateThreshold, playlistId=None):
    results = []
    for fullpath, short in getScopedRecurseFiles(dir, filterOutLib=True):
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

def tools_saveFilenamesMetadataToText():
    outName = getInputString('save to what output file:', False)
    if files.exists(outName):
        trace('already exists.')
        return
        
    fileIterator = getScopedRecurseFiles(getMusicRoot(), filterOutLib=True)
    useSpotify = getSpotifyClientID() and getInputBool('retrieve Spotify metadata?')
    saveFilenamesMetadataToText(fileIterator, useSpotify, outName)
    
class ExtendedSongInfo():
    def __init__(self, filename, short):
        self.info = dict(filename=filename, short=short, localLength=0, localBitrate=0, localAlbum = u'', 
            uri='', spotifyArtist = u'', spotifyTitle = u'', spotifyLength = u'', spotifyAlbum = u'', isMarketWarn=u'')
        
        if not filename:
            pass
        elif filename.endswith('.url'):
            self.info['uri'] = getFromUrlFile(filename)
        elif filename.endswith('.txt'):
            self.info['localAlbum'] = readall(filename).replace('\r\n','\n').replace('\n','|')
        elif getFieldForFile(filename, throw=False):
            obj = CoordMusicAudioMetadata(filename)
            self.info['uri'] = obj.getLink()
            self.info['localLength'] = get_audio_duration(filename, obj)
            self.info['localBitrate'] = get_empirical_bitrate(filename, obj)
            
            parentname = files.getname(files.getparent(filename))
            if not(parentname[4:5]==',' and parentname[0:4].isdigit()):
                self.info['localAlbum'] = obj.get_or_default('album', '')
                
    def addSpotifyInfo(self, track):
        self.info['spotifyArtist'] = ';'.join(art['name'] for art in track['artists'])
        self.info['spotifyTitle'] = track['name']
        self.info['spotifyLength'] = track['duration_ms']/1000.0
        self.info['spotifyAlbum'] = track['album']['name']
        if getSpotifyGeographicMarketName() not in track['available_markets']:
            self.info['isMarketWarn'] = 'warning: market unavailable'
        
    def __unicode__(self):
        return u'%s\t%s\t%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s'%(self.info['filename'], 
            getFormattedDuration(self.info['localLength'], True), int(self.info['localBitrate']), 
            self.info['localAlbum'], self.info['uri'].replace('spotify:track:','').replace('spotify:',''),
            self.info['spotifyArtist'], self.info['spotifyTitle'], 
            getFormattedDuration(self.info['spotifyLength'], True),
            self.info['spotifyAlbum'],self.info['isMarketWarn'])

def saveFilenamesMetadataToText(fileIterator, useSpotify, outName, requestBatchSize=15, maxBatchSize=50):
    batch = []
    mapUriToExtendedSongInfo = dict()
    def goBatch(batch=batch, mapUriToExtendedSongInfo=mapUriToExtendedSongInfo):
        if useSpotify and len(mapUriToExtendedSongInfo):
            tracks = spotipyconn().tracks([uri for uri in mapUriToExtendedSongInfo])
            for track in tracks['tracks']:
                songInfo = mapUriToExtendedSongInfo[unicode(track['uri'])]
                songInfo.addSpotifyInfo(track)
                del mapUriToExtendedSongInfo[unicode(track['uri'])]
            if len(mapUriToExtendedSongInfo)>0:
                warn('did not find a spotify track for %s'%(
                    '\n'.join(uri+','+mapUriToExtendedSongInfo[uri].filename
                        for uri in mapUriToExtendedSongInfo)))
        
        for songInfo in batch:
            fout.write(unicode(songInfo))
            fout.write('\n')
        
        batch[:] = []
        mapUriToExtendedSongInfo.clear()
        
    with codecs.open(outName, 'a', "utf-8-sig") as fout:
        for filename, short in fileIterator:
            batch.append(ExtendedSongInfo(filename, short))
            if 'spotify:track:' in batch[-1].info['uri']:
                mapUriToExtendedSongInfo[unicode(batch[-1].info['uri'])] = batch[-1]
                
            if len(mapUriToExtendedSongInfo)>=requestBatchSize or len(batch)>=maxBatchSize:
                time.sleep(0.2)
                goBatch()
                
        goBatch()
        
