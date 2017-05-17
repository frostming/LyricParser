# -*- coding: utf-8 -*-
"""The crawler module"""
import threading
from .source import NetEaseCloudSource
from .storage import SqliteStorage

netease = NetEaseCloudSource()


class Spider(object):
    """The spider class containing all utilities that a crawler does"""
    def __init__(self, q_size=100, worker_num=4, storage_cls=SqliteStorage):
        pass
