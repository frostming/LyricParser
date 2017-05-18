# -*- coding: utf-8 -*-
"""The crawler module"""
import threading
import Queue
from .source import NetEaseCloudSource
from .storage import SqliteStorage
from .defaults import config
from . import lyrics


def make_thread(target, args=(), kwargs={}):
    thread = threading.Thread(target=target, args=args, kwargs=kwargs)
    thread.setDaemon(True)
    thread.start()
    return thread


class SongsQueue(Queue.Queue):
    """A thread-safe queue to store songs to parse"""
    def _init(self, maxnum):
        self.queue = set()

    def _qsize(self, len=len):
        return len(self.queue)

    def _put(self, item):
        self.queue.add(item)

    def _get(self):
        return self.queue.pop()


class Spider(object):
    """The spider class containing all utilities that a crawler does"""
    def __init__(self, playlist_q_size=None, songs_q_size=None,
                 worker_num=None, storage_cls=SqliteStorage,
                 source_cls=NetEaseCloudSource):
        playlist_q_size = playlist_q_size or config.PLAYLIST_QUEUE_SIZE
        songs_q_size = songs_q_size or config.SONGS_QUEUE_SIZE
        self.worker_num = worker_num or config.WORKERS_NUM
        self.playlist_q = Queue.Queue(playlist_q_size)
        self.songs_q = SongsQueue(songs_q_size)
        self.storage = storage_cls('result.db')
        self.source_cls = source_cls
        self.finished_playlist = threading.Event()
        columns = [('name', 'text'), ('artist', 'text'), ('playtime', 'int'),
                   ('writer', 'text'), ('rhyme', 'char(10)'),
                   ('lyric_len', 'int')]
        self.storage.init_storage(columns)

    def fetch_playlist(self, maxnum=None):
        self.finished_playlist.clear()
        source = self.source_cls()
        for pl_id in source.get_chinese_playlists(maxnum):
            self.playlist_q.put(pl_id, True)
        self.finished_playlist.set()

    def fetch_songs(self):
        source = self.source_cls()
        while True:
            try:
                pl_id = self.playlist_q.get(False)
            except Queue.Empty:
                if self.finished_playlist.is_set():
                    break
                else:
                    continue
            for song in source.get_songs_in_playlist(pl_id):
                self.songs_q.put(song, True)
            self.playlist_q.task_done()

    def fetch_song_info(self):
        while self.playlist_q.unfinished_tasks or \
              not self.finished_playlist.is_set():
            try:
                song = self.songs_q.get(False)
            except Queue.Empty:
                continue
            source = self.source_cls()
            lyric = source.get_song_lyric(song.id)
            writer, rhyme, lyric_len = (
                lyrics.get_lyric_writer(lyric),
                ', '.join(lyrics.get_song_rhyme(lyric, config.RHYME_NUM)),
                lyrics.get_lyric_len(lyric))
            data = (song.id, song.name, song.artist, song.playtime,
                    writer, rhyme, lyric_len)
            self.storage.add_row(data)

    def start_fetching(self):
        import time
        threads = []
        start_time = time.time()
        print "Start fetching..."
        threads.append(make_thread(self.fetch_playlist))
        for _ in range(5):
            threads.append(make_thread(self.fetch_songs))
            threads.append(make_thread(self.fetch_song_info))
        for th in threads:
            th.join()
        print "End. time cost: %.2f" % time.time() - start_time


if __name__ == '__main__':
    spider = Spider()
    spider.start_fetching()
