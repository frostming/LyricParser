# -*- coding: utf-8 -*-
import os


class Config(object):
    # The threshold ratio of rhyme, if the ratio is less than this value,
    # it is not returned as rhyme
    MIN_RHYME_RATIO = 0.2
    # The number of rhymes returned by LyricParser
    RHYME_NUM = 1
    # The number of playlists that spider fetches
    MAX_PLAYLIST_NUM = 100
    # The size of worker queue containing playlists
    PLAYLIST_QUEUE_SIZE = 100
    # The size of worker queue containing songs
    SONGS_QUEUE_SIZE = 100
    # Threads number
    WORKERS_NUM = 8

    def __init__(self):
        self.load_from_envs()

    def load_from_pyfile(self, filename):
        d = {}
        with open(filename) as fp:
            exec(compile(fp.read(), filename, 'exec'), d)
        self.load_from_dict(d)

    def load_from_envs(self, prefix='LYRIC'):
        for k in Config.__dict__:
            if not k.isupper():
                continue
            env_name = ('%s_%s' % (prefix, k)).upper()
            if os.getenv(env_name, None) is not None:
                typ = type(Config.__dict__[k])
                self.__dict__[k] = typ(os.environ[env_name])

    def load_from_dict(self, obj):
        for k, v in obj.iteritems():
            if k.upper() in Config.__dict__:
                self.__dict__[k.upper()] = v


config = Config()
