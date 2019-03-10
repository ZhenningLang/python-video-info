# -*- coding: utf-8 -*-

"""
Check video type
"""

from importlib import import_module

from input import VideoReader

__all__ = ('VideoTypeEnum', 'type_to_parser', 'check_video_type')


class VideoTypeEnum:
    """
    'VideoTypeEnum.SOME_TYPE' is used for other scripts
    !!! 'some_type' is used inside this script (test_checker.py) !!!
    """

    UNKNOWN = 'VideoTypeEnum.UNKNOWN'

    ASF = 'VideoTypeEnum.ASF'  # usually wmv
    AVI = 'VideoTypeEnum.AVI'
    FLV = 'VideoTypeEnum.FLV'
    MKV = 'VideoTypeEnum.MKV'
    MOV = 'VideoTypeEnum.MOV'
    MP4 = 'VideoTypeEnum.MP4'
    RM = 'VideoTypeEnum.RM'  # the container of rm and rmvb are the same
    RMVB = 'VideoTypeEnum.RMVB'

    _all = ('asf', 'avi', 'flv', 'mkv', 'mov', 'mp4', 'rm', 'rmvb',)
    # _all = ('mp4',)

    @staticmethod
    def get_type(t: str) -> str:
        return getattr(VideoTypeEnum, t.upper(), VideoTypeEnum.UNKNOWN)

    @staticmethod
    def get_type_from_extend(t: str) -> str:
        return VideoTypeEnum.get_type(t)

    @staticmethod
    def get_all_types():
        return VideoTypeEnum._all


def type_to_parser(t: str):
    """Map VideoTypeEnum.? to parser module in parsers"""

    return _type_to_parser(t.split('.')[-1].lower())


def _type_to_parser(t: str):
    """Map video type to parser module in parsers
    't' belongs to one of VideoTypeEnum._all
    """
    return import_module('parsers.{}'.format(t))


def _video_parser_iter(first: str=None) -> iter:
    """ Iteration of all video parsers
    yield 'type in lower case' and 'parser module'
    """
    if first is not None:
        if first in VideoTypeEnum.get_all_types():
            yield first, _type_to_parser(first)
        else:
            first = None
    for t in VideoTypeEnum.get_all_types():
        if t == first:
            continue
        yield t, _type_to_parser(t)


def check_video_type(reader: VideoReader, potential=VideoTypeEnum.UNKNOWN):
    if potential == VideoTypeEnum.UNKNOWN:
        first = None
    else:
        first = potential.split('.')[-1].lower()

    for t, parser in _video_parser_iter(first):
        res = parser.type_checking_passed(reader)
        reader.refresh()
        if res:
            return VideoTypeEnum.get_type(t)

    raise Exception('Unrecognized video type!')
