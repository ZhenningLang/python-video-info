# -*- coding: utf-8 -*-


def type_checking_passed(reader):
    # first three bytes are 'FLV'
    return reader.read(3) == b'FLV'


def parse(reader):
    return "In flv parser.parse"
