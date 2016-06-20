import os
import sys
import traceback


VALID = ['.mp3', '.ogg', '.m4a']
ENCODING = 'utf-8'
M3U = '.m3u'

SKIP_FOLDERS = ['SCS.4DJ_', 'RECYCLE.BIN']


def skipFolder(name):
    for s in SKIP_FOLDERS:
        if s in name:
            return True  # SKIP
    return False # ACCEPT


def normalise(base, absolute):
    relative = os.path.relpath(absolute, base)
    relative = relative.replace('\\', '/')
    relative = './' + relative
    return relative


def removePlaylist(base):
    # we are not recursing in here
    filenames = next(os.walk(base))[2]
    for file in filenames:
        name, ext = os.path.splitext(file)
        if ext == M3U:
            absolute = os.path.join(base, file)
            os.remove(absolute)


def createNewPlaylist(base):
    name = os.path.basename(os.path.normpath(base))
    playlist = os.path.join(base, name + M3U)

    with open(playlist, 'w', encoding = ENCODING) as pl:
        for path, dirs, files in os.walk(base):
            for f in files:
                name, ext = os.path.splitext(f)
                if ext in VALID:
                    absolute = os.path.join(path, f)
                    relative = normalise(base, absolute)
                    pl.write(relative)
                    pl.write('\n')

    print('New playlist written to: {}'.format(playlist))


def processFolder(base):
    try:
        removePlaylist(base)
        createNewPlaylist(base)
    except (PermissionError, UnicodeDecodeError, UnicodeEncodeError):
        traceback.print_exc()


def main():
    base = sys.argv[1]

    for path, dirs, files in os.walk(base):
        for dir in dirs:
            absolute = os.path.abspath(os.path.join(path, dir))
            if skipFolder(dir):
                print('Skipping {}'.format(absolute))
            else:
                print('Processing {}'.format(absolute))
                # this will recurse inside
                processFolder(absolute)
            print()

        # we only look at the immediate children
        # they will be recursing inside
        break

main()
