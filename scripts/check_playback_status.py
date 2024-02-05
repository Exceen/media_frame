#!/usr/bin/python
import os
import subprocess
import time

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
USE_FAKED_LOOP_STATUS_INSTEAD_OF_DBUS_FOR_SPOTIFYD = False

def is_spotify_running():
    try:
        access_token = execute('/usr/bin/playerctl -p spotifyd loop').split('got unknown loop status: ')[-1].split('\n')[0]
        sp = spotipy.Spotify(auth=access_token)
        sp_track = sp.current_user_playing_track()
        return sp_track != None and sp_track['is_playing'] == True
    except Exception as e:
        print(e)
        return False

def get_running_player():
    # these debug messages where implemented on 2022-12-15
    players = execute('/usr/bin/playerctl -l').strip().split('\n')
    anything_playing = False
    print('found players (' + str(len(players)) + '):', players)
    for player in players:
        status = execute('/usr/bin/playerctl --player=' + player + ' status').replace('\n', '').strip()
#        print(player, status)

        print('status for player ' + str(player) + ':', status)
        if 'Playing' in status:
            print('returning player:', player)
            return player

    print('returning None (no player running)')
    return None

def is_anything_playing():
    return get_running_player() != None or (USE_FAKED_LOOP_STATUS_INSTEAD_OF_DBUS_FOR_SPOTIFYD and is_spotify_running())

def is_music_view_active():
    music_is_active_file = '/home/pi/scripts/github/media_frame/data/music/is_active'
    return os.path.isfile(music_is_active_file)

def main():
    print('check disabled')
    quit()
    if is_music_view_active() and not is_anything_playing():
        print('music seems to be stopped, checking again in 1 minute')
        time.sleep(60*1)

        if is_music_view_active() and not is_anything_playing():
            print('music seems to be stopped, this is the final check')
            print('changing PictureFrame to photos')
            os.system('/home/pi/scripts/github/media_frame/scripts/change_media_to_photos.sh')

def execute(command):
    result = subprocess.run([command], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    return result.stdout.decode('utf-8')#.replace('\n', '')

if __name__ == '__main__':
    main()
