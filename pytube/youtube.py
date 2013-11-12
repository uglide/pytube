# -*- coding: utf-8 -*-

from urllib import urlencode
from urllib2 import urlopen
from urlparse import urlparse, parse_qs
from os.path import join

BASE_URL = 'http://www.youtube.com/get_video_info'


class YouTube(object):
    """PyTube: Lightweight wrapper for downloading YouTube videos
    """

    def __init__(self, url):
        """Initialize class instance.

        :param url: url to YouTube video
        :returns: instance of YouTube class
        """
        self.url = url
        self.video_id = self.get_id_by_url(url)

    def get_id_by_url(self, url):
        """Extracts the video Id from a YouTube url.

        :param video_id: YouTube url
        :returns: string video Id
        """

        parts = urlparse(url)
        if hasattr(parts, 'query'):
            query_str = parse_qs(parts.query)
            if 'v' in query_str and len(query_str['v']) is 1:
                return query_str['v'][0]

    def mget_videos_by_id(self, video_id):
        """multi-get (Redis-nomenclature) returns a list of object
        representation of YouTube videos for a given video Id.

        :param video_id: YouTube video Id
        :returns: list of Video objects
        """

        raise NotImplemented

    def get_metadata_by_id(self, video_id):
        """Returns the YouTube meta data for a given Id.

        :param video_id: YouTube video Id
        :returns: dict representation of the meta data
        """

        return self._request(video_id)

    def _url(self, url, *paths, **query):
        """Lazily constructs a url given optional paths and query string as
        keyword args.

        :param url: base url (e.g.: http://example.com)
        :param paths: optional path(s) to append to the url
        :param query: optional query string as keyword args
        :returns: a properly formed url
        """

        paths = (join(*paths) if paths else '')

        if query:
            return ''.join([url, paths, '?', urlencode(query)])
        return ''.join([url, paths])

    def _parse_query_string(self, qs):
        """Parses query string to a coerced datatype.

        :param qs: A uri query string
        :returns: a flattened dict representation of a query string
        """

        d = {}
        for key, val in parse_qs(qs).iteritems():
            d[key] = (val if len(val) > 1 else val[0])
        return d

    def _request(self, video_id):
        """Executes request to YouTube v3 service detailpage and handles the
        response, parsing out the meta data and decodes the format stream
        map.

        :param video_id: the YouTube video Id
        :returns: a dict representation of the metadata
        """

        url = self._url(BASE_URL, asv=3, el='detailpage', hl='en_US',
                           video_id=video_id)

        response = urlopen(url)
        if response.getcode() != 200:
            raise

        metadata = self._parse_query_string(response.read())

        stream_map = (self._parse_query_string(fsm) for fsm in
                      metadata['url_encoded_fmt_stream_map'].split(','))
        for fsm in stream_map:
            fsm.update({'url': '{url}&signature={sig}'.format(**fsm)})

        metadata['fmt_stream_map'] = stream_map
        return metadata

if __name__ == '__main__':
    from pprint import pprint
    yt = YouTube("http://www.youtube.com/watch?v=Ik-RsDGPI5Y")
    video_id = yt.video_id
    pprint(yt.get_metadata_by_id(video_id))
