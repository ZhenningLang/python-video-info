# -*- coding: utf-8 -*-

"""
Video Readers

Open a file data stream with 'refresh' operation based on memory buffer.

The 'refresh' operation performs like re-open the data stream.
However in this implement, after 'refresh' data is read from buffer.

This is especially useful when the video is located at remote host, for
the reason that a new request for remote resources is a bit 'expensive'.

This 'refresh' operation is mainly designed for a connection between
video type-checking and reading video meta data.
After type-checking the pointer to the data stream has an offset, and we
neither want to pass both the stream and offset between two modules，
nor 'really' re-open the data stream.

"""

import os

import requests


__all__ = ('FileVideoReader', 'RemoteFileReader')

MAX_BUFFER_LENGTH = 1024 * 1024  # 1 Mb


class VideoReader:

    def __init__(self, video_loc: str, max_buffer_length: int=MAX_BUFFER_LENGTH):
        self.video_loc = video_loc
        self.max_buffer_length = max_buffer_length
        self.stream = None  # self.stream object should support read and close
        self._open_stream()
        assert hasattr(self.stream, 'read') and callable(self.stream.read), "self.stream does not has 'read' method"
        assert hasattr(self.stream, 'close') and callable(self.stream.close), "self.stream does not has 'close' method"
        self._buffer = bytearray()
        self._buffer_pointer = -1

    def _open_stream(self):
        """Initial self.stream"""
        raise NotImplementedError()

    def _is_buffer_full(self):
        return len(self._buffer) > self.max_buffer_length

    def read(self, num_of_byte: int=1) -> bytes:
        """Read and return num_of_byte bytes of the video"""
        if self._is_buffer_full():
            return self.stream.read(num_of_byte)

        buffer_len = len(self._buffer)
        if buffer_len == self._buffer_pointer + 1:  # all real read
            data = self.stream.read(num_of_byte)
            self._buffer += data
            self._buffer_pointer = self._buffer_pointer + num_of_byte
            return data
        elif buffer_len - (self._buffer_pointer + 1) >= num_of_byte:  # all from buffer
            self._buffer_pointer += num_of_byte
            return bytes(self._buffer[self._buffer_pointer - num_of_byte + 1: self._buffer_pointer + 1])
        elif buffer_len - (self._buffer_pointer + 1) < num_of_byte:  # one part from buffer and the other real read
            data_buffer_part = self._buffer[self._buffer_pointer + 1:]
            remained_not_read_num = num_of_byte - (buffer_len - (self._buffer_pointer + 1))
            data_read_part = self.stream.read(remained_not_read_num)
            self._buffer += data_read_part
            self._buffer_pointer += num_of_byte
            return bytes(data_buffer_part + data_read_part)

    def refresh(self) -> None:
        """Move the reader 'pointer' back to the head"""
        if self._is_buffer_full():
            self.stream.close()
            self._open_stream()  # re-initial self.stream
            self._buffer = bytearray()
        self._buffer_pointer = -1

    def close(self):
        self.stream.close()
        self._buffer = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class StreamAdapter:

    def read(self, num_of_byte: int=1) -> bytes:
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()


class FileVideoReader(VideoReader):

    def __init__(self, video_loc: str, max_buffer_length: int=MAX_BUFFER_LENGTH):
        if not os.path.exists(video_loc) or not os.path.getsize(video_loc) > 0:
            raise Exception('File {} not exist.'.format(video_loc))
        super().__init__(video_loc, max_buffer_length)

    def _open_stream(self):
        self.stream = open(self.video_loc, 'rb')


FAKE_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'UTF-8,*;q=0.5',
    'Accept-Encoding': 'gzip,deflate,sdch',
    'Accept-Language': 'en-US,en;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0'
}


class RemoteFileStreamAdapter(StreamAdapter):

    def __init__(self, response):
        self.response = response
        self.iter = response.iter_content(chunk_size=1, decode_unicode=False)

    def read(self, num_of_byte: int = 1) -> bytes:
        b_list = []
        for _ in range(num_of_byte):
            b_list.append(next(self.iter))
        return b''.join(b_list)

    def close(self):
        self.response.close()


class RemoteFileReader(VideoReader):

    def __init__(self, video_loc: str, max_buffer_length: int=MAX_BUFFER_LENGTH):
        super().__init__(video_loc, max_buffer_length)

    def _open_stream(self):
        response = requests.get(self.video_loc, headers=FAKE_HEADERS, stream=True, timeout=10)
        if response.status_code != 200:
            raise Exception(
                'Can not open the remote video, _response status code: %s' % response.status_code)
        self.stream = RemoteFileStreamAdapter(response)
