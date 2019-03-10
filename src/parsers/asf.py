# -*- coding: utf-8 -*-


def type_checking_passed(reader):
    # first 16 bytes are header object uuid
    # b'\x30\x26\xB2\x75\x8E\x66\xCF\x11\xA6\xD9\x00\xAA\x00\x62\xCE\x6C'
    return reader.read(16) == b'\x30\x26\xB2\x75\x8E\x66\xCF\x11\xA6\xD9\x00\xAA\x00\x62\xCE\x6C'


def parse(reader):
    return "In asf parser.parse"
