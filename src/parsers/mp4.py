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
from pprint import pprint

from consts import TYPE_CHECK_MAX_BYTES
from excptions import EOF

FTYP_CONSEQUENCE_TYPES = (
    b'avc1', b'iso2', b'isom', b'mmp4', b'mp41',
    b'mp42', b'NDSC', b'NDSH', b'NDSM', b'NDSP',
    b'NDSS', b'NDXC', b'NDXH', b'NDXM', b'NDXP',
    b'NDXS', b'M4V '
)

BASE_DATETIME = datetime.datetime.strptime('1904-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')


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


def find_first_box_by_type(reader, wanted_box_type: str):
    """

    :param reader:
    :param wanted_box_type:
    :return: box_size: found box size
             box_type: found box type, always equal to wanted_box_type
             offset: offset of current reader compared with wanted box's beginning
             ignored_size: total ignored box size in while loop
    """
    ignored_size = 0
    while True:
        # If read to file end and box is not found, read_box_size_and_type would raise an None Type error
        # So here I do not check box_size == 0
        box_size, box_type, offset = read_box_size_and_type(reader)
        logging.debug('Find first {} box: box_size: {} bytes, box_type: {}, offset: {}'.format(
            wanted_box_type, box_size, box_type, offset))
        if box_type == wanted_box_type:
            return box_size, box_type, offset, ignored_size
        ignored_size += box_size
        reader.read(box_size - offset)  # skip unused data


class HEADBox(Box):

    def __init__(self, reader, box_meta: BoxMeta=None):
        """
        Side effect: reader offset change
        """
        super().__init__(reader, box_meta)
        self.version = self.read_int(1)
        assert(self.version == 0)  # TODO: currently only support version=0
        self.flags = self.read_int(3)
        self.creation_time = BASE_DATETIME + datetime.timedelta(seconds=self.read_int(4))
        self.modification_time = BASE_DATETIME + datetime.timedelta(seconds=self.read_int(4))


class MVHDBox(HEADBox):

    def __init__(self, reader, box_meta: BoxMeta=None):
        super().__init__(reader, box_meta)
        assert self.box_type == 'mvhd'
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


class TKHDBox(HEADBox):

    def __init__(self, reader, box_meta: BoxMeta=None):
        super().__init__(reader, box_meta)
        assert self.box_type == 'tkhd'
        self.track_id = self.read(4)
        self.read(4)  # 4 bytes reserved
        self.duration = self.read_int(4)
        self.read(8)  # 8 bytes reserved
        self.layer = self.read_int(2)
        self.alternate_group = self.read_int(2)
        self.volume = self.read_float(1, 1)
        self.read(2)  # 2 bytes reserved
        self.read(36)  # video transform matrix ???
        self.width = self.read_float(2, 2)
        self.height = self.read_float(2, 2)
        self.ignore_remained()


class MDHDBox(HEADBox):
    def __init__(self, reader, box_meta: BoxMeta=None):
        """
        Side effect: reader offset change
        """
        super().__init__(reader, box_meta)
        assert self.box_type == 'mdhd'
        self.time_scale = self.read_int(4)
        self.duration = self.read_int(4)
        self.fixed_duration = round(self.duration / self.time_scale, 2)
        # self.language = self.read(2)
        # self.pre_defined = self.read(2)
        self.ignore_remained()


class HDLRBox(Box):

    def __init__(self, reader, box_meta: BoxMeta=None):
        """
        Side effect: reader offset change
        """
        super().__init__(reader, box_meta)
        assert self.box_type == 'hdlr'
        self.version = self.read_int(1)
        assert(self.version == 0)  # TODO: currently only support version=0
        self.flags = self.read_int(3)
        self.read(4)  # self.pre_defined
        self.handler_type = self.read_str(4)  # vide, soun, hint
        self.read(12)  # reserved
        if self.box_size - self.offset > 1 and self.box_size != 0:
            self.name = self.read_str(self.box_size - self.offset - 1)
        self.ignore_remained()  # reserved and name


class MediaBox(Box):

    def __init__(self, reader, box_meta: BoxMeta=None):
        """
        Side effect: reader offset change
        """
        super().__init__(reader, box_meta)
        assert self.box_type == 'mdia'
        self.mdhd_box = MDHDBox(reader)
        self.offset += self.mdhd_box.offset
        self.hdlr_box = HDLRBox(reader)
        self.offset += self.hdlr_box.offset
        self.ignore_remained()


class TrackBox(Box):

    def __init__(self, reader, box_meta: BoxMeta=None):
        """
        Side effect: reader offset change
        """
        super().__init__(reader, box_meta)
        assert self.box_type == 'trak'
        self.tkhd_box = TKHDBox(reader)
        self.offset += self.tkhd_box.box_size
        box_size, box_type, offset, ignored_size = find_first_box_by_type(reader, wanted_box_type='mdia')
        self.offset += ignored_size
        self.media_box = MediaBox(reader, box_meta=BoxMeta(box_size, box_type, offset))
        self.offset += self.media_box.box_size
        assert self.media_box is not None
        self.ignore_remained()


class MOOVBox(Box):

    def __init__(self, reader, box_meta: BoxMeta=None):
        """
        Side effect: reader offset change
        """
        super().__init__(reader, box_meta)
        assert self.box_type == 'moov'
        self.mvhd_box = MVHDBox(reader)
        self.offset += self.mvhd_box.box_size
        self.track_box_list = []
        while self.offset < self.box_size:
            box_size, box_type, offset = read_box_size_and_type(reader)
            logging.debug(
                'Find track box: box_size: {} bytes, box_type: {}, offset: {}'.format(box_size, box_type, offset))
            if box_type == 'trak':
                self.track_box_list.append(
                    TrackBox(reader, box_meta=BoxMeta(box_size, box_type, offset))
                )
            else:
                self.read(box_size - offset)
            self.offset += box_size


def parse(reader):
    # parse ftyp box
    ftyp_box = FTYPBox(reader)
    logging.debug('ftyp: {}'.format(ftyp_box.json()))
    moov_box_list = []
    try:
        while True:
            box_size, box_type, offset, _ = find_first_box_by_type(reader, wanted_box_type='moov')
            moov_box = MOOVBox(reader, box_meta=BoxMeta(box_size, box_type, offset))
            moov_box_list.append(moov_box)
    except EOF:
        pass

    if logging.getLogger().level == logging.DEBUG:
        import time
        time.sleep(1)
        for moov_box in moov_box_list:
            pprint(moov_box.json(), indent=2)
