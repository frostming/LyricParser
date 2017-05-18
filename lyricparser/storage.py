# -*- coding: utf-8 -*-
import os
import csv
import sqlite3
import threading
import io


class BaseStorage(object):
    STORAGE_ROOT = os.path.join(os.path.dirname(__file__), '../storage')
    if not os.path.isdir(STORAGE_ROOT):
        os.mkdir(STORAGE_ROOT)


class SqliteStorage(BaseStorage):
    def __init__(self, filename, *args, **kwargs):
        self.filepath = os.path.join(self.STORAGE_ROOT, filename)
        kwargs.setdefault('check_same_thread', False)
        self.conn = sqlite3.connect(self.filepath, *args, **kwargs)
        self.cursor = self.conn.cursor()
        self._lock = threading.RLock()

    def __del__(self):
        self.conn.close()

    def init_storage(self, columns):
        self._lock.acquire()
        try:
            self.cursor.execute('drop table songs;')
        except Exception:
            pass
        table_cmd = ', '.join(' '.join(col) for col in columns)
        self.cursor.execute('create table songs(%s);' % table_cmd)
        self.conn.commit()
        self._lock.release()

    def add_row(self, data):
        with self._lock:
            self.cursor.execute('insert into songs values'
                                '(%s);' % ','.join(['?'] * len(data)), data)
            self.conn.commit()

    def get_row_count(self):
        self.cursor.execute('select count(*) from songs;')
        return self.cursor.fetchone()[0]

    def to_excel(self, filename):
        filepath = os.path.join(self.STORAGE_ROOT, filename)
        with open(filepath, 'w') as fp:
            writer = csv.writer(fp, delimiter='\t')
            writer.writerow(['id', 'name', 'artist', 'playtime', 'writer',
                             'rhyme', 'lyric_len'])
            self.cursor.execute('select * from songs')
            for line in self.cursor.fetchall():
                writer.writerow([unicode(v).encode('utf-8') for v in line])
