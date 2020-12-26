#!/usr/bin/python
import paho.mqtt.client as mqtt
import os
import subprocess
import urllib.request

base_path = '/home/pi/scripts/github/media_frame/data/music/'

def main():
    playerctl_state = execute('/usr/bin/playerctl --player=spotifyd status')

    state = None
    if playerctl_state == 'Paused':
        state = 'pause'
    elif playerctl_state == 'Playing':
        state = 'play'
    else:
        print('Error at receiving status')
        quit()

    track_information = execute('/usr/bin/playerctl --player=spotifyd metadata --format "{{ artist }} - {{ title }}"')

    if state == 'pause':
        track_information = 'PAUSED ' + track_information

    path = base_path + 'current_track.txt'

    previous_track = None
    with open(base_path + 'current_track.txt', 'r') as f:
        previous_track = f.read()

    if previous_track != track_information:
        f = open(path, 'w')
        f.write(track_information)
        f.close()

        artwork_url = execute('/usr/bin/playerctl --player=spotifyd metadata --format "{{ mpris:artUrl }}"')

        pic_dir = base_path + 'artwork/'
        artwork_filename = artwork_url.split('/')[-1] + '.jpeg'
        new_artwork_path = os.path.join(pic_dir, artwork_filename)
        urllib.request.urlretrieve(artwork_url, new_artwork_path)

        remove_old_artworks(new_artwork_path)

        frame_next('spotifyd')

    if state == 'pause':
        # frame_next('track pause')
        print('paused')
        print('starting new PictureFrame for photos')
        os.system('/home/pi/scripts/github/media_frame/scripts/change_media_to_photos.sh')


def remove_old_artworks(exceptFile = None):
    pic_dir = base_path + 'artwork/'
    files_to_remove = []
    for f in os.listdir(pic_dir):
        full_path = os.path.join(pic_dir, f)
        if os.path.isfile(full_path):
            if exceptFile is None or full_path != exceptFile:
                files_to_remove.append(full_path)
    for path in files_to_remove:
        os.remove(path)

def execute(command):
    result = subprocess.run([command], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    return result.stdout.decode('utf-8').replace('\n', '')

def frame_next(info = ''):
    if os.path.isfile(base_path + 'is_active'):
        client = mqtt.Client()
        client.connect("localhost", 1883, 60)
        client.publish("frame/next")
        client.disconnect()
        print('frame/next ' + info)
    else:
        print('frame/next ' + info)
        print('starting new PictureFrame for music')
        os.system('/home/pi/scripts/github/media_frame/scripts/change_media_to_music.sh')

if __name__ == '__main__':
    main()

# playerctl --player=spotifyd metadata --format "{{ artist }} - {{ title }} | {{ mpris:artUrl }}"
# playerctl --player=spotifyd metadata --format "{{ artist }} - {{ title }}" > /home/pi/scripts/github/media_frame/data/music/current_track.txt