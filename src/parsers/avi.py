# -*- coding: utf-8 -*-


def type_checking_passed(reader):
    # first four bytes are 'RIFF'
    # 5th to 8th bytes are 'AVI '
    first_four_bytes = reader.read(4)
    _ = reader.read(4)
    third_four_bytes = reader.read(4)

    return first_four_bytes == b'RIFF' and third_four_bytes == b'AVI '


def parse(reader):
    return "In avi parser.parse"
