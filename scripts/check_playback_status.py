#!/usr/bin/python
import os
import subprocess
import time


def get_running_player():
    players = execute('/usr/bin/playerctl -l').strip().split('\n')
    anything_playing = False
    for player in players:
        status = execute('/usr/bin/playerctl --player=' + player + ' status').replace('\n', '').strip()
#        print(player, status)

        if 'Playing' in status:
            return player

    return None

def is_anything_playing():
    return get_running_player() != None

def is_music_view_active():
    music_is_active_file = '/home/pi/scripts/github/media_frame/data/music/is_active'
    return os.path.isfile(music_is_active_file)

def main():

    if is_music_view_active() and not is_anything_playing():
        print('music seems to be stopped, checking again in 8 minutes')
        time.sleep(60*8)

        if is_music_view_active() and not is_anything_playing():
            print('music seems to be stopped, this is the final check')
            print('changing PictureFrame to photos')
            os.system('/home/pi/scripts/github/media_frame/scripts/change_media_to_photos.sh')

def execute(command):
    result = subprocess.run([command], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    return result.stdout.decode('utf-8')#.replace('\n', '')

if __name__ == '__main__':
    main()
