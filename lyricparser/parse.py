"""
Parse lyric data and get the rhyme
"""
import os
import collections
from xpinyin import Pinyin
from string import ascii_letters

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
min_rhyme_ratio = os.getenv('MIN_RHYME_RATIO', 0.2)

p = Pinyin()


def get_rhyme(char):
    """Get the rhyme of a Chinese character, returns None if the character is
    not Chinese or yunmu is not found. Merge possible yunmus to one rhyme.
    """
    # Search from long yunmu to short ones
    pinyin = p.get_pinyin(char)
    if not pinyin or not pinyin.isalpha():
        return None
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
    ignore it."""
    # Discard None values
    count = collections.Counter(
        filter(None, (get_line_rhyme(line) for line in lyric.splitlines())))
    rv = count.most_common(return_num)
    total = sum(count.values())

    return [k for k, v in rv if float(v) / total >= min_rhyme_ratio]
