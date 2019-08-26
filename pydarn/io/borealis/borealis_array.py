# Copyright 2019 SuperDARN Canada, University of Saskatchewan
# Author: Marci Detwiller
"""
This file contains classes for reading, and 
writing of Borealis array file types. Array file 
types are restructured Borealis files. Files are restructured
after being written by the radar to condense all information 
from that time period into arrays. The other type of 
Borealis file is the site file. Site file types
are Borealis site files, ie. stored in a record-by-record
fashion, before being converted to array types.

Classes
-------
BorealisArrayRead: Reads array-style Borealis SuperDARN file types (hdf5). 
    These are the files commonly distributed and available.
BorealisArrayWrite: Writes array-style Borealis SuperDARN file types (hdf5).
    These are the files commonly distributed and available.

Functions
---------
borealis_array_to_site_file: uses BorealisArrayRead and BorealisSiteWrite
    to convert an array file and write it to a site file.
borealis_site_to_array_file: uses BorealisSiteRead and BorealisArrayWrite
    to convert a site file and write it to an array file.

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

from pydarn import borealis_exceptions, DarnWrite, borealis_formats, \
				   BorealisUtilities, code_to_stid, borealis_array_to_site_dict,
                   BorealisSiteRead, BorealisSiteWrite
from pydarn.utils.conversions import dict2dmap

pydarn_log = logging.getLogger('pydarn')


class BorealisArrayRead():
    """
    Class for reading Borealis 'array' filetypes. Array files have
    been restructured to no longer be read in record-by-record
    style. 

    See Also
    --------
    BorealisRawacf
    BorealisBfiq
    BorealisAntennasIq
    BorealisRawrf

    Attributes
    ----------
    filename: str
        The filename of the Borealis HDF5 file being read.
    borealis_filetype: str
        The type of Borealis file. Restructured types include:
        'bfiq'
        'antennas_iq'
        'rawacf'
    record_names: list(str)
    records: dict
    arrays: dict
    """

    def __init__(self, filename: str, borealis_filetype: str):
        """
        Reads Borealis array file types into a dictionary.

        Parameters
        ----------
        filename: str
            file name containing Borealis hdf5 data.
        borealis_filetype: str
            The type of Borealis file. Types include:
            'bfiq'
            'antennas_iq'
            'rawacf'
            'rawrf'

        Raises
        ------
        OSError
            Unable to open file
        """
        self.filename = filename

        if borealis_filetype not in ['bfiq', 'antennas_iq', 'rawacf', 'rawrf']:
            raise borealis_exceptions.BorealisFileTypeError(
                self.filename, borealis_filetype)
        self.borealis_filetype = borealis_filetype

        # Records are private to avoid tampering.
        self._arrays = {}
        self.read_file()

    def __repr__(self):
        """ for representation of the class object"""
        # __class__.__name__ allows to grab the class name such that
        # when a class inherits this one, the class name will be the child
        # class and not the parent class
        return "{class_name}({filename}, {borealis_filetype})"\
            "".format(class_name=self.__class__.__name__,
                      filename=self.filename, 
                      borealis_filetype=self.borealis_filetype)

    def __str__(self):
        """ for printing of the class object"""

        return "Reading from {filename}"\
            "".format(filename=self.filename)

    @property
    def record_names(self):
        """
        A sorted list of the set of record names in the HDF5 file read. 
        These correspond to Borealis file record write times (in ms), and
        are equal to the group names in the site file types.
        """
        return sorted(list(records.keys()))

    @property
    def records(self):
        """
        The Borealis data in a dictionary of records, according to the 
        site file format.
        """
        return borealis_array_to_site_dict(self.arrays, 
                                           self.borealis_filetype)

    @property 
    def arrays(self):
        """
        The Borealis data in a dictionary of arrays, according to the 
        restructured array file format.
        """
        return self._arrays

    def read_file(self) -> dict:
        """
        Reads the specified Borealis file using the other functions for 
        the proper file type.

        Reads the entire file.

        See Also
        --------
        read_bfiq
        read_rawacf
        read_antennas_iq

        Returns
        -------
        arrays: dict
            borealis data dictionary. Keys are data field names and
            unshared fields have a first dimension = number of records 
            in the file.

        Raises
        ------
        BorealisFileTypeError
        """
        if self.borealis_filetype == 'bfiq':
            return self.read_bfiq()
        elif self.borealis_filetype == 'rawacf':
            return self.read_rawacf()
        elif self.borealis_filetype == 'antennas_iq':
            return self.read_antennas_iq()
        else:
            raise borealis_exceptions.BorealisFileTypeError(
                self.filename, borealis_filetype)

    def read_bfiq(self) -> dict:
        """
        Reads Borealis bfiq file that has been structured into arrays.

        Returns
        -------
        arrays: dict
            The Borealis data in a dictionary of arrays, according to the 
            restructured array file format.
        """
        pydarn_log.debug("Reading Borealis bfiq file: {}"
                         "".format(self.filename))
        attribute_types = borealis_formats.BorealisBfiq.single_element_types
        dataset_types = borealis_formats.BorealisBfiq.array_dtypes
        unshared_fields = borealis_formats.BorealisBfiq.unshared_fields
        self._read_borealis_arrays(attribute_types, dataset_types, 
            unshared_fields)
        return self._arrays

    def read_rawacf(self) -> dict:
        """
        Reads Borealis rawacf file that has been structured into arrays.

        Returns
        -------
        arrays: dict
            The Borealis data in a dictionary of arrays, according to the 
            restructured array file format.
        """
        pydarn_log.debug(
            "Reading Borealis rawacf file: {}".format(self.filename))
        attribute_types = borealis_formats.BorealisRawacf.single_element_types
        dataset_types = borealis_formats.BorealisRawacf.array_dtypes
        unshared_fields = borealis_formats.BorealisRawacf.unshared_fields
        self._read_borealis_arrays(attribute_types, dataset_types, 
            unshared_fields)
        return self._arrays

    def read_antennas_iq(self) -> dict:
        """
        Reads Borealis antennas_iq file that has been structured into arrays.

        Returns
        -------
        arrays: dict
            The Borealis data in a dictionary of arrays, according to the 
            restructured array file format.
        """
        pydarn_log.debug("Reading Borealis antennas_iq file: {}"
                         "".format(self.filename))
        attribute_types = \
            borealis_formats.BorealisAntennasIq.single_element_types
        dataset_types = borealis_formats.BorealisAntennasIq.array_dtypes
        unshared_fields = borealis_formats.BorealisAntennasIq.unshared_fields
        self._read_borealis_arrays(attribute_types, dataset_types, 
            unshared_fields)
        return self._arrays

    def _read_borealis_arrays(self, attribute_types: dict,
                              dataset_types: dict, 
                              unshared_fields: List[str]):
        """
        Read the entire file while checking all data fields.

        Parameters
        ----------
        attribute_types: dict
            Dictionary with the required types for the attributes in the file.
        dataset_types: dict
            Dictionary with the require dtypes for the numpy arrays in the 
            file.
        unshared_fields: List[str]
            List of fields that are not shared between the records and 
            therefore should be an array with first dimension = number of 
            records

        Raises
        ------
        BorealisFieldMissingError - when a field is missing from the Borealis
                                file
        BorealisExtraFieldError - when an extra field is present in the
                                Borealis file
        BorealisDataFormatTypeError - when a field has the incorrect
                                field type for the Borealis file
        BorealisNumberOfRecordsError - when the number of records cannot 
                                be discerned from the arrays

        See Also
        --------
        array_missing_field_check(filename, format_fields, parameters) 
                        - checks for missing fields. See this 
                        method for information on why we use format_fields.
        array_extra_field_check(filename, format_fields, parameters) 
                        - checks for extra fields in the record
        array_incorrect_types_check(filename, attribute_types_dict, 
                        dataset_types_dict, unshared_fields, file_data)
                         - checks for incorrect data types for file fields
        array_num_records_check(filename, unshared_fields, file_data)
        """
        all_format_fields = [attribute_types, dataset_types]
        arrays = dd.io.load(self.filename)
        BorealisUtilities.array_missing_field_check(self.filename,
            all_format_fields, arrays)
        BorealisUtilities.array_extra_field_check(self.filename,
            all_format_fields, arrays)
        BorealisUtilities.array_incorrect_types_check(self.filename,
            attribute_types, dataset_types, unshared_fields, arrays)
        BorealisUtilities.array_num_records_check(self.filename,
            unshared_fields, arrays)
        self._arrays = arrays


class BorealisArrayWrite():
    """
    Class for writing Borealis 'array' filetypes. Array files have
    been restructured to no longer be read in record-by-record
    style. 

    See Also
    --------
    BorealisRawacf
    BorealisBfiq
    BorealisAntennasIq
    BorealisRawrf

    Attributes
    ----------
    filename: str
        The filename of the Borealis HDF5 file being written.
    borealis_filetype: str
        The type of Borealis file. Restructured types include:
        'bfiq'
        'antennas_iq'
        'rawacf'
    compression: str
        The type of compression to write the file as. Default zlib.
    arrays: dict
    """

    def __init__(self, filename: str, borealis_arrays: dict, 
                 borealis_filetype: str, compression: str = 'zlib'):
        """
        Write borealis records to a file.

        Parameters
        ----------
        filename: str
            Name of the file the user wants to write to
        borealis_arrays: dict
            borealis data dictionary. Keys are data field names and
            unshared fields have a first dimension = number of records 
            in the file.
        borealis_filetype: str
            The type of Borealis file. Restructured types include:
            'bfiq'
            'antennas_iq'
            'rawacf'
        compression: str
            String representing compression type. Default zlib.
        """
        self.filename = filename
        self._arrays = borealis_arrays
        self.borealis_filetype = borealis_filetype
        self.compression = compression
        self.write_file()

    def __repr__(self):
        """For representation of the class object"""

        return "{class_name}({filename}, {current_record_name})"\
               "".format(class_name=self.__class__.__name__,
                         filename=self.filename,
                         current_record_name=self.current_record_name)

    def __str__(self):
        """For printing of the class object"""

        return "Writing to filename: {filename} at record name: "\
               "{current_record_name}".format(filename=self.filename,
                    current_record_name=self.current_record_name)

    @property 
    def arrays(self):
        """
        The Borealis data in a dictionary of arrays, according to the 
        restructured array file format.
        """
        return self._arrays

    def write_file(self) -> str:
        """
        Write Borealis records to a file given filetype.

        Raises
        ------
        BorealisFileTypeError
        """

        if self.borealis_filetype == 'bfiq':
            self.write_bfiq()
        elif self.borealis_filetype == 'rawacf':
            self.write_rawacf()
        elif self.borealis_filetype == 'antennas_iq':
            self.write_antennas_iq()
        else:
            raise borealis_exceptions.BorealisFileTypeError(self.filename,
                                                            borealis_filetype)

    def write_bfiq(self) -> str:
        """
        Writes Borealis bfiq file

        Returns
        -------
        filename: str
            Filename of written file.
        """
        pydarn_log.debug(
            "Writing Borealis bfiq file: {}".format(self.filename))
        attribute_types = borealis_formats.BorealisBfiq.single_element_types
        dataset_types = borealis_formats.BorealisBfiq.array_dtypes
        unshared_fields = borealis_formats.BorealisBfiq.unshared_fields
        self._write_borealis_arrays(attribute_types, dataset_types, 
            unshared_fields)
        return self.filename

    def write_rawacf(self) -> str:
        """
        Writes Borealis rawacf file

        Returns
        -------
        filename: str
            Filename of written file.
        """
        pydarn_log.debug(
            "Writing Borealis rawacf file: {}".format(self.filename))
        attribute_types = borealis_formats.BorealisRawacf.single_element_types
        dataset_types = borealis_formats.BorealisRawacf.array_dtypes
        unshared_fields = borealis_formats.BorealisRawacf.unshared_fields
        self._write_borealis_arrays(attribute_types, dataset_types, 
            unshared_fields)
        return self.filename

    def write_antennas_iq(self) -> str:
        """
        Writes Borealis antennas_iq file

        Returns
        -------
        filename: str
            Filename of written file.
        """
        pydarn_log.debug(
            "Writing Borealis antennas_iq file: {}".format(self.filename))
        attribute_types = \
            borealis_formats.BorealisAntennasIq.single_element_types
        dataset_types = borealis_formats.BorealisAntennasIq.array_dtypes
        unshared_fields = borealis_formats.BorealisAntennasIq.unshared_fields
        self._write_borealis_arrays(attribute_types, dataset_types, 
            unshared_fields)
        return self.filename

    def _write_borealis_arrays(self, attribute_types: dict,
                              dataset_types: dict, 
                              unshared_fields: List[str]):
        """
        Write the entire file while checking all data fields.

        Parameters
        ----------
        attribute_types: dict
            Dictionary with the required types for the attributes in the file.
        dataset_types: dict
            Dictionary with the require dtypes for the numpy arrays in the 
            file.
        unshared_fields: List[str]
            List of fields that are not shared between the records and 
            therefore should be an array with first dimension = number of 
            records


        Raises
        ------
        BorealisFieldMissingError - when a field is missing from the Borealis
                                file
        BorealisExtraFieldError - when an extra field is present in the
                                Borealis file
        BorealisDataFormatTypeError - when a field has the incorrect
                                field type for the Borealis file
        BorealisNumberOfRecordsError - when the number of records cannot 
                                be discerned from the arrays

        See Also
        --------
        array_missing_field_check(filename, format_fields, parameters) 
                        - checks for missing fields. See this 
                        method for information on why we use format_fields.
        array_extra_field_check(filename, format_fields, parameters) 
                        - checks for extra fields in the record
        array_incorrect_types_check(filename, attribute_types_dict, 
                        dataset_types_dict, unshared_fields, file_data)
                         - checks for incorrect data types for file fields
        array_num_records_check(filename, unshared_fields, file_data) -
                        checks for correct number of records across arrays.
        """
        all_format_fields = [attribute_types, dataset_types]

        BorealisUtilities.array_missing_field_check(self.filename,
            all_format_fields, self._arrays)
        BorealisUtilities.array_extra_field_check(self.filename,
            all_format_fields, self._arrays)
        BorealisUtilities.array_incorrect_types_check(self.filename,
            attribute_types, dataset_types, unshared_fields, self._arrays)
        BorealisUtilities.array_num_records_check(self.filename,
            unshared_fields, self._arrays)
        dd.io.save(self.filename, self._arrays, compression=self.compression)


def borealis_site_to_array_file(read_data_path, write_data_path):
    """
    Restructure the data from site style (record by record) to array style,
    where unshared fields across records are formed into arrays where the 
    first dimension = the number of records. 

    Shared fields that do not change between records will be
    stored as fields in one metadata record within the file. 
    
    Parameters
    ----------
    read_data_path
        string containing the path to the data file for restructuring
    write_data_path
        string containing the path of where to write the restructured data
    
    Raises
    ------
    BorealisFileTypeError
        if cannot determine the borealis filetype
    """

    if read_data_path == write_data_path:
        raise ConvertFileOverWriteError(read_data_path)

    if ('output_ptrs_iq' in read_data_path) or \
            ('antennas_iq' in read_data_path):
        borealis_filetype = 'antennas_iq'
    elif 'bfiq' in read_data_path:
        borealis_filetype = 'bfiq'
    elif 'rawacf' in read_data_path:
        borealis_filetype = 'rawacf'
    else:
        raise BorealisFileTypeError(read_data_path, read_data_path[-2:])

    print("Reading {} site file: {}".format(borealis_filetype, read_data_path))
    site_reader = BorealisSiteRead(read_data_path, borealis_filetype)
    print("Restructuring to array and writing to file: {}"\
        "".format(write_data_path))
    array_writer = BorealisArrayWrite(write_data_path, site_reader.arrays, 
                                      borealis_filetype)

    print("Success!")


def borealis_array_to_site_file(read_data_path, write_data_path):
    """
    Converts a restructured and compressed hdf5 borealis datafile
    back to its original, record based format.
    
    Parameters
    ----------
    read_data_path
        string containing the path to the array data file
    write_data_path
        string containing the path of where to write the record-by-record data
    
    Raises
    ------
    BorealisFileTypeError
        if cannot determine the borealis filetype
    """

    if read_data_path == write_data_path:
        raise ConvertFileOverWriteError(read_data_path)

    warnings.simplefilter('ignore')

    if ('output_ptrs_iq' in read_data_path) or \
            ('antennas_iq' in read_data_path):
        borealis_filetype = 'antennas_iq'
    elif 'bfiq' in read_data_path:
        borealis_filetype = 'bfiq'
    elif 'rawacf' in read_data_path:
        borealis_filetype = 'rawacf'
    else:
        raise BorealisFileTypeError(read_data_path, read_data_path[-2:])

    print("Reading {} array file: {}".format(borealis_filetype, 
                                             read_data_path))
    array_reader = BorealisArrayRead(read_data_path, borealis_filetype)
    print("Restructuring to site and writing to file: {}"\
        "".format(write_data_path))
    site_writer = BorealisSiteWrite(write_data_path, array_reader.records, 
                                    borealis_filetype)
    print("Success!")
