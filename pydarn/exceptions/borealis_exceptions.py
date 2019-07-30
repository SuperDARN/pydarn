# Copyright 2019 SuperDARN Canada, University of Saskatchewan
# Author: Marci Detwiller
"""
This file contains several exception classes used by the pydarn io borealis
module. 

Classes
-------
BorealisFileTypeError
BorealisFieldMissingError
BorealisExtraFieldError
BorealisDataFormatTypeError
BorealisConversionTypesError
BorealisConvert2IqdatError
BorealisConvert2RawacfError

See Also
--------
BorealisRawacf
BorealisBfiq
BorealisOutputPtrsIq
BorealisRawrf

"""

import logging
pydarn_logger = logging.getLogger('pydarn')


class BorealisFileTypeError(Exception):
    """
    SuperDARN Borealis file type is not implemented or an incorrect type

    Parameters
    ----------
    filename: str
        name of the file associated to the wrong SuperDARN Borealis file type
    file_type: str
        SuperDARN Borealis file type that is not implement or correct

    Attributes
    ----------
    message: str
        The message to display with the error
    """

    def __init__(self, filename: str, file_type: str):
        self.message = "{file_type} is not a Borealis file format type."\
            "{filename} was not used. Please check that the spelling of"\
            " the file type is correct and that the file type has been"\
            " implemented.".format(file_type=file_type,
                                   filename=filename)
        Exception.__init__(self, self.message)


class BorealisFieldMissingError(Exception):
    """
    Raised when a required data field is missing.

    Raised when a field from the filetype's fields is not present.

    Parameters
    ----------
    record_name: int
        record name of the problem record
    fields: set
        set of fields that are missing from the record

    Attributes
    ----------
    message: str
        The message to display with the error
    """

    def __init__(self, record_name: int, fields: set):
        self.message = "The following fields in record {num} are missing:"\
            " {fields}".format(num=record_name,
                               fields=fields)
        Exception.__init__(self, self.message)


class BorealisExtraFieldError(Exception):
    """
    Raised on extra unknown field in the data.

    Occurs when an extra field is in the data that is not included in 
    the Borealis format file type fields

    Parameters
    ----------
    record_name: int
        record name of the problem record
    fields: set
        set of fields that are missing from the record

    Attributes
    ----------
    message: str
        The message to display with the error
    """

    def __init__(self, record_name: int, fields: set):
        self.message = "The following fields in record {num} are not allowed:"\
            " {fields}".format(num=record_name,
                               fields=fields)
        Exception.__init__(self, self.message)


class BorealisDataFormatTypeError(Exception):
    """
    Raised on incorrect format of a data field.

    Occurs when a data type does not match the Borealis format file type's
    data types

    Parameters
    ----------
    incorrect_type: dict
        set of the fields that have incorrect types
    record_name: int
        record name of the problem record

    Attributes
    ----------
    message: str
        The message to display with the error
    """

    def __init__(self, incorrect_types: set, record_name: int):
        self.message = "In record {num}, the following parameters"\
            " need to be the data type:"\
            " {incorrect}".format(num=record_name,
                                  incorrect=incorrect_types)
        Exception.__init__(self, self.message)


class BorealisConversionTypesError(Exception):
    """
    SuperDARN Borealis filetype cannot be converted to desired type.

    Parameters
    ----------
    filename: str
        name of the file attempting to convert
    origin_filetype: str
        Borealis origin filetype, ex. bfiq.
    dmap_filetype: str
        desired SuperDARN dmap type, ex. iqdat.

    Attributes
    ----------
    message: str
        The message to display with the error
    """

    def __init__(self, filename: str, origin_filetype: str, 
                 dmap_filetype: str):
        self.message = "{filename} cannot be converted from its "\
                       "origin_filetype {origin_filetype} to  dmap "\
                       " filetype {dmap_filetype} because the types are not"\
                       "compatible or are currently not supported."\
                       "".format(filename=filename,
                                 origin_filetype=origin_filetype, 
                                 dmap_filetype=dmap_filetype)
        Exception.__init__(self, self.message)


class BorealisConvert2IqdatError(Exception):
    """
    Raised when the file cannot be converted to DARN dmap iqdat format.

    Parameters
    ----------
    error_str: str
        explanation for why the file cannot be converted to DARN iqdat.

    Attributes
    ----------
    message: str
        The message to display with the error
    """

    def __init__(self, error_str: str):
        self.message = "The file cannot be converted to DARN iqdat due to "\
            "the following error which indicates increased complexity not "\
            "accounted for in DARN iqdat format: {error_str}"\
            "".format(error_str=error_str)
        Exception.__init__(self, self.message)


class BorealisConvert2RawacfError(Exception):
    """
    Raised when the file cannot be converted to DARN dmap rawacf format.

    Parameters
    ----------
    error_str: str
        explanation for why the file cannot be converted to DARN rawacf.
    
    Attributes
    ----------
    message: str
        The message to display with the error
    """

    def __init__(self, error_str: str):
        self.message = "The file cannot be converted to DARN rawacf due to "\
            "the following error which indicates increased complexity not "\
            "accounted for in DARN iqdat format: {error_str}"\
            "".format(error_str=error_str)
        Exception.__init__(self, self.message)
