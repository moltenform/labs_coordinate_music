# BenPythonCommon,
# 2015 Ben Fisher, released under the GPLv3 license.

class Bucket(object):
    "simple named-tuple; o.field looks nicer than o['field']. "
    def __init__(self, **kwargs):
        for key in kwargs:
            object.__setattr__(self, key, kwargs[key])
    def __repr__(self): 
        return '\n\n\n'.join(('%s=%s'%(unicode(key), unicode(self.__dict__[key])) for key in sorted(self.__dict__)))
            
class SimpleEnum(object):
    "simple enum; prevents modification after creation."
    _set = None
    def __init__(self, listStart):
        self._set = set(listStart)
    def __getattribute__(self, name):
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        elif name in self._set:
            return name
        else:
            raise AttributeError
    def __setattribute__(self, name, value):
        if name.startswith('_'):
            object.__setattr__(self, name, value)
        else:
            raise RuntimeError
    def __delattr__(self, name):
        raise RuntimeError
    
def getPrintable(s, okToIgnore=False):
    if not isinstance(s, unicode): return str(s)
    import unicodedata
    s = unicodedata.normalize('NFKD', s)
    if okToIgnore: return s.encode('ascii', 'ignore')
    else: return s.encode('ascii', 'replace')
        
def trace(*args):
    print(' '.join(map(getPrintable, args)))
        
def safefilename(s):
    return s.replace(u'\u2019', u"'").replace(u'?', u'').replace(u'!', u'') \
        .replace(u'\\ ', u', ').replace(u'\\', u'-') \
        .replace(u'/ ', u', ').replace(u'/', u'-') \
        .replace(u': ', u', ').replace(u':', u'-') \
        .replace(u'| ', u', ').replace(u'|', u'-') \
        .replace(u'*',u'') \
        .replace(u'"', u"'").replace(u'<', u'[').replace(u'>', u']')
        
def getRandomString():
    import random
    return '%s'%random.randrange(99999)
        
def warnWithOptionToContinue(s):
    trace('WARNING '+s)
    if not getInputBool('continue?'):
        raise RuntimeError()
        

def re_replacewholeword(starget, sin, srep):
    import re
    sin = '\\b'+re.escape(sin)+'\\b'
    return re.sub(sin, srep, starget)

def re_replace(starget, sre, srep):
    import re
    return re.sub(sre, srep, starget)

'''
re.search(pattern, string, flags=0)
    look for at most one match starting anywhere
re.match(pattern, string, flags=0)
    look for match starting only at beginning of string
re.findall(pattern, string, flags=0)
    returns list of strings
re.finditer(pattern, string, flags=0)
    returns iterator of match objects
    
re.IGNORECASE, re.MULTILINE, re.DOTALL
'''
 
def getClipboardText():
    from Tkinter import Tk
    try:
        r = Tk()
        r.withdraw()
        s = r.clipboard_get()
    finally:
        r.destroy()
    return s
    
def setClipboardText(s):
    from Tkinter import Tk
    text = unicode(s)
    try:
        r = Tk()
        r.withdraw()
        r.clipboard_clear()
        r.clipboard_append(text)
    finally:
        r.destroy()

def takeBatchOnArbitraryIterable(iterable, size):
    import itertools
    it = iter(iterable)
    item = list(itertools.islice(it, size))
    while item:
        yield item
        item = list(itertools.islice(it, size))

def takeBatch(l, n):
    """ Yield successive n-sized chunks from l."""
    return list(takeBatchOnArbitraryIterable(l, n))
        
def startThread(fn, args=None):
    import threading
    if args is None: args=tuple()
    t = threading.Thread(target=fn, args=args)
    t.start()
    
# inspired by http://code.activestate.com/recipes/496879-memoize-decorator-function-with-cache-size-limit/
def BoundedMemoize(fn):
    from collections import OrderedDict
    cache = OrderedDict()
    def memoize_wrapper(*args, **kwargs):
        try:
           import cPickle as pickle
        except ImportError:
           import pickle 
        key = pickle.dumps((args, kwargs))
        try:
            return cache[key]
        except KeyError:
            result = fn(*args, **kwargs)
            cache[key] = result
            if len(cache) > memoize_wrapper._limit:
                cache.popitem(False) # the false means remove as FIFO
            return result

    memoize_wrapper._limit = 20
    memoize_wrapper._cache = cache
    memoize_wrapper.func_name = fn.func_name
    return memoize_wrapper
    
def DBG(obj=None):
    import pprint
    if obj is None:
        import inspect
        fback = inspect.currentframe().f_back
        framelocals = fback.f_locals
        newDict = {}
        for key in framelocals:
            if not callable(framelocals[key]) and not inspect.isclass(framelocals[key]) and not inspect.ismodule(framelocals[key]):
                newDict[key] = framelocals[key]
        pprint.pprint(newDict)
    else:
        pprint.pprint(obj)
            
def assertTrue(condition, *messageArgs):
    if not condition:
        msg = ' '.join(map(getPrintable, messageArgs)) if messageArgs else ''
        raise AssertionError(msg)
    
def assertEq(expected, received, *messageArgs):
    if expected!=received:
        import pprint
        msg = ' '.join(map(getPrintable, messageArgs)) if messageArgs else ''
        msg += '\nassertion failed, expected:\n'
        msg += getPrintable(pprint.pformat(expected))
        msg += '\nbut got:\n'
        msg += getPrintable(pprint.pformat(received))
        raise AssertionError(msg)
        
def assertException(fn, excType, excTypeExpectedString=None, msg='', regexp=False):
    import pprint
    import sys
    e = None
    try:
        fn()
    except:
        e = sys.exc_info()[1]
    
    assertTrue(e != None, 'did not throw '+msg)
    if excType:
        assertTrue(isinstance(e, excType), 'exception type check failed '+msg+ ' \ngot \n'+pprint.pformat(e)+'\n not \n'+pprint.pformat(excType))
    if excTypeExpectedString:
        if regexp:
            import re
            passed = re.search(excTypeExpectedString, str(e))
        else:
            passed = excTypeExpectedString in str(e)
        assertTrue(passed, 'exception string check failed '+msg+'\ngot exception string:\n'+ str(e))
        
        
if __name__=='__main__':
    # test assertException
    def raisevalueerr(): raise ValueError('msg')
    assertException(lambda: raisevalueerr(), None)
    assertException(lambda: raisevalueerr(), ValueError)
    assertException(lambda: raisevalueerr(), ValueError, 'msg')
    assertException(lambda: assertException(lambda: 1, None), AssertionError, 'did not throw')
    assertException(lambda: assertException(lambda: raisevalueerr(), TypeError), AssertionError, 'exception type check failed')
    assertException(lambda: assertException(lambda: raisevalueerr(), ValueError, 'notmsg'), AssertionError, 'exception string check failed')
    
    # test assertTrue
    assertTrue(True)
    assertException(lambda: assertTrue(False, 'msg here'), AssertionError, 'msg here')
    
    # test assertEq
    assertEq(1, 1)
    assertException(lambda: assertEq(1, 2,'msg here'), AssertionError, 'msg here')
    
    # test Bucket
    b = Bucket()
    b.elem1 = '1'
    b.elem2 = '2'
    assertEq('elem1=1\n\n\nelem2=2', b.__repr__())
    
    # test getPrintable
    assertEq('normal ascii', getPrintable('normal ascii'))
    assertEq('normal unicode', getPrintable(u'normal unicode'))
    assertEq('k?u?o??n', getPrintable(u'\u1E31\u1E77\u1E53\u006E')) #mixed non-ascii and ascii
    assertEq('k?u?o??n', getPrintable(u'\u006B\u0301\u0075\u032D\u006F\u0304\u0301\u006E')) #mixed composite sequence and ascii
    
    # test getRandomString
    s1 = getRandomString()
    s2 = getRandomString()
    assertTrue(all((c in '0123456789' for c in s1)))
    assertTrue(all((c in '0123456789' for c in s2)))
    assertTrue(s1 != s2)
    
    # test re_replacewholeword
    assertEq('w,n,w other,wantother,w.other', re_replacewholeword('want,n,want other,wantother,want.other', 'want', 'w'))
    assertEq('w,n,w other,w??|tother,w.other', re_replacewholeword('w??|t,n,w??|t other,w??|tother,w??|t.other', 'w??|t', 'w'))
    assertEq('and A fad pineapple A da', re_replacewholeword('and a fad pineapple a da', 'a', 'A'))
    assertEq('and a GAd pinGApple a GA', re_replace('and a fad pineapple a da', '[abcdef]a', 'GA'))
    
    # test getClipboardText
    prev = getClipboardText()
    try:
        setClipboardText('normal ascii')
        assertEq('normal ascii', getClipboardText())
        setClipboardText(u'\u1E31\u1E77\u1E53\u006E')
        assertEq(u'\u1E31\u1E77\u1E53\u006E', getClipboardText())
    finally:
        setClipboardText(prev)
    
    # takeBatch and takeBatchOnArbitraryIterable have the same implementation
    assertEq( [[1,2,3],[4,5,6],[7]], takeBatch([1,2,3,4,5,6,7], 3))
    assertEq( [[1,2,3],[4,5,6]], takeBatch([1,2,3,4,5,6], 3))
    assertEq( [[1,2,3],[4,5]], takeBatch([1,2,3,4,5], 3))
    assertEq( [[1,2],[3,4],[5]], takeBatch([1,2,3,4,5], 2))
    
    # test OrderedDict equality checks
    from collections import OrderedDict
    assertEq(OrderedDict(a=1, b=2), OrderedDict(b=2, a=1))
    assertTrue(OrderedDict(a=1, b=2) != OrderedDict(a=1, b=3))
    
    # test BoundedMemoize
    countCalls = Bucket(count=0)
    @BoundedMemoize
    def addTwoNumbers(a, b, countCalls=countCalls):
        countCalls.count += 1
        return a+b
    assertEq(2, addTwoNumbers(1,1))
    assertEq(1, countCalls.count)
    assertEq(2, addTwoNumbers(1,1))
    assertEq(1, countCalls.count)
    assertEq(4, addTwoNumbers(2,2))
    assertEq(2, countCalls.count)
    
    
    
    