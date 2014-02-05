#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
.. module:: pytube.video
   :platform: Unix
   :synopsis: TODO

.. moduleauthor:: Nick Ficano <nficano@gmail.com>
"""

from urlparse import urlparse, parse_qs
from datetime import datetime

import re


class Video(object):
    fallback_host = None
    itag = None
    quality = None
    media_type = None
    url = None

    def __init__(self, fallback_host, itag, quality, media_type, url):
        self.fallback_host = fallback_host
        self.itag = itag
        self.quality = quality
        self.media_type = media_type
        self.url = url

    def _get_expiration(self):
        url = urlparse(self.url)
        qs = parse_qs(url)
        timestamp = qs.get('expire')[0]
        return datetime.fromtimestamp(timestamp)

    @property
    def mimetype(self):
        pattern = re.compile('(video\/[A-Za-z0-9-_]*)')
        match = pattern.match(self.media_type)
        if match:
            return match.group()

    def is_expired(self):
        expiration_date = self._get_expiration()
        return datetime.now() > expiration_date

    def __repr__(self):
        return "<Video: ('{0}') - quality=\"{1}\">".format(
            self.mimetype, self.quality)

    def __lt__(self, other):
        #we use itag to determine the highest quality, see
        #http://en.wikipedia.org/wiki/YouTube#Quality_and_codec for more
        #information
        if type(other) == Video:
            v1 = "{0} {1}".format(self.mimetype, self.itag)
            v2 = "{0} {1}".format(other.mimetype, other.itag)
            return (v1 > v2) - (v1 < v2) < 0
