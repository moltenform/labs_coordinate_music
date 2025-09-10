# labs_coordinate_music
# Ben Fisher, 2016
# Released under the GNU General Public License version 3

import os
import sys
import time
import codecs

import recurring_linkspotify
import recurring_music_to_url
from coordmusicutil import *


def tools_getPlaylistId(playlistId=None):
    if not playlistId:
        playlistId = getDefaultSpotifyPlaylist()
        if not playlistId:
            warn(
                'no default playlist, please edit coordmusicuserconfig.py ' +
                'and implement getDefaultSpotifyPlaylist()'
            )
    return playlistId


def tools_clearPlaylist(playlistId=None):
    playlistId = tools_getPlaylistId(playlistId)
    sp = spotipyconn()
    tracks = getTracksFromPlaylist(sp, playlistId)
    trace('removing %d tracks.' % len(tracks))
    urisToRemove = [track[u'uri'] for track in tracks]

    for res in takeBatch(urisToRemove, 10):
        sp.user_playlist_remove_all_occurrences_of_tracks(getSpotifyUsername(), playlistId, res)
        time.sleep(0.2)


def tools_viewSpotifyPlaylist(playlistId=None):
    playlistId = tools_getPlaylistId(playlistId)
    tracks = getTracksFromPlaylist(spotipyconn(), playlistId)
    for i, track in enumerate(tracks):
        info = ExtendedSongInfo(None, None)
        info.info['uri'] = track['uri'].replace('spotify:track:', '')
        info.addSpotifyInfo(track)
        trace(str(i + 1), info.toString().replace('None	00:00:000	0', ''))


def tools_spotifyPlaylistToSongLengths(playlistId=None):
    playlistId = tools_getPlaylistId(playlistId)
    tracks = getTracksFromPlaylist(spotipyconn(), playlistId)
    startInPlaylist = getInputInt('start where in the playlist (default 1)?', 1, len(tracks)) - 1
    tracks = tracks[startInPlaylist:]
    outpath = getDefaultDirectorySpotifyToFilenames() + '/data/lengths.txt'
    with open(outpath, 'w', encoding='utf-8') as fout:
        for i, track in enumerate(tracks):
            fout.write('%f|%d %s' % (track['duration_ms'] / 1000.0, i + 1, track['uri']))
            fout.write('\n')
    trace('wrote %d lengths to %s' % (len(tracks), outpath))


def tools_spotifyPlaylistToFilenames(playlistId=None):
    playlistId = tools_getPlaylistId(playlistId)
    tracks = getTracksFromPlaylist(spotipyconn(), playlistId)
    startInPlaylist = getInputInt('start where in the playlist (default 1)?', 1, len(tracks)) - 1
    tracks = tracks[startInPlaylist:]

    potentialRenames = []
    localfiles = list(files.listFiles(getDirChoice(getDefaultDirectorySpotifyToFilenames(), '')))
    for i, track in enumerate(tracks):
        if i >= len(localfiles):
            trace('reached end of available files, %d files needed but got %d' % (len(tracks), len(localfiles)))
            if not getInputBool('continue?'):
                return
            else:
                break

        trace(
            '%d) %s %s\t->%s %s - %s' % (
                i + 1, localfiles[i][1], getFormattedDuration(get_audio_duration(localfiles[i][0])),
                getFormattedDuration(track['duration_ms'] / 1000.0), track['artists'][0]['name'], track['name']
            )
        )
        newname = files.getParent(
            localfiles[i][0]
        ) + files.sep + getFilenameFromTrack(i + 1, track) + '.' + files.getExt(localfiles[i][0])
        potentialRenames.append((localfiles[i][0], newname))

    if getInputBool('begin renaming?'):
        for old, new in potentialRenames:
            trace('renaming "%s" to "%s"' % (files.getName(old), files.getName(new)))
            files.move(old, new, False)


def getFilenameFromTrack(number, track):
    spartist = track['artists'][0]['name'].replace('$', 'S')
    sptitle = track['name'].split(u' - ')[0].replace('$', 'S')
    spalbum = track[u'album'][u'name'].replace('$', 'S')

    newname = '$%s$%02d$%s$' % (spartist, int(track['track_number']), sptitle)
    newname += track['uri'].replace('spotify:track:', '')

    # add either the album name, or part of the album name if our name is too long
    if len(newname) > 160:
        warn('filename is too long ' + newname)
    elif len(newname) + len(spalbum) > 160:
        warn('truncating album name for too long ' + newname)
        newname = spalbum[0:5] + newname
    else:
        newname = spalbum + newname

    newname = '%04d ' % number + newname
    return toValidFilename(newname)


def setMetadataFromFilename(fullpath):
    parts = files.getName(fullpath).split('$')
    if len(parts) != 5:
        trace('for file %s incorrect # of $' % (fullpath))
        return
    alb, artist, tracknum, title, spotifyUri = parts
    _position, alb = alb.split(' ', 1)
    spotifyUri = spotifyUri.split('.')[0]
    obj = CoordMusicAudioMetadata(fullpath)
    obj.setLink('spotify:track:' + spotifyUri)
    obj.set('album', alb)
    obj.set('artist', artist)
    obj.set('title', title)
    obj.set('tracknumber', tracknum)
    obj.save()


def tools_filenamesToMetadataAndRemoveLowBitrate(localfiles=None, styleGiven=None):
    respondToSmallFiles = 'makeLink' # makeLink|skip|delete
    if localfiles is None:
        localfiles = list(files.listFiles(getDirChoice(getDefaultDirectorySpotifyToFilenames(), '')))
    for _fullpath, short in localfiles:
        if short.endswith('.wav'):
            warn('why is there still a wav here? ' + short)
        if '__MARKAS' in short:
            warn('why is there a file with MARKAS here? ' + short)

    renameAlbumHasManyArtists = None
    if styleGiven:
        renameAlbumStyle = styleGiven['renameAlbumStyle']
        renameAlbumHasManyArtists = styleGiven['renameAlbumHasManyArtists']
        renameLooseStyle = styleGiven['renameLooseStyle']
    else:
        renameAlbumStyle = getInputBool('Rename albums style?')
        renameLooseStyle = getInputBool('Rename loose songs style?')
        if renameAlbumStyle:
            renameAlbumHasManyArtists = getInputBool('Album has multiple artists?')

    for fullpath, short in localfiles:
        if fullpath.endswith('.m4a') or fullpath.endswith('.flac'):
            newpath = None
            setMetadataFromFilename(fullpath)
            tag = CoordMusicAudioMetadata(fullpath)
            if get_empirical_bitrate(fullpath) <= 30:
                trace('found low bitrate', short)
                if respondToSmallFiles == 'skip':
                    trace('skipping low bitrate file', fullpath)
                elif respondToSmallFiles == 'delete':
                    softDeleteFile(fullpath)
                elif respondToSmallFiles == 'makeLink':
                    newpath = recurring_music_to_url.m4aToUrlWithBitrate(files.getParent(fullpath), tag.short, tag)
                else:
                    raise Exception('unknown respondToSmallFiles')
            else:
                trace('saved tags for', short)

            if renameAlbumStyle:
                path = newpath or fullpath
                if renameAlbumHasManyArtists:
                    newshort = ('%02d' % int(tag.get('tracknumber'))
                               ) + ' ' + tag.get('artist') + ' - ' + tag.get('title') + files.splitExt(path)[1]
                    newDir = files.getParent(path) + '/' + tag.get('album')
                else:
                    newshort = ('%02d' % int(tag.get('tracknumber'))) + ' ' + tag.get('title') + files.splitExt(path)[1]
                    newDir = files.getParent(path) + '/' + tag.get('album')
                files.makeDirs(newDir)
                files.move(path, newDir + '/' + newshort, False)
            elif renameLooseStyle:
                path = newpath or fullpath
                newshort = tag.get('artist') + ' - ' + tag.get('title') + files.splitExt(path)[1]
                files.move(path, files.getParent(path) + '/' + newshort, False)


def tools_outsideMp3sToSpotifyPlaylist(dir=None, mustSort=False, confirmAll=True):
    if not dir:
        clipboardText = getClipboardText()
        defaultDir = clipboardText if (files.exists(clipboardText)) else getDefaultDirectorySpotifyToFilenames()
        dir = getInputStringGui('choose input directory:', defaultDir)
        if not dir:
            return

    diriter = files.recurseDirs(dir)
    if mustSort:
        diriter = sorted(diriter, reverse=True)

    # first, associate all files with Spotify
    for fullpathdir, shortdir in diriter:
        filepaths = [
            filepath for (filepath, fileshort) in files.listFiles(fullpathdir) if getFieldForFile(filepath, False)
        ]
        for filepath in filepaths:
            if '__MARKAS' not in filepath:
                assertTrue(False, 'cannot continue, file does not have __MARKAS. ' + filepath)
            if '__MARKAS__16.' in filepath:
                alert('for file ' + filepath + ' just delete instead of using __MARKAS__16.')

        tags = [CoordMusicAudioMetadata(filepath) for filepath in filepaths]
        countFilesWithMissingNumber = len([tag for tag in tags if tag.get_or_default('tracknumber', None)])
        parsed = []
        for tag in tags:
            if not tag.get_or_default('tracknumber', None):
                num = getInputInt(
                    '%s\nenter tracknum for "%s" (%d files missing tracknum)' %
                    (fullpathdir, tag.short, countFilesWithMissingNumber)
                )
                tag.set('tracknumber', num)
                tag.save()
            parsed.append(
                Bucket(
                    short=tag.short,
                    tracknumber=int(tag.get('tracknumber')),
                    artist=tag.get_or_default('artist', None),
                    title=tag.get_or_default('title', None),
                    album=shortdir,
                    discnumber=int(tag.get_or_default('discnumber', 1))
                )
            )

        alreadyAll = all(('spotify:' in tag.getLink() for tag in tags))
        recurring_linkspotify.linkspotify(
            len(tags) > 0 and not alreadyAll, fullpathdir, tags, parsed, True, getSpotifyGeographicMarketName()
        )

    # check that all files have a spotify link
    if confirmAll:
        for fullpath, _short in files.recurseFiles(dir):
            if getFieldForFile(fullpath, False):
                if not 'spotify:' in CoordMusicAudioMetadata(fullpath).getLink():
                    warn('file has no spotify link: ' + fullpath)

    # add URIs to list
    addToPlaylist = []
    for fullpath, short in files.recurseFiles(dir):
        if getFieldForFile(fullpath, False) and '__MARKAS__24.' not in short:
            link = CoordMusicAudioMetadata(fullpath).getLink()
            if 'spotify:track:' in link:
                addToPlaylist.append(link)

    # add URIs to Spotify playlist
    if len(addToPlaylist):
        playlistId = tools_getPlaylistId()
        trace('adding %d tracks' % len(addToPlaylist))
        for batch in takeBatch(addToPlaylist, 10):
            spotipyconn().user_playlist_add_tracks(getSpotifyUsername(), playlistId, list(batch))
            time.sleep(0.2)


def tools_newFilesBackToReplaceOutsideMp3s(dir=None, dirNewFiles=None):
    if not dir:
        trace('where are the old files to be replaced?')
        clipboardText = getClipboardText()
        defaultDir = clipboardText if (files.exists(clipboardText)) else getDefaultDirectorySpotifyToFilenames()
        dir = getInputStringGui('old files to be replaced:', defaultDir)
        if not dir:
            return

    # make mapSpotifyIdToNewFile
    mapSpotifyIdToNewFile = dict()
    if not dirNewFiles:
        dirNewFiles = getDirChoice(getDefaultDirectorySpotifyToFilenames(), 'where are incoming files?')
    for newfilepath, newfileshort in files.listFiles(dirNewFiles):
        if newfileshort.endswith('.wav') and '__MARKAS' not in newfileshort:
            parts = newfileshort.split('$')
            assertTrue(len(parts) == 5, 'unexpected number of $ in file ' + newfilepath)
            uri = 'spotify:track:' + parts[4].split('.')[0]
            mapSpotifyIdToNewFile[uri] = newfilepath
        else:
            warn('expected wav files with $ and no __MARKAS but got ' + newfilepath)

    # rename new files
    oldFiles = []
    for fullpath, short in files.recurseFiles(dir):
        if getFieldForFile(fullpath, False) and '__MARKAS__' in short:
            link = CoordMusicAudioMetadata(fullpath).getLink()
            oldFiles.append((fullpath, short, link))
            if link in mapSpotifyIdToNewFile:
                suffix = short.split('__MARKAS__')[1].split('.')[0]
                newname = files.splitExt(mapSpotifyIdToNewFile[link])[0] + '__MARKAS__' + suffix + '.wav'
                trace('renaming\n', files.getName(mapSpotifyIdToNewFile[link]), '\nto\n', files.getName(newname))
                files.move(mapSpotifyIdToNewFile[link], newname, False)

    # wait for user to convert .wav to .m4a
    if len(mapSpotifyIdToNewFile):
        loop = True
        while loop:
            toM4aExe = r'C:\data\data_1\b\pydev\devhiatus\sort_downloaded_pictures\bin\x64\Release\sortpictures.exe'
            if files.exists(toM4aExe) and getInputBool('run toM4aExe tool?'):
                files.run([toM4aExe, files.join(dirNewFiles, 'a.wav')])

            alert('new files renamed. convert them to .m4a before continuing.')
            loop = False
            for key in mapSpotifyIdToNewFile:
                if files.exists(mapSpotifyIdToNewFile[key]):
                    loop = True
                    trace('forgot to convert to m4a? expect not exist ' + mapSpotifyIdToNewFile[key])
                if not files.exists(mapSpotifyIdToNewFile[key].replace('.wav', '.m4a')):
                    loop = True
                    trace(
                        'forgot to convert to m4a? expect exist ' + mapSpotifyIdToNewFile[key].replace('.wav', '.m4a')
                    )

    # rebuild mapSpotifyIdToNewFile, in case resuming and there are m4as present
    mapSpotifyIdToNewFile = dict()
    for newfilepath, newfileshort in files.listFiles(dirNewFiles):
        if newfileshort.endswith('.m4a') and '__MARKAS' not in newfileshort:
            parts = newfileshort.split('$')
            assertTrue(len(parts) == 5, 'unexpected number of $ in file ' + newfilepath)
            uri = 'spotify:track:' + parts[4].split('.')[0]
            mapSpotifyIdToNewFile[uri] = newfilepath
        else:
            warn('expected m4a files with $ and no __MARKAS but got ' + newfilepath)

    # add id3 metadata
    alert('adding metadata.')
    filepaths = (mapSpotifyIdToNewFile[key] for key in mapSpotifyIdToNewFile)
    filenamesToMetadataAndRemoveLowBitratePrevVersion([(s, files.getName(s)) for s in filepaths])

    # move newfile back and replace existing.
    alert('about to move newfiles back and replace existing files.')
    for fullpath, short, link in oldFiles:
        pathNoMark = fullpath.split('__MARKAS__')[0]
        if '__MARKAS__24.' in short:
            # turn 24 into a url shortcut.
            if 'spotify:track:' in link:
                writeUrlFile(pathNoMark + '.url', link)
                softDeleteFile(fullpath)
            else:
                if getInputBool(fullpath + ' can\'t be made a shortcut because it\'s not on Spotify. keep?'):
                    files.move(fullpath, pathNoMark + files.splitExt(fullpath)[1], False)
                else:
                    softDeleteFile(fullpath)

        elif 'spotify:track:' in link:
            # replace this file with corresponding new file
            if link not in mapSpotifyIdToNewFile:
                alert('note: for file ' + fullpath + ' did not see corresponding new file')
            else:
                assertTrue(files.exists(mapSpotifyIdToNewFile[link]), 'expect exist ' + mapSpotifyIdToNewFile[link])
                trace('replacing', fullpath, 'with', mapSpotifyIdToNewFile[link], 'to', pathNoMark + '.m4a')
                files.move(mapSpotifyIdToNewFile[link], pathNoMark + '.m4a', False)
                softDeleteFile(fullpath)
        else:
            # has no corresponding new file, so rename it
            suffix = short.split('__MARKAS__')[1].split('.')[0]
            newshortWithQual = short if len(
                suffix
            ) <= 2 else files.getName(pathNoMark) + ' (%s)' % suffix[0:2] + files.splitExt(fullpath)[1]
            newshortNoQual = files.getName(pathNoMark) + files.splitExt(fullpath)[1]
            choice, s = getInputFromChoices(
                fullpath + ' this file isn\'t on Spotify, new name is?', [newshortWithQual, newshortNoQual]
            )
            if choice >= 0:
                files.move(fullpath, files.join(files.getParent(fullpath), s), False)


def filenamesToMetadataAndRemoveLowBitratePrevVersion(localfiles=None):
    if localfiles is None:
        localfiles = list(files.listFiles(getDirChoice(getDefaultDirectorySpotifyToFilenames(), '')))
    for _fullpath, short in localfiles:
        if short.endswith('.wav'):
            warn('why is there still a wav here? ' + short)
        if '__MARKAS' in short:
            warn('why is there a file with MARKAS here? ' + short)

    for fullpath, short in localfiles:
        if fullpath.endswith('.m4a'):
            setMetadataFromFilename(fullpath)
            if get_empirical_bitrate(fullpath) < 20:
                trace('auto-deleting low bitrate', short)
                softDeleteFile(fullpath)
            else:
                trace('saved tags for', short)


def tools_lookForMp3AndAddToPlaylist(dir, bitrateThreshold, playlistId=None):
    playlistId = tools_getPlaylistId(playlistId)
    results = []
    for fullpath, _short in getScopedRecurseFiles(dir, filterOutLib=True):
        if fullpath.endswith('.mp3') and not fullpath.endswith('.3.mp3') and not fullpath.endswith('.sv.mp3'):
            obj = CoordMusicAudioMetadata(fullpath)
            if 'spotify:track:' in obj.getLink() and get_empirical_bitrate(fullpath, obj) >= bitrateThreshold:
                trace('found file', fullpath)
                results.append((fullpath, obj.getLink()))

    if playlistId:
        sp = spotipyconn()
        for batch in takeBatch(results, 10):
            trace('adding to playlist', '\n'.join((item[0] for item in batch)))
            sp.user_playlist_add_tracks(getSpotifyUsername(), playlistId, [item[1] for item in batch])
            time.sleep(0.2)


def tools_saveFilenamesMetadataToText():
    outName = getInputString('save to what output file:', False)
    if files.exists(outName) and not getInputBool('append to existing file?'):
        return

    fileIterator = getScopedRecurseFiles(getMusicRoot(), filterOutLib=True)
    useSpotify = getSpotifyClientID() and getInputBool('retrieve Spotify metadata?')
    warnIfNotInMarket = getInputBool('warn if files are no longer in market?')
    saveFilenamesMetadataToText(fileIterator, useSpotify, outName, warnIfNotInMarket=warnIfNotInMarket)


class ExtendedSongInfo:
    def __init__(self, filename, short):
        self.info = dict(
            filename=filename,
            short=short,
            localLength=0,
            localBitrate=0,
            localAlbum=u'',
            uri='',
            spotifyArtist=u'',
            spotifyTitle=u'',
            spotifyLength=u'',
            spotifyAlbum=u'',
            spotifyIsInMarket=u'',
            spotifyPopularity=0
        )

        if not filename:
            pass
        elif filename.endswith('.url'):
            self.info['uri'] = getFromUrlFile(filename)
        elif filename.endswith('.txt'):
            # read the first 64k of utf8 text.
            self.info['localAlbum'] = files.readAll(filename, 'r',
                                                    'utf-8').replace('\r\n', '\n').replace('\n', '|')[0:1024 * 64]
        elif getFieldForFile(filename, throw=False):
            obj = CoordMusicAudioMetadata(filename)
            self.info['uri'] = obj.getLink()
            self.info['localLength'] = get_audio_duration(filename, obj)
            self.info['localBitrate'] = get_empirical_bitrate(filename, obj)

            parentname = files.getName(files.getParent(filename))
            if not (parentname[4:5] == ',' and parentname[0:4].isdigit()):
                self.info['localAlbum'] = obj.get_or_default('album', '')

    def addSpotifyInfo(self, track):
        self.info['spotifyArtist'] = ';'.join(art['name'] for art in track['artists'])
        self.info['spotifyTitle'] = track['name']
        self.info['spotifyLength'] = track['duration_ms'] / 1000.0
        self.info['spotifyAlbum'] = track['album']['name']
        self.info['spotifyPopularity'] = track['popularity']
        self.info['spotifyIsInMarket'] = '(not in market)' if \
            not isInSpotifyMarket(track) else ''

    def toString(self):
        fields = [
            self.info['filename'],
            getFormattedDuration(self.info['localLength'], True),
            int(self.info['localBitrate']), self.info['localAlbum'],
            self.info['uri'].replace('spotify:track:', '').replace('spotify:notfound', 'ns').replace('spotify:', ''),
            self.info['spotifyArtist'], self.info['spotifyTitle'],
            getFormattedDuration(self.info['spotifyLength'], True), self.info['spotifyAlbum'],
            self.info['spotifyPopularity'], self.info['spotifyIsInMarket']
        ]
        fields = [ustr(field).replace('\t', '') for field in fields]
        return u'\t'.join(fields)


def saveFilenamesMetadataToTextImplementation(useSpotify, warnIfNotInMarket, file, listOfSongInfoObjects):
    time.sleep(0.2)

    # find all URIs expected
    uriToSongInfo = dict()
    for item in listOfSongInfoObjects:
        uriToSongInfo[ustr(item.info['uri'])] = item

    if useSpotify and len(uriToSongInfo):
        tracks = spotipyconn().tracks(list(uriToSongInfo))
        for track in tracks['tracks']:
            songInfo = uriToSongInfo[ustr(track['uri'])]
            songInfo.addSpotifyInfo(track)
            del uriToSongInfo[ustr(track['uri'])]
        if len(uriToSongInfo) > 0:
            warn(
                'did not find a spotify track for %s' %
                ('\n'.join(uri + ',' + uriToSongInfo[uri].filename for uri in uriToSongInfo))
            )

    filesNotInMarket = [item.info['filename'] for item in listOfSongInfoObjects if len(item.info['spotifyIsInMarket'])]
    if warnIfNotInMarket and filesNotInMarket:
        trace(
            'Warning: The Spotify URI for these files is not in market ' +
            '(it is likely that they are available in this market under a different URI) \n' +
            '\n'.join(filesNotInMarket)
        )
        if getInputBool('Remove the link for these files?'):
            for filename in filesNotInMarket:
                if not filename.endswith('.url'):
                    obj = CoordMusicAudioMetadata(filename)
                    obj.setLink('')
                    obj.save()

    for item in listOfSongInfoObjects:
        file.write(item.toString())
        file.write(files.lineSep)


def saveFilenamesMetadataToText(fileIterator, useSpotify, outName, warnIfNotInMarket=False, requestBatchSize=15):
    listOfSongInfoObjects = []
    countObjectsNeedingHttp = 0
    with codecs.open(outName, 'a', 'utf-8-sig') as file:
        for filename, short in fileIterator:
            listOfSongInfoObjects.append(ExtendedSongInfo(filename, short))
            if 'spotify:track:' in listOfSongInfoObjects[-1].info['uri']:
                countObjectsNeedingHttp += 1

                # send network requests in batches
                if countObjectsNeedingHttp > requestBatchSize:
                    saveFilenamesMetadataToTextImplementation(
                        useSpotify, warnIfNotInMarket, file, listOfSongInfoObjects
                    )
                    listOfSongInfoObjects = []
                    countObjectsNeedingHttp = 0

        saveFilenamesMetadataToTextImplementation(useSpotify, warnIfNotInMarket, file, listOfSongInfoObjects)
        listOfSongInfoObjects = []
        countObjectsNeedingHttp = 0


def tools_assignTagIfUntagged():
    import recurring_coordinate
    fileIterator = getScopedRecurseFiles(getMusicRoot(), filterOutLib=True)
    logOnly = True
    for filename, _short in fileIterator:
        if getFieldForFile(filename, throw=False):
            obj = CoordMusicAudioMetadata(filename)
            if not obj.get_or_default('album', None) and not obj.get_or_default(
                'track', None
            ) and not obj.get_or_default('comment', None) and not obj.get_or_default('title', None):
                trace('hardly any tags set on', filename)
                if not logOnly:
                    obj.set('album', recurring_coordinate.emptyAlbumPlaceholder)
                    obj.save()


if __name__ == '__main__':
    fns = [
        tools_clearPlaylist,
        tools_viewSpotifyPlaylist,
        tools_spotifyPlaylistToSongLengths,
        tools_spotifyPlaylistToFilenames,
        tools_filenamesToMetadataAndRemoveLowBitrate,
        tools_outsideMp3sToSpotifyPlaylist,
        tools_newFilesBackToReplaceOutsideMp3s,
        tools_lookForMp3AndAddToPlaylist,
        tools_saveFilenamesMetadataToText,
        tools_assignTagIfUntagged,
    ]
    topchoice, tops = getInputFromChoices('', [fn.__name__.replace('tools_', '') for fn in fns])
    if topchoice >= 0:
        fns[topchoice]()
