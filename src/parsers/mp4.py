# -*- coding: utf-8 -*-

"""
Main Reference:
https://www.cnblogs.com/ranson7zop/p/7889272.html
https://blog.csdn.net/u013898698/article/details/77152347
https://www.cnblogs.com/qq260250932/p/4282304.html

MP4 is big endian
"""

import datetime
import logging

from consts import TYPE_CHECK_MAX_BYTES

FTYP_CONSEQUENCE_TYPES = (
    b'avc1', b'iso2', b'isom', b'mmp4', b'mp41',
    b'mp42', b'NDSC', b'NDSH', b'NDSM', b'NDSP',
    b'NDSS', b'NDXC', b'NDXH', b'NDXM', b'NDXP',
    b'NDXS',
)


def type_checking_passed(reader):
    # search ftyp and consequence type
    # see: http://www.ftyps.com/
    for _ in range(TYPE_CHECK_MAX_BYTES // 4):
        four_bytes_data = reader.read(4)
        if four_bytes_data == b'ftyp':
            if reader.read(4) in FTYP_CONSEQUENCE_TYPES:
                return True
            else:
                return False
    return False


def read_box_size_and_type(reader) -> (int, str, int):
    """
    Side effect: reader offset change
    """
    # if box_size == 1, find size in largesize
    # if box_size == 0, this is the last box
    box_size = reader.read_int(4)
    box_type = reader.read_str(4)
    offset = 8
    if box_size == 1:
        box_size = reader.read_int(8)
        offset = 16
    return box_size, box_type, offset


class BoxMeta:

    def __init__(self, box_size, box_type, offset):
        self.box_size = box_size
        self.box_type = box_type
        self.offset = offset


class Box:

    def __init__(self, reader, box_meta: BoxMeta=None):
        if box_meta is None:
            self.box_size, self.box_type, self.offset = read_box_size_and_type(reader)
        else:
            self.box_size, self.box_type, self.offset = box_meta.box_size, box_meta.box_type, box_meta.offset
        logging.debug(
            'box_size: {} bytes, box_type: {}, offset: {}'.format(self.box_size, self.box_type, self.offset))

    def json(self) -> dict:
        r_val = dict(self.__dict__)
        for key in self.__dict__.keys():
            if isinstance(r_val[key], Box):
                r_val[key] = r_val[key].json()
            if key == 'offset':
                del r_val[key]
        return r_val


class FTYPBox(Box):

    def __init__(self, reader, box_meta: BoxMeta=None):
        """
        Side effect: reader offset change
        """
        super().__init__(reader, box_meta)
        assert self.box_type == 'ftyp'
        self.major_brand = reader.read_str(4)
        self.minor_version = reader.read_int(4)
        compatible_brands_size = self.box_size - self.offset - 8
        self.compatible_brands = [reader.read_str(4) for _ in range(compatible_brands_size // 4)]


def find_moov_box(reader):
    while True:
        # If read to file end and moov is not found, read_box_size_and_type would raise an None Type error
        # So here I do not check box_size == 0
        box_size, box_type, offset = read_box_size_and_type(reader)
        logging.debug('box_size: {} bytes, box_type: {}, offset: {}'.format(box_size, box_type, offset))
        if box_type == 'moov':
            return box_size, box_type, offset
        reader.read(box_size - offset)  # skip unused data


class MVHDBox(Box):

    def __init__(self, reader, box_meta: BoxMeta=None):
        """
        Side effect: reader offset change
        """
        super().__init__(reader, box_meta)
        assert self.box_type == 'mvhd'
        self.version = reader.read_int(1)
        assert(self.version == 0)  # TODO: currently only support version=0
        self.flags = reader.read_int(3)
        base_datetime = datetime.datetime.strptime('1904-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
        self.creation_time = base_datetime + datetime.timedelta(seconds=reader.read_int(4))
        self.modification_time = base_datetime + datetime.timedelta(seconds=reader.read_int(4))
        self.time_scale = reader.read_int(4)
        self.duration = reader.read_int(4)
        self.scaled_duration = self.duration / self.time_scale  # unit: s
        self.suggested_rate = reader.read_float(2, 2)  # suggested play rate
        self.suggested_volume = reader.read_float(1, 1)  # suggested play volume
        reader.read(10)  # ignore reserved
        # self.matrix = reader.read(36)  # video transform matrix ???
        # self.pre_defined = reader.read(24)  # ???
        # self.next_track_id = reader.read(4)
        # TODO: I have not figured out the above data structure, so they are just ignored
        reader.read(36)
        reader.read(24)
        reader.read(4)


class MOOVBox(Box):

    def __init__(self, reader, box_meta: BoxMeta=None):
        """
        Side effect: reader offset change
        """
        super().__init__(reader, box_meta)
        assert self.box_type == 'moov'
        self.mvhd_box = MVHDBox(reader)


def parse(reader):
    # parse ftyp box
    ftyp_box = FTYPBox(reader)
    logging.debug('ftyp: {}'.format(ftyp_box.json()))
    box_size, box_type, offset = find_moov_box(reader)
    moov_box = MOOVBox(reader, box_meta=BoxMeta(box_size, box_type, offset))
    logging.debug('moov: {}'.format(moov_box.json()))
