# -*- coding: utf-8 -*-
import os
import csv
import sqlite3


class BaseStorage(object):
    STORAGE_ROOT = os.path.join(os.path.dirname(__file__), '../storage')
    if not os.path.isdir(STORAGE_ROOT):
        os.mkdir(STORAGE_ROOT)


class SqliteStorage(BaseStorage):
    def __init__(self, filename):
        self.filepath = os.path.join(self.STORAGE_ROOT, filename)

    def init_storage(self, columns):
        if os.path.exists(self.filepath):
            print "Storage file already exists, do nothing"
            return

    def add_row(self, data):
        pass

    def get_row(self, row):
        pass

    def get_row_count(self):
        pass

    def to_excel(self, filename):
        filepath = os.path.join(self.STORAGE_ROOT, filename)
