#!/usr/bin/python
import paho.mqtt.client as mqtt
import os
import time
from datetime import date
from datetime import timedelta
from shutil import copyfile
from multiprocessing import Process
import urllib.request
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

base_path = '/home/pi/scripts/github/media_frame/data/music/'

wait_for_artwork_process = []

def set_track_information(state, track_information):
    global wait_for_artwork_process

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

        process = Process(target=set_default_artwork, args=(track_information, ))
        process.start()
        wait_for_artwork_process.append(process)

    if state == 'pause':
        # frame_next('track pause')

        print('paused')
        print('changing PictureFrame to photos')
        kill_wait_for_artwork_process()
        os.system('/home/pi/scripts/github/media_frame/scripts/change_media_to_photos.sh')


def set_default_artwork(track_information):
    time.sleep(5)

    artwork_url = get_artwork_url(track_information)
    if artwork_url != None:
        artwork_filename = artwork_url.split('/')[-1] + '.jpeg'
        new_artwork_path = base_path + 'artwork/' + artwork_filename
        remove_old_artworks()
        urllib.request.urlretrieve(artwork_url, new_artwork_path)
        frame_next('spotify artwork')
    else:
        remove_old_artworks()
        copyfile(base_path + 'default.jpg', base_path + 'artwork/default.jpg')
        frame_next('default artwork')

def set_album_artwork(path):
    pic_dir = base_path + 'artwork/'
    new_artwork_path = os.path.join(pic_dir, os.path.basename(path))
    copyfile(path, new_artwork_path)
    os.remove(path)
    remove_old_artworks(new_artwork_path)
    kill_wait_for_artwork_process()
    frame_next('artwork')

####################################

def kill_wait_for_artwork_process():
    global wait_for_artwork_process
    for p in wait_for_artwork_process:
        if p.is_alive():
            p.kill()
            print('killed no artwork process')
        wait_for_artwork_process.remove(p)


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

def frame_next(info = ''):
    if os.path.isfile(base_path + 'is_active'):
        client = mqtt.Client()
        client.connect("localhost", 1883, 60)
        client.publish("frame/next")
        client.disconnect()
        print('frame/next ' + info)
    else:
        print('frame/next ' + info)
        kill_wait_for_artwork_process()
        print('changing PictureFrame to music')
        os.system('/home/pi/scripts/github/media_frame/scripts/change_media_to_music.sh')

def get_artwork_url(track_information):
    ti_split = track_information.split(' - ')
    if len(ti_split) == 2:
        search_artist = ti_split[0]
        search_title = ti_split[1]

        sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id='14e48d315bb649dba1a37ce4c764f58c', client_secret='ba72e489deb8442b90263689df69f8fb'))
        result = sp.search(search_artist + ' ' + search_title)
        rresult = result['tracks']['items']
        for r in rresult:
            if r['name'] == search_title and get_artists(r['artists']) == search_artist:
                biggest_size_index = -1
    
                images = r['album']['images']
                biggest_size = -1
                for i in range(0, len(images)):
                    image = images[i]
                    if image['height'] > biggest_size:
                        biggest_size = int(image['height'])
                        biggest_size_index = i

                if biggest_size_index != -1:
                    return images[biggest_size_index]['url']
    return None
      
def get_artists(artists):
    artist = ''
    for i in range(0, len(artists)):
        artist += artists[i]['name']
        if i != len(artists) - 1:
            artists += ', '

    return artist

