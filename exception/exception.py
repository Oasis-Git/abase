class FileOpenFailException(Exception):
    """
    for file.open == -1
    """


class FileCloseFail(Exception):
    """
    for closing a file with a not found file_id
    """


class ValidPageError(Exception):
    """
    valid page does not have empty slot
    """


class SameKeyError(Exception):
    """
    same key in index
    """
