import re
import spotipy
import recurring_linkspotify
import recurring_music_to_url
import copy
from coordmusicutil import *
    
# directories with these words in the name have different properties:
# ' Compilation': within this directory, allow tracks to have tag for a different album
# ' Selections': do not require track numbers in this directory

Namestyle = SimpleEnum('Title|ArtistTitle|TrackTitle|TrackArtistTitle|DiscTrackTitle|DiscTrackArtistTitle'.split('|'))
def parseAFilename(short):
    name = bnsplitext(short)[0]
    name = name.replace(' (^)','').replace(' (v)','')
    res = Bucket(short=short, album=None, style = None, 
        discnumber = None, tracknumber = None, artist = None, title = None)
    
    tryRe = re.match('([0-9][0-9]) ([0-9][0-9]) (.*?) - (.*)', name)
    if tryRe:
        res.style = Namestyle.DiscTrackArtistTitle
        res.discnumber = int(tryRe.group(1))
        res.tracknumber = int(tryRe.group(2))
        res.artist = tryRe.group(3)
        res.title = tryRe.group(4)
        return res
    
    tryRe = re.match('([0-9][0-9]) ([0-9][0-9]) (.*)', name)
    if tryRe:
        res.style = Namestyle.DiscTrackTitle
        res.discnumber = int(tryRe.group(1))
        res.tracknumber = int(tryRe.group(2))
        res.title = tryRe.group(3)
        return res
    
    tryRe = re.match('([0-9][0-9]) (.*?) - (.*)', name)
    if tryRe:
        res.style = Namestyle.TrackArtistTitle
        res.tracknumber = int(tryRe.group(1))
        res.artist = tryRe.group(2)
        res.title = tryRe.group(3)
        return res
        
    tryRe = re.match('([0-9][0-9]) (.*)', name)
    if tryRe:
        res.style = Namestyle.TrackTitle
        res.tracknumber = int(tryRe.group(1))
        res.title = tryRe.group(2)
        return res
        
    tryRe = re.match('(.*?) - (.*)', name)
    if tryRe:
        res.style = Namestyle.ArtistTitle
        res.artist = tryRe.group(1)
        res.title = tryRe.group(2)
        return res
    
    res.style = Namestyle.Title
    res.title = name
    return res

def renderAFilename(res, short):
    rest = bnsplitext(short)[1]
    if res.style==Namestyle.Title:
        name = res.title
    elif res.style==Namestyle.ArtistTitle:
        name = '%s - %s'%(res.artist, res.title)
    elif res.style==Namestyle.TrackTitle:
        name = '%02d %s'%(res.tracknumber, res.title)
    elif res.style==Namestyle.TrackArtistTitle:
        name = '%02d %s - %s'%(res.tracknumber, res.artist, res.title)
    elif res.style==Namestyle.DiscTrackTitle:
        name = '%02d %02d %s'%(res.discnumber, res.tracknumber, res.title)
    elif res.style==Namestyle.DiscTrackArtistTitle:
        name = '%02d %02d %s - %s'%(res.discnumber, res.tracknumber, res.artist, res.title)
    
    if ' (^)' in short: name += ' (^)'
    if ' (v)' in short: name += ' (v)'
    name += rest
    return name
    
def bnsplitext(s):
    "splits file and extension, also treats .3.mp3 as .mp3, and any (12) annotation is not part of the name"
    name, ext = files.splitext(s)
   
    # divide test.3.mp3 into (test, 3.mp3)
    if name.endswith('.3'):
        name = name[0:-len('.3')]
        ext ='.3'+ext
    elif name.endswith('.sv'):
        name = name[0:-len('.sv')]
        ext ='.sv'+ext
    elif name.endswith('.movetosv'):
        name = name[0:-len('.movetosv')]
        ext ='.movetosv'+ext
    
    # divide test (12).mp3 into (test (12), mp3)
    if name[-1] == ')' and name[-2] in '0123456789' and name[-3] in '012' and name[-4] == '(' and name[-5] == ' ':
        ext = name[-5:]+ext
        name = name[0:-5]
    
    return name, ext
                        
class CheckFileExtensions(object):
    def __init__(self):
        self.goodExts = dict(url=1, mp3=1, m4a=1, flac=1, jpg=1, m4v=1, txt=1, png=1, flv=1, zip=1, rtf=1, lnk=1)
        
    def check(self, directory, short):
        spl = short.split('.')
        assertTrue(len(spl)>1, 'no extension found ', directory, short)
        ext = spl[-1]
        assertTrue(ext == ext.lower(), 'extension must be lowercase ', directory, short)
        assertTrue(ext in self.goodExts, 'unsupported file extension ', directory, short)
        return ext

def parseDirname(s):
    # input is "1999, Artist Name - The Album"
    m = re.match(r'([0-9][0-9][0-9][0-9], )?(.*? - )?(.*)', s)
    year = m.group(1).replace(', ','') if m.group(1) else None
    albumartist = m.group(2).replace(' - ','') if m.group(2) else None
    albumtitle = m.group(3)
    return year, albumartist, albumtitle

def fillFieldsFromContext(res, parentpath, dirsplit, helpers):
    if res.discnumber is None:
        res.discnumber = 1
    
    diryear, diralbumartist, diralbumtitle = parseDirname(dirsplit[-1])
    if res.artist is None:
        if len(dirsplit) <= len(helpers.splroot)+1:
            assertTrue(False, 'cannot infer Artist because not within artist directory ', parentpath)
        
        if diralbumartist != None:
            res.artist = diralbumartist
        elif diryear is None and diralbumartist is None:
            res.artist = dirsplit[-1]
        else:
            res.artist = dirsplit[-2]
    
    if res.album is None:
        if diryear is None and diralbumartist is None:
            pass
        else:
            res.album = diralbumtitle

def checkDuplicatedTrackNumbers(dir, allParsed):
    seen = dict()
    seenTitles = dict()
    for parsed in allParsed:
        if 'Track' in str(parsed.style):
            assertTrue(int(parsed.discnumber)!=0,'discnumber should not be 0.',dir, parsed.short)
            assertTrue(int(parsed.tracknumber)!=0,'tracknumber should not be 0.',dir, parsed.short)
            key = (int(parsed.discnumber), int(parsed.tracknumber))
            if key in seen:
                assertTrue(False, 'for file ',dir, parsed.short,' duplicate track numbers')
            if (parsed.artist, parsed.title) in seenTitles:
                assertTrue(False, 'for file ',dir, parsed.short,' duplicate artist+title')
            
            seen[key] = 1
            seenTitles[(parsed.artist, parsed.title)] = 1

def doStringsMatchForField(a, b, field):
    "a is from filesystem, b is from id3tag"
    if a == b:
        return True
    a = unicode(a)
    b = unicode(b)
    if a==safefilename(b) or a==removeCharsFlavor1(b) or a==removeCharsFlavor2(b):
        return True
    if field=='tracknumber' or field=='discnumber':
        try:
            if a!=None and b!=None and int(a)==int(b):
                return True
        except ValueError:
            pass
    elif field=='title':
        a = a.replace(' (^)','').replace(' (v)','').replace(' (vv)','')
        b = b.rstrip('!')
        return doStringsMatchForField(a, b, None)
    return False

def checkDeleteUrlsInTheWayOfM4as(fullpathdir, shorts):
    changedAtLeastOne = False
    for short in shorts:
        if short.endswith('.url'):
            filem4a = fullpathdir+'/'+files.splitext(short)[0]+'.m4a'
            if files.exists(filem4a):
                trace('Keeping m4a in favor of url', short)
                softDeleteFile(fullpathdir+'/'+short)
                changedAtLeastOne = True
    
    stopIfFileRenamed(changedAtLeastOne)

def checkForLowBitratesFile(fullpathdir, bitrate, tag):
    if '.sv.' in tag.short or '.movetosv.' in tag.short:
        return None
    if ' (vv)' in tag.short:
        return 'makeurl'
    if bitrate < 19 and tag.short.endswith('.m4a'):
        trace('automatically deleting low bitrate file ', fullpathdir, tag.short)
        return 'delete'
    if bitrate < 27 and tag.short.endswith('.m4a'):
        trace('automatically urling low bitrate file ', fullpathdir, tag.short)
        return 'makeurl'
    if bitrate < 29 or ' (v)' in tag.short:
        trace(fullpathdir, tag.short)
        choice = getInputFromChoices('file has low bitrate (%f)'%bitrate, ['remove', 'make url'])
        if choice[0]==0: return 'delete'
        if choice[0]==1: return 'makeurl'

def checkForLowBitrates(fullpathdir, tags):
    changedAtLeastOne = False
    for tag in tags:
        if tag.short.endswith('.url'):
            continue
        
        bitrate = getFileBitrate(fullpathdir+'/'+tag.short, tag)
        action = checkForLowBitratesFile(fullpathdir, bitrate, tag)
        if action=='delete':
            softDeleteFile(fullpathdir +'/'+ tag.short)
            changedAtLeastOne = True
        elif action=='makeurl':
            # m4aToUrl will automatically remove and ' (vv)' ' (v)' in filename
            m4aToUrl(fullpathdir, tag.short, tag)
            changedAtLeastOne = True
        elif action != None:
            assert False, 'unknown action '+action
            
    stopIfFileRenamed(changedAtLeastOne)
        
def checkFilenameIrregularitiesLookForInconsistency(fullpathdir, shorts):
    changedAtLeastOne = False
    countDashes = len(fullpathdir.split(' - '))-1
    assertTrue(countDashes <= 1, 'name has too many dashes',fullpathdir)
    
    bAtLeastOneHasArtist = False
    bAtLeastOneNoArtist = False
    for short in shorts:
        countDashes = len(short.split(' - '))-1
        assertTrue(countDashes <= 1, 'name has too many dashes', fullpathdir, short)
        assertTrue((len(fullpathdir) + len(short))<180, 'name is dangerously long', fullpathdir, short)
        
        bAtLeastOneHasArtist |= countDashes == 1
        bAtLeastOneNoArtist |= countDashes == 0
        if u'\u2013' in short: #em-dash
            newname = short.replace(u'\u2013', u'-')
            if askRename(fullpathdir, short, newname):
                changedAtLeastOne = True
                
    return changedAtLeastOne, bAtLeastOneHasArtist and bAtLeastOneNoArtist
                
def checkFilenameIrregularities(fullpathdir, shorts):
    changedAtLeastOne, isInconsistent = checkFilenameIrregularitiesLookForInconsistency(fullpathdir, shorts)
    
    if isInconsistent:
        trace('in directory', fullpathdir, 'some files have dash and some do not.')
        for short in shorts:
            if ' - ' in short:
                first, second = short.split(' - ')
                proposednames = [first+' ('+bnsplitext(second)[0]+')'+bnsplitext(second)[1],
                    first+', '+second,
                    first+' '+second]
                choice = getInputFromChoices('choose a new name:', proposednames)
                if choice >= 0:
                    files.move(parentName +'/'+ short, parentName +'/'+ proposednames[choice[0]])
                    changedAtLeastOne = True
    
    stopIfFileRenamed(changedAtLeastOne)
    
def checkUrlContents(fullpathdir, shorts):
    for short in shorts:
        if short.endswith('.url'):
            url = getFromUrlFile(fullpathdir+'/'+short)
            assertTrue(url, 'could not retrieve url', fullpathdir, short)
            assertTrue(not ':notfound' in url, 'must point to location', fullpathdir, short)
            assertTrue(not ':local' in url, 'local shortcuts disallowed.', fullpathdir, short)
            assertTrue(not 'boinjyboing' in url, 'user shortcuts disallowed', fullpathdir, short)

def checkStyleConsistency(fullpathdir, parsedNames):
    seenFirst = parsedNames[0]
    for parsed in parsedNames:
        assertTrue(parsed.style==seenFirst.style, 'in dir %s file %s has style %s but file %s has style %s' %
            (fullpathdir, seenFirst.short, seenFirst.style, parsed.short, parsed.style))

def getNewnameFromTag(parsed, field, fromFilename, fromTag):
    parsedProposed = copy.deepcopy(parsed)
    if fromTag is None:
        newval = '(None)'
    elif isinstance(fromTag, int):
        newval = fromTag
    else:
        newval = safefilename(fromTag)
    if 'number' in field and not isinstance(newval, int):
        newval = newval.split('-')[0].split('/')[0]
        try: newval = int(newval)
        except ValueError: newval = 0

    object.__setattr__(parsedProposed, field, newval)
    return renderAFilename(parsedProposed, parsedProposed.short)

def checkTagAndNameConsistency(fullpathdir, dirsplit, tag, parsed, userAllowsBulkSet):
    fields = ['album', 'discnumber', 'tracknumber', 'artist', 'title']
    optionalFields = ['album', 'tracknumber']
    needSave = False
    if tag.short.endswith('.url'):
        return
    for field in fields:
        fromFilename = object.__getattribute__(parsed, field)
        fromTag = tag.get(field)
        if not fromFilename and field in optionalFields:
            continue
        if not fromFilename and not fromTag and not field in optionalFields:
            assertTrue(False, 'file',fullpathdir,tag.short,'could not infer value for field',field)
        if not doStringsMatchForField(fromFilename, fromTag, field):
            # the Compilation keyword allows files with different album tags to coexist in the same directory.
            if field=='album' and fromTag != None and ' Compilation' in dirsplit[-1]:
                continue
                
            bulkSetValue = userAllowsBulkSet.get((field, fromTag, fromFilename), None)
            if bulkSetValue != None and (field=='album' or field=='discnumber' or field=='artist'):
                trace('file',fullpathdir,tag.short,'setting tag based on bulkset',field,fromFilename,bulkSetValue)
                tag.set(field, bulkSetValue)
                needSave = True
            else:
                trace('for file %s/%s,\n field %s,\nfilename says "%s"\ntag says "%s"'%(fullpathdir,tag.short,field,fromFilename,fromTag))
                proposedNameFromTag = getNewnameFromTag(parsed, field, fromFilename, fromTag)
                
                choices = ['set from filename (%s=%s)'%(field, fromFilename), 
                    'bulk set from filename (%s=%s only for this album+field)'%(field, fromFilename)]
                if proposedNameFromTag != parsed.short:
                    choices.append('set filename from tag (%s)'%proposedNameFromTag)
                choice = getInputFromChoices('', choices)
                if choice[0]==0 or choice[0]==1:
                    tag.set(field, fromFilename)
                    needSave = True
                if choice[0]==1:
                    userAllowsBulkSet[(field, fromTag, fromFilename)] = fromFilename
                if choice[0]==2:
                    files.move(fullpathdir+'/'+tag.short, fullpathdir+'/'+proposedNameFromTag)
                    raise StopBecauseWeRenamedFile
    if needSave:
        tag.save()


def checkRequiredFieldsSet(fullpathdir, dirsplit, tags, parsedNames):
    requiredfields = ['album', 'artist', 'title', 'discnumber']
    isAlbum = len(dirsplit[-1])>4 and dirsplit[-1][0:4].isdigit() and not ' Selections' in dirsplit[-1]
    if isAlbum:
        requiredfields.append('tracknumber')
    
    seenWithoutSpotify = False
    seenTracknumber = False
    for tag, parsed in zip(tags, parsedNames):
        if not isAlbum:
            assertTrue(not (tag.short[0:2].isdigit() and tag.short[2]==' '), 'file outside of album has tracknumber',fullpathdir,tag.short)
        if tag.short.endswith('.url'):
            continue
            
        seenTracknumber |= 'Track' in parsed.style
        seenWithoutSpotify |= not tag.getLink()
        for field in requiredfields:
            if not tag.get(field):
                spotlink = tag.getLink()
                if field=='album':
                    recurring_linkspotify.lookupAlbumForFile(fullpathdir+'/'+tag.short, tag,parsed, spotlink)
                    raise StopBecauseWeRenamedFile
                else:
                    assertTrue(False, 'missing required field',field,fullpathdir,tag.short)
    
    return seenTracknumber, seenWithoutSpotify

def checkFilenamesMain(fullpathdir, dirsplit, tags, helpers):
    if not len(tags):
        return

    shorts = [tag.short for tag in tags]
    checkDeleteUrlsInTheWayOfM4as(fullpathdir, shorts)
    checkForLowBitrates(fullpathdir, tags)
    checkFilenameIrregularities(fullpathdir, shorts)
    checkUrlContents(fullpathdir, shorts)
    helpers.removeRemasteredString.check(fullpathdir, shorts)
    
    userAllowsBulkSet = dict()
    parsedNames = [parseAFilename(short) for short in shorts]
    [fillFieldsFromContext(parsed, fullpathdir, dirsplit, helpers) for parsed in parsedNames]
    [checkTagAndNameConsistency(fullpathdir, dirsplit, tag, parsed, userAllowsBulkSet) for tag, parsed in zip(tags, parsedNames)]
    checkStyleConsistency(fullpathdir, parsedNames)
    checkDuplicatedTrackNumbers(fullpathdir, parsedNames)
    seenTracknumber, seenWithoutSpotify = checkRequiredFieldsSet(fullpathdir, dirsplit, tags, parsedNames)
    recurring_linkspotify.linkspotify(seenWithoutSpotify, fullpathdir, tags, parsedNames, seenTracknumber, helpers.market)
    helpers.music_to_url.go(fullpathdir, tags, parsedNames)

def goPerDirectory(fullpathdir, dirsplit, helpers):
    allshorts = files.listchildren(fullpathdir, filenamesOnly=True)
    tags = []
    seenOne = False
    for short in allshorts:
        seenOne = True
        path = fullpathdir + '/' + short
        if files.isfile(path):
            ext = helpers.checkFileExtensions.check(fullpathdir, short)
            if ext in helpers.extsCheckFilenames:
                if ext=='url':
                    tags.append(Bucket(short=short, ext=ext))
                else:
                    tags.append(BnTagWrapper(path))
                    tags[-1].short = short
    
    if not seenOne:
        if getInputBool('empty directories not allowed '+fullpathdir+' delete?'):
                files.rmdir(fullpathdir)

    checkFilenamesMain(fullpathdir, dirsplit, tags, helpers)

def getHelpers(root, market, enableSaveSpace):
    helpers = Bucket()
    helpers.checkFileExtensions = CheckFileExtensions()
    helpers.removeRemasteredString = recurring_linkspotify.RemoveRemasteredString()
    helpers.music_to_url = recurring_music_to_url.SaveDiskSpaceMusicToUrl(enableSaveSpace)
    helpers.extsCheckFilenames = dict(mp3=1,m4a=1,flac=1,url=1)
    helpers.splroot = root.replace('\\','/').split('/')
    helpers.market = market
    return helpers
        
# example: if root is ~/music, scope is c:/music/classic rock, and startingpoint is c:/music/classic rock/hendrix
# we'll go through c:/music/classic rock and process all directories that sort lower than c:/music/classic rock/hendrix
def mainCoordinate(scope=None, startingpoint=None, isTopDown = True, spotifyEnabled=True, market='US', enableSaveSpace=False):
    root = getMusicRoot()
    if not scope:
        scope = root
    if spotifyEnabled:
        trace('Spotify market set to %s.'%market)
        
    assertTrue(scope.startswith(root), 'scope %s must be within root %s'%(scope, root))
    assertTrue(not startingpoint or startingpoint.startswith(scope), 'startingpoint %s must be within scope %s'%(startingpoint, scope))
    
    reachedstartingpoint = False
    startingpointlower = startingpoint.lower() if startingpoint else None
    helpers = getHelpers(root, market, enableSaveSpace)
    for fullpathdir, pathshort in files.recursedirs(scope, topdown=isTopDown):
        # don't start until we've reached startingpoint
        fullpathdirlower = fullpathdir.lower()
        if not reachedstartingpoint:
            if fullpathdirlower==startingpointlower:
                reachedstartingpoint = True
            if startingpoint:
                continue
        
        # ignore anything under a 'lib' directory
        dirsplit = fullpathdir.replace('\\','/').split('/')
        if 'lib' in dirsplit:
            continue
        
        # we'll need a few passes through the directory in some cases
        while True:
            err = None
            try:
                goPerDirectory(fullpathdir, dirsplit, helpers)
            except StopBecauseWeRenamedFile:
                trace('we renamed a file; re-entering directory.')
                continue
            except (KeyboardInterrupt, IOError, OSError, AssertionError) as err:
                trace(err)
                choice = getInputFromChoices('encountered exception.', ['retry', 'next dir'])
                if choice[0] == -1: return #exit
                elif choice[0] == 0: continue #retry dir
                elif choice[0] == 1: break #go to next dir
                
            break
            