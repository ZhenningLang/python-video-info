# -*- coding: utf-8 -*-

from consts import TYPE_CHECK_MAX_BYTES


def type_checking_passed(reader):
    # search ftyp
    for _ in range(TYPE_CHECK_MAX_BYTES // 4):
        four_bytes_data = reader.read(4)
        if four_bytes_data == b'\x66\x74\x79\x70':
            return True
    return False
