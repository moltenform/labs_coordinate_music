from coordmusicutil import *
import unittest

dirtestmedia = getTestMediaLocation()+files.sep+'media'+files.sep
tmpdir = getTestTempLocation()+files.sep+'test'
tmpdirsl = tmpdir+files.sep

def cleardirectoryfiles(d):
    files.rmtree(d)
    files.makedirs(d)
    assertTrue(files.isemptydir(d))

def testsOrganize():
    from main import parseAFilename, getNewnameFromTag, bnsplitext, renderAFilename, doStringsMatchForField, \
    fillFieldsFromContext, checkDeleteUrlsInTheWayOfM4as, checkForLowBitratesFile, checkFilenameIrregularitiesLookForInconsistency,\
    checkUrlContents, CheckFileExtensions, checkDuplicatedTrackNumbers, Namestyle, checkStyleConsistency, checkRequiredFieldsSet
    def resToString(obj):
        return ';'.join(key+'='+str(object.__getattribute__(obj, key)) 
            for key in dir(obj) if (not key.startswith('_') and key!='short' and key!='album'))

    # test parseAFilename
    assertEq('artist=testart;discnumber=1;style=DiscTrackArtistTitle;title=testtitle;tracknumber=2', 
        resToString(parseAFilename('01 02 testart - testtitle.m4a')))
    assertEq('artist=test-art 01;discnumber=1;style=DiscTrackArtistTitle;title=testtitle 01;tracknumber=2', 
        resToString(parseAFilename('01 02 test-art 01 - testtitle 01 (^).m4a')))
    assertEq('artist=None;discnumber=1;style=DiscTrackTitle;title=j-ust name;tracknumber=2', 
        resToString(parseAFilename('01 02 j-ust name.m4a')))
    assertEq('artist=art art;discnumber=None;style=TrackArtistTitle;title=title title;tracknumber=12', 
        resToString(parseAFilename('12 art art - title title.m4a')))
    assertEq('artist=None;discnumber=None;style=TrackTitle;title=title title;tracknumber=12', 
        resToString(parseAFilename('12 title title.m4a')))
    assertEq('artist=art art;discnumber=None;style=ArtistTitle;title=title title;tracknumber=None', 
        resToString(parseAFilename('art art - title title.m4a')))
    assertEq('artist=None;discnumber=None;style=Title;title=title title;tracknumber=None', 
        resToString(parseAFilename('title title.m4a')))
        
    # test parseAFilename round trip
    tests = ['01 02 testart - testtitle.m4a', '01 02 test-art 01 - testtitle 01 (^).m4a','01 02 j-ust name.m4a',
        '12 art art - title title.m4a', '12 title title.m4a', 'art art - title title.m4a', 'title title.m4a']
    for test in tests:
        parsed = parseAFilename(test)
        backToName = renderAFilename(parsed, test)
        assertEq(test, backToName)
        
    # test getNewnameFromTag
    parsed = parseAFilename('01 02 testart - testtitle.sv.m4a')
    assertEq('01 02 testart changed - testtitle.sv.m4a', getNewnameFromTag(parsed, 'artist', parsed.artist, 'testart changed'))
    assertEq('01 02 testart - testtitle changed.sv.m4a', getNewnameFromTag(parsed, 'title', parsed.title, 'testtitle changed'))
    assertEq('01 09 testart - testtitle.sv.m4a', getNewnameFromTag(parsed, 'tracknumber', parsed.tracknumber, 9))
    assertEq('01 09 testart - testtitle.sv.m4a', getNewnameFromTag(parsed, 'tracknumber', parsed.tracknumber, '9'))
    assertEq('01 09 testart - testtitle.sv.m4a', getNewnameFromTag(parsed, 'tracknumber', parsed.tracknumber, '9/9'))
    assertEq('01 02 (None) - testtitle.sv.m4a', getNewnameFromTag(parsed, 'artist', parsed.artist, None))
    assertEq('01 02 bad-char - testtitle.sv.m4a', getNewnameFromTag(parsed, 'artist', parsed.artist, 'bad:char'))
        
    # test bnsplitext
    assertEq(('test', '.mp3'), bnsplitext('test.mp3'))
    assertEq(('t.est', '.mp3'), bnsplitext('t.est.mp3'))
    assertEq(('test word', '.mp3'), bnsplitext('test word.mp3'))
    assertEq(('test word 12)', '.mp3'), bnsplitext('test word 12).mp3'))
    assertEq(('test word(12)', '.mp3'), bnsplitext('test word(12).mp3'))
    assertEq(('test is', ' (12).mp3'), bnsplitext('test is (12).mp3'))
    assertEq(('test is', ' (09).mp3'), bnsplitext('test is (09).mp3'))
    assertEq(('test is', ' (09).m4a'), bnsplitext('test is (09).m4a'))
    assertEq(('test not savesv', '.mp3'), bnsplitext('test not savesv.mp3'))
    assertEq(('test save', '.sv.mp3'), bnsplitext('test save.sv.mp3'))
    assertEq(('test.save', '.sv.mp3'), bnsplitext('test.save.sv.mp3'))
    assertEq(('test save ', '.sv.mp3'), bnsplitext('test save .sv.mp3'))
    assertEq(('test save', '.movetosv.mp3'), bnsplitext('test save.movetosv.mp3'))
    assertEq(('test notsave.nsv', '.mp3'), bnsplitext('test notsave.nsv.mp3'))
    assertEq(('test both', ' (12).sv.mp3'), bnsplitext('test both (12).sv.mp3'))
    
    # test doStringsMatchForField
    assertTrue(doStringsMatchForField('a', 'a', 'field'))
    assertTrue(doStringsMatchForField('a a aa a a', u'a a aa a a', 'field'))
    assertTrue(not doStringsMatchForField('a', 'b', 'field'))
    assertTrue(doStringsMatchForField('test\'test', u'test\u2019test', 'field'))
    assertTrue(doStringsMatchForField('a-b', 'a\\b', 'field'))
    assertTrue(doStringsMatchForField('a, b', 'a/ b', 'field'))
    assertTrue(doStringsMatchForField('a-b', 'a/b', 'field'))
    assertTrue(doStringsMatchForField('ab', 'a*b', 'field'))
    assertTrue(doStringsMatchForField('a\'b', 'a"b', 'field'))
    assertTrue(not doStringsMatchForField('01', '1', 'title'))
    assertTrue(doStringsMatchForField('01', '1', 'tracknumber'))
    assertTrue(doStringsMatchForField('01', '1', 'discnumber'))
    assertTrue(not doStringsMatchForField('a (^)', 'a', 'field'))
    assertTrue(doStringsMatchForField('a (^)', 'a', 'title'))
    
    def testFillFieldsFromContextArtist(expected, fullpath):
        parsed = Bucket(album='a', artist=None, discnumber=None)
        fillFieldsFromContext(parsed, fullpath, fullpath.split('/'), helpers)
        assertEq(expected, parsed.artist)
        
    def testFillFieldsFromContextAlbum(expected, fullpath):
        parsed = Bucket(album=None, artist='a', discnumber=None)
        fillFieldsFromContext(parsed, fullpath, fullpath.split('/'), helpers)
        assertEq(expected, parsed.album)
        
    # test fillFieldsFromContext artist
    helpers = Bucket(splroot='c:/music'.split('/'))
    assertException(lambda: testFillFieldsFromContextArtist('','c:/music'), AssertionError, 'not within artist directory')
    assertException(lambda: testFillFieldsFromContextArtist('','c:/music/genre'), AssertionError, 'not within artist directory')
    testFillFieldsFromContextArtist('Artist Name', 'c:/music/genre/Artist Name')
    testFillFieldsFromContextArtist('Artist Name', 'c:/music/genre/Artist Name/1999, The Album')
    testFillFieldsFromContextArtist('Artist Name', 'c:/music/genre/Other Artist/1999, Artist Name - The Album')
    testFillFieldsFromContextArtist('Artist Name', 'c:/music/genre/Other Artist/Artist Name - The Album')
    testFillFieldsFromContextArtist('Artist Name', 'c:/music/genre/Other Artist/Artist Name')
    testFillFieldsFromContextArtist('Artist Name', 'c:/music/genre/Other Artist/Artist Name/1999, The Album')
    testFillFieldsFromContextArtist('Artist Name', 'c:/music/genre/Other Artist/Other/1999, Artist Name - The Album')
    
    # test fillFieldsFromContext album
    testFillFieldsFromContextAlbum(None, 'c:/music')
    testFillFieldsFromContextAlbum(None, 'c:/music/genre')
    testFillFieldsFromContextAlbum(None, 'c:/music/genre/Artist Name')
    testFillFieldsFromContextAlbum('The Album', 'c:/music/genre/Artist Name/1999, The Album')
    testFillFieldsFromContextAlbum('The Album', 'c:/music/genre/Other Artist/1999, Artist Name - The Album')
    testFillFieldsFromContextAlbum('The Album', 'c:/music/genre/Other Artist/Artist Name - The Album')
    testFillFieldsFromContextAlbum(None, 'c:/music/genre/Other Artist/Artist Name')
    testFillFieldsFromContextAlbum('The Album', 'c:/music/genre/Other Artist/Artist Name/1999, The Album')
    testFillFieldsFromContextAlbum('The Album', 'c:/music/genre/Other Artist/Other/1999, Artist Name - The Album')

    # test parseDirname
    testFillFieldsFromContextArtist('199, Artist Name', 'c:/music/genre/Other Artist/199, Artist Name')
    testFillFieldsFromContextArtist(', Artist Name', 'c:/music/genre/Other Artist/, Artist Name')
    testFillFieldsFromContextAlbum('Alb - Alb', 'c:/music/genre/Other Artist/Artist Name - Alb - Alb')
    testFillFieldsFromContextAlbum('Alb - Alb', 'c:/music/genre/Other Artist/1999, Artist Name - Alb - Alb')

    # test filename checks.
    if not files.exists(tmpdir):
        files.makedirs(tmpdir)	

    def getShorts():
        return sorted([file[1] for file in files.listfiles(tmpdir)])
        
    # test checkDeleteUrlsInTheWayOfM4as
    cleardirectoryfiles(tmpdir)
    files.writeall(tmpdirsl + 'test ok.url', '')
    files.writeall(tmpdirsl + 'test conflict.url', '')
    files.writeall(tmpdirsl + 'test conflict.m4a', '')
    assertEq(u'test conflict.m4a;test conflict.url;test ok.url', ';'.join(getShorts()))
    assertException(lambda: checkDeleteUrlsInTheWayOfM4as(tmpdir, getShorts()), StopBecauseWeRenamedFile)
    assertEq(u'test conflict.m4a;test ok.url', ';'.join(getShorts()))
    
    # test checkForLowBitrates
    assertEq('makeurl', checkForLowBitratesFile(tmpdir, 100, Bucket(short='file marked to makeurl (vv).m4a')))
    assertEq('makeurl', checkForLowBitratesFile(tmpdir, 16, Bucket(short='file marked to makeurl (vv).m4a')))
    assertEq('delete', checkForLowBitratesFile(tmpdir, 18, Bucket(short='lowbitrate.m4a')))
    assertEq('makeurl', checkForLowBitratesFile(tmpdir, 26, Bucket(short='lowbitrate.m4a')))
    assertEq(None, checkForLowBitratesFile(tmpdir, 64, Bucket(short='mediumbitrate.m4a')))
    assertEq(None, checkForLowBitratesFile(tmpdir, 64, Bucket(short='mediumbitrate.mp3')))
    assertEq(None, checkForLowBitratesFile(tmpdir, 16, Bucket(short='saved.movetosv.mp3')))
    assertEq(None, checkForLowBitratesFile(tmpdir, 16, Bucket(short='saved.sv.mp3')))
    assertEq(None, checkForLowBitratesFile(tmpdir, 16, Bucket(short='saved.sv.m4a')))
    
    # test checkFilenameIrregularities
    assertEq((False, False), checkFilenameIrregularitiesLookForInconsistency(tmpdir, []))
    assertEq((False, False), checkFilenameIrregularitiesLookForInconsistency(tmpdir, ['title1.m4a','title-2.m4a']))
    assertEq((False, False), checkFilenameIrregularitiesLookForInconsistency(tmpdir, ['a - title1.m4a','b - title 2.m4a']))
    assertEq((False, True), checkFilenameIrregularitiesLookForInconsistency(tmpdir, ['a title1.m4a','b - title 2.m4a']))
    assertEq((False, True), checkFilenameIrregularitiesLookForInconsistency(tmpdir, ['a - title1.m4a','b title 2.m4a', 'c 3.m4a']))
    assertException(lambda: checkFilenameIrregularitiesLookForInconsistency('c:/dir - toomany - dashes', []), AssertionError, 'too many')
    assertException(lambda: checkFilenameIrregularitiesLookForInconsistency(tmpdir, ['a - a - b.m4a']), AssertionError, 'too many')
    assertException(lambda: checkFilenameIrregularitiesLookForInconsistency(tmpdir, ['a'*300+'m4a']), AssertionError, 'dangerously long')
    
    # test checkUrlContents
    cleardirectoryfiles(tmpdir)
    writeUrlFile(tmpdirsl+'test1.url', 'https://www.youtube.com/watch?v=0OSF')
    writeUrlFile(tmpdirsl+'test2.url', 'spotify:track:0Svkvt5I79wficMFgaqEQJ')
    checkUrlContents(tmpdir, getShorts())
    writeUrlFile(tmpdirsl+'test3.url', '', '', True)
    assertException(lambda: checkUrlContents(tmpdir, getShorts()), AssertionError, 'not retrieve')
    writeUrlFile(tmpdirsl+'test3.url', 'spotify:notfound', '', True)
    assertException(lambda: checkUrlContents(tmpdir, getShorts()), AssertionError, 'must point')
    writeUrlFile(tmpdirsl+'test3.url', 'spotify:local:5d3642ab', '', True)
    assertException(lambda: checkUrlContents(tmpdir, getShorts()), AssertionError, 'local')
    writeUrlFile(tmpdirsl+'test3.url', 'spotify:boinjyboing', '', True)
    assertException(lambda: checkUrlContents(tmpdir, getShorts()), AssertionError, 'user')
        
    # test CheckFileExtensions
    obj = CheckFileExtensions()
    d = tmpdir
    assertEq('mp3', obj.check(d, 'file test.mp3'))
    assertEq('mp3', obj.check(d, 'file.m4a. test.mp3'))
    assertEq('mp3', obj.check(d, 'c:/a/b/file.m4a.test.sv.mp3'))
    assertException(lambda: obj.check(d, 'no extension'), AssertionError, 'no extension')
    assertException(lambda: obj.check(d, 'file test.MP3'), AssertionError, 'lowercase')
    assertException(lambda: obj.check(d, 'file test.test'), AssertionError, 'unsupported')
    assertException(lambda: obj.check(d, 'file test.mp31'), AssertionError, 'unsupported')
    
    # test checkDuplicatedTrackNumbers
    def makeMockParsed(discnumber, tracknumber, artist=None, title=None):
        return Bucket(style=Namestyle.TrackTitle, short=0,discnumber=discnumber, tracknumber=tracknumber, 
            artist=artist if artist else getRandomString(), title=title if title else getRandomString())
    checkDuplicatedTrackNumbers(d, [makeMockParsed(1,1)])
    checkDuplicatedTrackNumbers(d, [makeMockParsed(1,1), makeMockParsed(2,1)])
    checkDuplicatedTrackNumbers(d, [makeMockParsed(1,5), makeMockParsed(1,6)])
    assertException(lambda: checkDuplicatedTrackNumbers(d,[makeMockParsed(1,0)]), AssertionError, 'not be 0')
    assertException(lambda: checkDuplicatedTrackNumbers(d,[makeMockParsed(0,1)]), AssertionError, 'not be 0')
    assertException(lambda: checkDuplicatedTrackNumbers(d,[makeMockParsed(1,1), makeMockParsed(2,4), makeMockParsed(2,4)]), AssertionError, 'duplicate')
    assertException(lambda: checkDuplicatedTrackNumbers(d,[makeMockParsed(1,1), makeMockParsed(2,4), makeMockParsed(1,1)]), AssertionError, 'duplicate')
    assertException(lambda: checkDuplicatedTrackNumbers(d,[makeMockParsed(1,1,'a','t'), makeMockParsed(1,2,'a','t')]), AssertionError, 'duplicate artist+title')
    
    # test checkStyleConsistency
    checkStyleConsistency(d,[Bucket(short=0,style='style1')])
    checkStyleConsistency(d,[Bucket(short=0,style='style1'), Bucket(short=0,style='style1')])
    assertException(lambda: checkStyleConsistency(d,[Bucket(short=0,style='style1'), Bucket(short=0,style='style2')]), AssertionError)
    assertException(lambda: checkStyleConsistency(d,[Bucket(short=0,style='style1'), Bucket(short=0,style='style1'), Bucket(short=0,style='style2')]), AssertionError)
    
    # test checkRequiredFieldsSet
    class MockTag(object):
        def __init__(self, short, keysmissing=None):
            self.short = short
            self.fields = dict(album='sampledata', style = 'sampledata', discnumber = '1', tracknumber = '1', artist = 'sampledata', title = 'sampledata')
            for key in keysmissing if keysmissing else []:
                self.fields[key] = None
        def get(self, key):
            return self.fields[key]
        def getLink(self):
            return 'spotify:track:0Svkvt5I79wficMFgaqEQJ'
    def testCheckRequiredFieldsSet(dir, short, fieldsmissing):
        checkRequiredFieldsSet(dir, dir.split('/'), [MockTag(short, fieldsmissing)], [Bucket(style='')])
    
    testCheckRequiredFieldsSet('c:/test/1999, The Album', '01 test test.m4a', fieldsmissing=[])
    testCheckRequiredFieldsSet('c:/test/1999, The Album', 'test test.url', fieldsmissing=['artist'])
    testCheckRequiredFieldsSet('c:/test/1999, The Album Selections', 'test test.m4a', fieldsmissing=['tracknumber'])
    testCheckRequiredFieldsSet('c:/test', 'test test.m4a', fieldsmissing=['tracknumber'])
    testCheckRequiredFieldsSet('c:/test', '1234 test test.m4a', fieldsmissing=['tracknumber'])
    assertException(lambda: testCheckRequiredFieldsSet('c:/test', '01 test test.m4a', []), AssertionError, 'outside of album')
    assertException(lambda: testCheckRequiredFieldsSet('c:/test', '01 test test.url', []), AssertionError, 'outside of album')
    assertException(lambda: testCheckRequiredFieldsSet('c:/test/1999, The Album', 'test test.m4a', ['tracknumber']),AssertionError, 'required field tracknumber')
    assertException(lambda: testCheckRequiredFieldsSet('c:/test/1999, The Album', 'test test.m4a', ['artist']), AssertionError, 'required field artist')
    assertException(lambda: testCheckRequiredFieldsSet('c:/test/1999, The Album', 'test test.m4a', ['discnumber']), AssertionError, 'required field discnumber')
    

class EasyPythonMutagenComponentTests(unittest.TestCase):
    def setUp(self):
        import os
        import shutil
        import tempfile
        
        # create an empty directory
        self.tmpdir = tempfile.gettempdir()+'/testeasypythonmutagen'
        if os.path.exists(self.tmpdir):
            shutil.rmtree(self.tmpdir)
        os.makedirs(self.tmpdir)
        
        # copy test media to the directory
        if not os.path.exists('./test/media/flac.flac'):
            raise RuntimeError('could not find test media.')
            
        testfiles = ['flac.flac', 'm4a128.m4a', 'm4a16.m4a', 'm4a224.m4a', 'mp3_avgb128.mp3', 
            'mp3_avgb16.mp3', 'mp3_avgb224.mp3', 'mp3_cnsb128.mp3', 'mp3_cnsb16.mp3', 'mp3_cnsb224.mp3',
            'ogg_01.ogg', 'ogg_10.ogg']
        for file in testfiles:
            shutil.copy('./test/media/'+file, self.tmpdir+'/'+file)

    def tearDown(self):
        import os
        import shutil
        if 'testeasypythonmutagen' in self.tmpdir and os.path.exists(self.tmpdir):
            shutil.rmtree(self.tmpdir)
    
    def test_lengthAndBitrate(self):
        # get duration; no tag object provided
        tmpdirsl = self.tmpdir+'/'
        self.assertEqual(1023, int(1000*get_audio_duration(tmpdirsl+'flac.flac')))
        self.assertEqual(1160, int(1000*get_audio_duration(tmpdirsl+'m4a16.m4a')))
        self.assertEqual(1091, int(1000*get_audio_duration(tmpdirsl+'m4a128.m4a')))
        self.assertEqual(1091, int(1000*get_audio_duration(tmpdirsl+'m4a224.m4a')))
        self.assertEqual(2773, int(1000*get_audio_duration(tmpdirsl+'mp3_avgb16.mp3')))
        self.assertEqual(2773, int(1000*get_audio_duration(tmpdirsl+'mp3_avgb128.mp3')))
        self.assertEqual(2773, int(1000*get_audio_duration(tmpdirsl+'mp3_avgb224.mp3')))
        self.assertEqual(2873, int(1000*get_audio_duration(tmpdirsl+'mp3_cnsb16.mp3')))
        self.assertEqual(2773, int(1000*get_audio_duration(tmpdirsl+'mp3_cnsb128.mp3')))
        self.assertEqual(2773, int(1000*get_audio_duration(tmpdirsl+'mp3_cnsb224.mp3')))
        self.assertEqual(1591, int(1000*get_audio_duration(tmpdirsl+'ogg_01.ogg')))
        self.assertEqual(1591, int(1000*get_audio_duration(tmpdirsl+'ogg_10.ogg')))
        
        # get duration; tag object provided
        self.assertEqual(1023, int(1000*get_audio_duration(tmpdirsl+'flac.flac', EasyPythonMutagen(tmpdirsl+'flac.flac'))))
        self.assertEqual(1160, int(1000*get_audio_duration(tmpdirsl+'m4a16.m4a', EasyPythonMutagen(tmpdirsl+'m4a16.m4a'))))
        self.assertEqual(1091, int(1000*get_audio_duration(tmpdirsl+'m4a128.m4a', EasyPythonMutagen(tmpdirsl+'m4a128.m4a'))))
        self.assertEqual(1091, int(1000*get_audio_duration(tmpdirsl+'m4a224.m4a', EasyPythonMutagen(tmpdirsl+'m4a224.m4a'))))
        self.assertEqual(2773, int(1000*get_audio_duration(tmpdirsl+'mp3_avgb16.mp3', EasyPythonMutagen(tmpdirsl+'mp3_avgb16.mp3'))))
        self.assertEqual(2773, int(1000*get_audio_duration(tmpdirsl+'mp3_avgb128.mp3', EasyPythonMutagen(tmpdirsl+'mp3_avgb128.mp3'))))
        self.assertEqual(2773, int(1000*get_audio_duration(tmpdirsl+'mp3_avgb224.mp3', EasyPythonMutagen(tmpdirsl+'mp3_avgb224.mp3'))))
        self.assertEqual(2873, int(1000*get_audio_duration(tmpdirsl+'mp3_cnsb16.mp3', EasyPythonMutagen(tmpdirsl+'mp3_cnsb16.mp3'))))
        self.assertEqual(2773, int(1000*get_audio_duration(tmpdirsl+'mp3_cnsb128.mp3', EasyPythonMutagen(tmpdirsl+'mp3_cnsb128.mp3'))))
        self.assertEqual(2773, int(1000*get_audio_duration(tmpdirsl+'mp3_cnsb224.mp3', EasyPythonMutagen(tmpdirsl+'mp3_cnsb224.mp3'))))
        self.assertEqual(1591, int(1000*get_audio_duration(tmpdirsl+'ogg_01.ogg', EasyPythonMutagen(tmpdirsl+'ogg_01.ogg'))))
        self.assertEqual(1591, int(1000*get_audio_duration(tmpdirsl+'ogg_10.ogg', EasyPythonMutagen(tmpdirsl+'ogg_10.ogg'))))
        
        # get empirical bitrate
        self.assertEqual(29, int(get_empirical_bitrate(tmpdirsl+'m4a16.m4a')))
        self.assertEqual(136, int(get_empirical_bitrate(tmpdirsl+'mp3_avgb128.mp3')))
        self.assertEqual(233, int(get_empirical_bitrate(tmpdirsl+'mp3_cnsb224.mp3')))
        
        # unsupported extensions
        self.assertRaisesRegexp(ValueError, 'unsupported', lambda:get_audio_duration('missing_extension'))
        self.assertRaisesRegexp(ValueError, 'unsupported', lambda:get_audio_duration('unsupported.mp3.extension.mp5'))
        self.assertRaisesRegexp(ValueError, 'unsupported', lambda:get_empirical_bitrate('missing_extension'))
        self.assertRaisesRegexp(ValueError, 'unsupported', lambda:get_empirical_bitrate('unsupported.mp3.extension.mp5'))
    
    def test_metadataTags(self):
        # saving in id3_23 should be different than saving in id3_24
        from easypythonmutagen import EasyPythonMutagen, get_audio_duration, get_empirical_bitrate
        import filecmp
        import os
        import shutil
        tmpdirsl = self.tmpdir+'/'
        shutil.copy(tmpdirsl+'mp3_avgb128.mp3', tmpdirsl+'mp3_id3_23.mp3')
        shutil.copy(tmpdirsl+'mp3_avgb128.mp3', tmpdirsl+'mp3_id3_24.mp3')
        self.assertTrue(filecmp.cmp(tmpdirsl+'mp3_id3_23.mp3', tmpdirsl+'mp3_id3_24.mp3', shallow=False))
        o23 = EasyPythonMutagen(tmpdirsl+'mp3_id3_23.mp3', True)
        o23.set('title', 'test')
        o23.save()
        o24 = EasyPythonMutagen(tmpdirsl+'mp3_id3_24.mp3', False)
        o24.set('title', 'test')
        o24.save()
        self.assertFalse(filecmp.cmp(tmpdirsl+'mp3_id3_23.mp3', tmpdirsl+'mp3_id3_24.mp3', shallow=False))
        
        # unsupported extensions
        self.assertRaisesRegexp(ValueError, 'unsupported', lambda:EasyPythonMutagen('missing_extension'))
        self.assertRaisesRegexp(ValueError, 'unsupported', lambda:EasyPythonMutagen('unsupported.mp3.extension.mp5'))
        
        # test reading and writing
        for file in os.listdir(self.tmpdir):
            if 'id3' in file:
                continue
                
            fields = dict(album=1, comment=1, artist=1, title=1, 
                composer=1, discnumber=1, tracknumber=1, albumartist=1, website=1)
            obj = EasyPythonMutagen(tmpdirsl+file)
            self.assertRaises(KeyError, lambda: obj.get('composer'))
            if not file.endswith('.mp3'):
                fields['description'] = 1
            
            # we shouldn't be able to set invalid fields
            if '.m4a' in file:
                # workaround for mutagen bug easymp4.py, line 183,  __getitem__ when it fails to raise EasyMP4KeyError("%r is not a valid key" % key)
                self.assertRaisesRegexp(Exception, '(not a valid key)|(object is not callable)', lambda: obj.set('aartist', 'test'))
                self.assertRaisesRegexp(Exception, '(not a valid key)|(object is not callable)', lambda: obj.get('aartist'))
            else:
                self.assertRaises(KeyError, lambda: obj.set('aartist', 'test'))
                self.assertRaises(KeyError, lambda: obj.get('aartist'))
            
            for field in fields:
                # first, all fields should be empty
                self.assertEqual(None, obj.get_or_default(field, None))
                
                # then, put data into the field
                if field=='tracknumber':
                    val = 14
                elif field=='discnumber':
                    val = 7
                elif field=='website':
                    val = 'http://website'+field
                else:
                    val = u'test\u0107test\u1101'+field
                fields[field] = val
                obj.set(field, val)
                self.assertEqual(unicode(fields[field]), obj.get(field))
            
            # verify data was saved
            obj.save()
            obj = EasyPythonMutagen(tmpdirsl+file)
            for field in fields:
                self.assertEqual(unicode(fields[field]), obj.get(field))
 
def testsCoordMusicUtil():
    # test m4aToUrl
    cleardirectoryfiles(tmpdir)
    newname = tmpdirsl+'m4a24.m4a'
    files.copy(dirtestmedia+'m4a24.m4a', newname, False)
    stampM4a(newname, 'spotify:test')
    m4aToUrl(files.split(newname)[0], files.split(newname)[1], CoordMusicAudioMetadata(newname), False)
    assertEq('spotify:test', getFromUrlFile(tmpdirsl+'m4a24.url'))
    
    # test getFromUrlFile and writeUrlFile
    assertException(lambda: getFromUrlFile(dirtestmedia+'wav.wav'), AssertionError)
    writeUrlFile(tmpdirsl+'test1.url', 'https://www.youtube.com/watch?v=0OSF')
    writeUrlFile(tmpdirsl+'test2.url', 'spotify:track:0Svkvt5I79wficMFgaqEQJ')
    assertEq('https://www.youtube.com/watch?v=0OSF', getFromUrlFile(tmpdirsl+'test1.url'))
    assertEq('spotify:track:0Svkvt5I79wficMFgaqEQJ', getFromUrlFile(tmpdirsl+'test2.url'))
    assertException(lambda: writeUrlFile(tmpdirsl+'test1.url', 'a'), AssertionError, 'already exists')
    
    # test getFieldForFile
    assertEq(getFieldForFile(r'c:\dir\test.MP3'), 'website')
    assertEq(getFieldForFile(r'c:\dir\test.mp3'), 'website')
    assertEq(getFieldForFile(r'c:\dir\test.m4a'), 'description')
    assertEq(getFieldForFile(r'c:\dir\test.flac'), 'desc')
    assertException(lambda: getFieldForFile(r'c:\dir\test.mp4'), AssertionError, 'unexpected extension')
    assertException(lambda: getFieldForFile(r'c:\dir\test.ogg'), AssertionError, 'unexpected extension')
        
    # test getWavDuration
    assertEq(727, int(1000*getWavDuration('./test/media/wav.wav')))
    assertException(lambda: getWavDuration('./test/media/wav.wav.mp3'), AssertionError, 'unexpected extension')
    
    # test setLink and getLink
    filenames = ['flac.flac', 'm4a128.m4a', 'mp3_avgb128.mp3', 'mp3_cnsb128.mp3']
    for shortname in filenames:
        files.copy(dirtestmedia+shortname, tmpdirsl+'test'+shortname, False)
        obj = CoordMusicAudioMetadata(tmpdirsl+'test'+shortname)
        assertEq(1, obj.get('discnumber'))
        assertEq(1, obj.get('disc_number'))
        assertEq('abc', obj.get_or_default('track_number', 'abc'))
        assertEq('abc', obj.get_or_default('album', 'abc'))
        assertEq(None, obj.getLink())
        assertException(lambda: obj.get('track_number'), KeyError)
        assertException(lambda: obj.get('album'), KeyError)
       
        obj.set('disc_number', 2)
        obj.set('track_number', '3/13')
        obj.setLink('spotify:1234')
        obj.save()
        
        obj = CoordMusicAudioMetadata(tmpdirsl+'test'+shortname)
        assertEq('2', obj.get('disc_number'))
        assertEq('3', obj.get('track_number'))
        assertEq('abc', obj.get_or_default('album', 'abc'))
        assertException(lambda: obj.get('album'), KeyError)
        assertEq('spotify:1234', obj.getLink())
    
def testsLinkSpotify():
    from recurring_linkspotify import RemoveRemasteredString, getChoiceString, getStrRemoteAudio
    # test RemoveRemasteredString
    rem = RemoveRemasteredString()
    assertEq('test [Other] test', rem.getProposedName('test [Other Version] test'))
    assertEq('test [OtherVersion] test', rem.getProposedName('test [OtherVersion] test'))
    assertEq('test test', rem.getProposedName('test [Mono Version] test'))
    assertEq('test test', rem.getProposedName('test - Remastered Album Version test'))
    assertEq('test test', rem.getProposedName('test - 1999 Remaster test'))
    assertEq('test test', rem.getProposedName('test - 1999 - Remaster test'))
    assertEq('test test', rem.getProposedName('test - 1999 - Remastered test'))
    assertEq('test test', rem.getProposedName('test - 1234 Digital Remaster test'))
    assertEq('test test', rem.getProposedName('test - 4321 - Digital Remaster test'))
    assertEq('test test', rem.getProposedName('test - 2111 - Digital Remastered test'))
    
    # test getChoiceString 
    assertEq('(02:00)  title1 (a1;; a2) same lngth',
        getChoiceString(dict(duration_ms=120000,name='title1', artists=[dict(name='a1'),dict(name='a2')], track_number=2,disc_number=2), 120))
    assertEq('(02:05)  title1 (a1) same lngth',
        getChoiceString(dict(duration_ms=125000,name='title1', artists=[dict(name='a1')], track_number=2,disc_number=2), 120))
    assertEq('(02:09)  title1 (a1) lnger(9s)',
        getChoiceString(dict(duration_ms=129000,name='title1', artists=[dict(name='a1')], track_number=2,disc_number=2), 120))
    assertEq('(01:52)  title1 (a1) shrter(8s)',
        getChoiceString(dict(duration_ms=112000,name='title1', artists=[dict(name='a1')], track_number=2,disc_number=2), 120))
    
    # test getStrRemoteAudio
    assertEq('(00:00)  title1 (a1)', getStrRemoteAudio(dict(duration_ms=0,name='title1', artists=[dict(name='a1')], track_number=1,disc_number=2), False, False, ''))
    assertEq('(00:00) 01 title1 (a1)', getStrRemoteAudio(dict(duration_ms=0,name='title1', artists=[dict(name='a1')], track_number=1,disc_number=2), False, True, ''))
    assertEq('(00:00) 02 01 title1 (a1)', getStrRemoteAudio(dict(duration_ms=0,name='title1', artists=[dict(name='a1')], track_number=1,disc_number=2), True, True, ''))
    assertEq('(00:00)  title1 ', getStrRemoteAudio(dict(duration_ms=0,name='title1', artists=[dict(name='a1')], track_number=1,disc_number=2), False, False, 'a1'))
    
    
def testsLinkSpotifyInteractive():
    from recurring_linkspotify import linkspotify, launchSpotifyUri
    if not files.exists(tmpdir):
        files.makedirs(tmpdir)
    
    # testing files outside of an album
    trace('testing files outside of an album')
    cleardirectoryfiles(tmpdir)
    files.makedirs(tmpdir+'/classic rock/collection')
    files.copy(dirtestmedia+'/test_02_52.m4a', tmpdir+'/classic rock/collection/Queen - You\'re My Best Friend.m4a', False)
    parsedNames = [Bucket(short='Queen - You\'re My Best Friend.m4a', artist='Queen', title='You\'re My Best Friend', discnumber=1,tracknumber=None)]
    tags = [CoordMusicAudioMetadata(tmpdir+'/classic rock/collection/'+parsed.short) for parsed in parsedNames]
    for tag, parsed in zip(tags, parsedNames): tag.short = parsed.short
        
    # add a url, which should be ignored
    writeUrlFile(tmpdir+'/classic rock/collection/artist - ignored.url', 'spotify:track:7o4i6eiHjZqbASnSy3pKAq')
    assertTrue(files.exists(tmpdir+'/classic rock/collection/artist - ignored.url'))
    linkspotify(True, tmpdir+'/classic rock/collection', tags, parsedNames, False, 'US')
    if getInputBool('spotifylink was set to '+str(tags[0].getLink())+' open?'):
        launchSpotifyUri(tags[0].getLink())
    
    # testing files inside of an album with one disc
    trace('testing files inside of an album with one disc')
    cleardirectoryfiles(tmpdir)
    files.makedirs(tmpdir+'/classic rock/Queen/1975, A Night At The Opera')
    parsedNames = []
    files.copy(dirtestmedia+'/test_02_52.m4a', tmpdir+'/classic rock/Queen/1975, A Night At The Opera/04 You\'re My Best Friend.m4a', False)
    parsedNames.append(Bucket(short='04 You\'re My Best Friend.m4a', artist='Queen', album='A Night At The Opera', title='You\'re My Best Friend', discnumber=1,tracknumber=4))
    files.copy(dirtestmedia+'/test_03_31.m4a', tmpdir+'/classic rock/Queen/1975, A Night At The Opera/05 \'39.m4a', False)
    parsedNames.append(Bucket(short='05 \'39.m4a', artist='Queen', title='\'39', discnumber=1,tracknumber=5))
    tags = [CoordMusicAudioMetadata(tmpdir+'/classic rock/Queen/1975, A Night At The Opera/'+parsed.short) for parsed in parsedNames]
    for tag, parsed in zip(tags, parsedNames): tag.short = parsed.short
    
    # add a url, which should be ignored
    writeUrlFile(tmpdir+'/classic rock/Queen/1975, A Night At The Opera/01 Ignored.url', 'spotify:track:7o4i6eiHjZqbASnSy3pKAq')
    parsedNames.append(Bucket(short='01 Ignored.url'))
    tags.append(Bucket(short='01 Ignored.url'))
    linkspotify(True, tmpdir+'/classic rock/Queen/1975, A Night At The Opera', tags, parsedNames, True, 'US')
    if getInputBool('first spotifylink was set to '+str(tags[0].getLink())+' open?'):
        launchSpotifyUri(tags[0].getLink())
    
    # testing files inside of an album with several discs
    trace('testing files inside of an album with several discs')
    trace('"I Want to Break Free" is intentionally 04_09 instead of 02_05, to test misnumbering')
    trace('"Barcelona" is intentionally too short, to test checking mismatched duration')
    cleardirectoryfiles(tmpdir)
    files.makedirs(tmpdir+'/classic rock/Queen/2002, The Platinum Collection')
    parsedNames = []
    files.copy(dirtestmedia+'/test_02_52.m4a', tmpdir+'/classic rock/Queen/2002, The Platinum Collection/01 06 You\'re My Best Friend.m4a', False)
    parsedNames.append(Bucket(short='01 06 You\'re My Best Friend.m4a', artist='Queen', album='The Platinum Collection', title='You\'re My Best Friend', discnumber=1,tracknumber=6))
    files.copy(dirtestmedia+'/test_04_19.m4a', tmpdir+'/classic rock/Queen/2002, The Platinum Collection/04 09 I Want to Break Free.m4a', False)
    parsedNames.append(Bucket(short='04 09 I Want to Break Free.m4a', artist='Queen', title='I Want to Break Free', discnumber=4,tracknumber=9))
    files.copy(dirtestmedia+'/test_03_31.m4a', tmpdir+'/classic rock/Queen/2002, The Platinum Collection/03 03 Barcelona.m4a', False)
    parsedNames.append(Bucket(short='03 03 Barcelona.m4a', artist='Queen', title='Barcelona', discnumber=3,tracknumber=3))
    tags = [CoordMusicAudioMetadata(tmpdir+'/classic rock/Queen/2002, The Platinum Collection/'+parsed.short) for parsed in parsedNames]
    for tag, parsed in zip(tags, parsedNames): tag.short = parsed.short
        
    # add a url, which should be ignored
    writeUrlFile(tmpdir+'/classic rock/Queen/2002, The Platinum Collection/01 01 Ignored.url', 'spotify:track:7o4i6eiHjZqbASnSy3pKAq')
    parsedNames.append(Bucket(short='01 01 Ignored.url'))
    tags.append(Bucket(short='01 01 Ignored.url'))
    linkspotify(True, tmpdir+'/classic rock/Queen/2002, The Platinum Collection', tags, parsedNames, True, 'US')
    if getInputBool('second spotifylink was set to '+str(tags[1].getLink())+' open?'):
        launchSpotifyUri(tags[1].getLink())

if __name__=='__main__':
    unittest.main()
    testsOrganize()
    testsCoordMusicUtil()
    testsLinkSpotify()
    if getInputBool('Run interactive tests?'):
        testsLinkSpotifyInteractive()
        

