#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
.. module:: pytube.youtube
   :platform: Unix
   :synopsis: Library for downloading YouTube videos

.. moduleauthor:: Nick Ficano <nficano@gmail.com>
"""

from os.path import join
from urllib import urlencode
from urllib2 import urlopen
from urlparse import urlparse, parse_qs

from video import Video

BASE_URL = 'http://www.youtube.com/get_video_info'


class YouTube(object):
    """PyTube: Lightweight wrapper for downloading YouTube videos
    """

    def __init__(self, url=None, video_id=None):
        if not video_id:
            self.video_id = self.parse_id_from_url(url)

    def parse_id_from_url(self, url):
        #TODO: raise exception for malformed url, no '?v=xxx' found in query
        #string. Also test on url-shortened youtu.be

        #Split URI into 'parts', check if query string contains node 'v' and
        #return accordingly.
        parts = urlparse(url)
        if hasattr(parts, 'query'):
            qs = self._parse_qs(parts.query)
            #TODO: raise exception if video id cannot be extracted from url
            return qs.get('v')

    def get_videos(self):
        videos = []
        metadata = self.get_metadata()
        raw_videos = metadata.get('fmt_stream_map')

        for v in raw_videos:
            video = Video(v['fallback_host'], v['itag'], v['quality'],
                          v['type'], v['url'])
            videos.append(video)
        return sorted(videos)

    def get_metadata(self):
        return self._request(self.video_id)

    def _url(self, url, *paths, **qs):
        #Store url as list for easier assembly.
        url_parts = [url]

        #TODO: Sanitize paths ensuring slashes are handled properly.
        if isinstance(paths, list):
            paths = join(*paths)
            url_parts.append(paths)

        #TODO: Sanitize query string ensuring no leading '?' or training '&'
        if isinstance(qs, dict):
            qs = '?' + urlencode(qs)
            url_parts.append(qs)

        return ''.join(url_parts)

    @staticmethod
    def _parse_qs(qs):
        dct = {}
        #loop through object key/value yielded from parse_qs iteritems, check
        #if the value contains one item (no child nodes), replace tuple with
        #strings accordingly.
        for key, val in parse_qs(qs).iteritems():
            dct[key] = (val if len(val) > 1 else val[0])
        return dct

    def _request(self, video_id):
        #Assemble URL and execute http request.
        url = self._url(BASE_URL, asv=3, el='detailpage', hl='en_US',
                        video_id=video_id)
        http_conn = urlopen(url)

        if http_conn.getcode() is not 200:
            #TODO: raise proper exception if status code is not 200.
            raise

        #Parse the meta data found in the http_conn body using modified version
        #of parse_qs.
        body = self._parse_qs(http_conn.read())
        #Handle the parsing in a separate function primary to make testing
        #easier.
        metadata = self.__parse_body(body)

        return metadata

    def __parse_body(self, body):
        stream_map = []
        fsm_csv = body['url_encoded_fmt_stream_map'].split(',')
        for fsm in fsm_csv:
            fsm = self._parse_qs(fsm)
            stream_map.append(fsm)
        body['fmt_stream_map'] = stream_map
        return body
