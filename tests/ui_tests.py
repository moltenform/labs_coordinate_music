# labs_coordinate_music
# Ben Fisher, 2016
# Released under the GNU General Public License version 3

import sys
import os
import tempfile
from os.path import join

def testLinkSpotifyInteractive(tmpdir, mediadir):
    if not getInputBool('Run interactive LinkSpotify test (requires Spotify connection)?'):
        return
    
    # testing files outside of an album
    trace('testing files outside of an album')
    files.ensure_empty_directory(tmpdir)
    files.makedirs(tmpdir + '/classic rock/collection')
    files.copy(mediadir + '/test_02_52.m4a',
        tmpdir + '/classic rock/collection/Queen - You\'re My Best Friend.m4a', False)
    parsedNames = [Bucket(short='Queen - You\'re My Best Friend.m4a',
        artist='Queen', title='You\'re My Best Friend', discnumber=1, tracknumber=None)]
    tags = [CoordMusicAudioMetadata(tmpdir + '/classic rock/collection/' + parsed.short) for parsed in parsedNames]
    for tag, parsed in zip(tags, parsedNames):
        tag.short = parsed.short
    
    # add a url, which should be ignored
    writeUrlFile(tmpdir + '/classic rock/collection/artist - ignored.url', 'spotify:track:7o4i6eiHjZqbASnSy3pKAq')
    assertTrue(files.exists(tmpdir + '/classic rock/collection/artist - ignored.url'))
    linkspotify(True, tmpdir + '/classic rock/collection', tags, parsedNames, False, 'US')
    if getInputBool('spotifylink was set to ' + str(tags[0].getLink()) + ' open?'):
        launchSpotifyUri(tags[0].getLink())
    
    # testing files inside of an album with one disc
    trace('testing files inside of an album with one disc')
    files.ensure_empty_directory(tmpdir)
    files.makedirs(tmpdir + '/classic rock/Queen/1975, A Night At The Opera')
    parsedNames = []
    files.copy(mediadir + '/test_02_52.m4a',
        tmpdir + '/classic rock/Queen/1975, A Night At The Opera/04 You\'re My Best Friend.m4a', False)
    parsedNames.append(Bucket(short='04 You\'re My Best Friend.m4a',
        artist='Queen', album='A Night At The Opera', title='You\'re My Best Friend', discnumber=1, tracknumber=4))
    files.copy(mediadir + '/test_03_31.m4a',
        tmpdir + '/classic rock/Queen/1975, A Night At The Opera/05 \'39.m4a', False)
    parsedNames.append(Bucket(short='05 \'39.m4a',
        artist='Queen', title='\'39', discnumber=1, tracknumber=5))
        
    tags = [CoordMusicAudioMetadata(tmpdir + '/classic rock/Queen/1975, A Night At The Opera/' + parsed.short) for parsed in parsedNames]
    for tag, parsed in zip(tags, parsedNames):
        tag.short = parsed.short
    
    # add a url, which should be ignored
    writeUrlFile(tmpdir + '/classic rock/Queen/1975, A Night At The Opera/01 Ignored.url', 'spotify:track:7o4i6eiHjZqbASnSy3pKAq')
    parsedNames.append(Bucket(short='01 Ignored.url'))
    tags.append(Bucket(short='01 Ignored.url'))
    linkspotify(True, tmpdir + '/classic rock/Queen/1975, A Night At The Opera', tags, parsedNames, True, 'US')
    if getInputBool('first spotifylink was set to ' + str(tags[0].getLink()) + ' open?'):
        launchSpotifyUri(tags[0].getLink())
    
    # testing files inside of an album with several discs
    trace('testing files inside of an album with several discs')
    trace('"I Want to Break Free" is intentionally 04_09 instead of 02_05, to test misnumbering')
    trace('"Barcelona" is intentionally too short, to test checking mismatched duration')
    files.ensure_empty_directory(tmpdir)
    files.makedirs(tmpdir + '/classic rock/Queen/2002, The Platinum Collection')
    parsedNames = []
    
    files.copy(mediadir + '/test_02_52.m4a',
        tmpdir + '/classic rock/Queen/2002, The Platinum Collection/01 06 You\'re My Best Friend.m4a', False)
    parsedNames.append(Bucket(short='01 06 You\'re My Best Friend.m4a',
        artist='Queen', album='The Platinum Collection', title='You\'re My Best Friend', discnumber=1, tracknumber=6))
        
    files.copy(mediadir + '/test_04_19.m4a',
        tmpdir + '/classic rock/Queen/2002, The Platinum Collection/04 09 I Want to Break Free.m4a', False)
    parsedNames.append(Bucket(short='04 09 I Want to Break Free.m4a',
        artist='Queen', title='I Want to Break Free', discnumber=4, tracknumber=9))
        
    files.copy(mediadir + '/test_03_31.m4a',
        tmpdir + '/classic rock/Queen/2002, The Platinum Collection/03 03 Barcelona.m4a', False)
    parsedNames.append(Bucket(short='03 03 Barcelona.m4a',
        artist='Queen', title='Barcelona', discnumber=3, tracknumber=3))
        
    tags = [CoordMusicAudioMetadata(tmpdir + '/classic rock/Queen/2002, The Platinum Collection/' + parsed.short) for parsed in parsedNames]
    for tag, parsed in zip(tags, parsedNames):
        tag.short = parsed.short
        
    # add a url, which should be ignored
    writeUrlFile(tmpdir + '/classic rock/Queen/2002, The Platinum Collection/01 01 Ignored.url', 'spotify:track:7o4i6eiHjZqbASnSy3pKAq')
    parsedNames.append(Bucket(short='01 01 Ignored.url'))
    tags.append(Bucket(short='01 01 Ignored.url'))
    linkspotify(True, tmpdir + '/classic rock/Queen/2002, The Platinum Collection', tags, parsedNames, True, 'US')
    if getInputBool('second spotifylink was set to ' + str(tags[1].getLink()) + ' open?'):
        launchSpotifyUri(tags[1].getLink())

def testMusicToUrlInteractive(tmpdir, mediadir):
    if not getInputBool('Run interactive MusicToUrl test?'):
        return
    
    files.ensure_empty_directory(tmpdir)
    tmpdirsl = tmpdir + files.sep
    files.copy(mediadir + '/m4a128.m4a', tmpdirsl + 'Carly Rae Jepsen - Run Away With Me.m4a', False)
    files.copy(mediadir + '/mp3_avgb128.mp3', tmpdirsl + 'Qua - Ritmo Giallo.mp3', False)
    files.copy(mediadir + '/mp3_avgb128.mp3', tmpdirsl + 'Masato Nakamura - Green Hill Zone.mp3', False)
    
    assertEq('p01p Carly Rae Jepsen - Run Away With Me.m4a 0.0Mb 134k 00:01',
        getStringTrackAndPopularity(tmpdir, CoordMusicAudioMetadata(tmpdirsl + 'Carly Rae Jepsen - Run Away With Me.m4a'), 1))
    assertEq('p12p Qua - Ritmo Giallo.mp3 0.0Mb 136k 00:02',
        getStringTrackAndPopularity(tmpdir, CoordMusicAudioMetadata(tmpdirsl + 'Qua - Ritmo Giallo.mp3'), 12))
    assertEq('p00p Masato Nakamura - Green Hill Zone.mp3 0.0Mb 136k 00:02',
        getStringTrackAndPopularity(tmpdir, CoordMusicAudioMetadata(tmpdirsl + 'Masato Nakamura - Green Hill Zone.mp3'), 0))
    
    stampM4a(tmpdirsl + 'Carly Rae Jepsen - Run Away With Me.m4a', 'spotify:track:5e0vgBWfwToyphURwynSXa')
    stampM4a(tmpdirsl + 'Qua - Ritmo Giallo.mp3', 'spotify:track:5fAV6bhApK00urMyz4ceit')
    stampM4a(tmpdirsl + 'Masato Nakamura - Green Hill Zone.mp3', 'spotify:notfound')
    
    obj = SaveDiskSpaceMusicToUrl()
    try:
        obj.go(tmpdir, [CoordMusicAudioMetadata(fullfile) for fullfile, short in files.listfiles(tmpdir)], None)
    except StopBecauseWeRenamedFile:
        pass
        
    trace('Resulting filenames:\n' + '\n'.join(short for fullfile, short in files.listfiles(tmpdir)))

def testFromOutsideMp3Interactive(tmpdir, mediadir):
    if not getInputBool('Run interactive OutsideMp3 test?  (refer to test/walkthrough_interactive_test_from_outside.png)'):
        return
        
    # create "outside" files, mocking input files
    files.ensure_empty_directory(tmpdir)
    tmpdirsl = tmpdir + files.sep
    files.makedirs(tmpdirsl + 'outside')
    files.makedirs(tmpdirsl + 'outside/Space Oddity')
    files.makedirs(tmpdirsl + 'outside/The Essential Fifth Dimension')
    mp3 = mediadir + '/mp3_avgb128.mp3'
    files.copy(mp3, tmpdirsl + 'outside/Space Oddity/03 Letter To Hermione__MARKAS__128.mp3', False)
    files.copy(mp3, tmpdirsl + 'outside/Space Oddity/05 Janine__MARKAS__24.mp3', False)
    files.copy(mp3, tmpdirsl + 'outside/Space Oddity/96 Nonexistent song 1__MARKAS__24.mp3', False)
    files.copy(mp3, tmpdirsl + 'outside/Space Oddity/97 Nonexistent song 2__MARKAS__24.mp3', False)
    files.copy(mp3, tmpdirsl + 'outside/Space Oddity/98 Nonexistent song 3__MARKAS__128.mp3', False)
    files.copy(mp3, tmpdirsl + 'outside/Space Oddity/99 Nonexistent song 4__MARKAS__128.mp3', False)
    files.copy(mp3, tmpdirsl + 'outside/The Essential Fifth Dimension/01 17 Workin\' on a Groovy Thing__MARKAS__144.mp3', False)
    files.copy(mp3, tmpdirsl + 'outside/The Essential Fifth Dimension/02 19 No Love In The Room__MARKAS__24.mp3', False)
    artists = {'Space Oddity': 'David Bowie', 'The Essential Fifth Dimension': 'The Fifth Dimension'}
    for file, short in files.recursefiles(tmpdirsl + 'outside'):
        album = files.getname(files.getparent(file))
        name = short.split('__')[0]
        if name[3:5].isdigit():
            discnumber = int(name[0:2])
            tracknumber = int(name[3:5])
            title = name[6:]
        else:
            discnumber = 1
            tracknumber = int(name[0:2])
            title = name[3:]
    
        obj = CoordMusicAudioMetadata(file)
        obj.set('album', album)
        obj.set('artist', artists[album])
        obj.set('title', title)
        obj.set('discnumber', discnumber)
        obj.set('tracknumber', tracknumber)
        
        # intentionally remove some information
        if tracknumber == 98 or tracknumber == 99:
            obj.set('tracknumber', '')

        obj.save()
        
    coordmusictools.tools_outsideMp3sToSpotifyPlaylist(tmpdirsl + 'outside', mustSort=True)
    
    # get resulting spotify links
    link1 = CoordMusicAudioMetadata(tmpdirsl +
        'outside/Space Oddity/03 Letter To Hermione__MARKAS__128.mp3').getLink()
    link2 = CoordMusicAudioMetadata(tmpdirsl +
        'outside/The Essential Fifth Dimension/01 17 Workin\' on a Groovy Thing__MARKAS__144.mp3').getLink()
    assert 'spotify:track:' in link1
    assert 'spotify:track:' in link2
    link1 = link1.replace('spotify:track:', '')
    link2 = link2.replace('spotify:track:', '')
    
    # mock incoming files
    wav = mediadir + '/wav.wav'
    files.makedirs(tmpdirsl + 'incoming')
    files.copy(wav, tmpdirsl + 'incoming/0001 Space Oddity' +
        '$David Bowie$03$Letter To Hermione$%s.wav' % link1, False)
    files.copy(wav, tmpdirsl + 'incoming/0002 The Essential Fifth Dimension' +
        '$The Fifth Dimension$12$Workin\' on a Groovy Thing$%s.wav' % link2, False)
    
    print(u'.wav files in %s, please convert them to m4a' % (tmpdirsl + 'incoming'))
    coordmusictools.tools_newFilesBackToReplaceOutsideMp3s(tmpdirsl + 'outside', tmpdirsl + 'incoming')
    
    # see if the result is right
    all = sorted([filepath.replace(tmpdirsl + 'outside', '').replace(files.sep, '/')
        for filepath, short in files.recursefiles(tmpdirsl + 'outside')])
    assertEq(['/Space Oddity/03 Letter To Hermione.m4a',
        '/Space Oddity/05 Janine.url',
        '/Space Oddity/97 Nonexistent song 2.mp3',
        '/Space Oddity/98 Nonexistent song 3 (12).mp3',
        '/Space Oddity/99 Nonexistent song 4.mp3',
        '/The Essential Fifth Dimension/01 17 Workin\' on a Groovy Thing.m4a',
        '/The Essential Fifth Dimension/02 19 No Love In The Room.url'], all)
    
    # see if id3 info looks right
    obj = CoordMusicAudioMetadata(tmpdirsl + 'outside/Space Oddity/03 Letter To Hermione.m4a')
    assertEq('Space Oddity', obj.get('album'))
    assertEq('David Bowie', obj.get('artist'))
    assertEq('Letter To Hermione', obj.get('title'))
    assertEq('1', str(obj.get('discnumber')))
    assertEq('3', obj.get('tracknumber'))
    assertEq('97', CoordMusicAudioMetadata(tmpdirsl + 'outside/Space Oddity/97 Nonexistent song 2.mp3').get('tracknumber'))
    assertEq('98', CoordMusicAudioMetadata(tmpdirsl + 'outside/Space Oddity/98 Nonexistent song 3 (12).mp3').get('tracknumber'))
    assertEq('99', CoordMusicAudioMetadata(tmpdirsl + 'outside/Space Oddity/99 Nonexistent song 4.mp3').get('tracknumber'))
    assertEq('spotify:notfound', CoordMusicAudioMetadata(tmpdirsl + 'outside/Space Oddity/99 Nonexistent song 4.mp3').getLink())
    
    # use a set to check that all spotify links are different
    setOfLinks = set([CoordMusicAudioMetadata(tmpdirsl + 'outside/Space Oddity/03 Letter To Hermione.m4a').getLink(),
        getFromUrlFile(tmpdirsl + 'outside/Space Oddity/05 Janine.url'),
        CoordMusicAudioMetadata(tmpdirsl + 'outside/Space Oddity/99 Nonexistent song 4.mp3').getLink(),
        CoordMusicAudioMetadata(tmpdirsl + 'outside/The Essential Fifth Dimension/01 17 Workin\' on a Groovy Thing.m4a').getLink(),
        getFromUrlFile(tmpdirsl + 'outside/The Essential Fifth Dimension/02 19 No Love In The Room.url')])
    assertEq(5, len(setOfLinks))


# let this file be started as a script.
if __name__ == '__main__':
    if __package__ is None and not hasattr(sys, 'frozen'):
        path = os.path.realpath(os.path.abspath(__file__))
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(path))))

    from labs_coordinate_music import coordmusictools
    from labs_coordinate_music.ben_python_common import *
    from labs_coordinate_music.coordmusicutil import *
    from labs_coordinate_music.recurring_linkspotify import \
        linkspotify, launchSpotifyUri
    from labs_coordinate_music.recurring_music_to_url import \
        getStringTrackAndPopularity, SaveDiskSpaceMusicToUrl
    
    if not files.isfile(u'./media/flac.flac'):
        print('could not find test media. please ensure the current directory is labs_coordinate_music/tests')
        assert False
    
    tmpdir = ustr(join(tempfile.gettempdir(), 'test_music_coordination'))
    mediadir = u'./media'
    testMusicToUrlInteractive(tmpdir, mediadir)
    testFromOutsideMp3Interactive(tmpdir, mediadir)
    testLinkSpotifyInteractive(tmpdir, mediadir)

