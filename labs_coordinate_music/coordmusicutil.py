# labs_coordinate_music
# Ben Fisher, 2016
# Released under the GNU General Public License version 3

import sys
import string
import re
import wave

from shinerainsevenlib.standard import *
from shinerainsevenlib.core import *

from labs_coordinate_music.coordmusicuserconfig import *
from labs_coordinate_music.easypythonmutagen import \
    EasyPythonMutagen, mutagen_get_audio_duration

# get_empirical_bitrate is used by files that import this module
from labs_coordinate_music.easypythonmutagen import get_empirical_bitrate  # noqa: F401

stricter_matching = True

def getFromUrlFile(filename):
    assert filename.endswith('.url') or filename.endswith('.URL')
    with open(filename) as f:
        for line in f:
            if line.startswith('URL='):
                line = line.strip()
                return line.split('URL=')[1]
                
def writeUrlFile(urlfilepath, link, extrainfo='', okOverwrite=False):
    assertTrue(okOverwrite or not files.exists(urlfilepath), 'already exists at ' + urlfilepath)
    with open(urlfilepath, 'w') as fout:
        fout.write('[InternetShortcut]\n')
        fout.write('URL=' + link + '\n')
        fout.write(extrainfo)
        
def getFieldForFile(s, throw=True):
    slower = s.lower()
    field = None
    if slower.endswith('.mp3'):
        field = 'website'
    elif slower.endswith('.m4a'):
        field = 'description'
    elif slower.endswith('.flac'):
        field = 'desc'
    elif throw:
        assert False, 'unexpected extension'
    return field
        
class CoordMusicAudioMetadata(EasyPythonMutagen):
    def __init__(self, filename):
        super(CoordMusicAudioMetadata, self).__init__(filename)
        self.linkfield = getFieldForFile(filename, False)
        self.short = files.getName(filename)
        self.ext = files.getExt(filename)
        self.fullFilename = filename
        self.preserveLastModTime = True
    
    def normalizeFieldname(self, fieldname):
        if fieldname == '%spotifylink%':
            fieldname = self.linkfield
        elif fieldname == 'track_number':
            fieldname = 'tracknumber'
        elif fieldname == 'disc_number':
            fieldname = 'discnumber'
        return fieldname
    
    def getLink(self):
        return self.get_or_default('%spotifylink%', '')
        
    def setLink(self, val):
        return self.set('%spotifylink%', val)
    
    def get(self, fieldname):
        if fieldname == 'discnumber' or fieldname == 'disc_number':
            return self.get_or_default('discnumber', 1, True)
        else:
            return self.get_or_default(fieldname, None, False)
        
    def get_or_default(self, fieldname, default, allowThrow=True):
        import mutagen
        fieldname = self.normalizeFieldname(fieldname)
        if fieldname == 'discnumber' and default is None:
            default = 1
        
        if not allowThrow:
            ret = EasyPythonMutagen.get(self, fieldname)
        else:
            try:
                ret = EasyPythonMutagen.get(self, fieldname)
            except (KeyError, mutagen.easymp4.EasyMP4KeyError) as exc:
                return default
            
        if fieldname == 'tracknumber' and '/' in ret:
            ret = ret.split('/')[0]
            
        return ret
        
    def set(self, fieldname, val):
        fieldname = self.normalizeFieldname(fieldname)
        if isinstance(val, int):
            val = str(val)
        EasyPythonMutagen.set(self, fieldname, val)
    
    def save(self):
        assertTrue(files.exists(self.fullFilename))
        prevModTime = files.getLastModTime(self.fullFilename, files.TimeUnits.Nanoseconds)
        super(CoordMusicAudioMetadata, self).save()
        if self.preserveLastModTime:
            files.setLastModTime(self.fullFilename, prevModTime, files.TimeUnits.Nanoseconds)

def get_audio_duration(filename, obj=None):
    if filename.lower().endswith('.wav'):
        with wave.open(filename, 'rb') as parsedWave:
            channels = parsedWave.getnchannels()
            assertTrue(channels in [1, 2], 'unsupported # of channels', filename)
            bytewidth = parsedWave.getsampwidth()
            assertTrue(bytewidth in [1, 2, 3], 'unsupported bytewidth', filename)
            freq = parsedWave.getframerate()
            assertTrue(freq in [44100, 48000, 44100 * 2, 48000 * 2], 'unsupported freq', filename)
            
            # just an estimate, doesn't take metadata into account
            bits = bytewidth * 8
            sz = files.getSize(filename)
            sz /= (1.0 * channels * (bits / 8.0))
            length = sz / freq
            return length
    else:
        return mutagen_get_audio_duration(filename, obj)

def stripMarkersFromFilename(s):
    # markers like (^) aren't truly part of the name
    s = s.replace(' (^)', '').replace(' (^^)', '')
    s = s.replace(' (v)', '').replace(' (vv)', '')
    if ' {} ' in s:
        return s.split(' {} ')[-1]
    
    return s

def reconstructMarkersFromFilename(new, old):
    if ' (^)' in old:
        new += ' (^)'
    if ' (^^)' in old:
        new += ' (^^)'
    if ' (v)' in old:
        new += ' (v)'
    if ' (vv)' in old:
        new += ' (vv)'

    if ' {} ' in old:
        mark = old.split(' {} ')[0]
        new = mark + ' {} ' + new
    
    return new

def stampM4a(filename, spotifyurl, onlyIfNotAlreadySet=False):
    obj = CoordMusicAudioMetadata(filename)
    if not onlyIfNotAlreadySet or not obj.getLink():
        obj.setLink(spotifyurl)
    obj.save()

def getSpotifyOrVideoUrlFromFile(obj):
    link = obj.getLink()
    if link and 'spotify:' in link and 'notfound' not in link:
        return link
    else:
        return videoUrlFromFile(obj.get_or_default('comment', ''))

def videoUrlFromFile(comment):
    if comment and len(comment) == 11 and not any(c in string.whitespace for c in comment):
        return 'https://www.youtube.com/watch?v=' + comment
    elif comment:
        reg = re.compile(r'\[([^ 	]{11})\]')
        for match in reg.finditer(comment):
            if match.group(1) and len(match.group(1)) == 11:
                return 'https://www.youtube.com/watch?v=' + match.group(1)
    return None

def m4aToUrl(directory, short, obj, replaceMarkersInName=True, softDelete=True):
    prevTime = files.getLastModTime(directory + '/' + short, files.TimeUnits.Nanoseconds)
    newname = files.splitExt(short)[0]
    if replaceMarkersInName:
        newname = newname.replace(' (v)', '').replace(' (vv)', '')
    newname = directory + '/' + newname + '.url'
    link = getSpotifyOrVideoUrlFromFile(obj)
    if link:
        writeUrlFile(newname, link)
    else:
        assertTrue(False, 'we are making\n%s' % (directory + '\\' + short) +
            '\n into a url, but no link to spotify or video found.')
    
    if softDelete:
        softDeleteFile(directory + '/' + short)
    else:
        files.delete(directory + '/' + short)
    files.setLastModTime(newname, prevTime, files.TimeUnits.Nanoseconds)
    return newname

def removeCharsFlavor1(s):
    s = s.replace(u'?', u'').replace(u'\\', u'-').replace(u'/', u'-').replace(u':', u'').replace(u'*', u'')
    return s.replace(u'"', u"").replace(u'<', u'').replace(u'>', u'').replace(u'|', u'')

def removeCharsFlavor2(s):
    s = s.replace(u'!', u'').replace(u'\\', u'-').replace(u'/', u'-').replace(u'\u2019', u'\'').replace(u'?', u'').replace(u'/', u'')
    return s.replace(u':', u'').replace(u'*', u'').replace(u'"', u"").replace(u'<', u'').replace(u'>', u'').replace(u'|', u'')

def _spotipyconnect():
    import spotipy
    import spotipy.util as sputil
    
    scope = 'playlist-modify-public'
    args = dict(client_id=getSpotifyClientID(), client_secret=getSpotifyClientSecret(), redirect_uri=getSpotifyCallbackUrl())
    if scope:
        args['scope'] = scope
    token = sputil.prompt_for_user_token(getSpotifyUsername(), **args)
    return spotipy.Spotify(auth=token)


g_spotipyObject = None
def spotipyconn():
    global g_spotipyObject
    if not g_spotipyObject:
        g_spotipyObject = _spotipyconnect()
    return g_spotipyObject

class StopBecauseWeRenamedFile(Exception):
    def __init__(self, value=None):
        self.value = value

    def __str__(self):
        return repr(self.value)
        
def stopIfFileRenamed(bNeedToStop):
    if bNeedToStop:
        raise StopBecauseWeRenamedFile

def getTracksFromPlaylist(sp, plid):
    tracksRet = []
    tracks = []
    results = sp.user_playlist(getSpotifyUsername(), plid, fields="tracks,next")
    tracks = results['tracks']
    tracksRet.extend(tracks['items'])
    while tracks['next']:
        tracks = sp.next(tracks)
        tracksRet.extend(tracks['items'])
        
    return [track['track'] for track in tracksRet]
        
def askRename(parentName, short1, short2, prompt=''):
    if short1 == short2:
        return True
    trace(prompt, ' in directory', parentName)
    if getInputBool('rename %s to %s?'%(short1, short2)):
        files.move(parentName + '/' + short1, parentName + '/' + short2, False)
        return True
    return False
    
def askExplorer(dir):
    if getInputBool('open explorer window?'):
        files.openDirectoryInExplorer(dir)
               
def typeIntoSpotifySearch(s):
    try:
        import pywinauto
        import time
    except ImportError:
        trace('pywinauto is not installed; to enable this feature first install the Python package pywinauto')
        return
        
    app = pywinauto.Application()
    try:
        app.connect(title_re="Spotify")
    except pywinauto.WindowNotFoundError:
        import subprocess
        subprocess.Popen(['start', 'spotify:'], shell=True)
        if getInputFromChoices('please wait for spotify to open', ['Spotify is open'])[0] == 0:
            return typeIntoSpotifySearch(s)
            
    try:
        sEscaped = s.replace('%', '{%}').replace('^', '{^}').replace('+', '{+}')
        window = app.top_window_()
        time.sleep(0.8)
        window.TypeKeys('^l')
        time.sleep(0.8)
        window.TypeKeys(sEscaped, with_spaces=True)
        time.sleep(0.1)
    except (pywinauto.WindowNotFoundError, pywinauto.application.AppNotConnected) as exc:
        trace('exception thrown, ', sys.exc_info()[1])
    
def launchSpotifyUri(uri):
    if not uri or uri == 'spotify:notfound':
        trace('cannot start uri', str(uri))
        return False
    if uri.startswith('https://www.youtube.com') or uri.startswith('https://youtube.com'):
        files.openUrl(uri)
        return True
    assert uri.startswith('spotify:track:')
    assert all(c == '#' or c == ':' or c.isalnum() for c in uri) and len(uri) < 50
    if sys.platform.startswith('win'):
        import subprocess
        args = ['start', uri]
        subprocess.Popen(args, shell=True)
        return True
    else:
        url = 'https://open.spotify.com/track/' + uri.replace('spotify:track:', '')
        files.openUrl(url)
        return True

def isInSpotifyMarket(track, market=None):
    if not market:
        market = getSpotifyGeographicMarketName()
    if 'available_markets' in track:
        return market in track['available_markets']
    else:
        is_playable = track.get('is_playable', True)
        is_local = track.get('is_local', False)
        return is_playable and not is_local

def launchMediaPlayer(path):
    mplayer = getMediaPlayer()
    files.runWithoutWaitUnicode([mplayer, path])
    
def launchGoogleQuery(query):
    assert '/' not in query and '\\' not in query and '^' not in query and '%' not in query and ':' not in query
    files.openUrl('http://google.com/search?q=' + query)

def getFormattedDuration(seconds, showMilliseconds=False):
    if not seconds and seconds != 0:
        return ''
    if showMilliseconds:
        milli = int(seconds * 1000)
        return '%02d:%02d:%03d'%(int(seconds) // 60, int(seconds) % 60, milli % 1000)
    else:
        return '%02d:%02d'%(int(seconds) // 60, int(seconds) % 60)

def getDirChoice(dir, prompt):
    if not files.exists(dir):
        dir = input('Please enter the path of the folder: ')
    
    assertTrue(files.exists(dir), 'Path not found.')
    choices = [item[1] for item in files.listChildren(dir) if files.isDir(item[0])]
    choices.insert(0, 'All')
    if len(choices) == 1 and choices[0] != 'All':
        return choices[0]
    ret = getInputFromChoices(prompt, choices)
    if ret[0] == -1:
        return None
    else:
        return dir if ret[1] == 'All' else files.join(dir, ret[1])

def getScopedRecurseDirs(dir, filterOutLib=False, isTopDown=True):
    dir = getDirChoice(dir, 'filter to files under which directory?')
    if not dir:
        return
    
    startingPlace = getDirChoice(dir, 'begin at which directory?')
    if not startingPlace:
        return
        
    startingPlace = startingPlace.lower()
    reachedStartingPlace = startingPlace == dir.lower()
    lib = files.sep + 'lib' + files.sep
    for fullpath, short in files.recurseDirs(dir, topdown=isTopDown):
        # don't start until we've reached startingpoint
        fullpathLower = fullpath.lower()
        if not reachedStartingPlace:
            if fullpathLower == startingPlace:
                reachedStartingPlace = True
            if startingPlace:
                continue
        
        if not filterOutLib or lib not in fullpathLower + files.sep:
            yield fullpath, short
        
def getScopedRecurseFiles(dir, filterOutLib=False, isTopDown=True):
    for fullpathdir, shortdir in getScopedRecurseDirs(dir, filterOutLib=filterOutLib, isTopDown=isTopDown):
        for fullpath, short in files.listFiles(fullpathdir):
            yield fullpath, short

