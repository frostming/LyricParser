# -*- coding: utf-8 -*-
"""
Parse lyric data and get the rhyme
"""
import os
import re
import collections
import xpinyin
from .defaults import config

__all__ = ['get_rhyme', 'get_line_rhyme', 'get_song_rhyme']
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

# If the rhyme ratio is less than this threshold, regard it as non-rhyme
# Set env variable "MIN_RHYME_RATIO"  to override this value

p = xpinyin.Pinyin()

# Regular expressions
DRY_RE = re.compile(u'(^\\[[^]]+\\]|\s)', re.M)
WRITER_RE = re.compile(u'(?:填词|作词)\\s*[:：]\\s*(.*)')
HEADER_RE = re.compile(u'[:：]')


def get_rhyme(char):
    """Get the rhyme of a Chinese character, returns None if the character is
    not Chinese or yunmu is not found. Merge possible yunmus to one rhyme.
    """
    pinyin = p.get_pinyin(char)
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


def get_line_rhyme(line):
    """Get the rhyme of a single line"""
    line = line.rstrip()
    if not line or line[-1] in '[]':
        return None
    return get_rhyme(line[-1])


def get_song_rhyme(lyric, return_num=1):
    """Get the rhyme of a song from lyric source. Returns no more than
    ``return_num`` values, if a rhyme ratio is less than ``min_rhyme_ratio``,
    ignore it.
    """
    # Discard None values
    count = collections.Counter(
        filter(None, (get_line_rhyme(line) for line in lyric.splitlines())))
    rv = count.most_common(return_num)
    total = sum(count.values())

    return [k for k, v in rv if float(v) / total >= config.MIN_RHYME_RATIO]


def get_lyric_len(lyric):
    """Get character number of dry lyrics, that is, remove any whitespaces
    and duplicated lines.
    """
    rv = 0
    # Create a set to store the counted lines
    temp = {}
    for line in lyric.splitlines():
        line = DRY_RE.sub('', line)
        if HEADER_RE.search(line) is not None:
            continue
        if line in temp:
            continue
        rv += len(line)
        temp.add(line)
    return rv


def get_lyric_writer(lyric):
    """Guess the writer of a lyric"""
    rv = WRITER_RE.findall(lyric)
    if rv:
        return rv[0]
