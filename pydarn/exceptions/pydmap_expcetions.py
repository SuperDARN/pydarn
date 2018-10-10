"""
    Author:
        Keith Kotyk
        Marina Schmidt
"""
import logging
logger = logging.getLogger(__name__)

class EmptyFileError(Exception):
    """
    Raised if a file is empty
    """
    def __init__(self,filename):
        self.filename = filename
        self.message = "Error: {} is empty,"\
                " please check this is the correct file".format(filename)
        super().__init__(self.message)
        logging.debug("EmptyFileError: {} is empty".format(filename))


class CorruptDataError(Exception):
    """
    Raise when data is curropt in the file
    """
    def __init__():
        pass
