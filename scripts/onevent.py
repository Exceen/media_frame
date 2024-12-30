#!/usr/bin/python
import shutil
import os
import argparse
import urllib.request
from shutil import copyfile
import paho.mqtt.client as mqtt
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import datetime, timedelta

from time import sleep
import subprocess

BASE_PATH = '/home/pi/scripts/github/media_frame/data/music/'
SHAIRPORT_ARTWORK_RETRIEVAL_TIMEOUT_SECONDS = 3

player = None
sp = None

def log(*message):
    print('ON_EVENT:', *message)

def authenticate_spotify():
    return spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id='14e48d315bb649dba1a37ce4c764f58c', client_secret='ba72e489deb8442b90263689df69f8fb'))

def main():
    global sp
    global player
    parser = argparse.ArgumentParser(description='onevent')
    parser.add_argument('player', nargs=1, help='player (playerctl -l)')
    parser.add_argument('forced_state', nargs='*', help='force state')
    args = parser.parse_args()
    player = args.player[0]

    if player == None:
        log('No player given!')
        quit()

    state = None
    track_information = None

    if player == 'spotifyd':
        # check env variables if something should be done at all
        event = os.getenv('PLAYER_EVENT') or '?'
        track_id = os.getenv('TRACK_ID') or ''
        play_request_id = os.getenv('PLAY_REQUEST_ID') or ''

        log('-'*80)
        log(track_id.ljust(25) + (player + ': ').center(25) + event.ljust(15) + play_request_id.rjust(15))
        log(' ')

        ####################################################################

        supported_events = ['play', 'pause', 'preloading', 'load', 'start', 'seeked'] # 'change'
        unsupported_events = ['volumeset', 'preload', 'change', 'endoftrack', 'stop', 'playrequestid_changed', 'sessionconnected', 'sessiondisconnected', 'filterexplicit_changed', 'autoplay_changed', 'clientchanged']

        # for name, value in os.environ.items():
        #     log("%%%%%%: {0}: {1}".format(name, value))

        if event == 'start':
            event = 'play'

        if event in supported_events:
            pass
        elif event in unsupported_events:
            log(event, 'not supported')
            quit()
        else:
            log('!!! UNKNOWN EVENT NOT IMPLEMENTED: ', event)
            quit()

        # if you made it here, the event is relevant for this script, so we need to update the player information
        sp = authenticate_spotify()

        # try:
        #     old_track = sp.track(track_id=os.getenv('OLD_TRACK_ID'))
        #     log('OLD::', get_artists(old_track) + ' - ' + old_track['name'])
        # except Exception as e:
        #     log('no old_track_id')

        track = None
        try:
            track = sp.track(track_id=os.getenv('TRACK_ID'))
            log('CUR::', get_artists(track) + ' - ' + track['name'])
        except Exception as e:
            log('no track_id')

        if track == None:
            log('no track found for given ID')
            quit()

        if event in ['preloading', 'load']: # 'preload' has the 'current' track, 'preloading' has the 'next' track
            log('pre-caching the artwork')
            cache_artwork_for_track(track)
            quit()
        elif event in ['play', 'seeked']:
            try:
                duration_s = int(int(track['duration_ms']) / 1000)
                position_s = int(os.getenv('POSITION_MS')) / 1000

                seconds_left = int(duration_s - position_s)
                log('seconds left:', seconds_left)
                mqtt_publish('music/seconds_left', str(seconds_left))
            except Exception as e:
                log('unable to communicate seconds left')

        state = event
        track_information = get_artists(track) + ' - ' + track['name']

    elif player == 'ShairportSync':
        sp = authenticate_spotify()
        state, track_information = get_track_information_playerctl()
    elif player == 'ShairportSync-artwork':
        frame_next(player)
    else:
        log('Unknown player:', player)
        quit()

    ########################################################
    ##### process the information

    log('found state:', state + (' (forced: ' + args.forced_state[0] + ')' if len(args.forced_state) > 0 else ''))

    if state == None:
        quit()

    if len(args.forced_state) > 0 and args.forced_state[0] != state:
        log('forcing state', args.forced_state[0], 'from', state)
        state = args.forced_state[0]

    if state != 'pause':
        path = BASE_PATH + 'current_track.txt'
        previous_track = None
        if os.path.isfile(path):
            with open(path, 'r') as f:
                previous_track = f.read()

        if previous_track != track_information:
            log('track changed, updating PictureFrame')
            try:
                with open(path, 'w') as f:
                    f.write(track_information)

                pic_dir = BASE_PATH + 'artwork/'

                if player == 'spotifyd':
                    spotifyd(track, pic_dir)
                elif player == 'ShairportSync':
                    shairport(track_information, pic_dir)

            except Exception as e:
                log('general exception!!')
                log(e)
                raise e
        else:
            log('same track as before')
    else:
        log('state == paused, changing PictureFrame to photos')
        os.system('/home/pi/scripts/github/media_frame/scripts/change_media_to_photos.sh')


def spotifyd(track, pic_dir):
    try:
        new_artwork_path = os.path.join(pic_dir, get_artwork_filename(track))

        log(track['album']['id'], '->', track['album']['name'])

        if os.path.isfile(new_artwork_path):
            log('artwork already set for current track')
        else:
            log('artwork not set for current track')
            new_artwork_cache_path = cache_artwork_for_track(track)
            copyfile(new_artwork_cache_path, new_artwork_path)
            remove_old_artworks(new_artwork_path)

    except Exception as e:
        log(e)
        log('error on retrieving artwork from url, using default artwork')
        remove_old_artworks()
        copy_default_artwork()
    frame_next(player)


def cache_artwork_for_track(track):
    artwork_filename = get_artwork_filename(track)
    artwork_url = get_artwork_url_from_spotipy_track(track)

    cache_dir = BASE_PATH + 'artwork_cache/'
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    new_artwork_cache_path = os.path.join(cache_dir, artwork_filename)
    if not os.path.isfile(new_artwork_cache_path):
        log('artwork not in cache, retrieving from url')
        urllib.request.urlretrieve(artwork_url, new_artwork_cache_path)
    else:
        log('artwork already in cache')
    return new_artwork_cache_path


def shairport(track_information, pic_dir):
    # shairport_spotify_fallback(track_information, pic_dir)

    artwork_url = None
    try:
        # NOTE: apparently there's a weird bug with shairport-sync, artwork always seems to be the artwork from the previous track
        # maybe the file-url is updated with a delay
        start_time = datetime.now()
        artwork_url = 'file:' + execute('/usr/bin/playerctl --player=' + player + ' metadata --format "{{ mpris:artUrl }}"').split('file:')[-1]
        while artwork_url is None or 'file://' not in artwork_url or not os.path.isfile(artwork_url[7:]):
            if start_time + timedelta(seconds=SHAIRPORT_ARTWORK_RETRIEVAL_TIMEOUT_SECONDS) < datetime.now():
                log('timeout on retrieving artwork url')
                break
            sleep(0.2)
            artwork_url = 'file:' + execute('/usr/bin/playerctl --player=' + player + ' metadata --format "{{ mpris:artUrl }}"').split('file:')[-1]

        if artwork_url != None and 'file://' in artwork_url and os.path.isfile(artwork_url[7:]):
            artwork_filename = artwork_url.split('/')[-1]
            new_artwork_path = os.path.join(pic_dir, artwork_filename)

            log('retrieving artwork', artwork_filename)

            # urllib.request.urlretrieve(artwork_url, new_artwork_path)
            shutil.copyfile(artwork_url[7:], new_artwork_path)
            remove_old_artworks(new_artwork_path)
            frame_next(player)
            return
        # else:
        #     shairport_spotify_fallback(track_information, pic_dir)
    except Exception as e:
        log('error on retrieving artwork url')
        log(e)
    
    shairport_spotify_fallback(track_information, pic_dir)

def shairport_spotify_fallback(track_information, pic_dir):
    log('shairport-sync artwork not found, trying spotify fallback')
    track = search_spotify_track(track_information)
    if track != None:
        spotifyd(track, pic_dir)
    else:
        log('track not found on spotify, using default artwork')
        remove_old_artworks()
        copy_default_artwork()
        frame_next(player)

def get_artwork_filename(track):
    return track['album']['id'] + '.jpeg'

def get_artists(track):
    return ', '.join([artist['name'] for artist in track['artists']])

def remove_old_artworks(exceptFile = None):
    pic_dir = BASE_PATH + 'artwork/'
    files_to_remove = []
    for f in os.listdir(pic_dir):
        full_path = os.path.join(pic_dir, f)
        if os.path.isfile(full_path):
            if exceptFile is None or full_path != exceptFile:
                files_to_remove.append(full_path)
    for path in files_to_remove:
        os.remove(path)

def get_artwork_url_from_spotipy_track(track):
    biggest_size = 0
    artwork_url = None
    for image in track['album']['images']:
        if image['height'] > biggest_size:
            biggest_size = image['height']
            artwork_url = image['url']
    return artwork_url

def search_spotify_track(track_information):
    ti_split = track_information.split(' - ')
    if len(ti_split) == 2:
        search_artist = ti_split[0]
        search_title = ti_split[1]

        result = sp.search(search_artist + ' ' + search_title)
        rresult = result['tracks']['items']
        for track in rresult:
            if track['name'] == search_title and get_artists(track) == search_artist:
                log('found track on spotify')
                return track
    log('track not found on spotify: ' + track_information)
    return None

def copy_default_artwork():
    copyfile(BASE_PATH + '../../files/spotify_logo.png', BASE_PATH + 'artwork/spotify_logo.png')

def frame_next(info = ''):
    if os.path.isfile(BASE_PATH + 'is_active'):
        mqtt_publish('frame/next')
        log('frame/next ' + info)
    else:
        log('frame/next ' + info)
        log('changing PictureFrame to music')
        os.system('/home/pi/scripts/github/media_frame/scripts/change_media_to_music.sh')

def mqtt_publish(topic, payload=None):
    client = mqtt.Client()
    client.connect("localhost", 1883, 60)
    client.publish(topic, payload)
    client.disconnect()



#### shairpoint sync specific functions

def get_track_information_playerctl():
    playerctl_state = execute('/usr/bin/playerctl --player=' + player + ' status')
    state = None
    if playerctl_state == 'Paused' or playerctl_state == 'Stopped':
        state = 'pause'
    elif playerctl_state == 'Playing':
        state = 'play'
    else:
        state = 'pause'
        log('Error at determining status via playerctl, assuming paused state')
        return state, ''
        # quit()

    cmd_output = execute('/usr/bin/playerctl --player=' + player + ' metadata')
    try:
        artist = cmd_output.split('xesam:artist')[1].split('ShairportSync')[0].strip()
    except Exception as e:
        artist = 'Unknown Artist'
    try:
        title = cmd_output.split('xesam:title')[1].split('ShairportSync')[0].strip()
    except Exception as e:
        title = 'Unknown Title'

    try:
        length = cmd_output.split('mpris:length')[1].split('ShairportSync')[0].strip()
        length = int(int(length) / 1000000)
        log('length:', length)
        mqtt_publish('music/seconds_left', str(length))
    except Exception as e:
        log('no length')

    track_information = artist + ' - ' + title

    if track_information == 'No player could handle this command':
        state = 'pause'

    return state, track_information

def execute(command, replace_new_lines=True):
    result = subprocess.run([command], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    ret = result.stdout.decode('utf-8')
    if replace_new_lines:
        ret = ret.replace('\n', '')
    return ret


if __name__ == '__main__':
    main()
