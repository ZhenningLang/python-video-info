# -*- coding: utf-8 -*-

import logging

CONTENTS = ['ver_and_expand', 'ctime', 'mtime', 'time_scale', 'duration']


def get_video_duration(file_path_name):
    """获取视频时常

    Args:
        file_path_name:

    Returns: duration, or -1 fail to dectect

    """
    try:
        with open(file_path_name, 'rb') as f:
            # find mvhd
            for i in range(1000):
                data = f.read(4)
                if data == b'\x6d\x76\x68\x64':
                    break
            # find time_scale and duration
            time_scale = 0
            duration = 0
            for i in range(len(CONTENTS)):
                data = f.read(4)
                if CONTENTS[i] == 'time_scale':
                    time_scale = int.from_bytes(data, byteorder='big')
                elif CONTENTS[i] == 'duration':
                    duration = int.from_bytes(data, byteorder='big')
            return round(duration / time_scale, 3)
    except Exception as e:
        logging.debug(file_path_name, e)
        return -1
