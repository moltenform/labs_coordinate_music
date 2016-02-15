from coordmusicutil import *

showAllAlbumsRegardlessOfPopularity = False

def getPopularitiesList(fullpathdir, tags):
    # create mapUriToListIndex
    result = [0]*len(tags)
    mapUriToListIndex = dict()
    trackIds = []
    for i in range(len(tags)):
        if tags[i].getLink() and 'spotify:track:' in tags[i].getLink():
            trackIds.append(tags[i].getLink())
            mapUriToListIndex[unicode(tags[i].getLink())] = i
        
    # save network traffic by using batches of 20
    for trackIdBatch in takeBatch(trackIds, 20):
        results = spotipyconn().tracks(trackIdBatch)
        for track in results['tracks']:
            mappedIndex = mapUriToListIndex.get(unicode(track['uri']), -1)
            if mappedIndex==-1: 
                trace('unexpected track?', track['name'])
            else:
                popularity = track['popularity'] if 'US' in track[u'available_markets'] else 0
                result[mappedIndex] = popularity
    return result
    
def getStringTrackAndPopularity(directory, obj, popularity):
    localLen = int(get_audio_duration(files.join(directory, obj.short), obj))
    localBitrate = int(get_empirical_bitrate(files.join(directory, obj.short), obj))
    size = '%.1fMb'%(files.getsize(files.join(directory, obj.short))/(1024.0*1024))
    return 'p%02dp %s %s %dk %02d:%02d'%(popularity, obj.short, size, localBitrate, localLen//60, localLen%60)
    

def m4aToUrlWithBitrate(directory, short, obj):
    # For m4a files, we use the bitrate to "rate" the song.
    # Url files cannot do this, but we can optionally add a urlRatingNumber, e.g. "Good Song (16).url"
    locbitrate = int(get_empirical_bitrate(directory+'/'+short, obj))
    urlRatingNumber = 1
    if locbitrate<=120: urlRatingNumber = 10
    elif locbitrate<=128+15: urlRatingNumber = 12
    elif locbitrate<=144+8: urlRatingNumber = 14
    elif locbitrate<=160+8: urlRatingNumber = 16
    elif locbitrate<=176+8: urlRatingNumber = 17
    elif locbitrate<=192+8: urlRatingNumber = 19
    elif locbitrate<=224+8: urlRatingNumber = 22
    elif locbitrate<=256+8: urlRatingNumber = 25
    elif locbitrate<=288+8: urlRatingNumber = 28
    else: urlRatingNumber = 30
    while True:
        inp = getInputString('quality marker of "%d" look good, or enter another or "none" for none.'%urlRatingNumber, False)
        if inp=='y':
            break
        elif inp.isdigit():
            urlRatingNumber = int(inp)
            break
        elif inp=='none':
            urlRatingNumber = 'none'
            break
        elif inp=='no' or inp=='n':
            return
    newname = directory+'/'+files.splitext(short)[0]
    newname += (' (%d).url'%urlRatingNumber) if urlRatingNumber!='none' else '.url'
    assert 'spotify:track:' in obj.getLink()
    writeUrlFile(newname, obj.getLink())
    try:
        softDeleteFile(directory+'/'+short)
    except WindowsError:
        alert('you need to close the file first!')
        softDeleteFile(directory+'/'+short)
    
class SaveDiskSpaceMusicToUrl(object):
    def __init__(self, enabled=True):
        self.enabled = enabled
        
    def go(self, fullpathdir, tags, parsedNames):
        if not self.enabled:
            return
        
        tags = [tag for tag in tags if not tag.short.endswith('.url') and not tag.short.endswith('.3.mp3') and not '.sv.' in tag.short and 'spotify:track:' in tag.getLink()]
        if not tags:
            return
        
        popularitiesList = getPopularitiesList(fullpathdir, tags)
        nothingMeetsCutoff = all((not popularity or isinstance(popularity, str) or popularity<getPopularityCutoff()) for popularity in popularitiesList)
        if not showAllAlbumsRegardlessOfPopularity and nothingMeetsCutoff:
            return
        
        # if it's an album, show the entire album, for context
        trace('looking to save disk space in %s (%.1fMb)\n'%(fullpathdir, sum(files.getsize(files.join(fullpathdir, tag.short)) for tag in tags)/(1024.0*1024)))
        for tag, popularity in zip(tags, popularitiesList):
            trace(getStringTrackAndPopularity(fullpathdir, tag, popularity))
        
        # pause to let the user look at the album
        if showAllAlbumsRegardlessOfPopularity and nothingMeetsCutoff:
            alert('')
        
        # now go one by one and ask if replacements are ok
        replacedAny = False
        for tag, popularity in zip(tags, popularitiesList):
            if popularity>=getPopularityCutoff():
                trace('\n\n', getStringTrackAndPopularity(fullpathdir, tag, popularity))
                while True:
                    inp = getInputString('replace this with .url? (y/n/N, hear0, hear1)', False)
                    if inp=='y':
                        m4aToUrlWithBitrate(fullpathdir, tag.short, tag)
                        replacedAny = True
                        break
                    elif inp=='n':
                        break
                    elif inp=='N':
                        return
                    elif inp=='hear0':
                        launchMediaPlayer(files.join(fullpathdir, tag.short))
                    elif inp=='hear1':
                        launchSpotifyUri(tag.getLink())
                    elif inp == 'explorer':
                        askExplorer(fullpathdir, False)
                    
        stopIfFileRenamed(replacedAny)

