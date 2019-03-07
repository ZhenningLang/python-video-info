# -*- coding: utf-8 -*-


def type_checking_passed(reader):
    # first four bytes are 'RIFF'
    # 5th to 8th bytes are 'AVI '
    first_four_bytes = reader.read(4)
    _ = reader.read(4)
    third_four_bytes = reader.read(4)

    return first_four_bytes == b'\x52\x49\x46\x46' and third_four_bytes == b'\x41\x56\x49\x20'
