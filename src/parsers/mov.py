# -*- coding: utf-8 -*-

from consts import TYPE_CHECK_MAX_BYTES


def type_checking_passed(reader):
    # search 'ftypqt  '
    for _ in range(TYPE_CHECK_MAX_BYTES // 4):
        four_bytes_data = reader.read(4)
        if four_bytes_data == b'ftyp':
            if reader.read(4) == b'qt  ':
                return True
            else:
                return False
    return False
