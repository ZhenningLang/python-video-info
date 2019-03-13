# -*- coding: utf-8 -*-

import argparse
import logging
import os
import sys

from input import FileVideoReader, RemoteFileReader
from type_checker import check_video_type, VideoTypeEnum, type_to_parser
from utils import format_video_info, set_logging

__git_url__ = 'https://github.com/JenningLang/python-video-info'


def format_help(formatted_help):
    return formatted_help + '\nOr Visit: {} for more help\n'.format(__git_url__)


def read_args():
    parser = argparse.ArgumentParser(description='Get video info by PURE python codes')
    parser.add_argument('video_location', nargs='?', help='the location of video (local path or url)')
    parser.add_argument('--debug', action='store_const', const=True, default=False, help='using debug mode')
    parser.add_argument('--json', action='store_const', const=True, default=False, help='json format output')
    return parser.format_help(), parser.parse_args()


def get_file_reader(loc):
    try:
        if os.path.isfile(loc):
            file_reader = FileVideoReader(loc)
        else:
            file_reader = RemoteFileReader(loc)
    except Exception as e:
        logging.error("Open video location '{}' error: {}".format(loc, repr(e)), exc_info=True)
        sys.exit(-1)

    if isinstance(file_reader, FileVideoReader):
        logging.debug('Local File')
    else:
        logging.debug('Remote File')
    return file_reader


def main() -> None:
    formatted_help, args = read_args()
    set_logging(logging.DEBUG if args.debug else logging.INFO)

    if not args.video_location:
        logging.info(formatted_help)
        sys.exit(-1)
    loc = args.video_location
    file_reader = get_file_reader(loc)
    extend = file_reader.extend  # potential extend
    logging.debug('Potential extend: {}'.format(extend))
    # type checking
    video_type = check_video_type(file_reader, potential=VideoTypeEnum.get_type_from_extend(extend))
    parser = type_to_parser(video_type)  # one proper parse in parsers
    # raw video info, always json
    video_info = parser.parse(file_reader)
    # format video info indicated by fmt
    formatted_video_info = format_video_info(video_info, fmt='json' if args.json else 'text')
    print(formatted_video_info)


if __name__ == '__main__':
    main()
