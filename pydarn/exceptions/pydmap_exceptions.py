"""
    Author:
        Keith Kotyk
        Marina Schmidt
"""
import logging
pydarn_logger = logging.getLogger('pydarn')

class CursorError(Exception):
    """
    Raise if the cursor is not correctly set
    """
    def __init__(self,cursor, expected_value=0, mesage=''):
        self.cursor
        if message == '':
            self.message = "Error: Cursor is at {cursor} and"\
                    "it needs to be {expected}".format(cursor=cursor,
                                                       expected=expected_value)
        else:
            self.message=message
        super().__init__(self.message)
        pydarn_logger.error(self.message)


class EmptyFileError(Exception):
    """
    Raised if a file is empty
    """
    def __init__(self,filename):
        self.filename = filename
        self.message = "Error: {} is empty or"\
                " please check this is the correct file".format(filename)
        super().__init__(self.message)
        pydarn_logger.error(self.message)


class DmapDataTypeError(Exception):
    """
    Raised if the data type is not correct.
    """
    def __init__(self, filename, data_name, data_type, cursor):
        self.filename = filename
        self.message = "Error: Dmap data type {data_type} for {name}"\
                " at cursor = {cursor} does not exist in dmap data types."\
                "filename: {filename}".format(name=data_name,
                                              data_type=data_type
                                              filename=filename,
                                              cursor=cursor)
        super().__init__(self.message)
        pydarn_logger.error(self.message)


class ZeroByteError(Exception):
    """
    Raised if an element has <= 0 bytes.
        :pram filename: The file that contains the element
        :pram element_info: String containg element info.
    """
    def __init__(self,filename, element_info, cursor):
        self.filename = filename
        self.message = "Error: {filename} contains an {element} <= 0"\
                " at cursor = {cursor}.".format(filename=filename,
                                              element=element_info,
                                              cursor=cursor)
        super().__init__(self.message)
        pydarn_logger.error(self.message)


class MismatchByteError(Exception):
    """
    Raised if an element has <= 0 bytes.
        :pram filename: The file that contains the element
        :pram element_info: String containg element info.
    """
    def __init__(self, filename, element_info, cursor):
        self.filename = filename
        self.message = "Error: {filename} contains an {element}"\
                " at cursor = {cursor}.".format(filename=filename,
                                              element=element_info,
                                              cursor=cursor)
        super().__init__(self.message)
        pydarn_logger.error(self.message)


class DmapDataError(Exception):
    """Raised if there is an error in parsing of data

    """
    def __init__(self,filename, message):
        self.filename = filename
        self.message = "Error: {filename} is data,"\
                " is corrupt because: {msg}".format(filename=filename,
                                                    msg=message)
        super().__init__(self.message)
        pydarn_logger.error("DmapDataError: {} is corrupt {}".format(filename,
                                                                     message))


class CorruptDataError(Exception):
    """
    Raise when data is corrupt in the file
    """
    def __init__():
        pass
