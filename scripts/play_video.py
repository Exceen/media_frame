#!/usr/bin/python
import paho.mqtt.client as mqtt
import os
import subprocess
import argparse
from multiprocessing import Process
import check_playback_status
import time

shairport = 'ShairportSync'

os.system('export DISPLAY=:0.0;')

def main():
    parser = argparse.ArgumentParser(description='play_video')
    parser.add_argument('video_url', nargs=1, help='video url/file')
    args = parser.parse_args()
    video_url = args.video_url[0]

    print(video_url)

    running_player = check_playback_status.get_running_player()

    if running_player != None:
        execute('/usr/bin/playerctl --player=' + running_player + ' pause')

    # play_command = 'youtube-dl -f best -o - $URL | vlc -f --play-and-exit -'
    play_command = 'vlc -f --play-and-exit "' + video_url + '"; '

    if running_player != None:
        play_command += ' /usr/bin/playerctl --player=' + running_player + ' next; '
        # execute('/usr/bin/playerctl --player=' + running_player + ' next')
        if running_player == shairport:
            play_command += ' /usr/bin/playerctl --player=' + running_player + ' play; '
            # execute('/usr/bin/playerctl --player=' + running_player + ' play')


    print(execute(play_command))


def execute(command):
    result = subprocess.run([command], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    return result.stdout.decode('utf-8').replace('\n', '')

if __name__ == '__main__':
    main()