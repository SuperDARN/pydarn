# Copyright 2019 SuperDARN Canada, University of Saskatchewan
# Author: Marci Detwiller
"""
This file contains a utility class for Borealis file type 
checks. 

Classes
-------
BorealisUtilities: utilites class that contains static methods for
SuperDARN Borealis file type checking

Exceptions
----------
BorealisFileTypeError
BorealisFieldMissingError
BorealisExtraFieldError
BorealisDataFormatTypeError
BorealisConversionTypesError
BorealisConvert2IqdatError
BorealisConvert2RawacfError
ConvertFileOverWriteError
BorealisNumberOfRecordsError

Notes
-----
BorealisConvert makes use of DarnWrite to write to SuperDARN file types

See Also
--------

For more information on Borealis data files and how they convert to dmap,
see: https://borealis.readthedocs.io/en/latest/ 

"""
import deepdish as dd
import h5py
import logging
import math
import numpy as np
import os

from collections import OrderedDict
from datetime import datetime
from typing import Union, List

from pydarn import borealis_exceptions, DarnWrite, borealis_formats
from pydarn.utils.conversions import dict2dmap
import restructure_borealis

pydarn_log = logging.getLogger('pydarn')


class BorealisUtilities():
    """
    Utility class containing static methods used by other classes.

    Contains static methods that do dictionary set calculations 
    used for determining if there is any missing or extra
    fields in Borealis file types. Also does data format type checks
    for Borealis file types.

    Static Methods
    --------------
    set_diff(dict1, dict2)
        Returns a set of the difference between dict1 and dict2 keys or the 
        elements of the dict1 and dict2 sets/lists
    dict_list2set(dict_list)
        Converts a list of dictionaries to a set containing their keys
    missing_field_check(file_struct_list, record, record_name)
        Checks if there is any missing fields in the record from
        a list of possible file fields
    extra_field_check(file_struct_list, record, record_name)
        Checks if there is any extra fields in the record from
        a list of possible file fields
    incorrect_types_check(file_struct_list, record_name)
        Checks if there is any incorrect types in the record from
        a list of possible file fields and their data type formats
    """

    @staticmethod
    def set_diff(dict1: Union[dict, set, list],
                      dict2: Union[dict, set, list]) -> set:
        """
        Determines the difference in the key set from the
        first dictionary to the second dictionary.
        ex) Let A = {a, b, c} and B = {d, a, b}
        Then A - B = {c}

        Parameters
        ----------
        dict1: dict or set
            dictionary or set to subtract from
        dict2: dict or set
            dictionary or set subtracting from dict1

        Returns
        -------
        dict_keys: set
            difference between dict1 and dict2 keys or the sets/lists
        """
        diff_keys = set(dict1) - set(dict2)
        return diff_keys

    @staticmethod
    def dict_list2set(dict_list: List[dict]) -> set:
        """
        Converts a list of dictionaries to list of sets

        Parameters
        ----------
        dict_list: list
            list of dictionaries

        Returns
        -------
        complete_set: set
            set containing all dictionary key from the list of dicts
        """
        # convert dictionaries to set to do some set magic
        sets = [set(dic) for dic in dict_list]
        # create a complete set list
        # * - expands the list out into multiple set arguments
        # then the union operator creates it into a full unique set
        # example:
        # s = [{'a','v'}, {'v','x'}] => set.union(*s) = {'a', 'v', 'x'}
        complete_set = set.union(*sets)
        return complete_set

    @staticmethod
    def missing_field_check(filename: str, file_struct_list: List[dict],
                            parameter_names: List[str], **kwargs):
        """
        Checks if any fields are missing from the file/record compared to the 
        file structure.

        Parameters
        ----------
        filename: str
            Name of the file being checked
        file_struct_list: List[dict]
            List of dictionaries for the possible file structure fields
        parameter_names: List[str]
            List of parameter names in the file or in the record.
        record_name: int
            The name of the record (first sequence start time), if in a 
            record style file.

        Raises
        -------
        BorealisFieldMissingError
        
        Notes
        -----
        Checks sets and subsets. Any missing fields are a problem because
        Borealis field names are well-defined.
        """
        missing_fields = set()
        for file_struct in file_struct_list:
            diff_fields = BorealisUtilities.set_diff(file_struct, 
                                                     parameter_names)
            if len(diff_fields) != 0:
                missing_fields = missing_fields.union(diff_fields)

        if len(missing_fields) > 0:
            if 'record_name' in kwargs.keys():
                raise borealis_exceptions.BorealisFieldMissingError(filename,
                                                    missing_fields,
                                                    record_name=record_name)
            else:
                raise borealis_exceptions.BorealisFieldMissingError(filename,
                                                        missing_fields)                

    array_missing_field_check = record_missing_field_check = \
        missing_field_check

    @staticmethod
    def extra_field_check(filename: str, file_struct_list: List[dict],
                          parameter_names: List[str], **kwargs):
        """
        Check if there is an extra field in the file/record.

        Parameters
        ----------
        filename: str
            Name of the file being checked
        file_struct_list: List[dict]
            List of dictionaries for the possible file structure fields
        parameter_names: List[str]
            List of parameter names in the file.
        record_name: int
            Record name for better error message information, if in a 
            record style file.

        Raises
        ------
        BorealisExtraFieldError
        """
        file_struct = BorealisUtilities.dict_list2set(file_struct_list)
        extra_fields = BorealisUtilities.set_diff(parameter_names, file_struct)

        if len(extra_fields) > 0:
            if 'record_name' in kwargs.keys():
                raise borealis_exceptions.BorealisExtraFieldError(filename,
                                                    extra_fields,
                                                    record_name=record_name)
            else:
                raise borealis_exceptions.BorealisExtraFieldError(filename,
                                                        extra_fields)

    array_extra_field_check = record_extra_field_check = extra_field_check

    @staticmethod
    def record_incorrect_types_check(filename: str, attributes_type_dict: dict,
                              datasets_type_dict: dict,
                              record: dict,
                              record_name: int):
        """
        Checks if the record's data type formats are correct according 
        to the file structure fields data type formats.

        Checks both single element types and numpy array dtypes separately.

        Parameters
        ----------
        filename: str
            Name of the file being checked
        attributes_type_dict: dict
            Dictionary with the required types for the attributes in the file.
        datasets_type_dict: dict
            Dictionary with the require dtypes for the numpy
            arrays in the file.
        record: dict
            DMap record
        record_name: int
            Record name for a better error message information

        Raises
        ------
        BorealisDataFormatTypeError
        """
        incorrect_types_check = {param: str(attributes_type_dict[param])
                                 for param in attributes_type_dict.keys()
                                 if type(record[param]) !=
                                 attributes_type_dict[param]}

        incorrect_types_check.update({param: 'np.ndarray of ' +
                                      str(datasets_type_dict[param])
                                      for param in datasets_type_dict.keys()
                                      if record[param].dtype.type !=
                                      datasets_type_dict[param]})
        if len(incorrect_types_check) > 0:
            raise borealis_exceptions.BorealisDataFormatTypeError(
                filename, incorrect_types_check, record_name=record_name)

    @staticmethod
    def array_incorrect_types_check(filename: str,
                              attributes_type_dict: dict,
                              datasets_type_dict: dict, 
                              unshared_parameters: List[str], 
                              file_data: dict):
        """
        Checks if the file's data type formats are correct according 
        to the file structure fields data type formats and whether or 
        not the field is a shared field between records.

        Checks both single element types and numpy array dtypes separately.

        Parameters
        ----------
        filename: str
            Name of the file being checked
        attributes_type_dict: dict
            Dictionary with the required types for the attributes in the file.
        datasets_type_dict: dict
            Dictionary with the require dtypes for the numpy
            arrays in the file.
        unshared_parameters: List[str]
            List of parameter names that are not shared between all the records
            in the array restructured file, i.e. will have a dimension = to 
            number of records.
        file_data: dict
            dictionary containing all file information.

        Raises
        ------
        BorealisDataFormatTypeError
        """

        incorrect_types_check = {}

        for data_field, field_value in file_data:
            if data_field in attributes_type_dict:
                if data_field not in unshared_parameters:    
                    data_type = type(field_value)
                else:
                    # should be a numpy array of length = number of records.
                    data_type = field_value.dtype.type 
                incorrect_types_check.update({data_field: 
                                str(attributes_type_dict[data_field]) if
                                data_type != 
                                attributes_type_dict[data_field]}) 
            else: 
                incorrect_types_check.update({data_field: 'np.ndarray of ' +
                                str(datasets_type_dict[data_field]) if 
                                field_value.dtype.type != 
                                datasets_type_dict[data_field]})                   
        if len(incorrect_types_check) > 0:
            raise borealis_exceptions.BorealisDataFormatTypeError(
                filename, incorrect_types_check)

    @staticmethod
    def array_num_records_check(filename: str, unshared_parameters: List[str],
                                file_data:dict):
        """
        Checks the number of records in all unshared parameter fields to
        ensure they are the same for data integrity.

        Parameters
        ----------
        filename: str
            Name of the file being checked
        unshared_parameters: List[str]
            List of parameter names that are not shared between all the records
            in the array restructured file, i.e. will have a dimension = to 
            number of records.
        file_data: dict
            dictionary containing all file information.

        Raises
        ------
        BorealisNumberOfRecordsError
        """
        num_records = {parameter: file_data[parameter].shape[0] for parameter
                       in unshared_parameters}

        dimensions = list(num_records.values())
        if not all(x == dimensions[0] for x in dimensions):
            raise borealis_exceptions.BorealisNumberOfRecordsError(num_records)
