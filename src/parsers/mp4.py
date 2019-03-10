# -*- coding: utf-8 -*-

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
