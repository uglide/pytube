# -*- coding: utf-8 -*-

from urllib import urlencode
from urllib2 import urlopen
from urlparse import urlparse, parse_qs, unquote, parse_qsl
from os.path import join

BASE_URL = 'http://www.youtube.com/get_video_info'

#YouTube quality and codecs id map.
#source: http://en.wikipedia.org/wiki/YouTube#Quality_and_codecs
ITAGS = {
    5: ("flv", "240p", "H.263", None, 64),
    6: ("flv", "270p", "H.263", None, 64),
    34: ("flv", "360p", "H.264", "Main", 128),
    35: ("flv", "480p", "H.264", "Main", 128),
    36: ("3gp", "240p", "MPEG-4", "Simple", 38),
    13: ("3gp", None, "MPEG-4", None, None),
    17: ("3gp", "144p", "MPEG-4", "Simple", 24),
    18: ("mp4", "360p", "H.264", "Baseline", 96),
    22: ("mp4", "720p", "H.264", "High", 192),
    37: ("mp4", "1080p", "H.264", "High", 192),
    38: ("mp4", "3072p", "H.264", "High", 192),
    82: ("mp4", "360p", "H.264", "3D", 96),
    83: ("mp4", "240p", "H.264", "3D", 96),
    84: ("mp4", "720p", "H.264", "3D", 152),
    85: ("mp4", "520p", "H.264", "3D", 152),
    43: ("webm", "360p", "VP8", None, 128),
    44: ("webm", "480p", "VP8", None, 128),
    45: ("webm", "720p", "VP8", None, 192),
    46: ("webm", "1080p", "VP8", None, 192),
    100: ("webm", "360p", "VP8", "3D", 128),
    101: ("webm", "360p", "VP8", "3D", 192),
    102: ("webm", "720p", "VP8", "3D", 192)
}

class YouTube(object):
    metadata = {}
    video_id = None

    def __init__(self, url):
        ok, video_id = self.extract_id_from_url(url)
        self.video_id = video_id

    def extract_id_from_url(self, url):
        parts = urlparse(url)
        if hasattr(parts, 'query'):
            query_str = parse_qs(parts.query)
            if 'v' in query_str and len(query_str['v']) is 1:
                return (True, query_str['v'][0])
        return (False, None)

    def get_title(self):
        metadata = self.get_metadata(self.video_id)
        return metadata['title']

    def get_videos(self):
        videos = []
        metadata = self.get_metadata(self.video_id)
        fsm = metadata['fmt_stream_map']
        itag = [ITAGS.get(int(i), int(i)) for i in fsm['itag']]
        urls = fsm['url']
        return [Video(url, meta) for url, meta in zip(urls, itag)]


    def get_metadata(self, video_id):
        return self.metadata.get(video_id, self._extract_video_data(video_id))

    def _urlize(self, url, *paths, **query):
        paths = (join(*paths) if paths else '')

        if query:
            return ''.join([url, paths, '?', urlencode(query)])
        return ''.join([url, paths])

    def _parse_qs(self, qs):
        d = {}
        for key, val in parse_qs(qs).iteritems():
            d[key] = (val if len(val) > 1 else val[0])
        return d

    def _extract_video_data(self, video_id):
        url = self._urlize(BASE_URL, asv=3, el='detailpage', hl='en_US',
                           video_id=video_id)

        response = urlopen(url)
        if response.getcode() != 200:
            return None

        body = self._parse_qs(response.read())
        fsm = self._parse_qs(body['url_encoded_fmt_stream_map'])

        body['fmt_stream_map'] = fsm

        self.metadata[video_id] = body
        return body

class Video(object):
    def __init__(self, url, itag):
        self.url = url
        self._parse_itag(*itag)

    def _parse_itag(self, ext, res, v_codec, profile, a_bitrate):
        self.ext = ext
        self.res = res
        self.video_codec = v_codec
        self.profile = profile
        self.audio_bitrate = a_bitrate

    def __repr__(self):
        return "<Video: {0} (.{1}) - {2}>".format(
            self.video_codec, self.extension, self.resolution)

if __name__ == '__main__':
    yt = YouTube("http://www.youtube.com/watch?v=Ik-RsDGPI5Y")
    print yt.get_videos()
