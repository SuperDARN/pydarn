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
ConvertFileOverWriteError

See Also
--------
BorealisRawacf
BorealisBfiq
BorealisAntennasIq
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
        self.message = "{file_type} is not a Borealis file format or has"\
            " not been implemented yet. {filename} was not used. Please check"\
            " the spelling of {file_type}.".format(file_type=file_type,
                                   filename=filename)
        Exception.__init__(self, self.message)


class BorealisFieldMissingError(Exception):
    """
    Raised when a required data field is missing.

    Raised when a field from the filetype's fields is not present.

    Parameters
    ----------
    filename: str
        name of the file with the issue
    fields: set
        set of fields that are missing from the file
    record_name: int
        record name of the problem record

    Attributes
    ----------
    message: str
        The message to display with the error
    """

    def __init__(self, filename: str, fields: set, **kwargs):
        if 'record_name' in kwargs.keys():
            error_source = 'record {} of file {}'.format(kwargs['record_name'],
                                                         filename)
        else:
            error_source = 'file {}'.format(filename)

        self.message = "The following fields in {source} are missing:"\
            " {fields}".format(source=error_source,
                               fields=fields)
        Exception.__init__(self, self.message)


class BorealisExtraFieldError(Exception):
    """
    Raised on extra unknown field in the data.

    Occurs when an extra field is in the data that is not included in 
    the Borealis format file type fields

    Parameters
    ----------
    filename: str
        name of the file with the issue
    fields: set
        set of fields that are extra in the file
    record_name: int
        record name of the problem record

    Attributes
    ----------
    message: str
        The message to display with the error
    """

    def __init__(self, filename: str, fields: set, **kwargs):
        if 'record_name' in kwargs.keys():
            error_source = 'record {} of file {}'.format(kwargs['record_name'],
                                                         filename)
        else:
            error_source = 'file {}'.format(filename)

        self.message = "The following fields in {source} are not allowed:"\
            " {fields}".format(source=error_source,
                               fields=fields)
        Exception.__init__(self, self.message)


class BorealisDataFormatTypeError(Exception):
    """
    Raised on incorrect format of a data field.

    Occurs when a data type does not match the Borealis format file type's
    data types

    Parameters
    ----------
    filename: str
        name of the file with the issue
    incorrect_types: dict
        dict of field : correct type for all fields that were incorrect
    record_name: int
        record name of the problem record

    Attributes
    ----------
    message: str
        The message to display with the error
    """

    def __init__(self, filename: str, incorrect_types: dict, **kwargs):
        if 'record_name' in kwargs.keys():
            error_source = 'record {} of file {}'.format(kwargs['record_name'],
                                                         filename)
        else:
            error_source = 'file {}'.format(filename)

        self.message = "In {source}, the following parameters"\
            " are not of their given correct type:"\
            " {incorrect}".format(source=error_source,
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
        desired SuperDARN DMap type, ex. iqdat.

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
    Raised when the file cannot be converted to DARN DMap iqdat format.

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
    Raised when the file cannot be converted to DARN DMap rawacf format.

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
            "accounted for in DARN rawacf format: {error_str}"\
            "".format(error_str=error_str)
        Exception.__init__(self, self.message)


class BorealisRestructureError(Exception):
    """
    Raised when the file cannot be restructured to or from site/array 
    styles. 

    Parameters
    ----------
    error_str: str
        explanation for why the file cannot be restructured.
    
    Attributes
    ----------
    message: str
        The message to display with the error

    See Also
    --------
    restructure_borealis.py
    """

    def __init__(self, error_str: str):
        self.message = "The file cannot be restructured due to the "\
            " following error: {error_str}"\
            "".format(error_str=error_str)
        Exception.__init__(self, self.message)


class ConvertFileOverWriteError(Exception):
    """
    Trying to write to a file that also wish to read. 

    Parameters
    ----------
    filename: str
        name of the file associated to the wrong SuperDARN Borealis file type

    Attributes
    ----------
    message: str
        The message to display with the error
    """

    def __init__(self, filename: str, file_type: str):
        self.message = "Writing to {filename} not permitted while reading"\
            " as source to convert".format(filename=filename)
        Exception.__init__(self, self.message)


class BorealisNumberOfRecordsError(Exception):
    """
    Raised when the file is array structured and does not 
    have a consistent number of records across the unshared
    parameters (arrays).

    Parameters
    ----------
    array_types: dict
        dictionary of unshared parameter keys to 
        the first dimension of their array (indicating the number
        of records)
    
    Attributes
    ----------
    message: str
        The message to display with the error

    See Also
    --------
    restructure_borealis.py
    """

    def __init__(self, array_types: dict):
        self.message = "The number of records in the file cannot "\
            "be determined due to varying sizes of arrays: {array_types}"\
            "".format(array_types=array_types)
        Exception.__init__(self, self.message)
