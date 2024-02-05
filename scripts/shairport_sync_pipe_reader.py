#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# cat /tmp/shairport-sync-metadata | python3 output_text.py

import base64
import binascii
import codecs
import json
import logging
import math
import os
import re
import shutil
import sys
import tempfile
import time
from multiprocessing import Process

try:
    from asciimatics.renderers import ImageFile  # pip install asciimatics
    asciimatics_avail = True
except ImportError:
    asciimatics_avail = False

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    datefmt='%m-%d %H:%M',
    filemode='w')
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

logger = logging.getLogger(__name__)

# started with code from
# https://github.com/surekap/MMM-ShairportMetadata/blob/master/shairport-metadata.py

def start_item(line):
    regex = r"<item><type>(([A-Fa-f0-9]{2}){4})</type><code>(([A-Fa-f0-9]{2}){4})</code><length>(\d*)</length>"
    matches = re.findall(regex, line)
    #print(matches)
    # python2 only # typ = matches[0][0].decode('hex')
    # python2 only # code = matches[0][2].decode('hex')
    #typ = codecs.decode(matches[0][0], 'hex').decode()
    #code = codecs.decode(matches[0][2], 'hex').decode()
    #typ = base64.b16decode(matches[0][0], casefold=True).decode()
    #code = base64.b16decode(matches[0][2], casefold=True).decode()
    typ = str(binascii.unhexlify(matches[0][0]), 'ascii')
    code = str(binascii.unhexlify(matches[0][2]), 'ascii')
    length = int(matches[0][4])
    return (typ, code, length)


def start_data(line):
    # logger.debug(line)
    try:
        assert line == '<data encoding="base64">\n'
    except AssertionError:
        if line.startswith("<data"):
            return 0
        return -1
    return 0


def read_data(line, length):
    # convert to base64 size
    b64size = 4 * math.ceil((length) / 3)
    #if length < 100: print (line, end="")
    try:
        data = base64.b64decode(line[:b64size])
        # Assume it is a PICT and do not attempt to decode the binary data
        if length > 1000:
            # print (data[:4])
            return data
        data = data.decode()
    except TypeError:
        data = ""
        pass
    except UnicodeDecodeError:
        # print(data)
        data = ""
        pass
    return data


def guessImageMime(magic):
    # print(magic[:4])
    if magic.startswith(b'\xff\xd8'):
        return 'image/jpeg'
    elif magic.startswith(b'\x89PNG\r\n\x1a\r'):
        return 'image/png'
    else:
        return "image/jpg"


def main():
    metadata = {}
    fi = sys.stdin
    while True:
        line = sys.stdin.readline()
        if not line:  #EOF
            break
        sys.stdout.flush()
        if not line.startswith("<item>"):
            continue
        typ, code, length = start_item(line)

        data = ""
        if (length > 0):
            line2 = fi.readline()
            r = start_data(line2)
            if (r == -1):
                continue
            line3 = fi.readline()
            data = read_data(line3, length)

        # Everything read
        if (typ == 'core'):
            if (code == "asal"):
                metadata['songalbum'] = data
                # print(data)
            elif (code == "asar"):
                metadata['songartist'] = data
            #elif (code == "ascm"):
            #    metadata['Comment'] = data
            #elif (code == "asgn"):
            #    metadata['Genre'] = data
            elif (code == "minm"):
                metadata['itemname'] = data
            #elif (code == "ascp"):
            #    metadata['Composer'] = data
            #elif (code == "asdt"):
            #    metadata['File Kind'] = data
            #elif (code == "assn"):
            #    metadata['Sort as'] = data
            #elif (code == "clip"):
            #    metadata['IP'] = data

        if (typ == "ssnc" and code == "pend"):
            sys.stdout.flush()

        if (typ == "ssnc" and code == "mden"):
            state_changed('play', metadata)
            sys.stdout.flush()
        if (typ == "ssnc" and code == "prgr"):
            state_changed('play', None)
            sys.stdout.flush()

        if (typ == "ssnc" and (code == "pfls" or code == 'paus')):
            print('paused with code', code)
            state_changed('pause', None)
            sys.stdout.flush()

        if (typ == "ssnc" and code == "PICT"):
            if len(data) == 0:
                pass
            else:
                mime = guessImageMime(data)
                # print(mime)
                # if (mime == 'image/png'):
                #     temp_file = tempfile.NamedTemporaryFile(
                #         prefix="image_",
                #         suffix=".png",
                #         delete=False,
                #         dir=tempdirname)
                # elif (mime == 'image/jpeg'):
                #     temp_file = tempfile.NamedTemporaryFile(
                #         prefix="image_",
                #         suffix=".jpeg",
                #         delete=False,
                #         dir=tempdirname)
                # else:
                #     temp_file = tempfile.NamedTemporaryFile(
                #         prefix="image_",
                #         suffix=".jpg",
                #         delete=False,
                #         dir=tempdirname)

                # with temp_file as file:
                #     file.write(data)
                #     file.close()
                    
                notify_album_artwork()
            sys.stdout.flush()

previous_metadata = {}
pause_process = []
def state_changed(state, metadata):
    print('$'*20, 'state_changed', state, '$'*20)
    global previous_metadata
    global pause_process

    if metadata is not None:
        previous_metadata = metadata
    else:
        metadata = previous_metadata

    if metadata is not None:
        if state == 'play':
            for p in pause_process:
                if p.is_alive():
                    p.kill()
                    print('killed pause process!')
            pause_process = []
            notify(state, metadata)
        elif state == 'pause':
            process = Process(target=__state_changed_to_pause, args=(state, metadata, ))
            process.start()
            pause_process.append(process)
    else:
        print('metadata was None!')

def __state_changed_to_pause(state, metadata):
    time.sleep(4)
    notify(state, metadata)

def notify(state, metadata):
    # track_information = ''
    # if 'songartist' in metadata:
    #     track_information += metadata['songartist']
    # if 'itemname' in metadata:
    #     if len(track_information) > 0:
    #         track_information += ' - '
    #     track_information += metadata['itemname']

    # shairport_sync_onevent.set_track_information(state, track_information)
    print('notify', state, metadata)
    os.system('/home/pi/scripts/github/media_frame/scripts/onevent.py ShairportSync ' + state)

def notify_album_artwork():
    # print('notify album artwork!')
    # notify('album_artwork', path)

    # os.system('/home/pi/scripts/github/media_frame/scripts/onevent.py ShairportSync --artwork')
    # shairport_sync_onevent.set_album_artwork(path)
    pass

# cat /tmp/shairport-sync-metadata | /usr/bin/python3 ./output_text.py
# cat /tmp/shairport-sync-metadata | python3 ~/scripts/github/shairport-sync-metadata-python/bin/output_text.py
if __name__ == "__main__":
    main()        
