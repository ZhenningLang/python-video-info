# -*- coding: utf-8 -*-


def type_checking_passed(reader):
    # first foure bytes are '.RMF'
    return reader.read(4) == b'.RMF'


def parse(reader):
    return "In rmvb or rm parser.parse"
