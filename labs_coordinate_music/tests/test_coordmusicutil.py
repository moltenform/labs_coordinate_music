# labs_coordinate_music
# Ben Fisher, 2016
# Released under the GNU General Public License version 3

import pytest
from os.path import join
from labs_coordinate_music import coordmusictools
from labs_coordinate_music.tests import *
from labs_coordinate_music.coordmusicutil import *


class TestMusicUtils(object):
    # format duration
    def test_getDurationUsual(self):
        assert '02:01' == getFormattedDuration(121)
        
    def test_getDurationZeroSeconds(self):
        assert '00:00' == getFormattedDuration(0)

    def test_getDurationShouldTruncateMilliseconds(self):
        assert '02:01' == getFormattedDuration(121.75)

    def test_getDurationShouldNotWrapPast12(self):
        assert '13:10' == getFormattedDuration(790)

    def test_getDurationUsualWithMilli(self):
        assert '02:01:000' == getFormattedDuration(121, True)

    def test_getDurationZeroSecondsWithMilli(self):
        assert '00:00:000' == getFormattedDuration(0, True)

    def test_getDurationAddTrailingZeros(self):
        assert '02:01:750' == getFormattedDuration(121.75, True)

    def test_getDurationOnlyOneMillisecond(self):
        assert '12:13:001' == getFormattedDuration(733.001, True)

    def test_getDurationAlmostFullSecond(self):
        assert '12:13:999' == getFormattedDuration(733.999, True)
    
    # test getFieldForFile
    def test_getFieldMp3Capital(self):
        assert getFieldForFile(r'/dir/test.MP3') == 'website'

    def test_getFieldMp3(self):
        assert getFieldForFile(r'/dir/test.mp3') == 'website'

    def test_getFieldM4a(self):
        assert getFieldForFile(r'/dir/test.m4a') == 'description'

    def test_getFieldFlac(self):
        assert getFieldForFile(r'/dir/test.flac') == 'desc'

    def test_getFieldMp4(self):
        with pytest.raises(AssertionError):
            getFieldForFile(r'/dir/test.mp4')

    def test_getFieldOgg(self):
        with pytest.raises(AssertionError):
            getFieldForFile(r'/dir/test.ogg')

    def test_getFieldNoExtension(self):
        with pytest.raises(AssertionError):
            getFieldForFile(r'/dir/test')
    
class TestCoordMusicAudioMetadata(object):
    def test_m4aToUrl(self, fixture_getmedia):
        files.makeDirs(join(fixture_getmedia, 'toUrl'))
        files.copy(join(fixture_getmedia, 'm4a24.m4a'), join(fixture_getmedia, 'toUrl', 'test.m4a'), True)
        stampM4a(join(fixture_getmedia, 'toUrl', 'test.m4a'), 'spotify:test')
        obj = CoordMusicAudioMetadata(join(fixture_getmedia, 'toUrl', 'test.m4a'))
        m4aToUrl(join(fixture_getmedia, 'toUrl'), 'test.m4a', obj, False)
        assert 'spotify:test' == getFromUrlFile(join(fixture_getmedia, 'toUrl', 'test.url'))
    
    def test_settingTrackNumberShouldOnlyKeepFirstPart(self, fixture_getmedia):
        files.makeDirs(join(fixture_getmedia, 'setTag'))
        files.copy(join(fixture_getmedia, 'm4a24.m4a'), join(fixture_getmedia, 'setTag', 'setTrack.m4a'), True)
        obj = CoordMusicAudioMetadata(join(fixture_getmedia, 'setTag', 'setTrack.m4a'))
        obj.set('track_number', '3/13')
        obj.save()
        obj = CoordMusicAudioMetadata(join(fixture_getmedia, 'setTag', 'setTrack.m4a'))
        assert '3' == obj.get('track_number')
    
    def test_settingTitleTag(self, fixture_getmedia):
        files.makeDirs(join(fixture_getmedia, 'setTag'))
        files.copy(join(fixture_getmedia, 'm4a24.m4a'), join(fixture_getmedia, 'setTag', 'setTitle.m4a'), True)
        obj = CoordMusicAudioMetadata(join(fixture_getmedia, 'setTag', 'setTitle.m4a'))
        obj.set('title', u'title\u1101')
        obj.save()
        obj = CoordMusicAudioMetadata(join(fixture_getmedia, 'setTag', 'setTitle.m4a'))
        assert u'title\u1101' == obj.get('title')
    
    def test_setLink(self, fixture_getmedia):
        dir = join(fixture_getmedia, 'setLink')
        files.makeDirs(dir)
        for full, short in files.listFiles(fixture_getmedia):
            if not short.endswith('.ogg') and not short.endswith('.wav'):
                files.copy(full, join(dir, short), True)
                stampM4a(join(dir, short), 'spotify:1234')
                obj = CoordMusicAudioMetadata(join(dir, short))
                assert 'spotify:1234' == obj.getLink()
    
    def test_callingGetLinkBeforeLinkIsSetReturnEmptyString(self, fixture_getmedia):
        obj = CoordMusicAudioMetadata(join(fixture_getmedia, 'm4a24.m4a'))
        assert '' == obj.getLink()
    
    def test_cannotGetUrlFromWav(self, fixture_getmedia):
        with pytest.raises(AssertionError):
            getFromUrlFile(join(fixture_getmedia, 'wav.wav'))
    
    def test_makeUrlFileHttp(self, fixture_dir):
        writeUrlFile(join(fixture_dir, 'test1.url'), 'https://www.youtube.com/watch?v=0OSF')
        assert 'https://www.youtube.com/watch?v=0OSF' == getFromUrlFile(join(fixture_dir, 'test1.url'))
    
    def test_makeUrlFileSpotify(self, fixture_dir):
        writeUrlFile(join(fixture_dir, 'test1.url'), 'spotify:track:0Svkvt5I79wficMFgaqEQJ')
        assert 'spotify:track:0Svkvt5I79wficMFgaqEQJ' == getFromUrlFile(join(fixture_dir, 'test1.url'))
    
    def test_makeUrlFileFileAlreadyExists(self, fixture_dir):
        writeUrlFile(join(fixture_dir, 'test1.url'), 'spotify:track:0Svkvt5I79wficMFgaqEQJ')
        with pytest.raises(AssertionError):
            writeUrlFile(join(fixture_dir, 'test1.url'), 'spotify:track:0Svkvt5I79wficMFgaqEQJ')
    
    def test_readVideoUrlNone(self):
        assert None is videoUrlFromFile(None)
    
    def test_readVideoUrlEmpty(self):
        assert None is videoUrlFromFile('')
    
    def test_readVideoUrlShort(self):
        assert None is videoUrlFromFile('abc')
    
    def test_readVideoUrlLong(self):
        assert None is videoUrlFromFile('abcabcabcabcabc')
    
    def test_readVideoUrlWhitespace1(self):
        assert None is videoUrlFromFile('a b c d e f')
    
    def test_readVideoUrlWhitespace2(self):
        assert None is videoUrlFromFile('te xt. [a b c d e f] te xt.')
    
    def test_readVideoUrlValid1(self):
        assert 'https://www.youtube.com/watch?v=aabbccddeef' == videoUrlFromFile('aabbccddeef')
    
    def test_readVideoUrlValid2(self):
        assert 'https://www.youtube.com/watch?v=aabbccddeef' == videoUrlFromFile('te xt. [aabbccddeef] te xt.')
    
    def test_readVideoUrlValid3(self):
        assert 'https://www.youtube.com/watch?v=aa--CC__eef' == videoUrlFromFile('aa--CC__eef')
    
    def test_readVideoUrlValid4(self):
        assert 'https://www.youtube.com/watch?v=aa--CC__eef' == videoUrlFromFile('te xt. [aa--CC__eef] te xt.')
    
class TestFilenamesToText(object):
    def test_filenamesToText(self, fixture_dir, fixture_getmedia):
        writeUrlFile(join(fixture_dir, 'test1.url'), 'https://www.youtube.com/watch?v=0OSF')
        writeUrlFile(join(fixture_dir, 'test2.url'), 'spotify:track:0Svkvt5I79wficMFgaqEQJ')
        files.copy(join(fixture_getmedia, 'flac.flac'), join(fixture_dir, 'flac.flac'), True)
        files.copy(join(fixture_getmedia, 'm4a128.m4a'), join(fixture_dir, 'm4a.m4a'), True)
        files.copy(join(fixture_getmedia, 'mp3_avgb128.mp3'), join(fixture_dir, 'mp3.mp3'), True)
        info = coordmusictools.CoordMusicAudioMetadata(join(fixture_dir, 'flac.flac'))
        info.set('title', 'Title')
        info.set('album', 'Album')
        info.save()
        stampM4a(join(fixture_dir, 'm4a.m4a'), 'spotify:track:abcdefg')
        
        coordmusictools.saveFilenamesMetadataToText(
            sorted(files.listFiles(fixture_dir, allowedExts=['url', 'flac', 'mp3', 'm4a'])),
            False,
            join(fixture_dir, 'out.txt'),
            requestBatchSize=3)
        expected = u'''%dir%flac.flac	00:01:023	790	Album	0
%dir%m4a.m4a	00:01:091	142	abcdefg	0
%dir%mp3.mp3	00:02:773	136	0
%dir%test1.url	00:00:000	0	https://www.youtube.com/watch?v=0OSF	0
%dir%test2.url	00:00:000	0	0Svkvt5I79wficMFgaqEQJ	0
'''.replace('%dir%', fixture_dir + files.sep).replace('\r\n', '\n').replace('\n', '\t\n')
        got = files.readAll(join(fixture_dir, 'out.txt'), 'r', 'utf-8-sig')
        got = got.replace('\r\n', '\n').replace('\t\t', '\t').replace('\t\t', '\t').replace('\t\t', '\t')
        assert expected == got
