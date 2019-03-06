# -*- coding: utf-8 -*-

"""
Check video type
"""

from importlib import import_module


class VideoTypeEnum:
    """
    'VideoTypeEnum.SOME_TYPE' is used for other scripts
    !!! 'some_type' is used inside this script (test_checker.py) !!!
    """

    UNKNOWN = 'VideoTypeEnum.UNKNOWN'

    MP4 = 'VideoTypeEnum.MP4'
    AVI = 'VideoTypeEnum.AVI'
    FLV = 'VideoTypeEnum.FLV'
    MKV = 'VideoTypeEnum.MKV'
    MOV = 'VideoTypeEnum.MOV'
    WMV = 'VideoTypeEnum.WMV'
    MPEG4 = 'MPVideoType.EG4'
    RM = 'VideoTypeEnum.RM'
    RMVB = 'RVideoType.MVB'

    _all = ('mp4', 'avi', 'flv', 'mkv', 'mov', 'wmv', 'mpeg4', 'rm', 'rmvb',)
    # _all = ('mp4',)

    @staticmethod
    def get_type(t: str):
        return getattr(VideoTypeEnum, t.upper(), VideoTypeEnum.UNKNOWN)

    @staticmethod
    def get_all():
        return VideoTypeEnum._all


def type_to_parser(t: str):
    """Map video type to
    't' belongs to one of VideoTypeEnum._all
    """
    return import_module('parsers.{}'.format(t))


def video_parser_iter(first: str=None) -> iter:
    """ Iteration of all video parsers
    yield 'type in lower case' and 'parser module'
    """
    if first is not None:
        if first in VideoTypeEnum.get_all():
            yield first, type_to_parser(first)
        else:
            first = None
    for t in VideoTypeEnum.get_all():
        if t == first:
            continue
        yield t, type_to_parser(t)


def check_video_type(reader, potential=VideoTypeEnum.UNKNOWN):
    if potential == VideoTypeEnum.UNKNOWN:
        first = None
    else:
        first = potential.split('.')[-1].lower()

    for t, parser in video_parser_iter(first):
        if parser.type_checking_passed(reader):
            reader.refresh()
            return VideoTypeEnum.get_type(t)

    raise Exception('Unrecognized video type!')
