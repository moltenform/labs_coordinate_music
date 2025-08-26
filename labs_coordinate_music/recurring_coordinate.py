# labs_coordinate_music
# Ben Fisher, 2016
# Released under the GNU General Public License version 3

import re
import copy
import codecs
import time
import enum

from labs_coordinate_music.coordmusicutil import *
from labs_coordinate_music.recurring_music_to_url import SaveDiskSpaceMusicToUrl
from labs_coordinate_music.recurring_linkspotify import \
    lookupAlbumForFile, linkspotify, RemoveRemasteredString, \
    enableAutoTagFromFilenameForRecentFiles

# directories with these words in the name have different properties:
# ' Compilation': within this directory, allow tracks to have tag for a different album
# ' Selections': do not require track numbers in this directory

class NameStyle(enum.StrEnum):
    @staticmethod
    def _generate_next_value_(name, _start, _count, _last_values):
        return name
    
    Title = enum.auto()
    ArtistTitle = enum.auto()
    TrackTitle = enum.auto()
    TrackArtistTitle = enum.auto()
    DiscTrackTitle = enum.auto()
    DiscTrackArtistTitle = enum.auto()

def parseAFilename(short):
    name = bnsplitext(short)[0]
    name = stripMarkersFromFilename(name)
    class ParseAFilenameResults:
        def __init__(self, short=None, album=None, style=None,
                discnumber=None, tracknumber=None, artist=None, title=None):
            self.short = short
            self.album = album
            self.style = style
            self.discnumber = discnumber
            self.tracknumber = tracknumber
            self.artist = artist
            self.title = title
    
    res = ParseAFilenameResults(short=short, album=None, style=None,
        discnumber=None, tracknumber=None, artist=None, title=None)
    
    tryRe = re.match('([0-9][0-9]) ([0-9][0-9]) (.*?) - (.*)', name)
    if tryRe:
        res.style = NameStyle.DiscTrackArtistTitle
        res.discnumber = int(tryRe.group(1))
        res.tracknumber = int(tryRe.group(2))
        res.artist = tryRe.group(3)
        res.title = tryRe.group(4)
        return res
    
    tryRe = re.match('([0-9][0-9]) ([0-9][0-9]) (.*)', name)
    if tryRe:
        res.style = NameStyle.DiscTrackTitle
        res.discnumber = int(tryRe.group(1))
        res.tracknumber = int(tryRe.group(2))
        res.title = tryRe.group(3)
        return res
    
    tryRe = re.match('([0-9][0-9]) (.*?) - (.*)', name)
    if tryRe:
        res.style = NameStyle.TrackArtistTitle
        res.tracknumber = int(tryRe.group(1))
        res.artist = tryRe.group(2)
        res.title = tryRe.group(3)
        return res
        
    tryRe = re.match('([0-9][0-9]) (.*)', name)
    if tryRe:
        res.style = NameStyle.TrackTitle
        res.tracknumber = int(tryRe.group(1))
        res.title = tryRe.group(2)
        return res
        
    tryRe = re.match('(.*?) - (.*)', name)
    if tryRe:
        res.style = NameStyle.ArtistTitle
        res.artist = tryRe.group(1)
        res.title = tryRe.group(2)
        return res
    
    res.style = NameStyle.Title
    res.title = name
    return res

def renderAFilename(res, short):
    rest = bnsplitext(short)[1]
    if res.style == NameStyle.Title:
        name = res.title
    elif res.style == NameStyle.ArtistTitle:
        name = '%s - %s'%(res.artist, res.title)
    elif res.style == NameStyle.TrackTitle:
        name = '%02d %s'%(res.tracknumber, res.title)
    elif res.style == NameStyle.TrackArtistTitle:
        name = '%02d %s - %s'%(res.tracknumber, res.artist, res.title)
    elif res.style == NameStyle.DiscTrackTitle:
        name = '%02d %02d %s'%(res.discnumber, res.tracknumber, res.title)
    elif res.style == NameStyle.DiscTrackArtistTitle:
        name = '%02d %02d %s - %s'%(res.discnumber, res.tracknumber, res.artist, res.title)
    
    name = reconstructMarkersFromFilename(name, short)
    name += rest
    return name
    
def bnsplitext(s):
    "splits file and extension, also treats .3.mp3 as .mp3, and any (12) annotation is not part of the name"
    name, ext = files.splitExt(s)
   
    # divide test.3.mp3 into (test, 3.mp3)
    if name.endswith('.3'):
        name = name[0:-len('.3')]
        ext = '.3' + ext
    elif name.endswith('.sv'):
        name = name[0:-len('.sv')]
        ext = '.sv' + ext
    elif name.endswith('.movetosv'):
        name = name[0:-len('.movetosv')]
        ext = '.movetosv' + ext
    
    # divide test (12).mp3 into (test (12), mp3)
    if name[-1] == ')' and name[-2] in '0123456789' and name[-3] in '012' and name[-4] == '(' and name[-5] == ' ':
        ext = name[-5:] + ext
        name = name[0:-5]
    
    return name, ext
                        
class CheckFileExtensions(object):
    def __init__(self):
        self.goodExts = dict(url=1, mp3=1, m4a=1, flac=1, m4v=1, txt=1)
        
    def check(self, directory, short):
        spl = short.split('.')
        assertTrue(len(spl) > 1, 'no extension found ', directory, short)
        ext = spl[-1]
        assertTrue(ext == ext.lower(), 'extension must be lowercase ', directory, short)
        assertTrue(ext in self.goodExts or alsoAllowThisFileExtensionInMusicDirectory(ext),
            'unsupported file extension ', directory, short)
        
        return ext

def parseDirname(s):
    # input is "1999, Artist Name - The Album"
    m = re.match(r'([0-9][0-9][0-9][0-9], )?(.*? - )?(.*)', s)
    year = m.group(1).replace(', ', '') if m.group(1) else None
    albumartist = m.group(2).replace(' - ', '') if m.group(2) else None
    albumtitle = m.group(3)
    return year, albumartist, albumtitle

def fillFieldsFromContext(res, parentpath, dirsplit, helpers):
    if res.discnumber is None:
        res.discnumber = 1
    
    diryear, diralbumartist, diralbumtitle = parseDirname(dirsplit[-1])
    if res.artist is None:
        if len(dirsplit) <= len(helpers.splroot) + 1:
            assertTrue(False, 'cannot infer Artist because not within artist directory ', parentpath)
        
        if diralbumartist is not None:
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
            assertTrue(int(parsed.discnumber) != 0, 'discnumber should not be 0.', dir, parsed.short)
            assertTrue(int(parsed.tracknumber) != 0, 'tracknumber should not be 0.', dir, parsed.short)
            key = (int(parsed.discnumber), int(parsed.tracknumber))
            if key in seen:
                assertTrue(False, 'for file ', dir, parsed.short, ' duplicate track numbers')
            if (parsed.artist, parsed.title) in seenTitles:
                assertTrue(False, 'for file ', dir, parsed.short, ' duplicate artist+title')
            
            seen[key] = 1
            seenTitles[(parsed.artist, parsed.title)] = 1

def doStringsMatchForField(a, b, field):
    "a is from filesystem, b is from id3tag"
    if a == b:
        return True
    a = ustr(a)
    b = ustr(b)
    if a == toValidFilename(b) or a == removeCharsFlavor1(b) or a == removeCharsFlavor2(b):
        return True
    if field == 'tracknumber' or field == 'discnumber':
        try:
            if a is not None and b is not None and int(a) == int(b):
                return True
        except ValueError:
            pass
    elif field == 'title':
        a = stripMarkersFromFilename(a)
        b = b.rstrip('!')
        return doStringsMatchForField(a, b, None)
    return False

def checkDeleteUrlsInTheWayOfM4as(fullpathdir, shorts):
    changedAtLeastOne = False
    for short in shorts:
        if short.endswith('.url'):
            filem4a = fullpathdir + '/' + files.splitExt(short)[0] + '.m4a'
            if files.exists(filem4a):
                trace('Keeping m4a in favor of url', short)
                softDeleteFile(fullpathdir + '/' + short)
                changedAtLeastOne = True
    
    stopIfFileRenamed(changedAtLeastOne)

def checkForLowBitratesFile(fullpathdir, bitrate, tag, allowMakeUrl=True):
    if '.sv.' in tag.short or '.movetosv.' in tag.short:
        return None
    if ' (vv)' in tag.short:
        return 'makeurl'
    if bitrate < 19 and tag.short.endswith('.m4a'):
        trace('automatically deleting low bitrate file ', fullpathdir, tag.short)
        return 'delete'
    if bitrate < 27 and tag.short.endswith('.m4a') and allowMakeUrl:
        trace('automatically urling low bitrate file ', fullpathdir, tag.short)
        return 'makeurl'
    if allowMakeUrl and (bitrate < 27 or ' (v)' in tag.short) and '.3.mp3' not in tag.short:
        trace(fullpathdir, tag.short)
        choice = getInputFromChoices('file has low bitrate (%f)'%bitrate, ['remove', 'make url'])
        if choice[0] == 0:
            return 'delete'
        if choice[0] == 1:
            return 'makeurl'

def checkForLowBitrates(fullpathdir, tags, allowMakeUrl):
    changedAtLeastOne = False
    for tag in tags:
        if tag.short.endswith('.url'):
            continue
        
        bitrate = get_empirical_bitrate(fullpathdir + '/' + tag.short, tag)
        action = checkForLowBitratesFile(fullpathdir, bitrate, tag, allowMakeUrl)
        if action == 'delete':
            softDeleteFile(fullpathdir + '/' + tag.short)
            changedAtLeastOne = True
        elif action == 'makeurl':
            # m4aToUrl will automatically remove and ' (vv)' ' (v)' in filename
            if allowMakeUrl:
                m4aToUrl(fullpathdir, tag.short, tag)
                changedAtLeastOne = True
        elif action is not None:
            assert False, 'unknown action ' + action
            
    stopIfFileRenamed(changedAtLeastOne)
        
def checkFilenameIrregularitiesLookForInconsistency(fullpathdir, shorts):
    changedAtLeastOne = False
    countDashes = len(fullpathdir.split(' - ')) - 1
    assertTrue(countDashes <= 1, 'name has too many dashes', fullpathdir)
    
    bAtLeastOneHasArtist = False
    bAtLeastOneNoArtist = False
    for short in shorts:
        countDashes = len(short.split(' - ')) - 1
        assertTrue(countDashes <= 1, 'name has too many dashes', fullpathdir, short)
        assertTrue((len(fullpathdir) + len(short)) < 180, 'name is dangerously long', fullpathdir, short)
        
        bAtLeastOneHasArtist |= countDashes == 1
        bAtLeastOneNoArtist |= countDashes == 0
        if u'\u2013' in short:  # em-dash
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
                while True:
                    proposednames = ['Open in explorer',
                        first + ' (' + bnsplitext(second)[0] + ')' + bnsplitext(second)[1],
                        first + ', ' + second,
                        first + ' ' + second]
                    choice = getInputFromChoices('choose a new name:', proposednames)
                    if choice[0] >= 0:
                        if proposednames[choice[0]] == 'Open in explorer':
                            files.openDirectoryInExplorer(fullpathdir)
                            continue
                        else:
                            files.move(fullpathdir + '/' + short, fullpathdir + '/' + proposednames[choice[0]], False)
                            changedAtLeastOne = True
                    break
    
    stopIfFileRenamed(changedAtLeastOne)
    
def checkUrlContents(fullpathdir, shorts):
    for short in shorts:
        if short.endswith('.url'):
            url = getFromUrlFile(fullpathdir + '/' + short)
            assertTrue(url, 'could not retrieve url', fullpathdir, short)
            assertTrue(':notfound' not in url, 'must point to location', fullpathdir, short)
            assertTrue(':local' not in url, 'local shortcuts disallowed.', fullpathdir, short)
            assertTrue('boinjyboing' not in url, 'user shortcuts disallowed', fullpathdir, short)

def checkStyleConsistency(fullpathdir, parsedNames):
    seenFirst = parsedNames[0]
    for parsed in parsedNames:
        assertTrue(parsed.style == seenFirst.style, 'in dir %s file %s has style %s but file %s has style %s' %
            (fullpathdir, seenFirst.short, seenFirst.style, parsed.short, parsed.style))

def getNewnameFromTag(parsed, field, fromFilename, fromTag):
    parsedProposed = copy.deepcopy(parsed)
    if fromTag is None:
        newval = '(None)'
    elif isinstance(fromTag, int):
        newval = fromTag
    else:
        newval = toValidFilename(fromTag)
    if 'number' in field and not isinstance(newval, int):
        newval = newval.split('-')[0].split('/')[0]
        try:
            newval = int(newval)
        except ValueError:
            newval = 0

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
        fromTag = tag.get_or_default(field, None)
        if not fromFilename and field in optionalFields:
            continue
        if not fromFilename and not fromTag and field not in optionalFields:
            assertTrue(False, 'file', fullpathdir, tag.short, 'could not infer value for field', field)
        if not doStringsMatchForField(fromFilename, fromTag, field):
            # the Compilation/Selections keyword allows files with different album tags to coexist in the same directory.
            if field == 'album' and fromTag is not None and (dirsplit[-1].endswith(' Compilation') or
                    dirsplit[-1].endswith(' Selections')):
                continue
                
            bulkSetValue = userAllowsBulkSet.get((field, fromTag, fromFilename), None)
            if bulkSetValue is not None and (field == 'album' or field == 'discnumber' or field == 'artist'):
                trace('file', fullpathdir, tag.short, 'setting tag based on bulkset', field, fromFilename, bulkSetValue)
                tag.set(field, bulkSetValue)
                needSave = True
            else:
                message = 'for file %s/%s,\n field %s,\nfilename says "%s"\ntag says "%s"'%(
                    fullpathdir, tag.short, field, fromFilename, fromTag)
                trace(message)
                proposedNameFromTag = getNewnameFromTag(parsed, field, fromFilename, fromTag)
                
                choices = ['set from filename (%s=%s)'%(field, fromFilename),
                    'bulk set from filename (%s=%s only for this album+field)'%(field, fromFilename)]
                if proposedNameFromTag != parsed.short:
                    choices.append('set filename from tag (%s)'%proposedNameFromTag)
                    
                if shouldAutoAcceptTagFromFilename(fullpathdir, tag.short, tag, message):
                    # almost certainly, for newly added files in m4a format, if the tag and filename don't match,
                    # it is the filename that should be used.
                    # so for convenience, you can enable automatically setting tag based on filename in this case.
                    choice = [0, 0]
                    print('automatically choosing 1) for this recently added file.')
                else:
                    choice = getInputFromChoices('', choices)
                
                if choice[0] == 0 or choice[0] == 1:
                    tag.set(field, fromFilename)
                    needSave = True
                if choice[0] == 1:
                    userAllowsBulkSet[(field, fromTag, fromFilename)] = fromFilename
                if choice[0] == 2:
                    files.move(fullpathdir + '/' + tag.short, fullpathdir + '/' + proposedNameFromTag, False)
                    raise StopBecauseWeRenamedFile
    if needSave:
        tag.save()

def shouldAutoAcceptTagFromFilename(dir, short, tag, message):
    # it's almost always the case that, for newly added files in m4a format, if the tag and filename don't match,
    # it is the filename that should be used, since we usually don't add m4a files with the wrong filename.
    # if a filepath is provided, we'll write log statements to that path.
    if enableAutoTagFromFilenameForRecentFiles():
        if short.endswith('.m4a'):
            oneweek = 7 * 86400
            useIfYoungerThan = oneweek * enableAutoTagForFilesYoungerThanThisManyWeeks()
            if time.time() - files.getLastModTime(files.join(dir, short)) < useIfYoungerThan:
                if time.time() - files.createdTime(files.join(dir, short)) < useIfYoungerThan:
                    if isinstance(enableAutoTagFromFilenameForRecentFiles(), anystringtype):
                        f = codecs.open(enableAutoTagFromFilenameForRecentFiles(), 'a', 'utf8')
                        f.write('\n' + message.replace('\n', ' '))
                        f.close()
                    return True
    return False

def checkRequiredFieldsSet(fullpathdir, dirsplit, tags, parsedNames):
    requiredfields = ['album', 'artist', 'title', 'discnumber']
    isAlbum = len(dirsplit[-1]) > 4 and dirsplit[-1][0:4].isdigit() and ' Selections' not in dirsplit[-1]
    if isAlbum:
        requiredfields.append('tracknumber')
    
    seenWithoutSpotify = False
    seenTracknumber = False
    for tag, parsed in zip(tags, parsedNames):
        if not isAlbum:
            assertTrue(not (tag.short[0:2].isdigit() and tag.short[2] == ' '),
                'file outside of album has tracknumber', fullpathdir, tag.short)
        if tag.short.endswith('.url'):
            continue
            
        seenTracknumber |= 'Track' in parsed.style
        seenWithoutSpotify |= not tag.getLink()
        for field in requiredfields:
            if field == 'album' and tag.get_or_default(field, None) == emptyAlbumPlaceholder:
                tag.set('album', '')
            
            isInAnAlbum = 'Track' in parsed.style
            if not tag.get_or_default(field, None):
                spotlink = tag.getLink()
                if field == 'album':
                    if isInAnAlbum or askAlbumName():
                        if lookupAlbumForFile(fullpathdir + '/' + tag.short, tag, parsed, spotlink):
                            raise StopBecauseWeRenamedFile
                elif field == 'tracknumber' and not isInAnAlbum:
                    pass  # allowing missing tracknumber since non-album
                else:
                    assertTrue(False, 'missing required field', field, fullpathdir, tag.short)
    
    return seenTracknumber, seenWithoutSpotify

def checkFilenamesMain(fullpathdir, dirsplit, tags, helpers):
    if not len(tags):
        return

    shorts = [tag.short for tag in tags]
    checkDeleteUrlsInTheWayOfM4as(fullpathdir, shorts)
    checkForLowBitrates(fullpathdir, tags, False)
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
    linkspotify(seenWithoutSpotify, fullpathdir, tags, parsedNames, seenTracknumber, helpers.market)
    helpers.music_to_url.go(fullpathdir, tags, parsedNames)
    checkForLowBitrates(fullpathdir, tags, True)

def goPerDirectory(fullpathdir, dirsplit, helpers):
    allshorts = files.listChildren(fullpathdir, filenamesOnly=True)
    tags = []
    seenOne = False
    for short in allshorts:
        seenOne = True
        path = fullpathdir + '/' + short
        if files.isFile(path):
            ext = helpers.checkFileExtensions.check(fullpathdir, short)
            if ext in helpers.extsCheckFilenames:
                if ext == 'url':
                    tags.append(Bucket(short=short, ext=ext))
                else:
                    tags.append(CoordMusicAudioMetadata(path))
                    tags[-1].short = short
    
    if not seenOne:
        trace('\n\nempty directories are discouraged ... ' + fullpathdir + '\n\n')

    checkFilenamesMain(fullpathdir, dirsplit, tags, helpers)

def getHelpers(root, enableSaveSpace):
    helpers = Bucket()
    helpers.checkFileExtensions = CheckFileExtensions()
    helpers.removeRemasteredString = RemoveRemasteredString()
    helpers.music_to_url = SaveDiskSpaceMusicToUrl(enableSaveSpace)
    helpers.extsCheckFilenames = dict(mp3=1, m4a=1, flac=1, url=1)
    helpers.splroot = root.split(files.sep)
    helpers.market = getSpotifyGeographicMarketName()
    return helpers

emptyAlbumPlaceholder = '   '

def mainCoordinate(isTopDown=True, enableSaveSpace=False, dir=None):
    root = getMusicRoot()
    if not dir:
        dir = root
    
    helpers = getHelpers(root, enableSaveSpace)
    for fullpathdir, pathshort in getScopedRecurseDirs(dir, isTopDown=isTopDown, filterOutLib=True):
        # we'll need a few passes through the directory in some cases
        while True:
            err = None
            try:
                dirsplit = list(map(stripMarkersFromFilename, fullpathdir.split(files.sep)))
                goPerDirectory(fullpathdir, dirsplit, helpers)
            except StopBecauseWeRenamedFile:
                trace('we renamed a file; re-entering directory.')
                continue
            except (KeyboardInterrupt, IOError, OSError, AssertionError) as err:
                trace(err)
                choice = getInputFromChoices('encountered exception.', ['retry', 'next dir', 'explorer'])
                if choice[0] == -1:
                    return  # exit
                elif choice[0] == 0:
                    continue  # retry dir
                elif choice[0] == 1:
                    break  # go to next dir
                elif choice[0] == 2:
                    files.openDirectoryInExplorer(fullpathdir)
                    continue
                
            break

    trace('Complete.')

