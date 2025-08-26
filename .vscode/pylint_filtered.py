
import sys
from shinerainsevenlib.standard import *

def main():
    pyExe = sys.executable
    args = 'py -m pylint --rcfile pyproject.toml .'.split(' ')
    args[0] = pyExe
    retcode, stdout, stderr = files.run(args, throwOnFailure=False)
    stdout = stdout.decode('utf-8')
    allLines = srss.strToList(stdout)
    for line in allLines:
        if "E1101: Instance of 'Bucket' has no" in line:
            # skip this - we don't care about it for Bucket
            continue
        if "W0621: Redefining name 'fixture_" in line:
            # skip this - we don't care about it for fixures
            continue

        print(line)

if __name__=='__main__':
    main()