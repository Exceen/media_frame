#!/usr/bin/python
import paho.mqtt.client as mqtt
import os
import subprocess
import urllib.request
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import time

base_path = '/home/pi/scripts/github/media_frame/data/music/'


# def get_track_information_spotifyapi():
#     player_event = os.getenv('PLAYER_EVENT')
#     trackid = os.getenv('TRACK_ID')

#     sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id='', client_secret=''))
#     urn = 'spotify:track:' + trackid 

#     track = sp.track(urn)

#     state = None
#     if player_event == 'start' or player_event == 'change':
#         state = 'play'
#     elif player_event == 'stop':
#         state = 'pause'
#     else:
#         print('Error at receiving status')
#         quit()

#     artist = track['artists'][0]['name']
#     track_information = track['name'] + ' - ' + artist
#     return state, track_information


# def get_old_track_information_spotifyapi():
#     player_event = os.getenv('PLAYER_EVENT')
#     trackid = os.getenv('OLD_TRACK_ID')

#     sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id='', client_secret=''))
#     urn = 'spotify:track:' + trackid 

#     track = sp.track(urn)

#     state = None
#     if player_event == 'start' or player_event == 'change':
#         state = 'play'
#     elif player_event == 'stop':
#         state = 'pause'
#     else:
#         print('Error at receiving status')
#         quit()

#     artist = track['artists'][0]['name']
#     track_information = track['name'] + ' - ' + artist
#     return state, track_information



# def get_artists_from_track(track):
#     artist = ''
#     artists = track['artists']
#     for i in xrange(0, len(artists)):
#         artist += artists[i]['name']
#         if i != len(artists) - 1:
#             artists += ', '

#     return artist


def get_track_information_playerctl():
    playerctl_state = execute('/usr/bin/playerctl --player=spotifyd status')
    state = None
    if playerctl_state == 'Paused':
        state = 'pause'
    elif playerctl_state == 'Playing':
        state = 'play'
    else:
        state = 'pause'
        print('Error at receiving status, assuming paused state')
        return state, ''
        # quit()

    track_information = execute('/usr/bin/playerctl --player=spotifyd metadata --format "{{ artist }} - {{ title }}"')

    return state, track_information

def main():
    time.sleep(0.1)
    # state, track_information = get_track_information_spotifyapi()
    # print('Spotify:', state, track_information)

    # state, track_information = get_old_track_information_spotifyapi()
    # print('OldSpotify:', state, track_information)

    state, track_information = get_track_information_playerctl()
    # print('playerctl:', state, track_information)

#    if state == 'pause':
#        track_information = 'PAUSED ' + track_information

    path = base_path + 'current_track.txt'

    previous_track = None
    if os.path.isfile(path):
        with open(path, 'r') as f:
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
        print('changing PictureFrame to photos')
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
        print('changing PictureFrame to music')
        os.system('/home/pi/scripts/github/media_frame/scripts/change_media_to_music.sh')

if __name__ == '__main__':
    main()

# playerctl --player=spotifyd metadata --format "{{ artist }} - {{ title }} | {{ mpris:artUrl }}"
# playerctl --player=spotifyd metadata --format "{{ artist }} - {{ title }}" > /home/pi/scripts/github/media_frame/data/music/current_track.txt
