
from coordmusicutil import *
import re

def lookupAlbumForFile(path, tag, parsed, spotlink):
    trackSeen = None
    whatToSet = None
    if spotlink and 'spotify:track:' in spotlink and 'notfound' not in spotlink:
        results = spotipyconn().tracks([spotlink])
        for track in results['tracks']:
            if track['id']==spotlink or track['uri']==spotlink:
                trackSeen = track

    choices = ['enter manually', 'search online']
    if trackSeen:
        choices.extend(['Spotify: '+track['album']['name'], 'Spotify: '+track['album']['name'].split(' (')[0].split(' [')[0]])
       
    def callback(s, arrChoices, otherCommandsContext):
        if not s or s[0].isdigit(): return False
        else: return 'enteredmanally'+s
    choice = getInputFromChoices('\n\nthe album for %s is (or type name)'%path, choices, callback)
    if choice[0]==0:
        choice = (choice[0], getInputString('album name:'))
    elif choice[0]==-1 and choice[1].startswith('enteredmanally'):
        # instead of typing 0, 1, or 2, the user directly typed in text.
        choice = (choice[0], choice[1].replace('enteredmanally',''))
        if not getInputBool(choice[1]):
            choice = (choice[0], getInputString('album name:'))
    elif choice[0]==1:
        import urllib2, subprocess
        subprocess.Popen(['start', 'http://google.com/search?q='+urllib2.quote(parsed.artist+' '+parsed.title)], shell=True)
        return lookupAlbumForFile(path, tag, parsed, spotlink)
    elif choice[0] < 0:
        return

    tag.set('album', choice[1].replace('Spotify: ', ''))
    tag.save()

def linkspotify(seenWithoutSpotify, fullpathdir, tags, parsedNames, seenTracknumber, market):
    if not seenWithoutSpotify:
        return
        
    if not getSpotifyClientID():
        trace('Connecting to Spotify has been disabled, provide a clientID in coordmusicuserconfig.py to enable.')
        return
        
    trace('\n\n\n\nAssociate with Spotify, for directory\n'+fullpathdir+'\n\n')
    trace('containing\n', '\n\t'.join(tag.short for tag in tags),'\n\n')
    choices = ['associate with Spotify, each track individually']
    if seenTracknumber: choices.append('associate with Spotify, whole album')
    choice = getInputFromChoices('', choices)
    if choice[0]==0:
        [linkspotifypertrack(market, fullpathdir, tag, parsed) for tag, parsed in zip(tags, parsedNames)]
    elif choice[0]==1:
        linkspotifyperalbum(market, fullpathdir, tags, parsedNames)
        
def runspotifysearch(market, search_str, type, limit, filterCovers):
    assertTrue(type=='album' or type=='track', 'unsupported search type '+type)
    result = spotipyconn()._get('search', q=search_str, limit=limit, offset=0, type=type, market=market)
    result = result[type+'s']['items']
    resultFiltered = []
    for res in result:
        if type=='track': 
            textlower = res[u'name'].lower() + ' '+ ' '.join((getPrintable(art['name']) for art in res['artists'])).lower()
        else:
            textlower = res[u'name'].lower()
        
        if not filterCovers or not re.findall(r'\b(karaoke|style of|tribute|tributes|cover|parody|originally performed)\b', textlower):
            resultFiltered.append(res)
            
    # confirm that it is filtered by market
    resultFiltered = [track for track in resultFiltered if unicode(market) in track[u'available_markets'] 
        and track[u'uri'].startswith('spotify:'+type+':')]
    return resultFiltered

def getStrLocalAudioFile(path, parsed, tag, duration=None):
    if duration is None:
        duration = int(get_audio_duration(path, tag))
    return getPrintable('(%02d:%02d) (%s) %s'%(duration//60,duration%60, parsed.artist, parsed.title))

def getStrRemoteAudio(track, includeDiscNum, includeTracknum, artistsAlreadyShown=None):
    duration = int(track['duration_ms']/1000.0)
    artists = ';; '.join((art['name'] for art in track['artists']))
    artists = '' if artists==artistsAlreadyShown else '('+artists+')'
    tracknumber = '%02d'%track[u'track_number'] if includeTracknum else ''
    discnumber = '%02d '%track[u'disc_number'] if includeDiscNum else ''
    return getPrintable('(%02d:%02d) %s%s %s %s'%(duration//60, duration%60,
        discnumber, tracknumber, artists, track['name']))
    
def getTracksRemoteAlbum(albumid, market):
    results = spotipyconn().album_tracks(albumid)
    tracks = results['items']
    while results['next']:
        results = spotipyconn().next(results)
        tracks.extend(results['items'])
    return [track for track in tracks if unicode(market) in track[u'available_markets']]

def getStrRemoteAlbum(tracks, albumartists):
    ret = []
    includeDiscNum = any(track['disc_number'] not in (0,1) for track in tracks)
    for track in tracks:
        ret.append(getStrRemoteAudio(track, includeDiscNum, True, albumartists))
    return '\n'.join(ret)
    
def callbackForChoiceTrack(inp, arrChoices, otherCommandsContext):
    fullpathdir, search_str, tag, results, market = otherCommandsContext
    done = False
    if inp=='ns':
        tag.setLink('spotify:notfound')
        tag.save()
        done = True
    elif inp=='NS' and getInputBool('sure entire directory is not on spotify?'):
        for fullpath, short in files.listfiles(fullpathdir):
            if getFieldForFile(fullpath, False):
                trace('setting to spotify:notfound,', short)
                stampM4a(fullpath, 'spotify:notfound', onlyIfNotAlreadySet=True)
        
        done = True
        raise StopBecauseWeRenamedFile # because tags are now invalidated
    elif inp == 'explorer':
        askExplorer(fullpathdir)
    elif inp == 'hear0':
        launchMediaPlayer(files.join(fullpathdir, tag.short))
    elif inp == 'hear#':
        trace('type a number, e.g. hear1 to hear first track')
    elif inp.startswith('hear'):
        inp = inp[len('hear'):]
        if inp.isdigit():
            n = int(inp)-1
            if n>=0 and n<len(results):
                trace('starting in Spotify to hear.')
                launchSpotifyUri(results[n]['uri'])
    elif inp == 'type':
        typeIntoSpotifySearch(search_str)
    elif inp.startswith('more'):
        results[:] = runspotifysearch(market, search_str, type='track', limit=20, filterCovers=False)
        done = 'more'
    elif inp.startswith('spotify:track:'):
        inp = inp[len('spotify:track:'):]
        results.append(spotipyconn().track(inp))
        done = 'more'
    return done

def callbackForChoiceAlbum(inp, arrChoices, otherCommandsContext):
    fullpathdir, search_str, tags, results, market = otherCommandsContext
    done = False
    if inp=='ns' and getInputBool('sure entire directory is not on spotify?'):
        for fullpath, short in files.listfiles(fullpathdir):
            if getFieldForFile(fullpath, False):
                trace('setting to spotify:notfound,', short)
                stampM4a(fullpath, 'spotify:notfound', onlyIfNotAlreadySet=True)
        
        raise StopBecauseWeRenamedFile # because tags are now invalidated
        done = True
    elif inp == 'explorer':
        askExplorer(fullpathdir)
    elif inp == 'type':
        typeIntoSpotifySearch(search_str)
    elif inp.startswith('more'):
        results[:] = runspotifysearch(market, search_str, type='album', limit=20, filterCovers=True)
        done = 'more'
    elif inp.startswith('spotify:album:'):
        inp = inp[len('spotify:album:'):]
        results.append(spotipyconn().album(inp))
        done = 'more'
    return done
    
def callbackForChoiceAlbumTrack(inp, arrChoices, otherCommandsContext):
    fullpathdir, tag, key, remotetrack = otherCommandsContext
    path = fullpathdir+'/'+tag.short
    if inp == 'explorer':
        askExplorer(fullpathdir)
    elif inp == 'hear0':
        launchMediaPlayer(path)
    elif inp == 'hear1' and remotetrack:
        launchSpotifyUri(remotetrack['uri'])
    elif '_' in inp:
        try:
            dsc, trk = inp.split('_')
            key.key = '%02d_%02d' % (int(dsc), int(trk))
            return True
        except:
            trace('malformed track number, expected syntax 01_01 ', str(sys.exc_info()[1]))
    
def getChoiceString(track, localduration, artistExpected='', inclAlbum=False):
    ret = getStrRemoteAudio(track, False, False) + ' '
    remoteduration = track['duration_ms']/1000.0
    if abs(localduration - remoteduration)<6:
        ret += 'same lngth'
    elif remoteduration > localduration:
        ret += 'lnger(%ds)'%int(remoteduration - localduration)
    else:
        ret += 'shrter(%ds)'%int(localduration - remoteduration)
    if inclAlbum:
        ret += '\n\tfrom %s'%track['album']['name']
    return ret

def linkspotifypertrack(market, fullpathdir, tag, parsed):
    if tag.short.endswith('.url') or 'spotify:' in tag.getLink():
        return
    
    path = fullpathdir + '/' + tag.short
    localduration = get_audio_duration(path, tag)
    artist = (parsed.artist if parsed.artist else tag.get('artist')) or ''
    title = (parsed.title if parsed.title else tag.get('title')) or ''
    
    trace('\n\n\nin folder\n',files.getname(fullpathdir),'\n',tag.short)
    trace('\n00 %s\n\n'%getStrLocalAudioFile(path, parsed, tag, localduration) )
    search_str = unicode(artist) + ' '+title
    results = runspotifysearch(market, search_str, type='track', limit=8, filterCovers=True)
    
    while True:
        choices = [getChoiceString(track, localduration, artist, inclAlbum=True) for track in results]
        prompt = 'choose, or "hear#", "type", "more", "spotify:track:...", "ns" (notseenonspotify)'
        otherCommandsContext = (fullpathdir, search_str, tag, results, market)
        choice = getInputFromChoices(prompt, choices, callbackForChoiceTrack, otherCommandsContext)
        if choice[0] == -1 and choice[1]=='more':
            # the variable "results" has been updated; loop again
            continue
        elif choice[0] == -1:
            break
        else:
            tag.setLink(results[choice[0]]['uri'])
            tag.save()
            break

def getArtistFromAlbumid(albumid):
    id = spotipyconn()._get_id('album', 'spotify:album:52NFKuYav3gArQgbsxiHwS')
    results = spotipyconn()._get('albums/' + id + '/tracks/?offset=0&limit=1')
    if results and len(results['items']):
        return ';; '.join((artist['name'] for artist in results['items'][0]['artists']))
    else:
        return '(could not get artist)'
    
def linkspotifyperalbum(market, fullpathdir, tagsAll, parsedNamesAll):
    tags = []
    parsedNames = []
    # filter out .urls and also check for existing links
    for tag, parsed in zip(tagsAll, parsedNamesAll):
        if not tag.short.endswith('.url'):
            tags.append(tag)
            parsedNames.append(parsed)
            if 'spotify:track:' in tag.getLink():
                if not getInputBool('this will overwrite existing spotify link for '+tag.short+', continue?'):
                    return
    
    album = parsedNames[0].album
    artist = parsedNames[0].artist
    search_str = unicode(artist + ' ' + album)
    results = runspotifysearch(market, search_str, type='album', limit=10, filterCovers=True)
    
    while True:
        estimatedalbumartists = [getArtistFromAlbumid(albumobj['id']) for albumobj in results]
        choices = [albumobj['name'] +' by "'+estimatedalbumartists[i]+'"' for i, albumobj in enumerate(results)]
        prompt = 'choose, or "type", "more", "spotify:album:...", "ns" (notseenonspotify)'
        otherCommandsContext = (fullpathdir, search_str, tags, results, market)
        choice = getInputFromChoices(prompt, choices, callbackForChoiceAlbum, otherCommandsContext)
        if choice[0] == -1 and choice[1]=='more':
            # the variable "results" has been updated; loop again
            continue
        elif choice[0] == -1:
            break
        else:
            if linkspotifyperalbumtracks(market, fullpathdir, tags, parsedNames, results[choice[0]]['uri'], estimatedalbumartists[choice[0]]):
                break
    
def linkspotifyperalbumtracks(market, fullpathdir, tags, parsedNames, albumid, estimatedalbumartist):
    tracks = getTracksRemoteAlbum(albumid.replace('spotify:album:',''), market)
    showDiscNums = any(track['disc_number'] not in (None,0,1) for track in tracks) \
        or any(parsed.discnumber not in (None,0,1) for parsed in parsedNames)
    mapNumToTrack = { '%02d_%02d'%(int(track['disc_number']), int(track['track_number'])) : track for track in tracks }
    tracks = getTracksRemoteAlbum(albumid, market)
    
    # first, just print the tracks
    trace('local:\n'+'\n'.join('%s %s'%(getStrLocalAudioFile(fullpathdir+'/'+tag.short, Bucket(title='', artist=parsed.artist), tag), tag.short) for parsed, tag in zip(parsedNames, tags)))
    trace('\n\nremote:\n'+getStrRemoteAlbum(tracks, estimatedalbumartist))
    
    # now, go one-by one for each file on disk
    for tag, parsed in zip(tags, parsedNames):
        ret = linkspotifyperalbumtrack(fullpathdir, tag, parsed, mapNumToTrack, estimatedalbumartist)
        if not ret: return False
    
    # tell linkspotifyperalbum that we completed all tracks
    return True
    
def linkspotifyperalbumtrack(fullpathdir, tag, parsed, mapNumToTrack, estimatedalbumartist):
    path = fullpathdir+'/'+tag.short
    localduration = get_audio_duration(path, tag)
    key = Bucket(key = '%02d_%02d'%(int(parsed.discnumber), int(parsed.tracknumber)))
    
    while True:
        trace('\n\nDo the local and remote songs match?')
        trace('local:\n %s %s'%(getStrLocalAudioFile(path, Bucket(title='', artist=parsed.artist), tag, localduration), tag.short))
        remoteTrack = mapNumToTrack.get(key.key, None)
        if remoteTrack:
            trace('remote:\n %s'%getChoiceString(remoteTrack, localduration, estimatedalbumartist, False))
        else:
            trace('remote:\n no track matches %s, consider entering another disc_track'%key.key)
        choices = ['try another album', 'looks correct']
        prompt = 'choose, or "cancel" to skip, "hear0", "hear1", disc#_track# like "01_01"'
        otherCommandsContext = (fullpathdir, tag, key, remoteTrack)
        choice = getInputFromChoices(prompt, choices, callbackForChoiceAlbumTrack, otherCommandsContext)
        if choice[0]==0:
            return False
        elif choice[0]==1:
            if not remoteTrack:
                continue
            tag.setLink(remoteTrack['uri'])
            tag.save()
            break
        elif choice[0]==-1 and choice[1] is not True:
            break
        # otherwise we updated key.key, re-enter loop
    return True

class RemoveRemasteredString(object):
    def __init__(self):
        self.regexp = re.compile(r' - [0-9][0-9][0-9][0-9] (- )?(Digital )?Remaster(ed)?')
        self.knownBad = [' - mono version', ' - Remastered Album Version', ' - REMASTERED',' - Remastered', 
            ' - Single Version (Mono)',' - Single Version (Stereo)',' - Single Version - Stereo',' - Mono Single Version',
            ' - Album Version (Mono)',' - Album Version (Stereo)',' - Album Version-Stereo',
            ' - Album Version',' - Single Version',
            ' (Mono Version)',' [Mono Version]', ' (Remastered)', ' [Remastered]', ' Version']
            
    def getProposedName(self, short):
        newshort = short
        newshort = self.regexp.sub('', newshort)
        for bad in self.knownBad: 
            newshort = newshort.replace(bad, '')
        
        return newshort
        
    def check(self, parentName, allShorts):
        for short in allShorts:
            lower = short.lower()
            if 'remaster' in lower or 'version' in lower: 
                trace(parentName)
                trace('disallowed word in '+ short)
                newshort = self.getProposedName(short)
                
                if newshort==short or not getInputBool(u'use proposed name '+newshort+'?'):
                    print 'could not automatically fix.'; 
                    askExplorer(parentName)
                    newshort = getInputString('type a new name?')
                    
                if newshort!=short:
                    files.move(parentName+'/'+short, parentName+'/'+newshort, False)
                    stopIfFileRenamed(True)

def isTagAcceptibleToBeMadeIntoShortcuts(fullpathdir, tag):
    return not tag.short.endswith('.url') and not tag.short.endswith('.flac') and \
        (tag.short.endswith('.mp3') or (tag.short.endswith('.m4a') and getFileBitrate(fullpathdir+'/'+tag.short) < 170)) and \
        not '.sv.' in tag.short and not '.movetosv.' in tag.short and not '.3.mp3' in tag.short and \
        'spotify:track:' in tag.getLink()

def startSpotifyFromM4a(s):
    assert getFieldForFile(s, False) != None, 'unknown file type'
    assert files.exists(s), 'file not found'
    
    obj = BnTagWrapper(s)
    spotifyUri = obj.getLink()
    if 'spotify:notfound' in spotifyUri:
        assert False, 'audio file explicitly marked as not in spotify'
    elif not spotifyUri:
        assert False, 'no link to spotify found in file'
    else:
        launchSpotifyUri(spotifyUri)

def startSpotifyFromM4aArgs(args):
    # catch all exceptions; script output shown in a cmd window
    try:
        assertEq(3, len(args), 'wrong # of arguments')
        startSpotifyFromM4a(args[2])
    except:
        e = sys.exc_info()[1]
        alertGui(unicode(e))
        del e
        sys.exit(1)

def viewTagsFromM4aOrDirectory(path):
    def viewTagsFromFile(fullpath):
        if fullpath.lower().endswith('.url'):
            return getFromUrlFile(fullpath)
        elif getFieldForFile(fullpath, False):
            return CoordMusicAudioMetadata(fullpath).getLink()
        else:
            return ''
            
    if files.isdir(path):
        trace('Spotify links in', path)
        for full, short in files.listfiles(path):
            trace(short, viewTagsFromFile(full))
    else:
        trace('Spotify links in', files.getparent(path))
        trace(files.getname(path), viewTagsFromFile(path))
            

