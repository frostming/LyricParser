# -*- coding: utf-8 -*-
"""The crawler module"""
import threading
import Queue
from multiprocessing.pool import ThreadPool
from .source import NetEaseCloudSource
from .storage import SqliteStorage
from .defaults import config


def make_thread(target, args=(), kwargs={}):
    thread = threading.Thread(target=target, args=args, kwargs=kwargs)
    thread.setDaemon(True)
    thread.start()
    return thread


class SongsQueue(Queue.Queue):
    """A thread-safe queue to store songs to parse"""
    def _init(self, maxnum):
        self.queue = set()
        self.parsed = set()

    def _qsize(self, len=len):
        return len(self.queue)

    def _put(self, item):
        if item not in self.parsed:
            self.queue.add(item)

    def _get(self):
        item = self.queue.pop()
        self.parsed.add(item)
        return item


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
        self.pool = ThreadPool(self.worker_num)
        self.storage = storage_cls('result.db')
        self.source_cls = source_cls
        self.finished_playlist = threading.Event()
        columns = [('id', 'int'), ('name', 'text'), ('artist', 'text'),
                   ('playtime', 'int'), ('writer', 'text'),
                   ('rhyme', 'char(10)'), ('lyric_len', 'int')]
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
            writer, rhyme, lyric_len = source.get_song_lyric(song.id)
            data = (song.id, song.name, song.artist, song.playtime,
                    writer, rhyme, lyric_len)
            self.storage.add_row(data)

    def start_fetching(self):
        import time
        start_time = time.time()
        print "Start fetching..."
        self.pool.apply_async(self.fetch_playlist)
        for _ in range(self.worker_num):
            self.pool.apply_async(self.fetch_songs)
            self.pool.apply_async(self.fetch_song_info)
        self.pool.close()
        self.pool.join()
        print "End. time cost: %.2f" % (time.time() - start_time)


if __name__ == '__main__':
    spider = Spider()
    spider.start_fetching()
