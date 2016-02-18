
import os as os_hide
import shutil as shutil_hide
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
abspath = shutil_hide.abspath
rmtree = shutil_hide.rmtree

from common_util import *	

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
    a,b = splitext(s)
    if len(b)>0 and b[0]=='.':
        return b[1:].lower()
    else:
        return b.lower()
    
def deletesure(s):
    if files.exists(s): files.delete(s)
    assert not files.exists(s)
    
# copy and move
def copy(a, b, bOverwrite):
    import sys
    if not exists(a):
        raise IOError('source path does not exist')
        
    if sys.platform=='win32':
        from ctypes import windll, c_wchar_p, c_int
        failIfExists = c_int(0) if bOverwrite else c_int(1)
        res = windll.kernel32.CopyFileW(c_wchar_p(a), c_wchar_p(b), failIfExists)
        if not res:
            raise IOError('CopyFileW failed (maybe dest already exists?)')
    else:
        if bOverwrite:
            shutil_hide.copy(a,b)
        else:
            # raises OSError on failure
            os.link(a, b)
    
    assertTrue(exists(b))
        
def move(a, b, bOverwrite):
    import sys
    if not exists(a):
        raise IOError('source path does not exist')
    if a==b:
        return
    if sys.platform=='win32':
        from ctypes import windll, c_wchar_p, c_int
        replaceexisting = c_int(1) if bOverwrite else c_int(0)
        res = windll.kernel32.MoveFileExW(c_wchar_p(a), c_wchar_p(b), replaceexisting)
        if not res:
            raise IOError('MoveFileExW failed (maybe dest already exists?)')
    elif sys.platform.startswith('linux') and bOverwrite:
        os.rename(a,b)
    else:
        copy(a, b, bOverwrite)
        assertTrue(exists(b))
        os.unlink(a)
    
    assertTrue(exists(b))
    
# unicodetype can be utf-8, utf-8-sig, etc.
def readall(s, mode='r', unicodetype=None):
    if unicodetype:
        import codecs
        f=codecs.open(s, mode, unicodetype)
    else:
        f=open(s,mode)
    txt = f.read()
    f.close()
    return txt

# unicodetype can be utf-8, utf-8-sig, etc.
def writeall(s, txt, mode='w', unicodetype=None):
    if unicodetype:
        import codecs
        f=codecs.open(s, mode, unicodetype)
    else:
        f=open(s,mode)
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
            yield filename if filenamesOnly else (dir+os_hide.path.sep+filename, filename)
    
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
            newdirs = [dir for dir in dirnames if fnFilterDirs(join(dirpath,dir))]
            dirnames[:] = newdirs
        
        if includeFiles:
            for filename in filenames:
                if not allowedexts or getext(filename) in allowedexts:
                    yield filename if filenamesOnly else (dirpath+os_hide.path.sep+filename, filename)
        
        if includeDirs:
            yield getname(dirpath) if filenamesOnly else (dirpath, getname(dirpath))
    
def recursedirs(root, _ind=_enforceExplicitlyNamedParameters, filenamesOnly=False, fnFilterDirs=None, topdown=True):
    _checkNamedParameters(_ind)
    return recursefiles(root, filenamesOnly=filenamesOnly, fnFilterDirs=fnFilterDirs, includeFiles=False, includeDirs=True, topdown=topdown)
    
def isemptydir(dir):
    return len(os_hide.listdir(dir))==0
    
#processes
def openDirectoryInExplorer(dir):
    import os
    assert isdir(dir), 'not a dir? '+dir
    assert not '^' in dir and not '"' in dir
    import subprocess
    subprocess.call(['start', 'explorer.exe', dir], shell=True)

def openUrl(s):
    assert s.startsWith('http:') or s.startsWith('https:')
    assert not ' ' in s and not '^' in s and not '"' in s and not "'" in s
    import subprocess
    subprocess.call(['start', fullurl], shell=True)

# returns tuple (returncode, stdout, stderr)
def run(listArgs, _ind=_enforceExplicitlyNamedParameters, shell=False, createNoWindow=True, 
    throwOnFailure=RuntimeError, stripText=True, captureoutput=True, silenceoutput=False):
    import sys
    import subprocess
    _checkNamedParameters(_ind)
    kwargs = {}
    
    if sys.platform=='win32' and createNoWindow:
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
        
    if throwOnFailure and retcode!=0:
        if throwOnFailure is True: throwOnFailure = RuntimeError
        exceptionText = 'retcode is not 0 for process '+str(listArgs)+'\nstdout was '+str(stdout)+'\nstderr was '+str(stderr)
        raise throwOnFailure(getPrintable(exceptionText))
    
    return retcode, stdout, stderr

if __name__=='__main__':
    import tempfile
    tmpdir = tempfile.gettempdir()+sep+'pytest'
    tmpdirsl = tmpdir+sep
    if not os_hide.path.exists(tmpdir):
        os_hide.mkdir(tmpdir)
    def cleardirectoryfiles(d):
        shutil_hide.rmtree(d)
        os_hide.mkdir(d)
        assertTrue(isemptydir(d))
    
    # test copy_overwrite, source not exist
    cleardirectoryfiles(tmpdir)
    assertException(lambda: copy(tmpdirsl+'src.txt', tmpdirsl+'srccopy.txt', True), IOError)
    
    # test copy_overwrite, simple copy
    cleardirectoryfiles(tmpdir)
    writeall(tmpdirsl+'src.txt', 'src')
    copy(tmpdirsl+'src.txt', tmpdirsl+'srccopy.txt', True)
    assertEq('src', readall(tmpdirsl+'srccopy.txt'))
    assertTrue(exists(tmpdirsl+'src.txt'))
    
    # test copy_overwrite, overwrite
    cleardirectoryfiles(tmpdir)
    writeall(tmpdirsl+'src.txt', 'src')
    assertEq('src', readall(tmpdirsl+'src.txt'))
    writeall(tmpdirsl+'dest.txt', 'dest')
    assertEq('dest', readall(tmpdirsl+'dest.txt'))
    copy(tmpdirsl+'src.txt', tmpdirsl+'dest.txt', True)
    assertEq('src', readall(tmpdirsl+'dest.txt'))
    assertTrue(exists(tmpdirsl+'src.txt'))
    
    # test copy_nooverwrite, source not exist
    cleardirectoryfiles(tmpdir)
    assertException(lambda: copy(tmpdirsl+'src.txt', tmpdirsl+'srccopy.txt', False), IOError)
    
    # test copy_nooverwrite, simple copy
    cleardirectoryfiles(tmpdir)
    writeall(tmpdirsl+'src.txt', 'src')
    copy(tmpdirsl+'src.txt', tmpdirsl+'srccopy.txt', False)
    assertEq('src', readall(tmpdirsl+'srccopy.txt'))
    
    # test copy_nooverwrite, simple overwrite should fail
    cleardirectoryfiles(tmpdir)
    writeall(tmpdirsl+'src.txt', 'src')
    assertEq('src', readall(tmpdirsl+'src.txt'))
    writeall(tmpdirsl+'dest.txt', 'dest')
    assertEq('dest', readall(tmpdirsl+'dest.txt'))
    assertException(lambda: copy(tmpdirsl+'src.txt', tmpdirsl+'dest.txt', False), IOError, 'CopyFileW failed')
    assertEq('dest', readall(tmpdirsl+'dest.txt'))
    
    # test move_overwrite, source not exist
    cleardirectoryfiles(tmpdir)
    assertException(lambda: move(tmpdirsl+'src.txt', tmpdirsl+'srcmove.txt', True), IOError)
    assertTrue(not exists(tmpdirsl+'src.txt'))
    
    # test move_overwrite, simple move
    cleardirectoryfiles(tmpdir)
    writeall(tmpdirsl+'src.txt', 'src')
    move(tmpdirsl+'src.txt', tmpdirsl+'srcmove.txt', True)
    assertEq('src', readall(tmpdirsl+'srcmove.txt'))
    assertTrue(not exists(tmpdirsl+'src.txt'))
    
    # test move_overwrite, overwrite
    cleardirectoryfiles(tmpdir)
    writeall(tmpdirsl+'src.txt', 'src')
    assertEq('src', readall(tmpdirsl+'src.txt'))
    writeall(tmpdirsl+'dest.txt', 'dest')
    assertEq('dest', readall(tmpdirsl+'dest.txt'))
    move(tmpdirsl+'src.txt', tmpdirsl+'dest.txt', True)
    assertEq('src', readall(tmpdirsl+'dest.txt'))
    assertTrue(not exists(tmpdirsl+'src.txt'))
    
    # test move_nooverwrite, source not exist
    cleardirectoryfiles(tmpdir)
    assertException(lambda: move(tmpdirsl+'src.txt', tmpdirsl+'srcmove.txt', False), IOError)
    assertTrue(not exists(tmpdirsl+'src.txt'))
    
    # test move_nooverwrite, simple move
    cleardirectoryfiles(tmpdir)
    writeall(tmpdirsl+'src.txt', 'src')
    move(tmpdirsl+'src.txt', tmpdirsl+'srcmove.txt', False)
    assertEq('src', readall(tmpdirsl+'srcmove.txt'))
    assertTrue(not exists(tmpdirsl+'src.txt'))
    
    # test move_nooverwrite, simple overwrite should fail
    cleardirectoryfiles(tmpdir)
    writeall(tmpdirsl+'src.txt', 'src')
    assertEq('src', readall(tmpdirsl+'src.txt'))
    writeall(tmpdirsl+'dest.txt', 'dest')
    assertEq('dest', readall(tmpdirsl+'dest.txt'))
    assertException(lambda: move(tmpdirsl+'src.txt', tmpdirsl+'dest.txt', False), IOError, 'MoveFileExW failed')
    assertEq('dest', readall(tmpdirsl+'dest.txt'))
    assertTrue(exists(tmpdirsl+'src.txt'))
    
    # test _checkNamedParameters
    assertException(lambda: list(listchildren(tmpdir, True)), ValueError, 'please name parameters')
    
    # tmpdir has files, dirs
    # tmpdir/s1 has no files, dirs
    # tmpdir/s1/ss1 has files, no dirs
    # tmpdir/s1/ss2 has no files, dirs
    cleardirectoryfiles(tmpdir)
    dirstomake = [tmpdir, tmpdirsl+'s1', tmpdirsl+'s1'+sep+'ss1', tmpdirsl+'s1'+sep+'ss2', tmpdirsl+'s2']
    filestomake = [tmpdirsl+'P1.PNG', tmpdirsl+'a1.txt', tmpdirsl+'a2png',
        tmpdirsl+'s1'+sep+'ss1'+sep+'file.txt', tmpdirsl+'s2'+sep+'other.txt']
    for dir in dirstomake:
        if dir != tmpdir:
            makedir(dir)
    for file in filestomake:
        writeall(file, 'content')
    
    # test listchildren
    expected = ['P1.PNG', 'a1.txt', 'a2png', 's1', 's2']
    assertEq([(tmpdirsl+s,s) for s in expected], sorted(list(listchildren(tmpdir))))
    assertEq(expected, sorted(list(listchildren(tmpdir, filenamesOnly=True))))
    assertEq(['P1.PNG', 'a1.txt'], sorted(list(listchildren(tmpdir, filenamesOnly=True, allowedexts=['png','txt']))))
    
    # test listfiles
    expected = ['P1.PNG', 'a1.txt', 'a2png']
    assertEq([(tmpdirsl+s,s) for s in expected], sorted(list(listfiles(tmpdir))))
    assertEq(expected, sorted(list(listfiles(tmpdir, filenamesOnly=True))))
    assertEq(['P1.PNG', 'a1.txt'], sorted(list(listfiles(tmpdir, filenamesOnly=True, allowedexts=['png','txt']))))
    
    # test recursefiles
    assertEq([(s,getname(s)) for s in filestomake], sorted(list(recursefiles(tmpdir))))
    assertEq([getname(s) for s in filestomake], sorted(list(recursefiles(tmpdir, filenamesOnly=True))))
    assertEq(['a1.txt', 'file.txt', 'other.txt'], sorted(list(recursefiles(tmpdir, filenamesOnly=True, allowedexts=['txt']))))
    assertEq(['a1.txt', 'file.txt', 'other.txt'], sorted(list(recursefiles(tmpdir, filenamesOnly=True, allowedexts=['txt'], fnFilterDirs=lambda d:True))))
    assertEq(['a1.txt'], sorted(list(recursefiles(tmpdir, filenamesOnly=True, allowedexts=['txt'], fnFilterDirs=lambda d:False))))
    assertEq(['a1.txt', 'other.txt'], sorted(list(recursefiles(tmpdir, filenamesOnly=True, allowedexts=['txt'], fnFilterDirs=lambda dir:getname(dir)!='s1'))))
    assertEq(['a1.txt', 'file.txt'], sorted(list(recursefiles(tmpdir, filenamesOnly=True, allowedexts=['txt'], fnFilterDirs=lambda dir:getname(dir)!='s2'))))
    
    # test recursedirs
    assertEq(sorted([(s,getname(s)) for s in dirstomake]), sorted(list(recursedirs(tmpdir))))
    assertEq(sorted([getname(s) for s in dirstomake]), sorted(list(recursedirs(tmpdir, filenamesOnly=True))))
    assertEq(['pytest', 's2'], sorted(list(recursedirs(tmpdir, filenamesOnly=True, fnFilterDirs=lambda dir:getname(dir)!='s1'))))
    
    # test run process, simple batch script
    cleardirectoryfiles(tmpdir)
    writeall(tmpdirsl+'src.txt', 'src')
    writeall(tmpdirsl+'script.bat', 'copy "%ssrc.txt" "%sdest.txt"'%(tmpdirsl,tmpdirsl))
    assertTrue(not exists(tmpdirsl+'dest.txt'))
    returncode, stdout, stderr = run([tmpdirsl+'script.bat'])
    assertEq(0, returncode)
    assertTrue(exists(tmpdirsl+'dest.txt'))
    # specify no capture and run again
    delete(tmpdirsl+'dest.txt')
    returncode, stdout, stderr = run([tmpdirsl+'script.bat'], captureoutput=False)
    assertEq(0, returncode)
    assertTrue(exists(tmpdirsl+'dest.txt'))
    
    # test run process, batch script returns failure
    cleardirectoryfiles(tmpdir)
    writeall(tmpdirsl+'script.bat', '\nexit /b 123')
    returncode, stdout, stderr = run([tmpdirsl+'script.bat'], throwOnFailure=False)
    assertEq(123, returncode)
    # specify no capture and run again
    returncode, stdout, stderr = run([tmpdirsl+'script.bat'], throwOnFailure=False, captureoutput=False)
    assertEq(123, returncode)
    # except exception
    assertException(lambda: run([tmpdirsl+'script.bat']), RuntimeError, 'retcode is not 0')
    # specify no capture, except exception
    assertException(lambda: run([tmpdirsl+'script.bat'], captureoutput=False), RuntimeError, 'retcode is not 0')
    
    # test run process, get stdout
    writeall(tmpdirsl+'script.bat', '\n@echo off\necho testecho')
    returncode, stdout, stderr = run([tmpdirsl+'script.bat'])
    assertEq(0, returncode)
    assertEq('testecho', stdout)
    assertEq('', stderr)
    
    # test run process, get stderr
    writeall(tmpdirsl+'script.bat', '\n@echo off\necho testechoerr 1>&2')
    returncode, stdout, stderr = run([tmpdirsl+'script.bat'])
    assertEq(0, returncode)
    assertEq('', stdout)
    assertEq('testechoerr', stderr)
    
    # test run process, get both. (this deadlocks if done naively, but it looks like subprocess correctly uses 2 threads.)
    writeall(tmpdirsl+'script.bat', '\n@echo off\necho testecho\necho testechoerr 1>&2')
    returncode, stdout, stderr = run([tmpdirsl+'script.bat'])
    assertEq(0, returncode)
    assertEq('testecho', stdout)
    assertEq('testechoerr', stderr)
    
    # test run process, send argument without spaces
    writeall(tmpdirsl+'script.bat', '\n@echo off\necho %1')
    returncode, stdout, stderr = run([tmpdirsl+'script.bat', 'testarg'])
    assertEq(0, returncode)
    assertEq('testarg', stdout)
    
    # test run process, send argument with spaces (subprocess will quote the args)
    writeall(tmpdirsl+'script.bat', '\n@echo off\necho %1')
    returncode, stdout, stderr = run([tmpdirsl+'script.bat', 'test arg'])
    assertEq(0, returncode)
    assertEq('"test arg"', stdout)
    
    # test run process, run without shell
    cleardirectoryfiles(tmpdir)
    writeall(tmpdirsl+'src.txt', 'src')
    # won't work without the shell:
    assertException(lambda:run(['copy', tmpdirsl+'src.txt', tmpdirsl+'dest.txt']), OSError)
    assertTrue(not exists(tmpdirsl+'dest.txt'))
    # will work with the shell
    returncode, stdout, stderr = run(['copy', tmpdirsl+'src.txt', tmpdirsl+'dest.txt'], shell=True)
    assertEq(0, returncode)
    assertTrue(exists(tmpdirsl+'dest.txt'))
    

    
    