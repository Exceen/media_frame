#!/usr/bin/python
import paho.mqtt.client as mqtt
import os
import subprocess
import urllib.request
from shutil import copyfile
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import argparse
import youtube.get_music_video_url
from multiprocessing import Process

base_path = '/home/pi/scripts/github/media_frame/data/music/'

player = None

def get_music_video_path(track_information, music_videos_path):
    for f in os.listdir(music_videos_path):
        if track_information in f:
            return music_videos_path + f
    return None

def download_video(url, music_videos_path, track_information):
    # youtube-dl -f worst -o "Meshuggah - Clockworks.%(ext)s"   https://www.youtube.com/watch?v=oFiDcazicdk
    # download_cmd = '/home/pi/.local/bin/youtube-dl -f best -o "'  + music_videos_path + track_information + '.%(ext)s" "' + url + '"&';
    max_height = str(768)
    download_cmd = '/home/pi/.local/bin/youtube-dl -f \'bestvideo[height<=' + max_height + ']+bestaudio/best[height<=' + max_height + ']\' -o "'  + music_videos_path + track_information + '.%(ext)s" "' + url + '"&';

    print('executing: "' + download_cmd + '"')
    os.system(download_cmd)

def play_video(music_video_path):
    volume = 0.0
    try:
        volume = float(execute('/usr/bin/playerctl --player=' + player + ' volume'))
        if volume > 1.0:
            volume /= 100
    except Exception as e:
        print(e)
    print(player + ' volume: ' + str(volume))

    os.system('/usr/bin/playerctl --player=' + player + ' pause')
    # vlc_cmd = '/home/pi/.local/bin/youtube-dl -f worst -o - "' + url + '" | /usr/bin/vlc -f --play-and-exit -'
    vlc_cmd = '/usr/bin/vlc -f --play-and-exit "' + music_video_path + '"'
    next_cmd = '/usr/bin/playerctl --player=' + player + ' next'

    print('vlc_cmd: ' + vlc_cmd)
    os.system(vlc_cmd + '; ' + next_cmd + '&')
    # quit() # no need to check for available download

def check_for_music_video(track_information):
    play_youtube_videos = os.path.isfile(base_path + 'play_youtube_videos')
    download_youtube_videos = os.path.isfile(base_path + 'download_youtube_videos')

    play_youtube_videos = False
    download_youtube_videos = True

    music_videos_path = base_path + 'music_videos/'
    music_video_path = get_music_video_path(track_information, music_videos_path)

    if play_youtube_videos:
        if music_video_path is None:
            print('music video not found on local disk')
        else:
            print('music video found on local disk')
            print(music_video_path)

            process = Process(target=play_video, args=(music_video_path, ))
            process.start()

    if download_youtube_videos:
        if music_video_path is None:
            url = youtube.get_music_video_url.get_url(track_information)
            if url:
                print('music video url: ' + url)
                process = Process(target=download_video, args=(url, music_videos_path, track_information, ))
                process.start()
            else:
                print('no music video found on youtube')
        else:
            print('music video already downloaded!')
            print(music_video_path)

def main():
    print('onevent!')
    global player
    parser = argparse.ArgumentParser(description='onevent')
    parser.add_argument('player', nargs=1, help='player (playerctl -l)')
    args = parser.parse_args()
    player = args.player[0]

    if player == None:
        print('No player given!')
        quit()
    else:
        print('Player: ' + player)

    state, track_information = get_track_information_playerctl()
    print('track_information:', state, track_information)

    if state != 'pause':
        path = base_path + 'current_track.txt'
        previous_track = None
        if os.path.isfile(path):
            with open(path, 'r') as f:
                previous_track = f.read()

        if previous_track != track_information:
            f = open(path, 'w')
            f.write(track_information)
            f.close()

            artwork_url = execute('/usr/bin/playerctl --player=' + player + ' metadata --format "{{ mpris:artUrl }}"')
            pic_dir = base_path + 'artwork/'

            if player == 'spotifyd':
                spotifyd(artwork_url, pic_dir)
            elif player == 'ShairportSync':
                shairport(artwork_url, pic_dir, track_information)

            check_for_music_video(track_information)
    else:
        print('paused')
        print('changing PictureFrame to photos')
        os.system('/home/pi/scripts/github/media_frame/scripts/change_media_to_photos.sh')

def spotifyd(artwork_url, pic_dir):
    artwork_filename = artwork_url.split('/')[-1] + '.jpeg'
    new_artwork_path = os.path.join(pic_dir, artwork_filename)
    urllib.request.urlretrieve(artwork_url, new_artwork_path)

    remove_old_artworks(new_artwork_path)
    frame_next(player)

def shairport(artwork_url, pic_dir, track_information):
    if 'file://' in artwork_url and os.path.isfile(artwork_url[7:]):
        artwork_filename = artwork_url.split('/')[-1] + '.jpeg'
        new_artwork_path = os.path.join(pic_dir, artwork_filename)
        urllib.request.urlretrieve(artwork_url, new_artwork_path)
        remove_old_artworks(new_artwork_path)
    else:
        artwork_url = get_artwork_url(track_information)
        if artwork_url != None:
            artwork_filename = artwork_url.split('/')[-1] + '.jpeg'
            new_artwork_path = base_path + 'artwork/' + artwork_filename
            remove_old_artworks()
            urllib.request.urlretrieve(artwork_url, new_artwork_path)
            frame_next(player + ' artwork')
        else:
            remove_old_artworks()
            copyfile(base_path + 'default.jpg', base_path + 'artwork/default.jpg')
            frame_next('default artwork')

    frame_next(player)

def get_artists(artists):       
    artist = ''
    for i in range(0, len(artists)):
        artist += artists[i]['name']
        if i != len(artists) - 1:
            artists += ', '
    return artist

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

def get_track_information_playerctl():
    playerctl_state = execute('/usr/bin/playerctl --player=' + player + ' status')
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

    track_information = execute('/usr/bin/playerctl --player=' + player + ' metadata --format "{{ artist }} - {{ title }}"')

    return state, track_information

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