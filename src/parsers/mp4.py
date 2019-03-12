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
from excptions import EOF

FTYP_CONSEQUENCE_TYPES = (
    b'avc1', b'iso2', b'isom', b'mmp4', b'mp41',
    b'mp42', b'NDSC', b'NDSH', b'NDSM', b'NDSP',
    b'NDSS', b'NDXC', b'NDXH', b'NDXM', b'NDXP',
    b'NDXS', b'M4V '
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
    if box_size == 0 and box_type == '':
        raise EOF
    return box_size, box_type, offset


class BoxMeta:

    def __init__(self, box_size, box_type, offset):
        self.box_size = box_size
        self.box_type = box_type
        self.offset = offset


class Box:

    def __init__(self, reader, box_meta: BoxMeta=None):
        self.reader = reader
        # self.offset: total bytes from box beginning
        if box_meta is None:
            self.box_size, self.box_type, self.offset = read_box_size_and_type(reader)
        else:
            self.box_size, self.box_type, self.offset = box_meta.box_size, box_meta.box_type, box_meta.offset
        logging.debug(
            'box_size: {} bytes, box_type: {}, offset: {}'.format(self.box_size, self.box_type, self.offset))

    def read_int(self, num_of_byte: int = 1, byteorder: str = 'big') -> int:
        self.offset += num_of_byte
        return self.reader.read_int(num_of_byte, byteorder)

    def read_float(self, before_point_num_of_byte: int = 1, after_point_num_of_byte: int = 1,
                   byteorder: str = 'big') -> float:
        self.offset += before_point_num_of_byte
        self.offset += after_point_num_of_byte
        return self.reader.read_float(before_point_num_of_byte, after_point_num_of_byte, byteorder)

    def read_str(self, num_of_byte: int = 1, charset='utf8') -> str:
        self.offset += num_of_byte
        return self.reader.read_str(num_of_byte, charset)

    def read(self, num_of_byte: int = 1) -> bytes:
        self.offset += num_of_byte
        return self.reader.read(num_of_byte)

    def ignore_remained(self):
        if self.box_size - self.offset > 0 and self.box_size != 0:
            self.read(self.box_size - self.offset)
        elif self.box_size == 0:
            self.read(-1)

    def json(self) -> dict:
        r_val = dict(self.__dict__)
        for key in self.__dict__.keys():
            if isinstance(r_val[key], Box):
                r_val[key] = r_val[key].json()
            elif isinstance(r_val[key], list):
                new_val = [
                    item.json() if isinstance(item, Box) else item
                    for item in r_val[key]
                ]
                r_val[key] = new_val
            if key in ('offset', 'reader', ):  # not to json keys
                del r_val[key]
        return r_val


class FTYPBox(Box):

    def __init__(self, reader, box_meta: BoxMeta=None):
        """
        Side effect: reader offset change
        """
        super().__init__(reader, box_meta)
        assert self.box_type == 'ftyp'
        self.major_brand = self.read_str(4)
        self.minor_version = self.read_int(4)
        compatible_brands_size = self.box_size - self.offset
        self.compatible_brands = [self.read_str(4) for _ in range(compatible_brands_size // 4)]


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
        self.version = self.read_int(1)
        assert(self.version == 0)  # TODO: currently only support version=0
        self.flags = self.read_int(3)
        base_datetime = datetime.datetime.strptime('1904-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
        self.creation_time = base_datetime + datetime.timedelta(seconds=self.read_int(4))
        self.modification_time = base_datetime + datetime.timedelta(seconds=self.read_int(4))
        self.time_scale = self.read_int(4)
        self.duration = self.read_int(4)
        self.scaled_duration = round(self.duration / self.time_scale, 3)  # unit: s
        self.suggested_rate = self.read_float(2, 2)  # suggested play rate
        self.suggested_volume = self.read_float(1, 1)  # suggested play volume
        # self.read(10)  # ignore reserved
        # self.matrix = self.read(36)  # video transform matrix ???
        # self.pre_defined = self.read(24)  # ???
        # self.next_track_id = self.read(4)
        # TODO: I have not figured out the above data structure, so they are just ignored
        self.ignore_remained()


class TrackBox(Box):

    def __init__(self, reader, box_meta: BoxMeta=None):
        """
        Side effect: reader offset change
        """
        super().__init__(reader, box_meta)
        assert self.box_type == 'trak'
        self.ignore_remained()  # TODO


class MOOVBox(Box):

    def __init__(self, reader, box_meta: BoxMeta=None):
        """
        Side effect: reader offset change
        """
        super().__init__(reader, box_meta)
        assert self.box_type == 'moov'
        self.mvhd_box = MVHDBox(reader)
        self.track_box_list = []
        while True:
            box_size, box_type, offset = read_box_size_and_type(reader)
            if box_type == 'trak':
                self.track_box_list.append(
                    TrackBox(reader, box_meta=BoxMeta(box_size, box_type, offset))
                )
            else:
                break


def parse(reader):
    # parse ftyp box
    ftyp_box = FTYPBox(reader)
    logging.debug('ftyp: {}'.format(ftyp_box.json()))
    box_size, box_type, offset = find_moov_box(reader)
    moov_box = MOOVBox(reader, box_meta=BoxMeta(box_size, box_type, offset))
    logging.debug('moov: {}'.format(moov_box.json()))
