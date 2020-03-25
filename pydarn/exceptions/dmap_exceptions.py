# Copyright (C) SuperDARN Canada, University of Saskatchewan
# Authors: Keith Kotyk and Marina Schmidt
import logging
pydarn_logger = logging.getLogger('pydarn')


class CursorError(Exception):
    """
    Raise if the cursor is not correctly set

    Parameter
    ---------
    cursor : int
        Current position in the data buffer
    expected_value : int
        What you expected the value of the cursor to be.
        Default 0.
    message : str
        Another type of message that might give more information
        on the cursor error.
        Default empty.
    """
    def __init__(self, cursor: int, expected_value: int = 0,
                 rec_num: int = 0, message=''):
        self.cursor = cursor
        if message == '':
            self.message = "Error: Cursor is at {cursor} and"\
                    "it needs to be {expected}. Failed at record {rec}"\
                    "".format(cursor=cursor, expected=expected_value,
                              rec=rec_num)
        else:
            self.message = message
        super().__init__(self.message)
        pydarn_logger.error(self.message)


class EmptyFileError(Exception):
    """
    Raised if a file is empty.

    Parameter
    --------
    filename : str
        The name of the file that is empty.
    """
    def __init__(self, filename: str):
        self.filename = filename
        self.message = "Error: {} is empty or"\
            " please check this is the correct file".format(filename)
        super().__init__(self.message)
        pydarn_logger.error(self.message)


class DmapCharError(Exception):
    """
    Raised if a char type is str

    Parameter
    --------
    filename : str
        name of the file that the DMAP data is coming from.
    data_name : str
        parameter field name in the DMAP record
    rec_num : int
        Record number the error was raised at
    """
    def __init__(self, data_name: str, rec_num: int):
        self.data_name = data_name,
        self.rec_num = rec_num
        self.message = "Error: For field {field} at record number"\
            " {rec_num} is"\
            " a string type trying to be written in as a char."\
            " DMAP treats char as int8. Please revise this field"\
            " type".format(field=self.data_name,
                           rec_num=self.rec_num)
        super().__init__(self.message)
        pydarn_logger.error(self.message)


class DmapDataTypeError(Exception):
    """
    Raised if the data type is not correct.

    Parameter
    ---------
    filename : str
        name of the file that the DMAP data is coming from.
    data_name : str
        parameter field name in the DMAP record
    data_type : str
        data type of the field name.
    cursor : int
        current position in the data buffer
    """
    def __init__(self, filename: str, data_name: str,
                 data_type: str, rec_num: int):
        self.filename = filename
        self.message = "Error: Dmap data type {data_type} for {name}"\
            " at record {rec} does not exist in dmap data types."\
            " Filename: {filename}".format(name=data_name,
                                           data_type=data_type,
                                           filename=filename,
                                           rec=rec_num)
        super().__init__(self.message)
        pydarn_logger.error(self.message)


class NegativeByteError(Exception):
    """
    Raised if an element has < 0 bytes.

    Parameter
    ---------
    filename : str
        The file name of the DMAP data
    element_info : str
        String containing element name.
    """
    def __init__(self, filename: str, element_info: str, rec_num: int):
        self.filename = filename
        self.message = "Error: {filename} contains an {element} < 0"\
            " at record {rec}.".format(filename=filename,
                                       element=element_info,
                                       rec=rec_num)
        super().__init__(self.message)
        pydarn_logger.error(self.message)


class ZeroByteError(Exception):
    """
    Raised if an element has == 0 bytes.

    Parameter
    ---------
    filename : str
        Name of the file that contains the DMAP data
    element_info : str
        String containing element name.
    cursor : int
        Current position in the dmap buffer
    """
    def __init__(self, filename: str, element_info: str, rec_num: int):
        self.filename = filename
        self.message = "Error: {filename} contains an {element} == 0"\
            " at record {rec}.".format(filename=filename,
                                       element=element_info,
                                       rec=rec_num)
        super().__init__(self.message)
        pydarn_logger.error(self.message)


class MismatchByteError(Exception):
    """
    Raised if an element is > another element.

    Parameter
    ---------
    filename : str
        Name of the file that contains the DMAP data
    element_info : str
        String containing element info on the two elements being compared.
    cursor : int
        Current position in the dmap buffer.
    """
    def __init__(self, filename: str, element_info: str, rec_num: int):
        self.filename = filename
        self.rec_num = rec_num
        self.message = "Error: {filename} contains an {element}"\
            " at record = {rec}.".format(filename=filename,
                                         element=element_info,
                                         rec=rec_num)
        super().__init__(self.message)
        pydarn_logger.error(self.message)


# TODO: may need to delete later if not used in DmapWrite?
class DmapDataError(Exception):
    """Raised if there is an error in parsing of data

    Parameter
    ---------
    filename : str
        Name of the file that contains the DMAP data
    message : str
        Message containing information on the Error
    """
    def __init__(self, filename: str, message: str):
        self.filename = filename
        self.message = " The following error for {filename} was raised: "\
            "{msg}".format(filename=self.filename,
                           msg=message)
        super().__init__(self.message)
        pydarn_logger.error("DmapDataError: {}".format(self.message))


class DmapTypeError(Exception):
    """
    Raised if there mismatch between DMAP data type

    Parameters
    ----------
    filename : str
        name of the file associated to the error
    data_type : str
        the data that does not match what DMAP can read
    rec_num : int
        the record number associated to the error
    """
    def __init__(self, filename: str, data_type: str, rec_num: int):
        self.filename = filename
        self.data_type = data_type
        self.rec_num = rec_num
        self.message = "Error: {data_type} does not match the DMAP data type"\
            " structures: DmapScalar, DmapArray."\
            " Please make sure you have the correct"\
            " Data Structure. Failed at record "\
            "{rec}".format(data_type=self.data_type,
                           filename=self.filename,
                           rec=self.rec_num)
        Exception.__init__(self, self.message)
        pydarn_logger.error("DataTypeError: {}".format(self.message))


class FilenameRequiredError(Exception):
    """
    Raised if a filename is not provided when needed for the procedure
    """
    def __init__(self):
        self.message = "Error: Filename is required"
        Exception.__init__(self, self.message)
