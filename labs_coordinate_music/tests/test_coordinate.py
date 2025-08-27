# labs_coordinate_music
# Ben Fisher, 2016
# Released under the GNU General Public License version 3

import pytest
from os.path import join
from common import *

import sys

sys.path.append('..')

from coordmusicutil import *
from recurring_coordinate import *
from recurring_linkspotify import *


class TestMusicUtils:
    def objToString(self, obj):
        return ';'.join(
            key + '=' + str(object.__getattribute__(obj, key))
            for key in dir(obj) if (not key.startswith('_') and key != 'short' and key != 'album')
        )

    # parsing filenames
    def test_parsefilenameAlbumTrackArtistTitle(self):
        assert 'artist=testart;discnumber=1;style=DiscTrackArtistTitle;title=testtitle;tracknumber=2' == \
            self.objToString(parseAFilename('01 02 testart - testtitle.m4a'))

    def test_parsefilenameAlbumTrackArtistTitleWithNumbers(self):
        assert 'artist=test-art 01;discnumber=1;style=DiscTrackArtistTitle;title=testtitle 01;tracknumber=2' == \
            self.objToString(parseAFilename('01 02 test-art 01 - testtitle 01 (^).m4a'))

    def test_parsefilenameAlbumTrackTitleWithDash(self):
        assert 'artist=None;discnumber=1;style=DiscTrackTitle;title=j-ust name;tracknumber=2' == \
            self.objToString(parseAFilename('01 02 j-ust name.m4a'))

    def test_parsefilenameTrackArtistTitle(self):
        assert 'artist=art art;discnumber=None;style=TrackArtistTitle;title=title title;tracknumber=12' == \
            self.objToString(parseAFilename('12 art art - title title.m4a'))

    def test_parsefilenameTrackTitle(self):
        assert 'artist=None;discnumber=None;style=TrackTitle;title=title title;tracknumber=12' == \
            self.objToString(parseAFilename('12 title title.m4a'))

    def test_parsefilenameArtistTitle(self):
        assert 'artist=art art;discnumber=None;style=ArtistTitle;title=title title;tracknumber=None' == \
            self.objToString(parseAFilename('art art - title title.m4a'))

    def test_parsefilenameTitle(self):
        assert 'artist=None;discnumber=None;style=Title;title=title title;tracknumber=None' == \
            self.objToString(parseAFilename('title title.m4a'))

    # rendering filenames
    def test_renderfilenameAlbumTrackArtistTitle(self):
        s = '01 02 testart - testtitle.m4a'
        assert renderAFilename(parseAFilename(s), s) == s

    def test_renderfilenameAlbumTrackArtistTitleWithNumbers(self):
        s = '01 02 test-art 01 - testtitle 01 (^).m4a'
        assert renderAFilename(parseAFilename(s), s) == s

    def test_renderfilenameAlbumTrackTitleWithDash(self):
        s = '01 02 j-ust name.m4a'
        assert renderAFilename(parseAFilename(s), s) == s

    def test_renderfilenameTrackArtistTitle(self):
        s = '12 art art - title title.m4a'
        assert renderAFilename(parseAFilename(s), s) == s

    def test_renderfilenameTrackTitle(self):
        s = '12 title title.m4a'
        assert renderAFilename(parseAFilename(s), s) == s

    def test_renderfilenameArtistTitle(self):
        s = 'art art - title title.m4a'
        assert renderAFilename(parseAFilename(s), s) == s

    def test_renderfilenameTitle(self):
        s = 'title title.m4a'
        assert renderAFilename(parseAFilename(s), s) == s

    # changing a field
    def test_parsefilenameChangeArtist(self):
        parsed = parseAFilename('01 02 testart - testtitle.sv.m4a')
        assert '01 02 testart changed - testtitle.sv.m4a' == \
            getNewnameFromTag(parsed, 'artist', parsed.artist, 'testart changed')

    def test_parsefilenameChangeTitle(self):
        parsed = parseAFilename('01 02 testart - testtitle.sv.m4a')
        assert '01 02 testart - testtitle changed.sv.m4a' == \
            getNewnameFromTag(parsed, 'title', parsed.title, 'testtitle changed')

    def test_parsefilenameChangeTracknumber(self):
        parsed = parseAFilename('01 02 testart - testtitle.sv.m4a')
        assert '01 09 testart - testtitle.sv.m4a' == \
            getNewnameFromTag(parsed, 'tracknumber', parsed.tracknumber, 9)

    def test_parsefilenameChangeTrackNumberString(self):
        parsed = parseAFilename('01 02 testart - testtitle.sv.m4a')
        assert '01 09 testart - testtitle.sv.m4a' == \
            getNewnameFromTag(parsed, 'tracknumber', parsed.tracknumber, '9')

    def test_parsefilenameChangeTrackNumberRatio(self):
        parsed = parseAFilename('01 02 testart - testtitle.sv.m4a')
        assert '01 09 testart - testtitle.sv.m4a' == \
            getNewnameFromTag(parsed, 'tracknumber', parsed.tracknumber, '9/9')

    def test_parsefilenameChangeArtistToNone(self):
        parsed = parseAFilename('01 02 testart - testtitle.sv.m4a')
        assert '01 02 (None) - testtitle.sv.m4a' == \
            getNewnameFromTag(parsed, 'artist', parsed.artist, None)

    def test_parsefilenameChangeArtistToInvalidFilenameChar(self):
        parsed = parseAFilename('01 02 testart - testtitle.sv.m4a')
        assert '01 02 bad-char - testtitle.sv.m4a' == \
            getNewnameFromTag(parsed, 'artist', parsed.artist, 'bad:char')

    # test split
    def test_splitFilenameSimple(self):
        assert ('test', '.mp3') == bnsplitext('test.mp3')

    def test_splitFilenameDots(self):
        assert ('t.est', '.mp3') == bnsplitext('t.est.mp3')

    def test_splitFilenameTwoWords(self):
        assert ('test word', '.mp3') == bnsplitext('test word.mp3')

    def test_splitFilenameCloseParen(self):
        assert ('test word 12)', '.mp3') == bnsplitext('test word 12).mp3')

    def test_splitFilenameOpenCloseParen(self):
        assert ('test word(12)', '.mp3') == bnsplitext('test word(12).mp3')

    def test_splitFilenameQualityMarkerSeparateFromTitle(self):
        assert ('test is', ' (12).mp3') == bnsplitext('test is (12).mp3')

    def test_splitFilenameQualityMarkerSeparateFromTitleLeadingZero(self):
        assert ('test is', ' (09).mp3') == bnsplitext('test is (09).mp3')

    def test_splitFilenameQualityMarkerSeparateFromTitleM4a(self):
        assert ('test is', ' (09).m4a') == bnsplitext('test is (09).m4a')

    def test_splitFilenameNotASvMp3(self):
        assert ('test not savesv', '.mp3') == bnsplitext('test not savesv.mp3')

    def test_splitFilenameIsASvMp3(self):
        assert ('test save', '.sv.mp3') == bnsplitext('test save.sv.mp3')

    def test_splitFilenameIsASvMp3WithExtraDot(self):
        assert ('test.save', '.sv.mp3') == bnsplitext('test.save.sv.mp3')

    def test_splitFilenameIsASvMp3WithSpace(self):
        assert ('test save ', '.sv.mp3') == bnsplitext('test save .sv.mp3')

    def test_splitFilenameIsAMoveMp3(self):
        assert ('test save', '.movetosv.mp3') == bnsplitext('test save.movetosv.mp3')

    def test_splitFilenameNotASvMp3Nsv(self):
        assert ('test notsave.nsv', '.mp3') == bnsplitext('test notsave.nsv.mp3')

    def test_splitFilenameBothQualityMarkerAndSvMp3(self):
        assert ('test both', ' (12).sv.mp3') == bnsplitext('test both (12).sv.mp3')

    # test strings match
    def test_stringsMatchSameString(self):
        assert doStringsMatchForField('a', 'a', 'field')

    def test_stringsMatchUnicodeString(self):
        assert doStringsMatchForField('a a aa a a', u'a a aa a a', 'field')

    def test_stringsMatchDifferentString(self):
        assert not doStringsMatchForField('a', 'b', 'field')

    def test_stringsMatchQuoteCharacter(self):
        assert doStringsMatchForField('test\'test', u'test\u2019test', 'field')

    def test_stringsMatchNonFilenameCharacter(self):
        assert doStringsMatchForField('a-b', 'a\\b', 'field')

    def test_stringsMatchNonFilenameCharacterSlashSpace(self):
        assert doStringsMatchForField('a, b', 'a/ b', 'field')

    def test_stringsMatchNonFilenameCharacterSlash(self):
        assert doStringsMatchForField('a-b', 'a/b', 'field')

    def test_stringsMatchNonFilenameCharacterStar(self):
        assert doStringsMatchForField('ab', 'a*b', 'field')

    def test_stringsMatchNonFilenameCharacterQuote(self):
        assert doStringsMatchForField('a\'b', 'a"b', 'field')

    def test_stringsMatchLeadingZeroForString(self):
        assert not doStringsMatchForField('01', '1', 'title')

    def test_stringsMatchLeadingZeroForTrackNumber(self):
        assert doStringsMatchForField('01', '1', 'tracknumber')

    def test_stringsMatchLeadingZeroForDiscNumber(self):
        assert doStringsMatchForField('01', '1', 'discnumber')

    def test_stringsMatchMarkerIgnored(self):
        assert not doStringsMatchForField('a (^)', 'a', 'field')

    def test_stringsMatchMarkerIgnoredForTitle(self):
        assert doStringsMatchForField('a (^)', 'a', 'title')

    # test parseArtistFromFilename
    def parseArtistFromFilename(self, fullpath):
        helpers = Bucket(splroot=['c:', 'music'])
        parsed = Bucket(album='a', artist=None, discnumber=None)
        fillFieldsFromContext(parsed, fullpath, fullpath.split('/'), helpers)
        return parsed.artist

    def test_getArtistFromFilenameInRootNotArtist(self):
        with pytest.raises(AssertionError) as exc:
            self.parseArtistFromFilename('c:/music')
        exc.match('not within artist directory')

    def test_getArtistFromFilenameInGenreNotArtist(self):
        with pytest.raises(AssertionError) as exc:
            self.parseArtistFromFilename('c:/music/genre')
        exc.match('not within artist directory')

    def test_getArtistFromFilename1(self):
        assert 'Artist Name' == self.parseArtistFromFilename('c:/music/genre/Artist Name')

    def test_getArtistFromFilename2(self):
        assert 'Artist Name' == self.parseArtistFromFilename('c:/music/genre/Artist Name/1999, The Album')

    def test_getArtistFromFilename3(self):
        assert 'Artist Name' == self.parseArtistFromFilename(
            'c:/music/genre/Other Artist/1999, Artist Name - The Album'
        )

    def test_getArtistFromFilename4(self):
        assert 'Artist Name' == self.parseArtistFromFilename('c:/music/genre/Other Artist/Artist Name - The Album')

    def test_getArtistFromFilename5(self):
        assert 'Artist Name' == self.parseArtistFromFilename('c:/music/genre/Other Artist/Artist Name')

    def test_getArtistFromFilename6(self):
        assert 'Artist Name' == self.parseArtistFromFilename('c:/music/genre/Other Artist/Artist Name/1999, The Album')

    def test_getArtistFromFilename7(self):
        assert 'Artist Name' == self.parseArtistFromFilename(
            'c:/music/genre/Other Artist/Other/1999, Artist Name - The Album'
        )

    def test_getArtistFromFilename8(self):
        assert '199, Artist Name' == self.parseArtistFromFilename('c:/music/genre/Other Artist/199, Artist Name')

    def test_getArtistFromFilename9(self):
        assert ', Artist Name' == self.parseArtistFromFilename('c:/music/genre/Other Artist/, Artist Name')

    # test parseAlbumFromFilename
    def parseAlbumFromFilename(self, fullpath):
        helpers = Bucket(splroot=['c:', 'music'])
        parsed = Bucket(album=None, artist='a', discnumber=None)
        fillFieldsFromContext(parsed, fullpath, fullpath.split('/'), helpers)
        return parsed.album

    def test_parseAlbumFromFilename1(self):
        assert None is self.parseAlbumFromFilename('c:/music')

    def test_parseAlbumFromFilename2(self):
        assert None is self.parseAlbumFromFilename('c:/music/genre')

    def test_parseAlbumFromFilename3(self):
        assert None is self.parseAlbumFromFilename('c:/music/genre/Artist Name')

    def test_parseAlbumFromFilename4(self):
        assert 'The Album' == self.parseAlbumFromFilename('c:/music/genre/Artist Name/1999, The Album')

    def test_parseAlbumFromFilename5(self):
        assert 'The Album' == self.parseAlbumFromFilename('c:/music/genre/Other Artist/1999, Artist Name - The Album')

    def test_parseAlbumFromFilename6(self):
        assert 'The Album' == self.parseAlbumFromFilename('c:/music/genre/Other Artist/Artist Name - The Album')

    def test_parseAlbumFromFilename7(self):
        assert None is self.parseAlbumFromFilename('c:/music/genre/Other Artist/Artist Name')

    def test_parseAlbumFromFilename8(self):
        assert 'The Album' == self.parseAlbumFromFilename('c:/music/genre/Other Artist/Artist Name/1999, The Album')

    def test_parseAlbumFromFilename9(self):
        assert 'The Album' == self.parseAlbumFromFilename(
            'c:/music/genre/Other Artist/Other/1999, Artist Name - The Album'
        )

    def test_parseAlbumFromFilename10(self):
        assert 'Alb - Alb' == self.parseAlbumFromFilename('c:/music/genre/Other Artist/Artist Name - Alb - Alb')

    def test_parseAlbumFromFilename11(self):
        assert 'Alb - Alb' == self.parseAlbumFromFilename('c:/music/genre/Other Artist/1999, Artist Name - Alb - Alb')

    # test checkDeleteUrlsInTheWayOfM4as
    def getFileList(self, dir, joined=True):
        lst = (sorted([short for file, short in files.listFiles(dir)]))
        return '|'.join(lst) if joined else lst

    def test_checkDeleteUrlsInTheWayOfM4as(self, fixture_dir):
        files.writeAll(join(fixture_dir, 'test ok.url'), '')
        files.writeAll(join(fixture_dir, 'test conflict.url'), '')
        files.writeAll(join(fixture_dir, 'test conflict.m4a'), '')
        with pytest.raises(StopBecauseWeRenamedFile):
            checkDeleteUrlsInTheWayOfM4as(fixture_dir, self.getFileList(fixture_dir, False))

        assert self.getFileList(fixture_dir) == u'test conflict.m4a|test ok.url'

    # test checkUrlContents
    def test_checkUrlContentsWithAllValid(self, fixture_dir):
        writeUrlFile(join(fixture_dir, 'test1.url'), 'https://www.youtube.com/watch?v=0OSF')
        writeUrlFile(join(fixture_dir, 'test2.url'), 'spotify:track:0Svkvt5I79wficMFgaqEQJ')
        checkUrlContents(fixture_dir, self.getFileList(fixture_dir, False))

    def test_checkUrlContentsWithEmpty(self, fixture_dir):
        writeUrlFile(join(fixture_dir, 'test.url'), '')
        with pytest.raises(AssertionError) as exc:
            checkUrlContents(fixture_dir, self.getFileList(fixture_dir, False))
        exc.match('not retrieve')

    def test_checkUrlContentsWithLocal(self, fixture_dir):
        writeUrlFile(join(fixture_dir, 'test.url'), 'spotify:local:5d3642ab')
        with pytest.raises(AssertionError) as exc:
            checkUrlContents(fixture_dir, self.getFileList(fixture_dir, False))
        exc.match('local')

    def test_checkUrlContentsWithNotFound(self, fixture_dir):
        writeUrlFile(join(fixture_dir, 'test.url'), 'spotify:notfound')
        with pytest.raises(AssertionError) as exc:
            checkUrlContents(fixture_dir, self.getFileList(fixture_dir, False))
        exc.match('must point')

    def test_checkUrlContentsWithUser(self, fixture_dir):
        writeUrlFile(join(fixture_dir, 'test.url'), 'spotify:boinjyboing')
        with pytest.raises(AssertionError) as exc:
            checkUrlContents(fixture_dir, self.getFileList(fixture_dir, False))
        exc.match('user')

    # test checkForLowBitrates
    def test_checkLowBitrates1(self):
        assert 'makeurl' == checkForLowBitratesFile('c:/', 100, Bucket(short='file marked to makeurl (vv).m4a'))

    def test_checkLowBitrates2(self):
        assert 'makeurl' == checkForLowBitratesFile('c:/', 16, Bucket(short='file marked to makeurl (vv).m4a'))

    def test_checkLowBitrates3(self):
        assert 'delete' == checkForLowBitratesFile('c:/', 18, Bucket(short='lowbitrate.m4a'))

    def test_checkLowBitrates4(self):
        assert 'makeurl' == checkForLowBitratesFile('c:/', 26, Bucket(short='lowbitrate.m4a'))

    def test_checkLowBitrates5(self):
        assert None is checkForLowBitratesFile('c:/', 64, Bucket(short='mediumbitrate.m4a'))

    def test_checkLowBitrates6(self):
        assert None is checkForLowBitratesFile('c:/', 64, Bucket(short='mediumbitrate.mp3'))

    def test_checkLowBitrates7(self):
        assert None is checkForLowBitratesFile('c:/', 16, Bucket(short='saved.movetosv.mp3'))

    def test_checkLowBitrates8(self):
        assert None is checkForLowBitratesFile('c:/', 16, Bucket(short='saved.sv.mp3'))

    def test_checkLowBitrates9(self):
        assert None is checkForLowBitratesFile('c:/', 16, Bucket(short='saved.sv.m4a'))

    # test checkFilename
    def test_checkFilenameIrreg1(self):
        assert (False, False) == checkFilenameIrregularitiesLookForInconsistency('c:/', [])

    def test_checkFilenameIrreg2(self):
        assert (False, False) == checkFilenameIrregularitiesLookForInconsistency('c:/', ['title1.m4a', 'title-2.m4a'])

    def test_checkFilenameIrreg3(self):
        assert (False,
                False) == checkFilenameIrregularitiesLookForInconsistency('c:/', ['a - title1.m4a', 'b - title 2.m4a'])

    def test_checkFilenameIrreg4(self):
        assert (False,
                True) == checkFilenameIrregularitiesLookForInconsistency('c:/', ['a title1.m4a', 'b - title 2.m4a'])

    def test_checkFilenameIrreg5(self):
        assert (False, True) == checkFilenameIrregularitiesLookForInconsistency(
            'c:/', ['a - title1.m4a', 'b title 2.m4a', 'c 3.m4a']
        )

    def test_checkFilenameIrreg6(self):
        with pytest.raises(AssertionError) as exc:
            checkFilenameIrregularitiesLookForInconsistency('c:/dir - toomany - dashes', [])
        exc.match('too many')

    def test_checkFilenameIrreg7(self):
        with pytest.raises(AssertionError) as exc:
            checkFilenameIrregularitiesLookForInconsistency('c:/music', ['a - a - b.m4a'])
        exc.match('too many')

    def test_checkFilenameIrreg8(self):
        with pytest.raises(AssertionError) as exc:
            checkFilenameIrregularitiesLookForInconsistency('c:/music', ['a' * 300 + 'm4a'])
        exc.match('dangerously long')

    # test checkFileExt
    def test_checkFileExt1(self):
        assert 'mp3' == CheckFileExtensions().check('c:/', 'file test.mp3')

    def test_checkFileExt2(self):
        assert 'mp3' == CheckFileExtensions().check('c:/', 'file.m4a. test.mp3')

    def test_checkFileExt3(self):
        assert 'mp3' == CheckFileExtensions().check('c:/', 'c:/a/b/file.m4a.test.sv.mp3')

    def test_checkFileExt4(self):
        with pytest.raises(AssertionError) as exc:
            CheckFileExtensions().check('c:/', 'no extension')
        exc.match('no extension')

    def test_checkFileExt5(self):
        with pytest.raises(AssertionError) as exc:
            CheckFileExtensions().check('c:/', 'file test.MP3')
        exc.match('lowercase')

    def test_checkFileExt6(self):
        with pytest.raises(AssertionError) as exc:
            CheckFileExtensions().check('c:/', 'file test.test')
        exc.match('unsupported')

    def test_checkFileExt7(self):
        with pytest.raises(AssertionError) as exc:
            CheckFileExtensions().check('c:/', 'file test.mp31')
        exc.match('unsupported')

    # test checkStyleConsistency
    def test_checkStyleConsistency1(self):
        checkStyleConsistency('c:/', [Bucket(short=0, style='style1')])

    def test_checkStyleConsistency2(self):
        checkStyleConsistency('c:/', [Bucket(short=0, style='style1'), Bucket(short=0, style='style1')])

    def test_checkStyleConsistency3(self):
        with pytest.raises(AssertionError):
            checkStyleConsistency('c:/', [Bucket(short=0, style='style1'), Bucket(short=0, style='style2')])

    def test_checkStyleConsistency4(self):
        with pytest.raises(AssertionError):
            checkStyleConsistency(
                'c:/',
                [Bucket(short=0, style='style1'),
                 Bucket(short=0, style='style1'),
                 Bucket(short=0, style='style2')]
            )

    # test checkDuplicateTracks
    def test_checkDuplicatedTrackNumbers1(self):
        tracks = [
            Bucket(
                discnumber=1,
                tracknumber=1,
                style=NameStyle.TrackTitle,
                short=0,
                artist=getRandomString(),
                title=getRandomString()
            )
        ]
        checkDuplicatedTrackNumbers('c:/', tracks)

    def test_checkDuplicatedTrackNumbers2(self):
        tracks = [
            Bucket(
                discnumber=1,
                tracknumber=1,
                style=NameStyle.TrackTitle,
                short=0,
                artist=getRandomString(),
                title=getRandomString()
            ),
            Bucket(
                discnumber=2,
                tracknumber=1,
                style=NameStyle.TrackTitle,
                short=0,
                artist=getRandomString(),
                title=getRandomString()
            )
        ]
        checkDuplicatedTrackNumbers('c:/', tracks)

    def test_checkDuplicatedTrackNumbers3(self):
        tracks = [
            Bucket(
                discnumber=1,
                tracknumber=5,
                style=NameStyle.TrackTitle,
                short=0,
                artist=getRandomString(),
                title=getRandomString()
            ),
            Bucket(
                discnumber=1,
                tracknumber=6,
                style=NameStyle.TrackTitle,
                short=0,
                artist=getRandomString(),
                title=getRandomString()
            )
        ]
        checkDuplicatedTrackNumbers('c:/', tracks)

    def test_checkDuplicatedTrackNumbers4(self):
        tracks = [
            Bucket(
                discnumber=1,
                tracknumber=0,
                style=NameStyle.TrackTitle,
                short=0,
                artist=getRandomString(),
                title=getRandomString()
            )
        ]
        with pytest.raises(AssertionError) as exc:
            checkDuplicatedTrackNumbers('c:/', tracks)
        exc.match('not be 0')

    def test_checkDuplicatedTrackNumbers5(self):
        tracks = [
            Bucket(
                discnumber=0,
                tracknumber=1,
                style=NameStyle.TrackTitle,
                short=0,
                artist=getRandomString(),
                title=getRandomString()
            )
        ]
        with pytest.raises(AssertionError) as exc:
            checkDuplicatedTrackNumbers('c:/', tracks)
        exc.match('not be 0')

    def test_checkDuplicatedTrackNumbers6(self):
        tracks = [
            Bucket(
                discnumber=2,
                tracknumber=4,
                style=NameStyle.TrackTitle,
                short=0,
                artist=getRandomString(),
                title=getRandomString()
            ),
            Bucket(
                discnumber=2,
                tracknumber=4,
                style=NameStyle.TrackTitle,
                short=0,
                artist=getRandomString(),
                title=getRandomString()
            )
        ]
        with pytest.raises(AssertionError) as exc:
            checkDuplicatedTrackNumbers('c:/', tracks)
        exc.match('duplicate')

    def test_checkDuplicatedTrackNumbers7(self):
        tracks = [
            Bucket(
                discnumber=1,
                tracknumber=1,
                style=NameStyle.TrackTitle,
                short=0,
                artist=getRandomString(),
                title=getRandomString()
            ),
            Bucket(
                discnumber=2,
                tracknumber=4,
                style=NameStyle.TrackTitle,
                short=0,
                artist=getRandomString(),
                title=getRandomString()
            ),
            Bucket(
                discnumber=2,
                tracknumber=4,
                style=NameStyle.TrackTitle,
                short=0,
                artist=getRandomString(),
                title=getRandomString()
            )
        ]
        with pytest.raises(AssertionError) as exc:
            checkDuplicatedTrackNumbers('c:/', tracks)
        exc.match('duplicate')

    def test_checkDuplicatedTrackNumbers8(self):
        tracks = [
            Bucket(
                discnumber=1,
                tracknumber=1,
                style=NameStyle.TrackTitle,
                short=0,
                artist=getRandomString(),
                title=getRandomString()
            ),
            Bucket(
                discnumber=2,
                tracknumber=4,
                style=NameStyle.TrackTitle,
                short=0,
                artist=getRandomString(),
                title=getRandomString()
            ),
            Bucket(
                discnumber=1,
                tracknumber=1,
                style=NameStyle.TrackTitle,
                short=0,
                artist=getRandomString(),
                title=getRandomString()
            )
        ]
        with pytest.raises(AssertionError) as exc:
            checkDuplicatedTrackNumbers('c:/', tracks)
        exc.match('duplicate')

    def test_checkDuplicatedTrackNumbers9(self):
        tracks = [
            Bucket(discnumber=1, tracknumber=1, style=NameStyle.TrackTitle, short=0, artist='a', title='t'),
            Bucket(discnumber=1, tracknumber=2, style=NameStyle.TrackTitle, short=0, artist='a', title='t')
        ]
        with pytest.raises(AssertionError) as exc:
            checkDuplicatedTrackNumbers('c:/', tracks)
        exc.match('duplicate artist\\+title')

    def callCheckRequiredFieldsSet(self, dir, short, fieldsmissing, parsedstyle=''):
        class MockTagObject:
            def __init__(self, short, fieldsmissing=None):
                self.short = short
                self.fields = dict(
                    album='sampledata',
                    style='sampledata',
                    discnumber='1',
                    tracknumber='1',
                    artist='sampledata',
                    title='sampledata'
                )
                for key in fieldsmissing if fieldsmissing else []:
                    self.fields[key] = None

            def get(self, key):
                return self.fields[key]

            def get_or_default(self, key, default):
                return self.fields.get(key, default)

            def getLink(self):
                return 'spotify:track:0Svkvt5I79wficMFgaqEQJ'

        tagObject = MockTagObject(short, fieldsmissing)
        checkRequiredFieldsSet(dir, dir.split('/'), [tagObject], [Bucket(style=parsedstyle)])

    # test checkRequiredFields1
    def test_checkRequiredFields1(self):
        self.callCheckRequiredFieldsSet('c:/genre/1999, The Album', '01 test test.m4a', fieldsmissing=[])

    def test_checkRequiredFields2(self):
        self.callCheckRequiredFieldsSet('c:/genre/1999, The Album', 'test test.url', fieldsmissing=['artist'])

    def test_checkRequiredFields3(self):
        self.callCheckRequiredFieldsSet('c:/genre/1999, The Album Selections', 'test test.m4a', fieldsmissing=[])

    def test_checkRequiredFields4(self):
        self.callCheckRequiredFieldsSet('c:/genre', 'test test.m4a', fieldsmissing=['tracknumber'])

    def test_checkRequiredFields5(self):
        self.callCheckRequiredFieldsSet('c:/genre', '1234 test test.m4a', fieldsmissing=['tracknumber'])

    def test_checkRequiredFields6(self):
        with pytest.raises(AssertionError) as exc:
            self.callCheckRequiredFieldsSet('c:/genre', '01 test test.m4a', [])
        exc.match('outside of album')

    def test_checkRequiredFields7(self):
        with pytest.raises(AssertionError) as exc:
            self.callCheckRequiredFieldsSet('c:/genre', '01 test test.url', [])
        exc.match('outside of album')

    def test_checkRequiredFields8(self):
        with pytest.raises(AssertionError) as exc:
            self.callCheckRequiredFieldsSet(
                'c:/genre/1999, The Album', '01 test test.m4a', ['tracknumber'], 'TrackTitle'
            )
        exc.match('required field tracknumber')

    def test_checkRequiredFields9(self):
        with pytest.raises(AssertionError) as exc:
            self.callCheckRequiredFieldsSet('c:/genre/1999, The Album', 'test test.m4a', ['artist'])
        exc.match('required field artist')

    def test_checkRequiredFields10(self):
        with pytest.raises(AssertionError) as exc:
            self.callCheckRequiredFieldsSet('c:/genre/1999, The Album', 'test test.m4a', ['discnumber'])
        exc.match('required field discnumber')

    # test RemoveRemasteredString
    def test_removeRemasteredRemoveVersion(self):
        assert 'test [Other] test' == RemoveRemasteredString().getProposedName('test [Other Version] test')

    def test_removeRemasteredDoNotRemoveIfNotWholeWord(self):
        assert 'test [OtherVersion] test' == RemoveRemasteredString().getProposedName('test [OtherVersion] test')

    def test_removeRemasteredRemoveEntireBracketedString(self):
        assert 'test test' == RemoveRemasteredString().getProposedName('test [Mono Version] test')

    def test_removeRemasteredRemoveEntireString(self):
        assert 'test test' == RemoveRemasteredString().getProposedName('test - Remastered Album Version test')

    def test_removeRemasteredRemoveYear(self):
        assert 'test test' == RemoveRemasteredString().getProposedName('test - 1999 Remaster test')

    def test_removeRemasteredRemoveYearAndDash(self):
        assert 'test test' == RemoveRemasteredString().getProposedName('test - 1999 - Remaster test')

    def test_removeRemasteredRemoveYearAndDashRemastered(self):
        assert 'test test' == RemoveRemasteredString().getProposedName('test - 1999 - Remastered test')

    def test_removeRemasteredRemoveYearAndDigital(self):
        assert 'test test' == RemoveRemasteredString().getProposedName('test - 1234 Digital Remaster test')

    def test_removeRemasteredRemoveYearAndDigitalAndDash(self):
        assert 'test test' == RemoveRemasteredString().getProposedName('test - 4321 - Digital Remaster test')

    def test_removeRemasteredRemoveYearAndDashDigitalRemastered(self):
        assert 'test test' == RemoveRemasteredString().getProposedName('test - 2111 - Digital Remastered test')

    # test getChoiceString
    def testGetChoiceStringTwoTitles(self):
        assert '(02:00)  (a1;; a2) title1 same lngth' == \
            getChoiceString(dict(
                duration_ms=120000, name='title1', artists=[dict(name='a1'), dict(name='a2')],
                track_number=2, disc_number=2), 120)

    def testGetChoiceStringOneTitle(self):
        assert '(02:05)  (a1) title1 same lngth' == \
            getChoiceString(dict(
                duration_ms=125000, name='title1', artists=[dict(name='a1')],
                track_number=2, disc_number=2), 120)

    def testGetChoiceStringRenderDurationLonger(self):
        assert '(02:09)  (a1) title1 lnger(9s)' == \
            getChoiceString(dict(
                duration_ms=129000, name='title1', artists=[dict(name='a1')],
                track_number=2, disc_number=2), 120)

    def testGetChoiceStringRenderDurationShorter(self):
        assert '(01:52)  (a1) title1 shrter(8s)' == \
            getChoiceString(dict(
                duration_ms=112000, name='title1', artists=[dict(name='a1')],
                track_number=2, disc_number=2), 120)

    # test renderRemoteAudio
    def test_renderRemoteAudioShowNoNumber(self):
        assert '(00:00)  (a1) title1' == \
            getStrRemoteAudio(dict(duration_ms=0, name='title1', artists=[dict(name='a1')],
            track_number=1, disc_number=2), False, False, '')

    def test_renderRemoteAudioShowTrackNumber(self):
        assert '(00:00) 01 (a1) title1' == \
            getStrRemoteAudio(dict(duration_ms=0, name='title1', artists=[dict(name='a1')],
            track_number=1, disc_number=2), False, True, '')

    def test_renderRemoteAudioShowTrackAndAlbumNumber(self):
        assert '(00:00) 02 01 (a1) title1' == \
            getStrRemoteAudio(dict(duration_ms=0, name='title1', artists=[dict(name='a1')],
            track_number=1, disc_number=2), True, True, '')

    def test_renderRemoteAudioSameArtistName(self):
        assert '(00:00)   title1' == \
            getStrRemoteAudio(dict(duration_ms=0, name='title1', artists=[dict(name='a1')],
            track_number=1, disc_number=2), False, False, 'a1')
