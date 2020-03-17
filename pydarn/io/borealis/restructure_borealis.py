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
import numpy as np

from collections import OrderedDict

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
    def _site_to_array(cls, data_dict: OrderedDict, format_class: type) -> dict:
        """
        Base function for converting site Borealis data to
        restructured array format.

        Parameters
        ----------
        data_dict: OrderedDict
            a dict of timestamped records loaded from an hdf5 Borealis site file
        format_class: type
            the class to use to get the format information for this file. Can 
            be any class from the borealis_formats module.

        Returns
        -------
        new_data_dict
            A dictionary containing the data from data_dict
            reformatted to be stored entirely as arrays, or as
            one entry if the field does not change between records
        """
        new_data_dict = dict()
        num_records = len(data_dict)

        # write shared fields to dictionary
        first_key = list(data_dict.keys())[0]
        for field in format_class.shared_fields():
            new_data_dict[field] = data_dict[first_key][field]

        temp_array_dict = dict()

        # get dims of the unshared fields arrays
        field_dimensions = {}
        for field in format_class.unshared_fields():
            dims = [dimension_function(data_dict) for 
                    dimension_function in 
                    format_class.unshared_fields_dims()[field]]
            field_dimensions[field] = dims

        # get dims of the array only fields arrays
        for field in format_class.array_only_fields():
            dims = [dimension_function(data_dict) for 
                    dimension_function in 
                    format_class.array_only_fields_dims()[field]]
            field_dimensions[field] = dims

        # all fields to become arrays
        for field, dims in field_dimensions.items():
            array_dims = [num_records] + dims
            array_dims = tuple(array_dims)

            if field in format_class.single_element_types():
                datatype = format_class.single_element_types()[field]
            else: # field in array_dtypes
                datatype = format_class.array_dtypes()[field]  
            empty_array = np.empty(array_dims, dtype=datatype)
            # initialize all values to NaN; some indices may not be filled 
            # do to dimensions that are max values (num sequences, etc can
            # change between records)
            empty_array[:] = np.NaN 
            temp_array_dict[field] = empty_array
        
        # iterate through the records, filling the unshared and array only 
        # fields
        for rec_idx, k in enumerate(data_dict.keys()):
            for field in format_class.unshared_fields():  # all unshared fields
                print(field)
                empty_array = temp_array_dict[field]
                if type(data_dict[first_key][field]) == np.ndarray:
                    # only fill the correct length, appended NaNs occur for 
                    # dims with a determined max value
                    data_buffer = data_dict[k][field]
                    # some fields are linear and need to be reshaped.
                    data_buffer = data_buffer.reshape(tuple(field_dimensions[field]))
                    buffer_shape = data_buffer.shape 
                    print('buffer shape' + str(buffer_shape))
                    index_slice = [slice(0,i) for i in buffer_shape]
                    # insert record index at start of array's slice list
                    index_slice.insert(0, rec_idx) 
                    index_slice = tuple(index_slice)
                    print(index_slice)
                    # place data buffer in the correct place
                    empty_array[index_slice] = data_buffer 
                else: # not an array, num_records is the only dimension
                    empty_array[rec_idx] = data_dict[k][field]

            for field in format_class.array_only_fields():
                empty_array = temp_array_dict[field]
                if len(empty_array.shape) == 1:
                    # num_records is the only dimension
                    # pass record to the generate function to fill the array.
                    empty_array[rec_idx] = \
                        format_class.array_only_fields_generate()[field](
                        data_dict[k])
                else: # multi-dimensional
                    # only fill the correct length, appended NaNs occur for 
                    # dims with a determined max value
                    data_buffer = \
                        format_class.array_only_fields_generate()[field](
                        data_dict[k])

                    buffer_shape = data_buffer.shape 
                    index_slice = [slice(0,i) for i in buffer_shape]
                    # insert record index at start of array's slice list
                    index_slice.insert(0, rec_idx) 
                    index_slice = tuple(index_slice)
                    # place data buffer in the correct place
                    empty_array[index_slice] = data_buffer 

        new_data_dict.update(temp_array_dict)

        return new_data_dict

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
