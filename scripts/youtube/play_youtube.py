#!/usr/bin/python
import pafy
import math
import re
import sys
import json
import logging
from datetime import datetime, timezone
import g, c, terminalsize, description_parser
import content
import screen
import streams
from urllib.error import HTTPError, URLError
import socket
import util
import os


import time
# import traceback
# import locale

# import ctypes
# import subprocess
# import collections
# import unicodedata
# import urllib
# import platform


from argparse import ArgumentParser

API_KEY = 'AIzaSyAS82J1PBStNBBNF4yMMJco3Bg-ojtoG1A'




ISO8601_TIMEDUR_EX = re.compile(r'PT((\d{1,3})H)?((\d{1,3})M)?((\d{1,2})S)?')

mswin = os.name == "nt"
not_utf8_environment = mswin or "UTF-8" not in sys.stdout.encoding

DAYS = dict(day = 1,
            week = 7,
            month = 30,
            year = 365)

def main():
    parser = ArgumentParser()
    parser.add_argument('search', nargs='+')
    args = parser.parse_args()
    term = str(' '.join(args.search))
    pafy.set_api_key(API_KEY)
    
    songs = search(term)

    music_video = None
    for song in songs:
        if 'official music video' in song.title.lower() and term.lower() in song.title.lower():
            music_video = song
            break

    if music_video:
        base_url = 'https://www.youtube.com/watch?v=%s'

        print(music_video)
        print(base_url % music_video.ytid)



def search(term):
    query = generate_search_qs(term)
    return _search(term, query)

def generate_search_qs(term, match='term', videoDuration='any', after=None, category=None, is_live=False):
    """ Return query string. """

    aliases = dict(views='viewCount')
    qs = {
        'q': term,
        'maxResults': 50,
        'safeSearch': "none",
        'order': aliases.get('relevance', 'relevance'),
        'part': 'id,snippet',
        'type': 'video',
        'videoDuration': videoDuration,
        'key': API_KEY
    }

    if after:
        after = after.lower()
        qs['publishedAfter'] = '%sZ' % (datetime.utcnow() - timedelta(days=DAYS[after])).isoformat() \
                                if after in DAYS.keys() else '%s%s' % (after, 'T00:00:00Z' * (len(after) == 10))

    if match == 'related':
        qs['relatedToVideoId'] = term
        del qs['q']

    SEARCH_MUSIC = True
    if SEARCH_MUSIC:
        qs['videoCategoryId'] = 10

    if category:
        qs['videoCategoryId'] = category

    if is_live:
        qs['eventType'] = "live"

    return qs

def _search(progtext, qs=None):
    """ Perform memoized url fetch, display progtext. """
    loadmsg = "Searching for '%s'" % (progtext)
    wdata = pafy.call_gdata('search', qs)

    def iter_songs():
        wdata2 = wdata
        while True:
            for song in get_tracks_from_json(wdata2):
                yield song

            if not wdata2.get('nextPageToken'):
                break
            qs['pageToken'] = wdata2['nextPageToken']
            wdata2 = pafy.call_gdata('search', qs)

    # # The youtube search api returns a maximum of 500 results
    length = min(wdata['pageInfo']['totalResults'], 500)
    slicer = IterSlicer(iter_songs(), length)

    # paginatesongs(slicer, length=length, msg=msg, failmsg=failmsg, loadmsg=loadmsg)

    func = slicer
    s = 0
    e = 1
    

    if callable(func):
        songs = (s, e)
    else:
        songs = func[s:e]

    return songs

def utf8_replace(txt):
    """
    Replace unsupported characters in unicode string.

    :param txt: text to filter
    :type txt: str
    :returns: Unicode text without any characters unsupported by locale
    :rtype: str
    """
    sse = sys.stdout.encoding
    txt = str(txt)
    txt = txt.encode(sse, "replace").decode(sse)
    return txt

def xenc(stuff):
    """ Replace unsupported characters. """
    return utf8_replace(stuff) if not_utf8_environment else stuff

def num_repr(num):
    """ Return up to four digit string representation of a number, eg 2.6m. """
    if num <= 9999:
        return str(num)

    def digit_count(x):
        """ Return number of digits. """
        return int(math.floor(math.log10(x)) + 1)

    digits = digit_count(num)
    sig = 3 if digits % 3 == 0 else 2
    rounded = int(round(num, int(sig - digits)))
    digits = digit_count(rounded)
    suffix = "_kmBTqXYX"[(digits - 1) // 3]
    front = 3 if digits % 3 == 0 else digits % 3

    if not front == 1:
        return str(rounded)[0:front] + suffix

    return str(rounded)[0] + "." + str(rounded)[1] + suffix

def get_tracks_from_json(jsons):
    """ Get search results from API response """

    items = jsons.get("items")
    if not items:
        dbg("got unexpected data or no search results")
        return ()

    # fetch detailed information about items from videos API
    id_list = [get_track_id_from_json(i)
                for i in items
                if i['id']['kind'] == 'youtube#video']

    qs = {'part':'contentDetails,statistics,snippet',
          'id': ','.join(id_list)}

    wdata = pafy.call_gdata('videos', qs)

    items_vidinfo = wdata.get('items', [])
    # enhance search results by adding information from videos API response
    for searchresult, vidinfoitem in zip(items, items_vidinfo):
        searchresult.update(vidinfoitem)

    # populate list of video objects
    songs = []
    for item in items:

        try:

            ytid = get_track_id_from_json(item)
            duration = item.get('contentDetails', {}).get('duration')

            if duration:
                duration = ISO8601_TIMEDUR_EX.findall(duration)
                if len(duration) > 0:
                    _, hours, _, minutes, _, seconds = duration[0]
                    duration = [seconds, minutes, hours]
                    duration = [int(v) if len(v) > 0 else 0 for v in duration]
                    duration = sum([60**p*v for p, v in enumerate(duration)])
                else:
                    duration = 30
            else:
                duration = 30

            stats = item.get('statistics', {})
            snippet = item.get('snippet', {})
            title = snippet.get('title', '').strip()
            # instantiate video representation in local model
            cursong = Video(ytid=ytid, title=title, length=duration)
            likes = int(stats.get('likeCount', 0))
            dislikes = int(stats.get('dislikeCount', 0))
            #XXX this is a very poor attempt to calculate a rating value
            rating = 5.*likes/(likes+dislikes) if (likes+dislikes) > 0 else 0
            category = snippet.get('categoryId')
            

            # cache video information in custom global variable store
            g.meta[ytid] = dict(
                # tries to get localized title first, fallback to normal title
                title=snippet.get('localized',
                                  {'title':snippet.get('title',
                                                       '[!!!]')}).get('title',
                                                                      '[!]'),
                length=str(fmt_time(cursong.length)),
                rating=str('{}'.format(rating))[:4].ljust(4, "0"),
                uploader=snippet.get('channelId'),
                uploaderName=snippet.get('channelTitle'),
                category=category,
                aspect="custom", #XXX
                likes=str(num_repr(likes)),
                dislikes=str(num_repr(dislikes)),
                commentCount=str(num_repr(int(stats.get('commentCount', 0)))),
                viewCount=str(num_repr(int(stats.get('viewCount', 0)))))

        except Exception as e:
            print(e)
            dbg(json.dumps(item, indent=2))
            dbg('Error during metadata extraction/instantiation of ' +
                'search result {}\n{}'.format(ytid, e))

        songs.append(cursong)

    # return video objects
    return songs

def dbg(*args):
    """Emit a debug message."""
    # Uses xenc to deal with UnicodeEncodeError when writing to terminal
    logging.debug(*(xenc(i) for i in args))

def utc2local(utc):
    return utc.replace(tzinfo=timezone.utc).astimezone(tz=None)

def yt_datetime_local(yt_date_time):
    """ Return a datetime object, locale converted and formated date string and locale converted and formatted time string. """
    datetime_obj = datetime.strptime(yt_date_time, "%Y-%m-%dT%H:%M:%SZ")
    datetime_obj = utc2local(datetime_obj)
    locale_date = datetime_obj.strftime("%x")
    locale_time = datetime_obj.strftime("%X")
    # strip first two digits of four digit year
    short_date = re.sub(r"(\d\d\D\d\d\D)20(\d\d)$", r"\1\2", locale_date)
    return datetime_obj, short_date, locale_time

def fmt_time(seconds):
    """ Format number of seconds to %H:%M:%S. """
    hms = time.strftime('%H:%M:%S', time.gmtime(int(seconds)))
    H, M, S = hms.split(":")

    if H == "00":
        hms = M + ":" + S

    elif H == "01" and int(M) < 40:
        hms = str(int(M) + 60) + ":" + S

    elif H.startswith("0"):
        hms = ":".join([H[1], M, S])

    return hms

def get_track_id_from_json(item):
    """ Try to extract video Id from various response types """
    fields = ['contentDetails/videoId',
              'snippet/resourceId/videoId',
              'id/videoId',
              'id']
    for field in fields:
        node = item
        for p in field.split('/'):
            if node and isinstance(node, dict):
                node = node.get(p)
        if node:
            return node
    return ''

class Video:

    """ Class to represent a YouTube video. """
    description = ""
    def __init__(self, ytid, title, length):
        """ class members. """
        self.ytid = ytid
        self.title = title
        self.length = int(length)

    def __str__(self):
        return 'Video Object: ' + str(self.ytid) + ' | ' + str(self.title)

class IterSlicer():
    """ Class that takes an iterable and allows slicing,
        loading from the iterable as needed."""

    def __init__(self, iterable, length=None):
        self.ilist = []
        self.iterable = iter(iterable)
        self.length = length
        if length is None:
            try:
                self.length = len(iterable)
            except TypeError:
                pass

    def __getitem__(self, sliced):
        if isinstance(sliced, slice):
            stop = sliced.stop
        else:
            stop = sliced
        # To get the last item in an iterable, must iterate over all items
        if (stop is None) or (stop < 0):
            stop = None
        while (stop is None) or (stop > len(self.ilist) - 1):
            try:
                self.ilist.append(next(self.iterable))
            except StopIteration:
                break

        return self.ilist[sliced]

    def __len__(self):
        if self.length is None:
            self.length = len(self[:])
        return self.length



if __name__ == '__main__':
    main()