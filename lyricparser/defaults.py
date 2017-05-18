# -*- coding: utf-8 -*-


class Config(object):
    MIN_RHYME_RATIO = 0.2
    MAX_PLAYLIST_NUM = 100
    PLAYLIST_QUEUE_SIZE = 100
    SONGS_QUEUE_SIZE = 100
    WORKERS_NUM = 8
    RHYME_NUM = 1

    def load_from_pyfile(self, filename):
        pass

    def load_from_inifile(self, filename):
        pass

    def load_from_envs(self, prefix='LYRIC'):
        pass

    def load_from_dict(self, obj):
        pass


config = Config()
