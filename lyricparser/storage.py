# -*- coding: utf-8 -*-
import os
import csv
import sys
import sqlite3
import threading


class BaseStorage(object):
    STORAGE_ROOT = os.path.join(os.path.dirname(__file__), '../data')
    if not os.path.isdir(STORAGE_ROOT):
        os.mkdir(STORAGE_ROOT)


class SqliteStorage(BaseStorage):
    def __init__(self, filename, *args, **kwargs):
        self.filepath = os.path.join(self.STORAGE_ROOT, filename)
        kwargs.setdefault('check_same_thread', False)
        self.conn = sqlite3.connect(self.filepath, *args, **kwargs)
        self.cursor = self.conn.cursor()
        self.headers = None
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
        self.headers = [col[0] for col in columns]
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
        csv_storage = CsvStorage(filename, delimiter='\t')
        csv_storage.init_storage(self.headers)
        self.cursor.execute('select * from songs')
        for line in self.cursor.fetchall():
            csv_storage.add_row(line)


class CsvStorage(BaseStorage):
    def __init__(self, filename, dialect='excel', **kwargs):
        self.filepath = os.path.join(self.STORAGE_ROOT, filename)
        self.fp = open(self.filepath, 'wb')
        # Add BOM on Windows
        if sys.platform[:3] == 'win':
            self.fp.write(u'\ufeff'.encode('utf-8'))
        self.writer = csv.writer(fp, dialect, **kwargs)
        self.headers = None
        self._lock = RLock()

    def __del__(self):
        self.fp.close()

    def init_storage(self, columns):
        with self._lock:
            self.writer.writerow([col[0] for col in columns])
            self.headers = [col[0] for col in columns]

    def add_row(self, data):
        with self._lock:
            data = [unicode(v).encode('utf-8') for v in data]
            self.writer.writerow(data)
