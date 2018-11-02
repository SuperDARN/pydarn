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
        self.message = "Error: {} is empty,"\
                " please check this is the correct file".format(filename)
        super().__init__(self.message)
        pydarn_logger.debug("EmptyFileError: {} is empty".format(filename))

class DmapDataError(Exception):
    """Raised if there is an error in parsing of data

    """
    pass


class CorruptDataError(Exception):
    """
    Raise when data is curropt in the file
    """
    def __init__():
        pass
