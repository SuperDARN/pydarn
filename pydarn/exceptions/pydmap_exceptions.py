"""
    Author:
        Keith Kotyk
        Marina Schmidt
"""
import logging
pydarn_logger = logging.getLogger('pydarn')

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
