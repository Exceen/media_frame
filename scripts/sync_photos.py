#!/usr/bin/python
from pyicloud import PyiCloudService
from shutil import copyfileobj
import os

def get_filename(photo):
    filename  = str(photo.created.year).rjust(4, '0') +  '-'
    filename += str(photo.created.month).rjust(2, '0') +  '-'
    filename += str(photo.created.day).rjust(2, '0') +  '-'
    filename += str(photo.created.hour).rjust(2, '0') +  '-'
    filename += str(photo.created.minute).rjust(2, '0') +  '-'
    filename += photo.versions['original']['filename']
    return filename

def main():
    api = PyiCloudService('exceen.dev@gmail.com')

    # photos_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'photo_frame') + '/'
    photos_directory = '/home/pi/scripts/github/media_frame/data/photos/'
    if not os.path.exists(photos_directory):
        os.makedirs(photos_directory)

    album_photos = [] 
    album_photos_paths_only = []
    for photo in api.photos.albums['Splash']:
        full_photo_path = photos_directory + get_filename(photo)

        album_photos.append([photo, full_photo_path])
        album_photos_paths_only.append(full_photo_path)

    for existing_photo in os.listdir(photos_directory):
        existing_photo_path = os.path.join(photos_directory, existing_photo)
        if os.path.isfile(existing_photo_path) and existing_photo_path not in album_photos_paths_only:
            print('Removing: ' + existing_photo)
            os.remove(existing_photo_path)

    for photo, photo_path in album_photos:
        if not os.path.isfile(photo_path):
            filename = photo.versions['original']['filename']
            print('Saving: ' + filename)

            download = photo.download('original')
            with open(photo_path, 'wb') as opened_file:
                copyfileobj(download.raw, opened_file)

if __name__ == '__main__':
    main()
