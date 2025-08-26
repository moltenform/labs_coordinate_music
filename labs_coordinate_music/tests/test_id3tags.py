# labs_coordinate_music
# Ben Fisher, 2016
# Released under the GNU General Public License version 3

import pytest
from os.path import join
from labs_coordinate_music.coordmusicutil import *
from labs_coordinate_music.tests import fixture_getmedia as fixture_getmedia_
fixture_getmedia = fixture_getmedia_

class TestLengthAndBitrate(object):
    # get duration; no tag object provided
    def test_getDurationWav(self, fixture_getmedia):
        assert 727 == int(1000 * get_audio_duration(join(fixture_getmedia, 'wav.wav')))
    
    def test_getDurationFlac(self, fixture_getmedia):
        assert 1023 == int(1000 * get_audio_duration(join(fixture_getmedia, 'flac.flac')))
    
    def test_getDurationM4a16(self, fixture_getmedia):
        assert 1160 == int(1000 * get_audio_duration(join(fixture_getmedia, 'm4a16.m4a')))

    def test_getDurationM4a128(self, fixture_getmedia):
        assert 1091 == int(1000 * get_audio_duration(join(fixture_getmedia, 'm4a128.m4a')))

    def test_getDurationM4a224(self, fixture_getmedia):
        assert 1091 == int(1000 * get_audio_duration(join(fixture_getmedia, 'm4a224.m4a')))

    def test_getDurationMp3Avg16(self, fixture_getmedia):
        assert 2773 == int(1000 * get_audio_duration(join(fixture_getmedia, 'mp3_avgb16.mp3')))

    def test_getDurationMp3Avg126(self, fixture_getmedia):
        assert 2773 == int(1000 * get_audio_duration(join(fixture_getmedia, 'mp3_avgb128.mp3')))

    def test_getDurationMp3Avg224(self, fixture_getmedia):
        assert 2773 == int(1000 * get_audio_duration(join(fixture_getmedia, 'mp3_avgb224.mp3')))

    def test_getDurationMp3Cns16(self, fixture_getmedia):
        assert 2873 == int(1000 * get_audio_duration(join(fixture_getmedia, 'mp3_cnsb16.mp3')))

    def test_getDurationMp3Cns128(self, fixture_getmedia):
        assert 2773 == int(1000 * get_audio_duration(join(fixture_getmedia, 'mp3_cnsb128.mp3')))

    def test_getDurationMp3Cns224(self, fixture_getmedia):
        assert 2773 == int(1000 * get_audio_duration(join(fixture_getmedia, 'mp3_cnsb224.mp3')))

    def test_getDurationOgg01(self, fixture_getmedia):
        assert 1591 == int(1000 * get_audio_duration(join(fixture_getmedia, 'ogg_01.ogg')))

    def test_getDurationOgg10(self, fixture_getmedia):
        assert 1591 == int(1000 * get_audio_duration(join(fixture_getmedia, 'ogg_10.ogg')))
    
    # get duration; tag object provided
    def test_getDurationFlacWithObj(self, fixture_getmedia):
        assert 1023 == int(1000 * get_audio_duration(join(fixture_getmedia, 'flac.flac'),
            CoordMusicAudioMetadata(join(fixture_getmedia, 'flac.flac'))))
    
    def test_getDurationM4a16WithObj(self, fixture_getmedia):
        assert 1160 == int(1000 * get_audio_duration(join(fixture_getmedia, 'm4a16.m4a'),
            CoordMusicAudioMetadata(join(fixture_getmedia, 'm4a16.m4a'))))

    def test_getDurationM4a128WithObj(self, fixture_getmedia):
        assert 1091 == int(1000 * get_audio_duration(join(fixture_getmedia, 'm4a128.m4a'),
            CoordMusicAudioMetadata(join(fixture_getmedia, 'm4a128.m4a'))))

    def test_getDurationM4a224WithObj(self, fixture_getmedia):
        assert 1091 == int(1000 * get_audio_duration(join(fixture_getmedia, 'm4a224.m4a'),
            CoordMusicAudioMetadata(join(fixture_getmedia, 'm4a224.m4a'))))

    def test_getDurationMp3Avg16WithObj(self, fixture_getmedia):
        assert 2773 == int(1000 * get_audio_duration(join(fixture_getmedia, 'mp3_avgb16.mp3'),
            CoordMusicAudioMetadata(join(fixture_getmedia, 'mp3_avgb16.mp3'))))

    def test_getDurationMp3Avg126WithObj(self, fixture_getmedia):
        assert 2773 == int(1000 * get_audio_duration(join(fixture_getmedia, 'mp3_avgb128.mp3'),
            CoordMusicAudioMetadata(join(fixture_getmedia, 'mp3_avgb128.mp3'))))

    def test_getDurationMp3Avg224WithObj(self, fixture_getmedia):
        assert 2773 == int(1000 * get_audio_duration(join(fixture_getmedia, 'mp3_avgb224.mp3'),
            CoordMusicAudioMetadata(join(fixture_getmedia, 'mp3_avgb224.mp3'))))

    def test_getDurationMp3Cns16WithObj(self, fixture_getmedia):
        assert 2873 == int(1000 * get_audio_duration(join(fixture_getmedia, 'mp3_cnsb16.mp3'),
            CoordMusicAudioMetadata(join(fixture_getmedia, 'mp3_cnsb16.mp3'))))

    def test_getDurationMp3Cns128WithObj(self, fixture_getmedia):
        assert 2773 == int(1000 * get_audio_duration(join(fixture_getmedia, 'mp3_cnsb128.mp3'),
            CoordMusicAudioMetadata(join(fixture_getmedia, 'mp3_cnsb128.mp3'))))

    def test_getDurationMp3Cns224WithObj(self, fixture_getmedia):
        assert 2773 == int(1000 * get_audio_duration(join(fixture_getmedia, 'mp3_cnsb224.mp3'),
            CoordMusicAudioMetadata(join(fixture_getmedia, 'mp3_cnsb224.mp3'))))

    def test_getDurationOgg01WithObj(self, fixture_getmedia):
        assert 1591 == int(1000 * get_audio_duration(join(fixture_getmedia, 'ogg_01.ogg'),
            CoordMusicAudioMetadata(join(fixture_getmedia, 'ogg_01.ogg'))))

    def test_getDurationOgg10WithObj(self, fixture_getmedia):
        assert 1591 == int(1000 * get_audio_duration(join(fixture_getmedia, 'ogg_10.ogg'),
            CoordMusicAudioMetadata(join(fixture_getmedia, 'ogg_10.ogg'))))
        
    # get empirical bitrate
    def test_getBitrateM4a16(self, fixture_getmedia):
        assert 29 == int(get_empirical_bitrate(join(fixture_getmedia, 'm4a16.m4a')))
    
    def test_getBitrateMp3128(self, fixture_getmedia):
        assert 136 == int(get_empirical_bitrate(join(fixture_getmedia, 'mp3_avgb128.mp3')))
    
    def test_getBitrateMp3224(self, fixture_getmedia):
        assert 233 == int(get_empirical_bitrate(join(fixture_getmedia, 'mp3_cnsb224.mp3')))

    # unsupported types
    def test_getDurationUnknownExtension(self, fixture_getmedia):
        with pytest.raises(ValueError) as exc:
            get_audio_duration(join(fixture_getmedia, 'unknown.awav'))
        exc.match('unsupported extension')
    
    def test_getDurationNoExtension(self, fixture_getmedia):
        with pytest.raises(ValueError) as exc:
            get_audio_duration(join(fixture_getmedia, 'no extension'))
        exc.match('unsupported extension')
    
    def test_getBitrateUnknownExtension(self, fixture_getmedia):
        with pytest.raises(ValueError) as exc:
            get_empirical_bitrate(join(fixture_getmedia, 'unknown.awav'))
        exc.match('unsupported extension')
    
    def test_getBitrateNoExtension(self, fixture_getmedia):
        with pytest.raises(ValueError) as exc:
            get_empirical_bitrate(join(fixture_getmedia, 'no extension'))
        exc.match('unsupported extension')

class TestSettingTags(object):
    def getFieldsToSet(self):
        return dict(album=u'album\u1101!', comment=u'comment!', artist=u'artist!', title=u'title!',
            composer=u'composer!', albumartist=u'albumartist!', website=u'http://website!',
            discnumber=10, tracknumber=20)
    
    def iterMediaWithTags(self, d):
        return ((full, short) for full, short in files.listFiles(d) if not short.endswith('.wav'))
        
    def test_id23DiffersFromId24(self, fixture_getmedia):
        files.makeDirs(join(fixture_getmedia, 'id3'))
        files.copy(join(fixture_getmedia, 'mp3_avgb128.mp3'), join(fixture_getmedia, 'id3', 'id23.mp3'), True)
        files.copy(join(fixture_getmedia, 'mp3_avgb128.mp3'), join(fixture_getmedia, 'id3', 'id24.mp3'), True)
        o23 = EasyPythonMutagen(join(fixture_getmedia, 'id3', 'id23.mp3'), use_id3_v23=True)
        o23.set('title', 'test')
        o23.save()
        o24 = EasyPythonMutagen(join(fixture_getmedia, 'id3', 'id24.mp3'), use_id3_v23=False)
        o24.set('title', 'test')
        o24.save()
        assert files.computeHash(join(fixture_getmedia, 'id3', 'id23.mp3')) != files.computeHash(join(fixture_getmedia, 'id3', 'id24.mp3'))
    
    def test_tagUnknownExtension(self, fixture_getmedia):
        with pytest.raises(ValueError) as exc:
            EasyPythonMutagen(join(fixture_getmedia, 'unknown.awav'))
        exc.match('unsupported')
    
    def test_tagNoExtension(self, fixture_getmedia):
        with pytest.raises(ValueError) as exc:
            EasyPythonMutagen(join(fixture_getmedia, 'no extension'))
        exc.match('unsupported')
    
    def test_gettingUnsetTagShouldFail(self, fixture_getmedia):
        for full, short in self.iterMediaWithTags(fixture_getmedia):
            obj = EasyPythonMutagen(full)
            with pytest.raises(KeyError):
                obj.get('composer')
    
    def test_gettingInvalidTagShouldFail(self, fixture_getmedia):
        for full, short in self.iterMediaWithTags(fixture_getmedia):
            obj = EasyPythonMutagen(full)
            # workaround for mutagen bug in easymp4.py, line 183 EasyMP4KeyError("%r is not a valid key" % key)
            extype = Exception if full.endswith('.m4a') else KeyError
            with pytest.raises(extype):
                obj.get('aartist')
    
    def test_settingInvalidTagShouldFail(self, fixture_getmedia):
        for full, short in self.iterMediaWithTags(fixture_getmedia):
            obj = EasyPythonMutagen(full)
            extype = Exception if full.endswith('.m4a') else KeyError
            with pytest.raises(extype):
                obj.set('aartist', 'test')
    
    def test_allTagsShouldBeEmptyWhenNotSet(self, fixture_getmedia):
        for full, short in self.iterMediaWithTags(fixture_getmedia):
            obj = EasyPythonMutagen(full)
            for field in self.getFieldsToSet():
                assert obj.get_or_default(field, None) is None
        
    def test_roundTripAllTags(self, fixture_getmedia):
        dir = join(fixture_getmedia, 'modified')
        files.makeDirs(dir)
        for full, short in self.iterMediaWithTags(fixture_getmedia):
            # set every field
            files.copy(full, join(dir, short), True)
            obj = EasyPythonMutagen(join(dir, short))
            for field, val in self.getFieldsToSet().items():
                obj.set(field, val)
                assert obj.get(field) == ustr(val)
            
            # append to fields
            obj.save()
            obj = EasyPythonMutagen(join(dir, short))
            for field, val in self.getFieldsToSet().items():
                assert obj.get(field) == ustr(val)
                if 'number' not in field:
                    obj.set(field, ustr(val) + 'appended')
            
            # verify fields
            obj.save()
            obj = EasyPythonMutagen(join(dir, short))
            for field, val in self.getFieldsToSet().items():
                if 'number' not in field:
                    assert obj.get(field) == ustr(val) + 'appended'
