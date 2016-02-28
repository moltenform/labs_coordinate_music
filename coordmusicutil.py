import sys
from ben_python_common import *
from coordmusicuserconfig import *
from easypythonmutagen import EasyPythonMutagen
   
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
        self.short = files.getname(filename)
        self.ext = files.getext(filename)
    
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
            except KeyError, mutagen.easymp4.EasyMP4KeyError:
                return default
            
        if fieldname == 'tracknumber' and '/' in ret:
            ret = ret.split('/')[0]
            
        return ret
        
    def set(self, fieldname, val):
        fieldname = self.normalizeFieldname(fieldname)
        if isinstance(val, int):
            val = str(val)
        EasyPythonMutagen.set(self, fieldname, val)

def get_audio_duration(filename, obj=None):
    if filename.lower().endswith('.wav'):
        # rough estimate, doesn't take metadata into account
        sz = files.getsize(filename)
        channels, bits, freq = 2, 16, 44100
        sz /= (1.0 * channels * (bits / 8.0))
        length = sz / freq
        return length
    else:
        import easypythonmutagen
        return easypythonmutagen.get_audio_duration(filename, obj)
    
def stampM4a(filename, spotifyurl, onlyIfNotAlreadySet=False):
    obj = CoordMusicAudioMetadata(filename)
    if not onlyIfNotAlreadySet or not obj.getLink():
        obj.setLink(spotifyurl)
    obj.save()
    
def m4aToUrl(directory, short, obj, replaceMarkersInName=True, softDelete=True):
    newname = files.splitext(short)[0]
    if replaceMarkersInName:
        newname = newname.replace(' (v)', '').replace(' (vv)', '')
    newname = directory + '/' + newname + '.url'
    link = obj.getLink()
    assertTrue(link and 'spotify:' in link and 'notfound' not in link,
        'm4aToUrl needs valid spotify link' + directory + short)
    
    writeUrlFile(newname, obj.getLink())
    if softDelete:
        softDeleteFile(directory + '/' + short)
    else:
        files.delete(directory + '/' + short)
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
            return
            
    try:
        sEscaped = s.replace('%', '{%}').replace('^', '{^}').replace('+', '{+}')
        window = app.top_window_()
        time.sleep(0.8)
        window.TypeKeys('^l')
        time.sleep(0.8)
        window.TypeKeys(sEscaped, with_spaces=True)
        time.sleep(0.1)
    except pywinauto.WindowNotFoundError, pywinauto.application.AppNotConnected:
        trace('exception thrown, ', sys.exc_info()[1])
    
def launchSpotifyUri(uri):
    if not uri or uri == 'spotify:notfound':
        trace('cannot start uri', str(uri))
        return
    assert uri.startswith('spotify:track:')
    assert all(c == '#' or c == ':' or c.isalnum() for c in uri) and len(uri) < 50
    if sys.platform == 'win32':
        import subprocess
        args = ['start', uri]
        subprocess.Popen(args, shell=True)
    else:
        url = 'https://open.spotify.com/track/' + uri.replace('spotify:track:', '')
        files.openUrl(url)

def launchMediaPlayer(path):
    mplayer = getMediaPlayer()
    files.runWithoutWaitUnicode([mplayer, path])
    
def launchGoogleQuery(query):
    assert '/' not in query and '\\' not in query and '^' not in query and '%' not in query and ':' not in query
    files.openUrl('http://google.com/search?q=' + query)

def getTestMediaLocation():
    return './test'

def getTestTempLocation():
    import tempfile
    return tempfile.gettempdir() + '/test_music_coordination'
    
def getFormattedDuration(seconds, showMilliseconds=False):
    if not seconds and seconds != 0:
        return ''
    if showMilliseconds:
        milli = int(seconds * 1000)
        return '%02d:%02d:%03d'%(int(seconds) // 60, int(seconds) % 60, milli % 1000)
    else:
        return '%02d:%02d'%(int(seconds) // 60, int(seconds) % 60)

def getDirChoice(dir, prompt):
    choices = [item[1] for item in files.listchildren(dir) if files.isdir(item[0])]
    choices.insert(0, 'All')
    if len(choices) == 1:
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
    for fullpath, short in files.recursedirs(dir, topdown=isTopDown):
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
        for fullpath, short in files.listfiles(fullpathdir):
            yield fullpath, short
