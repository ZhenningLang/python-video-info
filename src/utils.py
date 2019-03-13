# -*- coding: utf-8 -*-

import logging


def set_logging(level=logging.INFO):
    logging.basicConfig(format='%(levelname)s: %(message)s', level=level)


def format_video_info(video_info: dict, fmt: str='json'):
    """

    :param video_info: dict
    :param fmt: json, text
    :return:
    """
    # TODO
    return str(video_info)
