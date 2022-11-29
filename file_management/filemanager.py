import sys
import os
from const import const
from exception import exception

sys.path.append('../')


# maybe to use @staticmethod
def close_file(file_id):
    os.close(file_id)


def read_page(file_id, page_id) -> bytes:
    offset = page_id * const.PAGE_SIZE
    os.lseek(file_id, offset, os.SEEK_SET)
    data = os.read(file_id, const.PAGE_SIZE)
    return data


def write_page(file_id, page_id, data: bytes):
    offset = page_id * const.PAGE_SIZE
    os.lseek(file_id, offset, os.SEEK_SET)
    os.write(file_id, data)


class FileManager:
    try:
        FILE_OPEN_MODE = os.O_RDWR | os.O_BINARY
    except AttributeError as exception:
        FILE_OPEN_MODE = os.O_RDWR

    def __init__(self):
        self.path = os.getcwd() + '/data/'

    def open_file(self, filename):
        file_id = os.open(self.path + filename, self.FILE_OPEN_MODE)
        if file_id is const.FILE_OPEN_FAIL:
            raise exception.FileOpenFailException
        return file_id

    def remove_file(self, filename):
        os.remove(self.path + filename)

    def create_file(self, filename):
        open(self.path + filename, 'w').close()
