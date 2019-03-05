# -*- coding: utf-8 -*-

import os
import unittest

from src.input import FileVideoReader, RemoteFileReader

CURRENT_PATH = os.path.split(os.path.realpath(__file__))[0]

MP4_TEST_VIDEO_LOC = os.path.join(CURRENT_PATH, './test_videos/test_video.mp4')
MP4_TEST_VIDEO_URL = 'https://sample-videos.com/video123/mp4/480/big_buck_bunny_480p_10mb.mp4'


# noinspection PyMethodMayBeStatic
class InputUnitTest(unittest.TestCase):

    def test_file_video_reader_read(self):
        with FileVideoReader(MP4_TEST_VIDEO_LOC) as file_reader:
            self.assertEqual(file_reader.read(), b'\x00')
            self.assertEqual(file_reader.read(1), b'\x00')
            self.assertEqual(file_reader.read(2), b'\x00\x20')
            self.assertEqual(file_reader.read(3), b'\x66\x74\x79')

    def test_file_video_reader_refresh(self):
        with FileVideoReader(MP4_TEST_VIDEO_LOC) as file_reader:
            self.assertEqual(file_reader.read(3), b'\x00\x00\x00')
            file_reader.refresh()
            self.assertEqual(file_reader.read(2), b'\x00\x00')
            self.assertEqual(file_reader.read(3), b'\x00\x20\x66')
            file_reader.refresh()
            self.assertEqual(file_reader.read(5), b'\x00\x00\x00\x20\x66')
            self.assertEqual(file_reader.read(3), b'\x74\x79\x70')

    def test_file_video_reader_buffer_overflow(self):
        with FileVideoReader(MP4_TEST_VIDEO_LOC, max_buffer_length=5) as file_reader:
            self.assertEqual(file_reader.read(3), b'\x00\x00\x00')
            file_reader.refresh()
            self.assertEqual(file_reader.read(2), b'\x00\x00')
            self.assertEqual(file_reader.read(3), b'\x00\x20\x66')
            file_reader.refresh()
            self.assertEqual(file_reader.read(3), b'\x00\x00\x00')
            self.assertEqual(file_reader.read(3), b'\x20\x66\x74')
            file_reader.refresh()
            self.assertEqual(file_reader.read(3), b'\x00\x00\x00')
            file_reader.refresh()
            self.assertEqual(file_reader.read(2), b'\x00\x00')
            file_reader.refresh()

    def test_remote_video_reader_read(self):
        with RemoteFileReader(MP4_TEST_VIDEO_URL) as file_reader:
            self.assertEqual(file_reader.read(), b'\x00')
            self.assertEqual(file_reader.read(1), b'\x00')
            self.assertEqual(file_reader.read(2), b'\x00\x20')
            self.assertEqual(file_reader.read(3), b'\x66\x74\x79')

    def test_remote_video_reader_refresh(self):
        with RemoteFileReader(MP4_TEST_VIDEO_URL) as file_reader:
            self.assertEqual(file_reader.read(3), b'\x00\x00\x00')
            file_reader.refresh()
            self.assertEqual(file_reader.read(2), b'\x00\x00')
            self.assertEqual(file_reader.read(3), b'\x00\x20\x66')
            file_reader.refresh()
            self.assertEqual(file_reader.read(5), b'\x00\x00\x00\x20\x66')
            self.assertEqual(file_reader.read(3), b'\x74\x79\x70')

    def test_remote_video_reader_buffer_overflow(self):
        with RemoteFileReader(MP4_TEST_VIDEO_URL, max_buffer_length=5) as file_reader:
            self.assertEqual(file_reader.read(3), b'\x00\x00\x00')
            file_reader.refresh()
            self.assertEqual(file_reader.read(2), b'\x00\x00')
            self.assertEqual(file_reader.read(3), b'\x00\x20\x66')
            file_reader.refresh()
            self.assertEqual(file_reader.read(3), b'\x00\x00\x00')
            self.assertEqual(file_reader.read(3), b'\x20\x66\x74')
            file_reader.refresh()
            self.assertEqual(file_reader.read(3), b'\x00\x00\x00')
            file_reader.refresh()
            self.assertEqual(file_reader.read(2), b'\x00\x00')
            file_reader.refresh()

    def test_remote_video_reader_large_trunk(self):
        with RemoteFileReader(MP4_TEST_VIDEO_URL) as file_reader:
            print(file_reader.read(10000))
