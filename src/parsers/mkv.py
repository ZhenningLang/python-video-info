# -*- coding: utf-8 -*-


def type_checking_passed(reader):
    # first four bytes are '\x1A\x45\xDF\xA3'
    return reader.read(4) == b'\x1A\x45\xDF\xA3'
