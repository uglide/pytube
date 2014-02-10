#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
.. module:: pytube.video
   :platform: Unix
   :synopsis: TODO

.. moduleauthor:: Nick Ficano <nficano@gmail.com>
"""

from datetime import datetime
from mimetypes import guess_extension
from urlparse import urlparse, parse_qs

import urllib2
import re


class Video(object):

    def __init__(self, fallback_host, itag, quality, media_type, url,
                 metadata={}):
        self.fallback_host = fallback_host
        self.itag = itag
        self.quality = quality
        self.media_type = media_type
        self.url = url
        self.metadata = metadata
        self.cb_func = None
        self.chunk_size = 1024

    def get_mimetype(self):
        pattern = re.compile('(video\/[A-Za-z0-9-_]*)')
        match = pattern.match(self.media_type)
        if match:
            return match.group()

    def get_file_extension(self):
        return guess_extension(self.get_mimetype())

    def is_expired(self):
        expiration_date = self._get_expiration()
        return datetime.now() > expiration_date

    def set_callback(self, fn):
        raise NotImplementedError
        self.cb_func = fn

    def save(self, filename):
        #TODO: verify filename path
        http_conn = urllib2.urlopen(self.url)
        file_size = http_conn.headers.getheader('Content-Length', 0)
        data_len = 0
        if self.cb_func:
            self.cb_func(data_len, file_size)
        with open(filename, 'w') as fp:
            while True:
                chunk = http_conn.read(self.chunk_size)
                if not chunk:
                    break
                data_len += len(chunk)
                fp.write(chunk)
                if self.cb_func:
                    self.cb_func(data_len, file_size)

    def _get_expiration(self):
        url = urlparse(self.url)
        qs = parse_qs(url)
        timestamp = qs.get('expire')[0]
        return datetime.fromtimestamp(timestamp)

    def __repr__(self):
        return "<Video: ('{0}') - quality=\"{1}\">".format(
            self.get_mimetype(), self.quality)

    def __lt__(self, other):
        #we use itag to determine the highest quality, see
        #http://en.wikipedia.org/wiki/YouTube#Quality_and_codec for more
        #information.
        if type(other) == Video:
            v1 = "{0} {1}".format(self.get_mimetype(), self.itag)
            v2 = "{0} {1}".format(other.get_mimetype(), other.itag)
            return (v1 > v2) - (v1 < v2) < 0
