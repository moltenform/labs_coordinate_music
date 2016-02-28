# BenPythonCommon,
# 2015 Ben Fisher, released under the GPLv3 license.

import os as os_hide
import shutil as shutil_hide
from common_util import *

rename = os_hide.rename
delete = os_hide.unlink
exists = os_hide.path.exists
join = os_hide.path.join
split = os_hide.path.split
splitext = os_hide.path.splitext
isdir = os_hide.path.isdir
isfile = os_hide.path.isfile
getsize = os_hide.path.getsize
rmdir = os_hide.rmdir
chdir = os_hide.chdir
makedir = os_hide.mkdir
makedirs = os_hide.makedirs
sep = os_hide.path.sep
linesep = os_hide.linesep
abspath = shutil_hide.abspath
rmtree = shutil_hide.rmtree

# simple wrappers
def getparent(s):
    return os_hide.path.split(s)[0]
    
def getname(s):
    return os_hide.path.split(s)[1]
    
def modtime(s):
    return os_hide.stat(s).ST_MTIME
    
def createdtime(s):
    return os_hide.stat(s).ST_CTIME
    
def getext(s):
    a, b = splitext(s)
    if len(b) > 0 and b[0] == '.':
        return b[1:].lower()
    else:
        return b.lower()
    
def deletesure(s):
    if files.exists(s):
        files.delete(s)
    assert not files.exists(s)
    
# copy and move
def copy(a, b, bOverwrite):
    import sys
    if not exists(a):
        raise IOError('source path does not exist')
        
    if sys.platform == 'win32':
        from ctypes import windll, c_wchar_p, c_int
        failIfExists = c_int(0) if bOverwrite else c_int(1)
        res = windll.kernel32.CopyFileW(c_wchar_p(a), c_wchar_p(b), failIfExists)
        if not res:
            raise IOError('CopyFileW failed (maybe dest already exists?)')
    else:
        if bOverwrite:
            shutil_hide.copy(a, b)
        else:
            # raises OSError on failure
            import os
            os.link(a, b)
    
    assertTrue(exists(b))
        
def move(a, b, bOverwrite):
    import sys
    if not exists(a):
        raise IOError('source path does not exist')
    if a == b:
        return
    if sys.platform == 'win32':
        from ctypes import windll, c_wchar_p, c_int
        replaceexisting = c_int(1) if bOverwrite else c_int(0)
        res = windll.kernel32.MoveFileExW(c_wchar_p(a), c_wchar_p(b), replaceexisting)
        if not res:
            raise IOError('MoveFileExW failed (maybe dest already exists?)')
    elif sys.platform.startswith('linux') and bOverwrite:
        import os
        os.rename(a, b)
    else:
        import os
        copy(a, b, bOverwrite)
        assertTrue(exists(b))
        os.unlink(a)
    
    assertTrue(exists(b))
    
# unicodetype can be utf-8, utf-8-sig, etc.
def readall(s, mode='r', unicodetype=None):
    if unicodetype:
        import codecs
        f = codecs.open(s, mode, unicodetype)
    else:
        f = open(s, mode)
    txt = f.read()
    f.close()
    return txt

# unicodetype can be utf-8, utf-8-sig, etc.
def writeall(s, txt, mode='w', unicodetype=None):
    if unicodetype:
        import codecs
        f = codecs.open(s, mode, unicodetype)
    else:
        f = open(s, mode)
    f.write(txt)
    f.close()

# use this to make the caller pass argument names,
# allowing foo(param=False) but preventing foo(False)
_enforceExplicitlyNamedParameters = object()

def _checkNamedParameters(o):
    if o is not _enforceExplicitlyNamedParameters:
        raise ValueError('please name parameters for this function or method')

# allowedexts in the form ['png', 'gif']
def listchildren(dir, _ind=_enforceExplicitlyNamedParameters, filenamesOnly=False, allowedexts=None):
    _checkNamedParameters(_ind)
    for filename in os_hide.listdir(dir):
        if not allowedexts or getext(filename) in allowedexts:
            yield filename if filenamesOnly else (dir + os_hide.path.sep + filename, filename)
    
def listfiles(dir, _ind=_enforceExplicitlyNamedParameters, filenamesOnly=False, allowedexts=None):
    _checkNamedParameters(_ind)
    for full, name in listchildren(dir, allowedexts=allowedexts):
        if not os_hide.path.isdir(full):
            yield name if filenamesOnly else (full, name)

def recursefiles(root, _ind=_enforceExplicitlyNamedParameters, filenamesOnly=False, allowedexts=None,
        fnFilterDirs=None, includeFiles=True, includeDirs=False, topdown=True):
    _checkNamedParameters(_ind)
    assert isdir(root)
    
    for (dirpath, dirnames, filenames) in os_hide.walk(root, topdown=topdown):
        if fnFilterDirs:
            newdirs = [dir for dir in dirnames if fnFilterDirs(join(dirpath, dir))]
            dirnames[:] = newdirs
        
        if includeFiles:
            for filename in filenames:
                if not allowedexts or getext(filename) in allowedexts:
                    yield filename if filenamesOnly else (dirpath + os_hide.path.sep + filename, filename)
        
        if includeDirs:
            yield getname(dirpath) if filenamesOnly else (dirpath, getname(dirpath))
    
def recursedirs(root, _ind=_enforceExplicitlyNamedParameters, filenamesOnly=False, fnFilterDirs=None, topdown=True):
    _checkNamedParameters(_ind)
    return recursefiles(root, filenamesOnly=filenamesOnly, fnFilterDirs=fnFilterDirs, includeFiles=False, includeDirs=True, topdown=topdown)
    
def isemptydir(dir):
    return len(os_hide.listdir(dir)) == 0
    
# processes
def openDirectoryInExplorer(dir):
    assert isdir(dir), 'not a dir? ' + dir
    assert '^' not in dir and '"' not in dir, 'dir cannot contain ^ or "'
    runWithoutWaitUnicode([u'cmd', u'/c', u'start', u'explorer.exe', dir])

def openUrl(s):
    assert s.startswith('http:') or s.startswith('https:')
    assert '^' not in s and '"' not in s, 'url cannot contain ^ or "'
    import webbrowser
    webbrowser.open(s, new=2)

# returns tuple (returncode, stdout, stderr)
def run(listArgs, _ind=_enforceExplicitlyNamedParameters, shell=False, createNoWindow=True,
        throwOnFailure=RuntimeError, stripText=True, captureoutput=True, silenceoutput=False):
    import sys
    import subprocess
    _checkNamedParameters(_ind)
    kwargs = {}
    
    if sys.platform == 'win32' and createNoWindow:
        kwargs['creationflags'] = 0x08000000
    
    if not captureoutput:
        retcode = subprocess.call(listArgs, shell=shell, **kwargs)
        if silenceoutput:
            stdout = open(os.devnull, 'wb')
            stderr = open(os.devnull, 'wb')
        else:
            stdout = None
            stderr = None
    else:
        sp = subprocess.Popen(listArgs, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
        comm = sp.communicate()
        stdout = comm[0]
        stderr = comm[1]
        retcode = sp.returncode
        if stripText:
            stdout = stdout.rstrip()
            stderr = stderr.rstrip()
        
    if throwOnFailure and retcode != 0:
        if throwOnFailure is True:
            throwOnFailure = RuntimeError
        exceptionText = 'retcode is not 0 for process ' + str(listArgs) + '\nstdout was ' + str(stdout) + '\nstderr was ' + str(stderr)
        raise throwOnFailure(getPrintable(exceptionText))
    
    return retcode, stdout, stderr
    
def runWithoutWaitUnicode(listArgs):
    # in Windows, non-ascii characters cause subprocess.Popen to fail.
    # https://bugs.python.org/issue1759845
    import sys
    if sys.platform != 'win32' or all(isinstance(arg, str) for arg in listArgs):
        import subprocess
        p = subprocess.Popen(listArgs, shell=False)
        return p.pid
    else:
        import winprocess, subprocess, types
        if isinstance(listArgs, types.StringTypes):
            combinedArgs = listArgs
        else:
            combinedArgs = subprocess.list2cmdline(listArgs)
            
        combinedArgs = unicode(combinedArgs)
        executable = None
        close_fds = False
        creationflags = 0
        env = None
        cwd = None
        startupinfo = winprocess.STARTUPINFO()
        handle, ht, pid, tid = winprocess.CreateProcess(executable, combinedArgs,
            None, None,
            int(not close_fds),
            creationflags,
            env,
            cwd,
            startupinfo)
        ht.Close()
        handle.Close()
        return pid
