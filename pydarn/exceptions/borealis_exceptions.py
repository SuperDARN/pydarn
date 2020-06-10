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
        self.file_type = file_type
        self.filename = filename
        self.message = "{file_type} is not a Borealis file format or has"\
            " not been implemented yet. {filename} was not used. Please check"\
            " the spelling of {file_type}.".format(file_type=self.file_type,
                                                   filename=self.filename)
        pydarn_logger.error(self.message)
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
            self.record_name = kwargs['record_name']
            error_source = 'record {} of file {}'.format(kwargs['record_name'],
                                                         filename)
        else:
            error_source = 'file {}'.format(filename)

        self.filename = filename
        self.fields = fields
        self.message = "The following fields in {source} are missing:"\
            " {fields}".format(source=error_source,
                               fields=self.fields)
        pydarn_logger.error(self.message)
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
            self.record_name = kwargs['record_name']
            error_source = 'record {} of file {}'.format(kwargs['record_name'],
                                                         filename)
        else:
            error_source = 'file {}'.format(filename)

        self.fields = fields
        self.message = "The following fields in {source} are not allowed:"\
            " {fields}".format(source=error_source,
                               fields=self.fields)
        pydarn_logger.error(self.message)
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
            self.record_name = kwargs['record_name']
            error_source = 'record {} of file {}'.format(kwargs['record_name'],
                                                         filename)
        else:
            error_source = 'file {}'.format(filename)

        self.incorrect_types = incorrect_types
        self.message = "In {source}, the following parameters"\
            " are not of their given correct type:"\
            " {incorrect}".format(source=error_source,
                                  incorrect=self.incorrect_types)
        pydarn_logger.error(self.message)
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

    def __init__(self, filename: str, array_types: dict):
        self.filename = filename
        self.array_types = array_types
        self.message = "The number of records in file {filename} cannot "\
            "be determined due to varying shapes of arrays for the unshared "\
            "parameters. All arrays of the unshared parameters should "\
            "have the same first dimension size equal to number of records: "\
            "{array_types}".format(filename=self.filename,
                                   array_types=self.array_types)
        pydarn_logger.error(self.message)
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

    def __init__(self, dmap_filename: str, origin_filetype: str,
                 allowed_types: dict):
        self.message = "Records destined to be converted and written to "\
                       "{dmap_filename} cannot be converted from origin "\
                       "filetype {origin_filetype} to a dmap "\
                       "filetype because origin filetype does not map "\
                       "to any currently available dmap filetypes: "\
                       "{allowed_types}".format(dmap_filename=dmap_filename,
                                                origin_filetype=origin_filetype,
                                                allowed_types=allowed_types)
        pydarn_logger.error(self.message)
        Exception.__init__(self, self.message)


class BorealisConvert2IqdatError(Exception):
    """
    Raised when the file cannot be converted to SDARN DMap iqdat format.

    Parameters
    ----------
    error_str: str
        explanation for why the file cannot be converted to SDARN iqdat.

    Attributes
    ----------
    message: str
        The message to display with the error
    """

    def __init__(self, error_str: str):
        self.message = "The file cannot be converted to SDARN DMap iqdat due"\
            " to the following error: {error_str}"\
            "".format(error_str=error_str)
        pydarn_logger.error(self.message)
        Exception.__init__(self, self.message)


class BorealisConvert2RawacfError(Exception):
    """
    Raised when the file cannot be converted to SDARN DMap rawacf format.

    Parameters
    ----------
    error_str: str
        explanation for why the file cannot be converted to SDARN rawacf.

    Attributes
    ----------
    message: str
        The message to display with the error
    """

    def __init__(self, error_str: str):
        self.message = "The file cannot be converted to SDARN DMap rawacf "\
            "due to the following error: {error_str}"\
            "".format(error_str=error_str)
        pydarn_logger.error(self.message)
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
        pydarn_logger.error(self.message)
        Exception.__init__(self, self.message)


class BorealisStructureError(Exception):
    """
    Raised when the file has major structural issues and may not
    be the correct style type (arrays vs records).

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
        self.message = "Structural errors found. You may be"\
                " attempting to use the file as the wrong"\
                " structure ('site' or 'array'"\
                " supported). Please check if you are interested"\
                " in records or arrays."\
                "{error_str}".format(error_str=error_str)
        pydarn_logger.error(self.message)
        Exception.__init__(self, self.message)


class ConvertFileOverWriteError(Exception):
    """
    Trying to write to a file that also reading.

    Parameters
    ----------
    filename: str
        name of the file trying to both read and write from/to

    Attributes
    ----------
    message: str
        The message to display with the error
    """

    def __init__(self, filename: str):
        self.message = "Writing to {filename} not permitted while reading"\
            " the file as source.".format(filename=filename)
        pydarn_logger.error(self.message)
        Exception.__init__(self, self.message)


class BorealisVersionError(Exception):
    """
    The Borealis software version of the file is not found in the current
    list of versions pydarn can read, which is found in the borealis_formats
    module.

    Parameters
    ----------
    filename: str
        File attempted to read/write
    file_version: str
        SuperDARN Borealis software version that is not implemented in
        pydarn or is incorrect

    Attributes
    ----------
    message: str
        The message to display with the error
    """

    def __init__(self, filename: str, file_version: str):
        self.file_version = file_version
        self.filename = filename
        self.message = "Version {file_version} from the borealis_git_hash is not"\
            " a recognized Borealis version or has not been implemented yet."\
            " {filename} was not used.".format(file_version=self.file_version,
                                   filename=self.filename)
        pydarn_logger.error(self.message)
        Exception.__init__(self, self.message)
