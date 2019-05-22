# labs_coordinate_music
# Ben Fisher, 2016
# Released under the GNU General Public License version 3

import pytest
import tempfile
import os
from os.path import join
import sys
sys.path.append('../bn_python_common.zip')
from bn_python_common import *

@pytest.fixture(scope='module')
def fixture_getmedia():
    basedir = ustr(join(tempfile.gettempdir(), 'test_music_coordination_media'))
    files.ensure_empty_directory(basedir)
    
    if not os.path.isfile(u'./media/flac.flac'):
        print('could not find test media. please ensure the current directory is labs_coordinate_music/tests')
        assert False

    # copy test media to temp directory
    for full, short in files.listfiles(u'./media'):
        files.copy(full, join(basedir, short), True)

    yield basedir
    files.ensure_empty_directory(basedir)

@pytest.fixture()
def fixture_dir():
    basedir = ustr(join(tempfile.gettempdir(), 'test_music_coordination'))
    files.ensure_empty_directory(basedir)
    yield basedir
    files.ensure_empty_directory(basedir)
