import os
import sys
import shutil


VALID = ['.mp3', '.ogg', '.m4a']
ENCODING = 'latin-1'
M3U = '.m3u'
BAK = '.bak'


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
            with open(absolute, 'r', encoding = ENCODING) as pl:
                line = pl.readline()
                if line and line.startswith('#EXTM3U'):
                    return absolute, True
            return absolute, False
    return None, None


def modifyPlaylist(base, playlist):
    backup = playlist + BAK

    # create backup copy
    shutil.copy(playlist, backup)

    # now we read the backup and recreate the playlist
    with open(backup, 'r', encoding = ENCODING) as plIn, open(playlist, 'w', encoding = ENCODING) as plOut:
        for line in plIn:
            if line and (not line.startswith('#')):
                relative = normalise(base, line)
                plOut.write(relative)

    print('New playlist written to: {}'.format(playlist))
    print('Old playlist backup in: {}'.format(backup))


def createNewPlaylist(base, playlist):
    if playlist == None:
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
            print('Processing {}'.format(absolute))
            # this will recurse inside
            processFolder(absolute)
            print()

        # we only look at the immediate children
        # they will be recursing inside
        break

main()
