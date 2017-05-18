# -*- coding: utf-8 -*-
"""The source of lyrics data"""
from __future__ import unicode_literals
import abc
import requests
from bs4 import BeautifulSoup
from .defaults import config
from collections import namedtuple


class BaseSource(object):
    """Abstract Base Class for sources"""
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.session = requests.session()

    @abc.abstractmethod
    def get_chinese_playlists(self):
        yield

    @abc.abstractmethod
    def get_songs_in_playlist(self, pl_id):
        yield

    @abc.abstractmethod
    def get_song_lyric(self, song_id):
        return None


class NetEaseCloudSource(BaseSource):
    """Net Ease Cloud Music"""
    ROOT = 'http://music.163.com'
    API_ROOT = ROOT + '/api'
    PLAYLIST_HUB = ROOT + '/discover/playlist/'
    SONG_STRUCT = namedtuple('Song', ['id', 'name', 'artist', 'playtime'])

    def get_chinese_playlists(self, maxnum=None):
        """Get the chinese playlists from the PLAYLIST_HUB url,
        returns a generator.
        """
        if maxnum is None:
            maxnum = config.MAX_PLAYLIST_NUM
        payload = {'cat': '华语',
                   'limit': 35,
                   'offset': 0}
        while payload['offset'] < maxnum:
            r = self.session.get(self.PLAYLIST_HUB, params=payload)
            content = BeautifulSoup(r.content, 'lxml')
            rv = content.select('#m-pl-container li .dec a')
            for item in rv:
                try:
                    yield item['href'].split('id=')[1]
                except Exception:
                    pass
            payload['offset'] += 35

    def get_songs_in_playlist(self, pl_id):
        """Get the songs contained in given playlist.

        :params pl_id: playlist id
        :returns: Song(id, name, artist, playtime)
        """
        url = self.API_ROOT + '/playlist/detail?id=%s&updateTime=-1' % pl_id
        r = self.session.get(url)
        for song in r.json()['result']['tracks']:
            id = song['id']
            name = song['name']
            artist = '/'.join(ar['name'] for ar in song['artists'])
            playtime = song['bMusic']['playTime']
            yield self.SONG_STRUCT(id, name, artist, playtime)

    def get_song_lyric(self, song_id):
        """Get the lyric of a song.

        :params song_id: song ID
        :returns: lyric content
        """
        url = self.API_ROOT + '/song/lyric?os=pc&id=%s&lv=-1' % song_id
        r = self.session.get(url)
        try:
            return r.json()['lrc']['lyric']
        except Exception:
            return None
