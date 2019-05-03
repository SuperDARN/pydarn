# Author: Marci Detwiller
import logging
pydarn_logger = logging.getLogger('pydarn')


class BorealisConversionTypesError(Exception):
    """
    SuperDARN Borealis filetype cannot be converted to desired type.

    Parameter
    --------
    filename : str
        name of the file attempting to convert
    origin_filetype: str
        Borealis origin filetype, ex. bfiq.
    dmap_filetype : str
        desired SuperDARN legacy dmap type, ex. iqdat.
    """
    def __init__(self, filename: str, origin_filetype: str, dmap_filetype: str):
        self.filename = filename
        self.origin_filetype = origin_filetype
        self.dmap_filetype = dmap_filetype
        self.message = "Error: {filename} cannot be converted from its origin_filetype "\
                       "{origin_filetype} to legacy dmap filetype {dmap_filetype} because the "\
                       "types are not compatible or currently not supported.".format(filename=self.filename,
                        origin_filetype=self.origin_filetype, dmap_filetype=self.dmap_filetype)


class BorealisFileTypeError(Exception):
    """
    SuperDARN Borealis file type that is not implemented or an incorrect type

    Parameter
    --------
    filename : str
        name of the file associated to the wrong SuperDARN Borealis file type
    file_type : str
        SuperDARN Borealis file type that is not implement or correct
    """
    def __init__(self, filename: str, file_type: str):
        self.filename = filename
        self.file_type = file_type
        self.message = "Error: {file_type} is not a Borealis file format type."\
            "{filename} was not read. Please check that the spelling of"\
            " the file type is correct and that the file type has been"\
            " implemented.".format(file_type=self.file_type,
                                   filename=self.filename)


class BorealisFieldMissingError(Exception):
    """
    Raised when a field is missing from data that is required of the Borealis
    file type fields

    Parameter
    ---------
    record_name : int
        record name of the problem record
    fields : set
        set of fields that are missing from the record
    """
    def __init__(self, record_name: int, fields: set):
        self.record_name = record_name
        self.fields = fields
        self.message = "Error: The following fields in record {num} are missing:"\
            " {fields}".format(num=self.record_name,
                               fields=self.fields)

class BorealisExtraFieldError(Exception):
    """
    Raised when a extra field is in the data that is not in the Borealis file
    type fields

    Parameter
    ---------
    record_name : int
        record name of the problem record
    fields : set
        set of fields that are missing from the record
    """
    def __init__(self, record_name: int, fields: set):
        self.record_name = record_name
        self.fields = fields
        self.message = "Error: The following fields in record {num} are not allowed:"\
            " {fields}".format(num=self.record_name,
                               fields=self.fields)



class BorealisDataFormatTypeError(Exception):
    """
    Raised when a data format type does not match the Borealis file type
    data types

    Parameter
    --------
    incorrect_type : dict
        set of the fields that have incorrect types
    record_name : int
        record name of the problem record
    """
    def __init__(self, incorrect_types: set, record_name: int):
        self.incorrect_params = incorrect_types
        self.record_name = record_name
        self.message = "Error: In record {num}, the following parameters"\
            " need to be the data type:"\
            " {incorrect}".format(num=self.record_name,
                                  incorrect=self.incorrect_params)


