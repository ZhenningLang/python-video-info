# -*- coding: utf-8 -*-


import os
import unittest

from parsers import asf, avi, flv, mkv, mov, mp4, rm, rmvb
from src.input import FileVideoReader
from src.type_checker import check_video_type, VideoTypeEnum

CURRENT_PATH = os.path.split(os.path.realpath(__file__))[0]

AVI_TEST_VIDEO_LOC = os.path.join(CURRENT_PATH, './test_videos/test_video.avi')
FLV_TEST_VIDEO_LOC = os.path.join(CURRENT_PATH, './test_videos/test_video.flv')
MKV_TEST_VIDEO_LOC = os.path.join(CURRENT_PATH, './test_videos/test_video.mkv')
MOV_TEST_VIDEO_LOC = os.path.join(CURRENT_PATH, './test_videos/test_video.mov')
MP4_TEST_VIDEO_LOC = os.path.join(CURRENT_PATH, './test_videos/test_video.mp4')
RM_TEST_VIDEO_LOC = os.path.join(CURRENT_PATH, './test_videos/test_video.rm')
RMVB_TEST_VIDEO_LOC = os.path.join(CURRENT_PATH, './test_videos/test_video.rmvb')
WMV_TEST_VIDEO_LOC = os.path.join(CURRENT_PATH, './test_videos/test_video.wmv')


class TypeCheckerTest(unittest.TestCase):

    def test_asf(self):
        with FileVideoReader(WMV_TEST_VIDEO_LOC) as reader:
            t = check_video_type(reader)
            self.assertEqual(t, VideoTypeEnum.ASF)

    def test_avi(self):
        with FileVideoReader(AVI_TEST_VIDEO_LOC) as reader:
            t = check_video_type(reader)
            self.assertEqual(t, VideoTypeEnum.AVI)

    def test_flv(self):
        with FileVideoReader(FLV_TEST_VIDEO_LOC) as reader:
            t = check_video_type(reader)
            self.assertEqual(t, VideoTypeEnum.FLV)

    def test_mkv(self):
        with FileVideoReader(MKV_TEST_VIDEO_LOC) as reader:
            t = check_video_type(reader)
            self.assertEqual(t, VideoTypeEnum.MKV)

    def test_mov(self):
        with FileVideoReader(MOV_TEST_VIDEO_LOC) as reader:
            t = check_video_type(reader)
            self.assertEqual(t, VideoTypeEnum.MOV)

    def test_mp4(self):
        with FileVideoReader(MP4_TEST_VIDEO_LOC) as reader:
            t = check_video_type(reader)
            self.assertEqual(t, VideoTypeEnum.MP4)

    def test_rm(self):
        with FileVideoReader(RM_TEST_VIDEO_LOC) as reader:
            t = check_video_type(reader)
            self.assertEqual(t, VideoTypeEnum.RM or VideoTypeEnum.RMVB)

    def test_rmvb(self):
        with FileVideoReader(RMVB_TEST_VIDEO_LOC) as reader:
            t = check_video_type(reader)
            self.assertEqual(t, VideoTypeEnum.RM or VideoTypeEnum.RMVB)
