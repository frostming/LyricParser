# -*- coding: utf-8 -*-
import os


class Config(object):
    MIN_RHYME_RATIO = 0.2
    MAX_PLAYLIST_NUM = 100
    PLAYLIST_QUEUE_SIZE = 100
    SONGS_QUEUE_SIZE = 100
    WORKERS_NUM = 8
    RHYME_NUM = 1

    def __init__(self):
        self.load_from_envs()

    def load_from_pyfile(self, filename):
        d = {}
        with open(filename) as fp:
            exec(compile(fp.read(), filename, 'exec'), d)
        self.load_from_dict(d)

    def load_from_envs(self, prefix='LYRIC'):
        for k in self.__dict__:
            env_name = ('%s_%s' % (prefix, k)).upper()
            if os.getenv(env_name, None) is not None:
                self.__dict__[k] = os.environ[env_name]

    def load_from_dict(self, obj):
        for k, v in d.iteritems():
            if k in self.__dict__:
                self.__dict__[k] = v


config = Config()
