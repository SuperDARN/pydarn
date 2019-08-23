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
				   BorealisUtilities, code_to_stid, borealis_array_to_site_dict
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
        The type of Borealis file. Types include:
        'bfiq'
        'antennas_iq'
        'rawacf'
        'rawrf'
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
        read_rawrf

        Returns
        -------
        records: OrderedDict{dict}
            records of borealis data. Keys are first sequence timestamp 
            (in ms since epoch).

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
        elif self.borealis_filetype == 'rawrf':
            return self.read_rawrf()
        else:
            raise borealis_exceptions.BorealisFileTypeError(
                self.filename, borealis_filetype)

    def read_bfiq(self) -> dict:
        """
        Reads Borealis bfiq file

        Returns
        -------
        records: OrderedDict{dict}
            records of beamformed iq data. Keys are first sequence timestamp
            (in ms since epoch).
        """
        pydarn_log.debug("Reading Borealis bfiq file: {}"
                         "".format(self.filename))
        attribute_types = borealis_formats.BorealisBfiq.single_element_types
        dataset_types = borealis_formats.BorealisBfiq.array_dtypes
        self._read_borealis_records(attribute_types, dataset_types)
        return self._records

    def read_rawacf(self) -> dict:
        """
        Reads Borealis rawacf file

        Returns
        -------
        records: OrderedDict{dict}
            records of borealis rawacf data. Keys are first sequence timestamp 
            (in ms since epoch).
        """
        pydarn_log.debug(
            "Reading Borealis rawacf file: {}".format(self.filename))
        attribute_types = borealis_formats.BorealisRawacf.single_element_types
        dataset_types = borealis_formats.BorealisRawacf.array_dtypes
        self._read_borealis_records(attribute_types, dataset_types)
        return self._records

    def read_antennas_iq(self) -> dict:
        """
        Reads Borealis antennas_iq file

        Returns
        -------
        records: OrderedDict{dict}
            records of borealis antennas iq data. Keys are first sequence
            timestamp (in ms since epoch).
        """
        pydarn_log.debug("Reading Borealis antennas_iq file: {}"
                         "".format(self.filename))
        attribute_types = \
            borealis_formats.BorealisAntennasIq.single_element_types
        dataset_types = borealis_formats.BorealisAntennasIq.array_dtypes
        self._read_borealis_records(attribute_types, dataset_types)
        return self._records

    def read_rawrf(self) -> dict:
        """
        Reads Borealis rawrf file

        Returns
        -------
        records: OrderedDict{dict}
            records of borealis rawrf data. Keys are first sequence timestamp
            (in ms since epoch).
        """
        pydarn_log.debug("Reading Borealis rawrf file: {}"
                         "".format(self.filename))
        attribute_types = borealis_formats.BorealisRawrf.single_element_types
        dataset_types = borealis_formats.BorealisRawrf.array_dtypes
        self._read_borealis_records(attribute_types, dataset_types)
        return self._records

    def _read_borealis_records(self, attribute_types: dict,
                               dataset_types: dict):
        """
        Read the entire file while checking all data fields.

        Parameters
        ----------
        attribute_types: dict
            Dictionary with the required types for the attributes in the file.
        dataset_types: dict
            Dictionary with the require dtypes for the numpy arrays in the 
            file.

        """
        for record_name in self._group_names:
            self._current_record_name = record_name
            self._read_borealis_record(attribute_types, dataset_types)

    def _read_borealis_record(self, attribute_types: dict,
                              dataset_types: dict):
        """
        Read a Borealis HDF5 record. 

        Several Borealis field checks are done to insure the integrity of the
        file. Appends to the records dictionary.

        Parameters
        ----------
        attribute_types: dict
            Dictionary with the required types for the attributes in the file.
        dataset_types: dict
            Dictionary with the require dtypes for the numpy arrays in the 
            file.

        Raises
        ------
        OSError: file does not exist
        BorealisFieldMissingError - when a field is missing from the Borealis
                                file/stream type
        BorealisExtraFieldError - when an extra field is present in the
                                Borealis file/stream type
        BorealisDataFormatTypeError - when a field has the incorrect
                                field type for the Borealis file/stream type

        See Also
        --------
        missing_field_check(format_fields, record, record_name) - checks
            for missing fields. See this method for information
            on why we use format_fields.
        extra_field_check(format_fields, record, record_name) - checks for
            extra fields in the record
        incorrect_types_check(attribute_types_dict, dataset_types_dict, record,
            record_name) - checks for incorrect data types for file fields
        """
        all_format_fields = [attribute_types, dataset_types]

        record = dd.io.load(self.filename, group='/' +
                            self._current_record_name)
        BorealisUtilities.missing_field_check(
            all_format_fields, record, self._current_record_name)
        BorealisUtilities.extra_field_check(
            all_format_fields, record, self._current_record_name)
        BorealisUtilities.incorrect_types_check(
            attribute_types, dataset_types, record, self._current_record_name)
        self._records[self._current_record_name] = record


class BorealisSiteWrite():
    """
    Class for writing Borealis 'site' filetypes. Site files are stored in
    a record-by-record style.

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
    borealis_records: OrderedDict{dict}
        The dictionary of Borealis records to write to HDF5 file.
    group_names: list(str)
        The list of record names of the Borealis data. These values 
        are the write time of the record in ms since epoch.
    current_record_name: str
    """

    def __init__(self, filename: str, 
                 borealis_records: OrderedDict = OrderedDict()):
        """
        Write borealis records to a file.

        Parameters
        ----------
        filename: str
            Name of the file the user wants to write to
        borealis_records: OrderedDict{dict}
            OrderedDict of borealis records, where keys are the 
            record name

        """
        self.borealis_records = borealis_records
        self.filename = filename
        self._group_names = sorted(list(borealis_records.keys()))
        # list of group keys for partial write
        self._current_record_name = ''

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
    def current_record_name(self):
        """
        The current record name, str, represented by ms since epoch.
        """
        return self._current_record_name

    def write_file(self, borealis_filetype) -> str:
        """
        Write Borealis records to a file given filetype.

        Parameters
        ----------
        borealis_filetype
            filetype to write as. Currently supported:
                - bfiq
                - rawacf
                - antennas_iq
                - rawrf

        Raises
        ------
        BorealisFileTypeError
        """

        if borealis_filetype == 'bfiq':
            self.write_bfiq()
        elif borealis_filetype == 'rawacf':
            self.write_rawacf()
        elif borealis_filetype == 'antennas_iq':
            self.write_antennas_iq()
        elif borealis_filetype == 'rawrf':
            self.write_rawrf()
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
        self._write_borealis_records(attribute_types, dataset_types)
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
        self._write_borealis_records(attribute_types, dataset_types)
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
        self._write_borealis_records(attribute_types, dataset_types)
        return self.filename

    def write_rawrf(self) -> str:
        """
        Writes Borealis rawrf file

        Returns
        -------
        filename: str
            Filename of written file.
        """
        pydarn_log.debug(
            "Writing Borealis rawrf file: {}".format(self.filename))
        attribute_types = borealis_formats.BorealisRawrf.single_element_types
        dataset_types = borealis_formats.BorealisRawrf.array_dtypes
        self._write_borealis_records(attribute_types, dataset_types)
        return self.filename

    def _write_borealis_records(self, attribute_types: dict,
                                dataset_types: dict):
        """
        Write the file record by record checking each record as we go.

        Parameters
        ----------
        attributes_type_dict: dict
            Dictionary with the required types for the attributes in the file.
        datasets_type_dict: dict
            Dictionary with the require dtypes for the numpy arrays in the 
            file.

        Raises
        ------
        OSError: file does not exist

        """
        for record_name in self._group_names:
            self._current_record_name = record_name
            self._write_borealis_record(attribute_types, dataset_types)

    def _write_borealis_record(self, attribute_types: dict,
                               dataset_types: dict):
        """
        Writes a Borealis HDF5 record. 

        Several Borealis field checks are done to insure the integrity of the 
        file. Appends to the file.

        Parameters
        ----------
        attributes_type_dict: dict
            Dictionary with the required types for the attributes in the file.
        datasets_type_dict: dict
            Dictionary with the require dtypes for the numpy arrays in the 
            file.

        Raises:
        -------
        BorealisFieldMissingError - when a field is missing from the Borealis
                                file/stream type
        BorealisExtraFieldError - when an extra field is present in the
                                Borealis file/stream type
        BorealisDataFormatTypeError - when a field has the incorrect
                                field type for the Borealis file/stream type

        See Also
        --------
        missing_field_check(format_fields, record, record_name) - checks
                        for missing fields. See this method for information
                        on why we use format_fields.
        extra_field_check(format_fields, record, record_name) - checks for
                        extra fields in the record
        incorrect_types_check(attribute_types_dict, dataset_types_dict,
                        record, record_name) - checks
                        for incorrect data types for file fields
        """

        all_format_fields = [attribute_types, dataset_types]
        record = self.borealis_records[self._current_record_name]
        BorealisUtilities.missing_field_check(all_format_fields, record,
                                              self._current_record_name)
        BorealisUtilities.extra_field_check(all_format_fields, record,
                                            self._current_record_name)
        BorealisUtilities.incorrect_types_check(attribute_types, 
                                                dataset_types, record,
                                                self._current_record_name)
        dd.io.save(self.filename, {self._current_record_name: record},
                   compression=None)
