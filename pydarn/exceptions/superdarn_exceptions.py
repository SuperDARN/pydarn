# Copyright (C) SuperDARN Canada, University of Saskatchewan
# Authors: Keith Kotyk and Marina Schmidt
import logging
pydarn_logger = logging.getLogger('pydarn')


class SuperDARNFileTypeError(Exception):
    """
    SuperDARN file type that is not implement or incorrect

    Parameter
    --------
    filename : str
        name of the file associated to the wrong SuperDARN file type
    file_type : str
        SuperDARN file type that is not implement or correct
    """
    def __init__(self, filename: str, file_type: str):
        self.filename = filename
        self.file_type = file_type
        self.message = "Error: {file_type} is not a SuperDARN file "\
            "format type."\
            "{filename} was not created. Please check the spelling of"\
            " the file type is correct or is"\
            " implemented.".format(file_type=self.file_type,
                                   filename=self.filename)
        super().__init__(self.message)
        pydarn_logger.error(self.message)


class SuperDARNFieldMissingError(Exception):
    """
    Raised when a field is missing from data that is required of the SuperDARN
    file type fields

    Parameter
    ---------
    record_num : int
        The record number associated to the error
    fields : set
        set of fields that are missing from the record
    """
    def __init__(self, record_num: int, fields: set):
        self.record_number = record_num
        self.fields = fields
        self.message = "Error: The following fields in record {num} "\
            "are missing:"\
            " {fields}".format(num=self.record_number,
                               fields=self.fields)
        super().__init__(self.message)
        pydarn_logger.error(self.message)


class SuperDARNExtraFieldError(Exception):
    """
    Raised when a extra field is in the data that is not in the SuperDARN file
    type fields

    Parameter
    ---------
    record_num : int
        record number associated to the error
    fields : set
        set of the fields that are extra in the record
    """
    def __init__(self, record_num, fields):
        self.record_number = record_num
        self.fields = fields
        self.message = "Error: The following fields in record {num} are"\
            " not allowed:"\
            " {fields}".format(num=self.record_number,
                               fields=self.fields)
        super().__init__(self.message)
        pydarn_logger.error(self.message)


class SuperDARNDataFormatTypeError(Exception):
    """
    Raised when a data format type does not match the SuperDARN file type
    data types

    Parameter
    --------
    incorrect_type : set
        set of the fields that have incorrect types
    record_num : int
        record number of the associated to the error
    """
    def __init__(self, incorrect_types: set, record_num: int):
        self.incorrect_params = incorrect_types
        self.record_number = record_num
        self.message = "Error: In record {num}, following parameters"\
            " need to be the data type:"\
            " {incorrect}".format(num=self.record_number,
                                  incorrect=self.incorrect_params)
        super().__init__(self.message)
        pydarn_logger.error(self.message)
