# labs_coordinate_music
# Ben Fisher, 2016
# Released under the GNU General Public License version 3

import pytest
import tempfile
import os
import sys
from os.path import join

from shinerainsevenlib.standard import *
from shinerainsevenlib.core import *


@pytest.fixture(scope='module', name='fixture_getmedia')
def fixture_getmedia_defn():
    # to avoid lint errors, give the function here a separate name
    basedir = ustr(join(tempfile.gettempdir(), 'test_music_coordination_media'))
    files.ensureEmptyDirectory(basedir)

    if not os.path.isfile(u'./tests/media/flac.flac'):
        print('could not find test media. please ensure the current directory is labs_coordinate_music')
        raise AssertionError()

    # copy test media to temp directory
    for full, short in files.listFiles(u'./tests/media'):
        files.copy(full, join(basedir, short), True)

    yield basedir
    files.ensureEmptyDirectory(basedir)


@pytest.fixture(name='fixture_dir')
def fixture_dir_defn():
    basedir = ustr(join(tempfile.gettempdir(), 'test_music_coordination'))
    files.ensureEmptyDirectory(basedir)
    yield basedir
    files.ensureEmptyDirectory(basedir)
