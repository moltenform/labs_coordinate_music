import os
import sys
import json
from shinerainsevenlib.standard import *
import toml

def mainPylint(thisCfg):
    args = [
        '-m', 'pylint', '--rcfile', 'pyproject.toml', '--ignore-paths=.*OUTSIDE.*',
        '--output-format=json2', '.'
    ]
    pyExe = sys.executable
    args.insert(0, pyExe)
    print(args)
    retcode, stdout, stderr = files.run(args, throwOnFailure=False)
    if stderr:
        print('pylint failed', stdout.decode('utf-8'), stderr.decode('utf-8'))
        return

    stdout = stdout.decode('utf-8')
    events = json.loads(stdout)
    events = events['messages']
    specificIgnores = thisCfg.get('pylint_specific_ignore', [])
    for event in events:
        line = formatOneLinePylint(event)
        for ignore in specificIgnores:
            if ignore in line:
                continue

        print(line)


def mainRuff(thisCfg):
    args = [
        '-m', 'ruff', 'check', '--config=pyproject.toml', '--output-format=json',
        '--exclude=.*OUTSIDE.*'
    ]
    if '--fix' in sys.argv:
        args.append('--fix')

    args.append('.')
    pyExe = sys.executable
    args.insert(0, pyExe)
    print(args)
    retcode, stdout, stderr = files.run(args, throwOnFailure=False)
    if stderr:
        print('ruff failed', stdout.decode('utf-8'), stderr.decode('utf-8'))
        return

    stdout = stdout.decode('utf-8')
    events = json.loads(stdout)
    specificIgnores = thisCfg.get('rufflint_specific_ignore', [])
    for event in events:
        if 'test' in files.getName(event['filename']) and event.get('code') == 'S101':
            # ok for test files to have asserts
            continue

        line = formatOneLineRuff(event)
        if "Variable `dir` is shadowing":
            continue

        for ignore in specificIgnores:
            if ignore in line:
                continue

        print(line)


def formatOneLineRuff(msg):
    # example.py:32:67: W0640: An example message (the-warning-type)
    return f"{msg['filename']}:{msg['location'].get('row')}:{msg['location'].get('column')}: {msg['code']} {msg['message']} ({msg.get('url', '').split('/')[-1]})"


def formatOneLinePylint(msg):
    # example.py:32:67: W0640: An example message (the-warning-type)
    return f"{msg['path']}:{msg['line']}:{msg['column']}: {msg['messageId']}: {msg['message']} ({msg['symbol']})"



def mainAutoformat(thisCfg):
    # note that yapf also supports  '--recursive', '--parallel' params
    # but we can't use them now that we target file-by-file
    args = [
        '-m', 'yapf', '--in-place'
    ]

    args.append('.')
    pyExe = sys.executable
    args.insert(0, pyExe)
    print(args)
    ignored = thisCfg.get('autoformat_ignore', [])
    #~ for f, short in files.recurseFiles('.'):
        #~ if short.endswith('.py'):
            #~ shouldIgnore = jslike.find(ignored, lambda item: )
    retcode, stdout, stderr = files.run(args, throwOnFailure=False)

def main():
    
        

if __name__ == '__main__':
    main()

