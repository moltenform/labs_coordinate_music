# labs_coordinate_music
# Ben Fisher, 2016
# Released under the GNU General Public License version 3

import os
import sys
import mutagen
from mutagen import easymp4

# A simple Mutagen wrapper.
# o = EasyPythonMutagen('file.mp3')
# o.set('title', 'song title')
# o.save()
#
# by Ben Fisher
#
# tags are intentionally restricted; otherwise a typo like o['aartist'] would succeed silently in some formats.
# use Mutagen directly if you want to intentionally add rare or custom fields.
# note that Mutagen's new mutagen.File interface makes much of this obsolete.


class EasyPythonMutagen:
    """Wraps interfaces, for convenience, will not return values as list."""
    def __init__(self, filename, use_id3_v23=True):
        filenamelower = filename.lower()
        if filenamelower.endswith('.mp3'):
            self.obj = _EasyPythonMutagenId3(filename, use_id3_v23=use_id3_v23)
        elif filenamelower.endswith('.ogg'):
            self.obj = _EasyPythonMutagenOggVorbis(filename)
        elif filenamelower.endswith('.flac'):
            self.obj = _EasyPythonMutagenFlac(filename)
        elif filenamelower.endswith('.mp4') or filenamelower.endswith('.m4a'):
            self.obj = _EasyPythonMutagenM4a(filename)
        else:
            raise ValueError('unsupported extension')

    def get(self, fieldname):
        ret = self.obj[fieldname]
        if not ret or isinstance(ret, anystringtype):
            return ret
        else:
            return ret[0]

    def get_or_default(self, fieldname, default):
        try:
            return self.get(fieldname)
        except (KeyError, mutagen.easymp4.EasyMP4KeyError):
            return default

    def set(self, fieldname, val):
        if isinstance(val, int):
            val = str(val)

        assert isinstance(val, anystringtype), 'val must be a string'
        try:
            self.obj[fieldname] = val
        except AttributeError as exc:
            # workaround for a mutagen bug (apparently _padding is for debugging)
            # https://github.com/quodlibet/mutagen/issues/334
            if "has no attribute '_padding'" in str(exc):
                from mutagen.mp4 import MP4Tags
                MP4Tags._padding = 0 # pylint: disable=W0212
                self.obj[fieldname] = val
            else:
                raise

    def save(self):
        self.obj.save()


class _EasyPythonMutagenFlac:
    '''An interface like EasyId3, but for Flac files.'''
    def __init__(self, filename):
        from mutagen import flac
        self.obj = flac.FLAC(filename)
        self.map = {
            'desc': 'desc',
            'description': 'desc',
            'album': 'album',
            'comment': 'comment',
            'artist': 'artist',
            'title': 'title',
            'tracknumber': 'tracknumber',
            'discnumber': 'discnumber',
            'albumartist': 'albumartist',
            'composer': 'composer',
            'disccount': 'disccount',
            'tracktotal': 'tracktotal',
            'date': 'date',
            'genre': 'genre',
            'website': 'www'
        }

    def __getitem__(self, key):
        return self.obj[self.map[key]]

    def __setitem__(self, key, val):
        self.obj[self.map[key]] = val

    def __contains__(self, key):
        return key in self.map and self.map[key] in self.obj

    def save(self):
        self.obj.save()


class _EasyPythonMutagenOggVorbis:
    '''An interface like EasyId3, but for OggVorbis files.'''
    def __init__(self, filename):
        from mutagen.oggvorbis import OggVorbis
        self.obj = OggVorbis(filename)
        self.map = {
            'album': 'album',
            'comment': 'comment',
            'artist': 'artist',
            'title': 'title',
            'albumartist': 'albumartist',
            'tracknumber': 'tracknumber',
            'discnumber': 'discnumber',
            'composer': 'composer',
            'genre': 'genre',
            'description': 'description',
            'website': 'www'
        }

    def __getitem__(self, key):
        return self.obj[self.map[key]]

    def __setitem__(self, key, val):
        self.obj[self.map[key]] = val

    def __contains__(self, key):
        return key in self.map and self.map[key] in self.obj

    def save(self):
        self.obj.save()


class _EasyPythonMutagenM4a(easymp4.EasyMP4):
    '''EasyMp4, with added fields.
        EasyMp4 already provides
        title
        album
        artist
        albumartist
        date
        comment
        description (maps to subtitle)
        genre, and more'''
    def __init__(self, filename):
        super(_EasyPythonMutagenM4a, self).__init__(filename)
        easymp4.EasyMP4Tags.RegisterTextKey('composer', '\xa9wrt')
        easymp4.EasyMP4Tags.RegisterTextKey('desc', 'desc')
        easymp4.EasyMP4Tags.RegisterFreeformKey('website', 'WWW')


class _EasyPythonMutagenId3:
    '''like EasyId3, but supports id3_v23 and handles missing tags more gracefully.'''
    def __init__(self, filename, use_id3_v23, keep_id3_v1=False):
        from mutagen import id3
        self.obj = None
        self.filename = filename
        self.use_id3_v23 = use_id3_v23
        self.keep_id3_v1 = keep_id3_v1
        self.map = {
            'album': 'TALB',
            'bpm': 'TBPM',
            'composer': 'TCOM',
            'copyright': 'TCOP',
            'encodedby': 'TENC',
            'lyricist': 'TEXT',
            'length': 'TLEN',
            'media': 'TMED',
            'mood': 'TMOO',
            'title': 'TIT2',
            'version': 'TIT3',
            'artist': 'TPE1',
            'performer': 'TPE2',
            'conductor': 'TPE3',
            'arranger': 'TPE4',
            'discnumber': 'TPOS',
            'organization': 'TPUB',
            'tracknumber': 'TRCK',
            'author': 'TOLY',
            'isrc': 'TSRC',
            'discsubtitle': 'TSST',
            'language': 'TLAN',
            # handled separately
            'website': None,
            # aliases
            'description': 'TSST',
            'comment': 'TIT3',
            'albumartist': 'TPE2'
        }

        try:
            self._load()
        except mutagen.id3._util.ID3NoHeaderError:
            # the id3 tag doesn't exist yet; let's just add it now.
            self.obj = id3.ID3()
            self['title'] = ''
            self.save()
            self._load()

    def _load(self):
        from mutagen import id3
        self.obj = id3.ID3()
        kwargs = dict(v2_version=3, translate=True) if self.use_id3_v23 else dict()
        self.obj.load(self.filename, **kwargs)

    def save(self):
        kwargs = dict(v2_version=3) if self.use_id3_v23 else dict()
        if not self.keep_id3_v1:
            kwargs['v1'] = 0
        self.obj.save(self.filename, **kwargs)

    def getWebsite(self):
        urls = [frame.url for frame in self.obj.getall('WOAR')]
        if urls:
            return urls
        else:
            raise KeyError('website')

    def setWebsite(self, value):
        self.obj.delall('WOAR')
        if isinstance(value, anystringtype):
            self.obj.add(mutagen.id3.WOAR(url=value))
        else:
            for v in value:
                self.obj.add(mutagen.id3.WOAR(url=v))

    def __getitem__(self, key):
        if key == 'website':
            return self.getWebsite()
        else:
            frameid = self.map[key]
            return list(self.obj[frameid])

    def __setitem__(self, key, val):
        if key == 'website':
            return self.setWebsite(val)
        else:
            assert isinstance(val, anystringtype), 'val must be a string'
            val = [val]
            frameid = self.map[key]
            encoding = 3 # Encoding.UTF8; mutagen apparently converts to UTF16 when needed
            try:
                frame = self.obj[frameid]
            except KeyError:
                self.obj.add(mutagen.id3.Frames[frameid](encoding=encoding, text=val))
            else:
                frame.encoding = encoding
                frame.text = val

            return None

    def __contains__(self, key):
        try:
            self[key] # pylint: disable=W0104
            return True
        except KeyError:
            return False


def mutagen_get_audio_duration(filename, alreadyobj=None):
    """returns audio duration in seconds"""
    filenamelower = filename.lower()
    if filenamelower.endswith('.mp3'):
        from mutagen.mp3 import MP3
        length = MP3(filename).info.length

    elif filenamelower.endswith('.mp4') or filenamelower.endswith('.m4a'):
        if isinstance(alreadyobj, EasyPythonMutagen):
            length = alreadyobj.obj.info.length
        elif isinstance(alreadyobj, easymp4.EasyMP4):
            length = alreadyobj.info.length
        else:
            length = easymp4.EasyMP4(filename).info.length

    elif filenamelower.endswith('.flac'):
        if isinstance(alreadyobj, EasyPythonMutagen):
            length = alreadyobj.obj.obj.info.length
        elif isinstance(alreadyobj, _EasyPythonMutagenFlac):
            length = alreadyobj.obj.info.length
        else:
            length = _EasyPythonMutagenFlac(filename).obj.info.length

    elif filenamelower.endswith('.ogg'):
        if isinstance(alreadyobj, EasyPythonMutagen):
            length = alreadyobj.obj.obj.info.length
        elif isinstance(alreadyobj, _EasyPythonMutagenOggVorbis):
            length = alreadyobj.obj.info.length
        else:
            length = _EasyPythonMutagenOggVorbis(filename).obj.info.length

    else:
        raise ValueError('unsupported extension')

    return length


def get_empirical_bitrate(filename, alreadyobj=None):
    """returns the "empirical" bitrate, as opposed to the "stated" bitrate that can be inaccurate"""

    duration = mutagen_get_audio_duration(filename, alreadyobj)
    return (8.0 * os.path.getsize(filename) / 1000.0) / duration


if sys.version_info[0] <= 2:
    anystringtype = basestring # pylint: disable=E0602
else:
    anystringtype = str
