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
    dict_key_diff(dict1, dict2)
        Returns a set of the difference between dict1 and dict2 keys
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
    def dict_key_diff(dict1: Union[dict, set],
                      dict2: Union[dict, set]) -> set:
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
        dict_diff: set
            difference between dict1 and dict2 keys or the sets
        """
        diff_dict = set(dict1) - set(dict2)
        return diff_dict

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
    def record_missing_field_check(file_struct_list: List[dict],
                            record: dict, record_name: int):
        """
        Checks if any fields are missing from the record compared to the file
        structure.

        Parameters
        ----------
        file_struct_list: List[dict]
            List of dictionaries for the possible file structure fields
        record: dict
            Dictionary representing the DMap record
        record_name: int
            The name of the record (first sequence start time)

        Raises
        -------
        BorealisFieldMissing
        
        Notes
        -----
        Checks sets and subsets. Any missing fields are a problem because
        Borealis field names are well-defined.
        """
        missing_fields = set()
        for file_struct in file_struct_list:
            diff_fields = BorealisUtilities.dict_key_diff(file_struct, record)
            if len(diff_fields) != 0:
                missing_fields = missing_fields.union(diff_fields)

        if len(missing_fields) > 0:
            raise borealis_exceptions.BorealisFieldMissingError(record_name,
                                                                missing_fields)

    @staticmethod
    def record_extra_field_check(file_struct_list: List[dict],
                          record: dict, record_name: int):
        """
        Check if there is an extra field in the record.

        Parameters
        ----------
        file_struct_list: List[dict]
            List of dictionaries for the possible file structure fields
        record: dict
            DMap record
        record_name: int
            Record name for better error message information

        Raises
        ------
        BorealisExtraField
        """
        file_struct = BorealisUtilities.dict_list2set(file_struct_list)
        extra_fields = BorealisUtilities.dict_key_diff(record, file_struct)

        if len(extra_fields) > 0:
            raise borealis_exceptions.BorealisExtraFieldError(record_name,
                                                              extra_fields)

    @staticmethod
    def record_incorrect_types_check(attributes_type_dict: dict,
                              datasets_type_dict: dict,
                              record: dict,
                              record_name: int):
        """
        Checks if the record's data type formats are correct according 
        to the file structure fields data type formats.

        Checks both single element types and numpy array dtypes separately.

        Parameters
        ----------
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
        BorealisFileFormatError
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
                incorrect_types_check, record_name)

    @staticmethod
    def array_missing_field_check(attributes_type_dict: dict,
                                  datasets_type_dict: dict, 
                                  parameter_names: List[str]):
        """
        Checks if any field provided is 

        Parameters
        ----------
        file_struct_list: List[dict]
            List of dictionaries for the possible file structure fields
        record: dict
            Dictionary representing the DMap record
        record_name: int
            The name of the record (first sequence start time)

        Raises
        -------
        BorealisFieldMissing
        
        Notes
        -----
        Checks sets and subsets. Any missing fields are a problem because
        Borealis field names are well-defined.
        """

    @staticmethod
    def array_extra_field_check(attributes_type_dict: dict,
                                datasets_type_dict: dict,
                                parameter_names: List[str])

    @staticmethod
    def array_incorrect_types_check(attributes_type_dict: dict,
                              datasets_type_dict: dict, parameter_name: str,
                              paratmeter_array: np.ndarray)
