# -*- coding: utf-8 -*-
"""
Parse lyric data and get the rhyme
"""
from __future__ import unicode_literals
import os
import re
import collections
import xpinyin
from .defaults import config

__all__ = ['LyricParser']
# zh, ch, sh are stripped by 'z' and 'h'
shengmu_list = 'bpmfdtnlgkhjqxzcsryw'

yunmu_list = ('a', 'o', 'e', 'i', 'u', 'v', 'ai', 'ei', 'ui', 'ao', 'ou', 'ie',
              'ue', 've', 'iu', 'an', 'en', 'in', 'un', 'ang', 'eng', 'ing',
              'ong')

# 'ong' and 'eng' are similar enough, merge them together
merge_rhyme = {'v'   : 'u',
               'ui'  : 'ei',
               'ue'  : 'ie',
               've'  : 'ie',
               'iu'  : 'ou',
               'un'  : 'en',
               'ong' : 'eng'}


class LyricParser(object):

    # Regular expressions
    DRY_RE = re.compile(r'(^\[[^]]+\]|\s)', re.M)
    WRITER_RE = re.compile(r'(?:填词|作词)\s*[:：]\s*(.*)')
    HEADER_RE = re.compile(r'[:：]')

    def __init__(self, lyric=None):
        self.p = xpinyin.Pinyin()
        # Dry lyric without whitespaces and timestamps
        self.dry_lyric = []
        # Header lines of lyric
        self.header = []
        # Lyric writer, maybe None
        self.writer = ''
        if lyric is not None:
            self.parse_lyric(lyric)

    def parse_lyric(self, lyric):
        if not lyric:
            return
        for line in lyric.splitlines():
            line = self.DRY_RE.sub('', line)
            if self.HEADER_RE.search(line):
                self.header.append(line)
                rv = self.WRITER_RE.search(line)
                if rv:
                    self.writer = rv.group(1)
            elif line:
                self.dry_lyric.append(line)

    def get_rhyme(self, char):
        """Get the rhyme of a Chinese character, returns None if the character is
        not Chinese or yunmu is not found. ßMerge possible yunmus to one rhyme.
        """
        pinyin = self.p.get_pinyin(char)
        if not pinyin or not pinyin.isalpha():
            return None
        # Search from long yunmu to short ones
        for y in yunmu_list[::-1]:
            if pinyin.endswith(y):
                try:
                    return merge_rhyme[y]
                except KeyError:
                    return y
        return None

    def get_line_rhyme(self, line):
        """Get the rhyme of a single line"""
        line = line.rstrip()
        if not line:
            return None
        return self.get_rhyme(line[-1])

    def get_song_rhyme(self, return_num=None):
        """Get the rhyme of a song from lyric source. Returns no more than
        ``return_num`` values, if a rhyme ratio is less than
        ``min_rhyme_ratio``, ignore it.
        """
        # Discard None values
        if not self.dry_lyric:
            return []
        return_num = return_num or config.RHYME_NUM
        count = collections.Counter(filter(None, (self.get_line_rhyme(line)
                                                  for line in self.dry_lyric)))
        rv = count.most_common(return_num)
        total = sum(count.values())

        return [k for k, v in rv if float(v) / total >= config.MIN_RHYME_RATIO]

    def get_dry_length(self):
        """Get character number of dry lyrics, that is, remove any whitespaces
        and duplicated lines.
        """
        if not self.dry_lyric:
            return 0
        rv = 0
        # Create a set to store the counted lines
        temp = set()
        for line in self.dry_lyric:
            if line in temp:
                continue
            rv += len(line)
            temp.add(line)
        return rv
