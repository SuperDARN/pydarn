# Copyright 2019 SuperDARN Canada, University of Saskatchewan
# Authors: Liam Graham, Marci Detwiller
"""
This file contains a utility class for restructuring Borealis files.
The files can be restructured from record-by-record format (as written on
site in real-time) to an array-based format where the number of records
is a dimension of the array. This makes the files much more human-readable
and also faster to read.

Classes
-------
BorealisRestructureUtilities

Exceptions
----------
BorealisRestructureError
"""
import datetime
import deepdish as dd
import numpy as np
import os
import subprocess as sp
import sys
import tempfile
import warnings

from collections import OrderedDict
from pathlib2 import Path
from typing import Union, List

from pydarn import borealis_exceptions, borealis_formats
from .borealis_utilities import BorealisUtilities


class BorealisRestructureUtilities():
    """
    Utility class containing static methods for restructuring Borealis files.

    Restructured files result in faster reads and a more human-readable
    format.

    The shared fields of the file are written as a single value in the file,
    and unshared fields are written as arrays where number of records is the
    first dimension.

    Class Methods
    -------------
    borealis_site_to_array_dict(origin_string, data_dict, conversion_type)
        uses the other BorealisRestructureUtilities
        methods to convert dictionary of records into a dictionary
        of arrays
    borealis_array_to_site_dict(origin_string, data_dict, conversion_type)
        uses the other BorealisRestructureUtilities
        methods to convert dictionary of arrays into a dictionary
        of records
    """

    @classmethod
    def borealis_site_to_array_dict(cls, origin_string: str, data_dict: OrderedDict,
                                    conversion_type: str, format_class: type) -> dict:
        """
        Converts a file from site style to restructured array style. Determines
        which base function to call based on conversion_type.

        Parameters
        ----------
        origin_string: str
            Filename or origin string for better error messages.
        data_dict: OrderedDict
            An opened rawacf hdf5 file in site record-by-record format
        conversion_type: str
            'bfiq', 'antennas_iq' or 'rawacf' to determine keys to convert
        format_class: type
            the class to use to get the format information for this file. Can 
            be any class from the borealis_formats module.

        Returns
        -------
        new_dict
            A dictionary containing the data from data_dict
            formatted to the array format
        """
        if conversion_type in ['bfiq', 'rawacf', 'antennas_iq']:
            try:
                new_dict = format_class._site_to_array(data_dict)
                BorealisUtilities.check_arrays(origin_string, new_dict,
                    format_class.array_single_element_types(),
                    format_class.array_array_dtypes(),
                    format_class.unshared_fields())
            except Exception as e:
                raise borealis_exceptions.BorealisRestructureError(''\
                    '{}: Error restructuring {} from site to array style:'\
                    '{}'.format(origin_string, cls.__name__, e)) from e
        else:
            raise borealis_exceptions.BorealisRestructureError('{}: '\
                'File type {} not recognized as restructureable from site to '\
                'array style'.format(origin_string, conversion_type))
        return new_dict

    @classmethod
    def borealis_array_to_site_dict(cls, origin_string: str, data_dict: dict,
                                    conversion_type: str, 
                                    format_class: type) -> OrderedDict:
        """
        Converts a file back to its original site format. Determines
        which base function to call based on conversion_type.

        Parameters
        ----------
        origin_string: str
            Filename or origin string for better error messages.
        data_dict: dict
            An opened rawacf hdf5 file in array format
        conversion_type: str
            'bfiq', 'antennas_iq' or 'rawacf' to determine keys to convert
        format_class: type
            the class to use to get the format information for this file. Can 
            be any class from the borealis_formats module.

        Returns
        -------
        new_dict
            A timestamped dictionary containing the data from data_dict
            formatted as the output from a site file.
        """
        if conversion_type in ['bfiq', 'rawacf', 'antennas_iq']:
            try:
                new_dict = format_class._array_to_site(data_dict)
                BorealisUtilities.check_records(origin_string, new_dict,
                    format_class.site_single_element_types(),
                    format_class.site_array_dtypes())
            except Exception as e:
                raise borealis_exceptions.BorealisRestructureError(''\
                        '{}: Error restructuring {} from array to site style:'\
                        '{}'.format(origin_string, cls.__name__, e)) from e
        else:
            raise borealis_exceptions.BorealisRestructureError('{}: '\
                'File type {} not recognized as restructureable from array to '\
                'site style'.format(origin_string, conversion_type))
        return new_dict
