import sys
from ben_python_common import *
from coordmusicuserconfig import *
from easypythonmutagen import EasyPythonMutagen, get_audio_duration, get_empirical_bitrate
   
def getFromUrlFile(filename):
    assert filename.endswith('.url') or filename.endswith('.URL')
    with open(filename) as fiter:
        for line in fiter:
            if line.startswith('URL='): 
                line = line.strip()
                return line.split('URL=')[1]
                
def writeUrlFile(urlfilepath, link, extrainfo = '', okOverwrite=False):
    assertTrue(okOverwrite or not files.exists(urlfilepath), 'already exists at '+urlfilepath)
    with open(urlfilepath, 'w') as fout:
        fout.write('[InternetShortcut]\n')
        fout.write('URL='+link+'\n')
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
        if fieldname== '%spotifylink%':
            fieldname = self.linkfield 
        elif fieldname== 'track_number':
            fieldname = 'tracknumber'
        elif fieldname== 'disc_number':
            fieldname = 'discnumber'
        return fieldname
    
    def getLink(self):
        return self.get_or_default('%spotifylink%', None)
        
    def setLink(self, val):
        return self.set('%spotifylink%', val)
    
    def get(self, fieldname):
        if fieldname=='discnumber' or fieldname=='disc_number':
            return self.get_or_default('discnumber', 1, False)
        else:
            return self.get_or_default(fieldname, None, True)
        
    def get_or_default(self, fieldname, default, allowThrow=False):
        import mutagen
        fieldname = self.normalizeFieldname(fieldname)
        catchable = str if allowThrow else (KeyError, mutagen.easymp4.EasyMP4KeyError)
        
        try:
            ret = EasyPythonMutagen.get(self, fieldname)
        except catchable:
            return default
            
        if fieldname=='tracknumber' and '/' in ret:
            ret = ret.split('/')[0]
            
        return ret
        
    def set(self, fieldname, val):
        fieldname = self.normalizeFieldname(fieldname)
        if isinstance(val, int):
            val = str(val)
        EasyPythonMutagen.set(self, fieldname, val)

def getWavDuration(filename):
    if filename.lower().endswith('.wav'):
        # rough estimate, doesn't take metadata into account
        sz = files.getsize(filename)
        channels, bits, freq = 2, 16, 44100
        sz /= (1.0 * channels * (bits/8.0))
        length = sz / freq
        return length
    else:
        assert False, 'unexpected extension'
    
def stampM4a(filename, spotifyurl, onlyIfNotAlreadySet=False):
    obj = CoordMusicAudioMetadata(filename)
    if not onlyIfNotAlreadySet or not obj.getLink():
        obj.setLink(spotifyurl)
    obj.save()
    
def m4aToUrl(directory, short, obj, replaceMarkersInName=True, softDelete=True):
    newname = files.splitext(short)[0]
    if replaceMarkersInName:
        newname = newname.replace(' (v)', '').replace(' (vv)', '')
    newname = directory+'/'+newname+'.url'
    link = obj.getLink()
    assertTrue(link and 'spotify:' in link and 'notfound' not in link, 
        'm4aToUrl needs valid spotify link' +directory + short)
    
    writeUrlFile(newname, obj.getLink())
    if softDelete:
        softDeleteFile(directory+'/'+short)
    else:
        files.delete(directory+'/'+short)
    return newname

def m4aToUrlWithBitrate(directory, short, obj):
    field = getFieldForFile(short)
    locbitrate = int(getFileBitrate(directory+'/'+short, obj))
    locbitrateOut = 1
    if locbitrate<=120: locbitrateOut = 10
    elif locbitrate<=128+15: locbitrateOut = 12
    elif locbitrate<=144+8: locbitrateOut = 14
    elif locbitrate<=160+8: locbitrateOut = 16
    elif locbitrate<=176+8: locbitrateOut = 17
    elif locbitrate<=192+8: locbitrateOut = 19
    elif locbitrate<=224+8: locbitrateOut = 22
    elif locbitrate<=256+8: locbitrateOut = 25
    elif locbitrate<=288+8: locbitrateOut = 28
    else: locbitrateOut = 30
    while True:
        inp = getInputString('quality marker of "%d" look good, or enter another or bad for none.'%locbitrateOut, False)
        if inp=='y':
            break
        elif all(c in '0123456789' for c in inp):
            locbitrateOut = int(inp)
            break
        elif inp=='bad':
            locbitrateOut = 'bad'
            break
        elif inp=='no' or inp=='n':
            return
    newname = directory+'/'+files.splitext(short)[0]
    newname += (' (%d).url'%locbitrateOut) if locbitrateOut!='bad' else '.url'
    writeUrlFile(newname, obj[field][0])
    try:
        softDeleteFile(directory+'/'+short)
    except WindowsError:
        alert('you need to close the file first!')
        softDeleteFile(directory+'/'+short)

def removeCharsFlavor1(s):
    return s.replace(u'?', u'').replace(u'\\', u'').replace(u'/', u'').replace(u':', u'').replace(u'*', u'').replace(u'"', u"").replace(u'<', u'').replace(u'>', u'').replace(u'|', u'')

def removeCharsFlavor2(s):
    return s.replace(u'!', u'').replace(u'\\', u'-').replace(u'/', u'-').replace(u'\u2019', u'\'').replace(u'?', u'').replace(u'/', u'').replace(u':', u'').replace(u'*', u'').replace(u'"', u"").replace(u'<', u'').replace(u'>', u'').replace(u'|', u'')

def spotipyconnect():
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
        g_spotipyObject = spotipyconnect()
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
    s = u''
    tracksRet = []
    tracks = []
    username = 'boinjyboing'
    results = sp.user_playlist(username, plid, fields="tracks,next")
    tracks = results['tracks']
    tracksRet.extend(tracks['items'])
    while tracks['next']:
        tracks = sp.next(tracks)
        tracksRet.extend(tracks['items'])
        
    return [track['track'] for track in tracksRet]
        
def askRename(parentName, short1, short2, prompt=''):
    if short1==short2:
        return True
    trace(prompt, ' in directory', parentName)
    if getInputBool('rename %s to %s?'%(short1, short2)):
        files.move(parentName+'/'+short1,parentName+'/'+short2, False)
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
        app.connect(title_re = "Spotify")
    except pywinauto.WindowNotFoundError:
        import subprocess
        subprocess.Popen(['start', 'spotify:'], shell=True)
        if getInputFromChoices('please wait for spotify to open', ['Spotify is open'])[0]==0:
            return typeIntoSpotifySearch(s)
            return
            
    try:
        sEscaped = s.replace('%', '{%}').replace('^', '{^}').replace('+', '{+}')
        window = app.top_window_(); time.sleep(0.8)
        window.TypeKeys('^l'); time.sleep(0.8)
        window.TypeKeys(sEscaped, with_spaces=True); time.sleep(0.1)
    except pywinauto.WindowNotFoundError, pywinauto.application.AppNotConnected:
        trace('exception thrown, ',sys.exc_info()[1])
    
def launchSpotifyUri(suri):
    import subprocess
    assert suri.startswith('spotify:track:')
    assert all(c=='#' or c==':' or c.isalnum() for c in suri)
    args = ['start', suri]
    subprocess.Popen(args, shell=True)

def launchMediaPlayer(path):
    import subprocess
    mplayer = getMediaPlayer()
    subprocess.Popen([mplayer, path], shell=False)


    
    