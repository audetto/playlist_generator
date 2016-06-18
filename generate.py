import os
import sys
import shutil


VALID = ['.mp3', '.ogg', '.m4a']
INPUT_ENCODING = 'latin-1'
OUTPUT_ENCODING = 'utf-8'
M3U = '.m3u'
BAK = '.bak'

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


def findPlaylist(base):
    filenames = next(os.walk(base))[2]
    for file in filenames:
        name, ext = os.path.splitext(file)
        if ext == M3U:
            absolute = os.path.join(base, file)
            with open(absolute, 'r', encoding = INPUT_ENCODING) as pl:
                line = pl.readline().strip()
                if line and line.startswith('#EXTM3U'):
                    return absolute, True
            return absolute, False
    return None, None


def modifyPlaylist(base, playlist):
    backup = playlist + BAK

    # create backup copy
    shutil.copy(playlist, backup)

    # now we read the backup and recreate the playlist
    with open(backup, 'r', encoding = INPUT_ENCODING) as plIn, open(playlist, 'w', encoding = OUTPUT_ENCODING) as plOut:
        for line in plIn:
            if line:
                sline = line.strip() # this will remove \n at the end
                if not sline.startswith('#'):
                    relative = normalise(base, sline)
                    plOut.write(relative)
                    plOut.write('\n')

    print('New playlist written to: {}'.format(playlist))
    print('Old playlist backup in: {}'.format(backup))


def createNewPlaylist(base, playlist):
    if playlist == None:
        name = os.path.basename(os.path.normpath(base))
        playlist = os.path.join(base, name + M3U)

    with open(playlist, 'w', encoding = OUTPUT_ENCODING) as pl:
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
    playlist, modify = findPlaylist(base)

    if playlist and modify:
        print('Found existing playlist to modify: {}'.format(playlist))
        modifyPlaylist(base, playlist)
    else:
        print('Creating playlist from folder: {}'.format(base))
        createNewPlaylist(base, playlist)


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
