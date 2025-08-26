# labs_coordinate_music
# Ben Fisher, 2016
# Released under the GNU General Public License version 3

import pytest
import tempfile
import os
from os.path import join
import sys

from shinerainsevenlib.standard import *
from shinerainsevenlib.core import *

@pytest.fixture(scope='module')
def fixture_getmedia():
    basedir = ustr(join(tempfile.gettempdir(), 'test_music_coordination_media'))
    files.ensureEmptyDirectory(basedir)
    
    if not os.path.isfile(u'./tests/media/flac.flac'):
        print('could not find test media. please ensure the current directory is labs_coordinate_music')
        assert False

    # copy test media to temp directory
    for full, short in files.listFiles(u'./tests/media'):
        files.copy(full, join(basedir, short), True)

    yield basedir
    files.ensureEmptyDirectory(basedir)

@pytest.fixture()
def fixture_dir():
    basedir = ustr(join(tempfile.gettempdir(), 'test_music_coordination'))
    files.ensureEmptyDirectory(basedir)
    yield basedir
    files.ensureEmptyDirectory(basedir)
