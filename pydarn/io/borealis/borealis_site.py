# Copyright 2019 SuperDARN Canada, University of Saskatchewan
# Author: Marci Detwiller
"""
This file contains classes for reading, writing, and
converting of Borealis site file types. Site file types
means Borealis site files, ie. stored in a record-by-record
fashion, before being converted to array types only.

Classes
-------
BorealisSiteRead: Reads Borealis site SuperDARN file types (hdf5)
BorealisSiteWrite: Writes Borealis SuperDARN file types (hdf5)

Exceptions
----------
BorealisFileTypeError
BorealisFieldMissingError
BorealisExtraFieldError
BorealisDataFormatTypeError

See Also
--------
BorealisUtilities
BorealisArrayRead
BorealisArrayWrite
BorealisRestructureUtilities

For more information on Borealis data files and how they convert to SDARN
files, see: https://borealis.readthedocs.io/en/latest/

Future Work
-----------
Add compression to bzip2

"""
import deepdish as dd
import h5py
import logging
import os
import subprocess as sp
import warnings

from collections import OrderedDict
from pathlib2 import Path
from typing import Union

from pydarn import borealis_exceptions, borealis_formats

from .borealis_utilities import BorealisUtilities
from .restructure_borealis import BorealisRestructureUtilities

pydarn_log = logging.getLogger('pydarn')


class BorealisSiteRead():
    """
    Class for reading Borealis 'site' filetypes. Site files are stored in
    a record-by-record style.

    See Also
    --------
    BorealisRawacf
    BorealisBfiq
    BorealisAntennasIq
    BorealisRawrf

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
        Reads Borealis site file types into a dictionary.

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

        with h5py.File(self.filename, 'r') as f:
            self._record_names = sorted(list(f.keys()))
            # list of group names in the HDF5 file, to allow partial read.

        # Records are private to avoid tampering.
        self._records = OrderedDict()
        self.read_file()

    def __repr__(self):
        """ for representation of the class object"""
        # __class__.__name__ allows to grab the class name such that
        # when a class inherits this one, the class name will be the child
        # class and not the parent class
        return "{class_name}({filename})"\
            "".format(class_name=self.__class__.__name__,
                      filename=self.filename)

    def __str__(self):
        """ for printing of the class object"""

        return "Reading from {filename} a total number of"\
            " records: {total_records}"\
            "".format(filename=self.filename,
                      total_records=len(list(self.records.keys())))

    @property
    def record_names(self):
        """
        A sorted list of the set of record names in the HDF5 file read.
        These correspond to Borealis file record write times (in ms since
        epoch), and are equal to the group names in the site file types.
        """
        return self._record_names

    @property
    def records(self):
        """
        The Borealis data in a dictionary of records, according to the
        site file format.
        """
        return self._records

    @property
    def arrays(self):
        """
        The Borealis data in a dictionary of arrays, according to the
        restructured array file format.
        """
        return BorealisRestructureUtilities.borealis_site_to_array_dict(
                                            self.filename, self.records,
                                            self.borealis_filetype)

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
                self.filename, self.borealis_filetype)

    def read_bfiq(self) -> dict:
        """
        Reads Borealis bfiq file

        Returns
        -------
        records: OrderedDict{dict}
            records of beamformed iq data. Keys are first sequence timestamp
            (in ms since epoch).
        """
        pydarn_log.info("Reading Borealis bfiq file: {}"
                        "".format(self.filename))
        attribute_types = \
            borealis_formats.BorealisBfiq.site_single_element_types()
        dataset_types = borealis_formats.BorealisBfiq.site_array_dtypes()
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
        pydarn_log.info(
            "Reading Borealis rawacf file: {}".format(self.filename))

        attribute_types = \
            borealis_formats.BorealisRawacf.site_single_element_types()
        dataset_types = borealis_formats.BorealisRawacf.site_array_dtypes()
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
        pydarn_log.info("Reading Borealis antennas_iq file: {}"
                        "".format(self.filename))
        attribute_types = \
            borealis_formats.BorealisAntennasIq.site_single_element_types()
        dataset_types = borealis_formats.BorealisAntennasIq.site_array_dtypes()
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
        pydarn_log.info("Reading Borealis rawrf file: {}"
                        "".format(self.filename))
        attribute_types = \
            borealis_formats.BorealisRawrf.site_single_element_types()
        dataset_types = borealis_formats.BorealisRawrf.site_array_dtypes()
        self._read_borealis_records(attribute_types, dataset_types)
        return self._records

    def _read_borealis_records(self, attribute_types: dict,
                               dataset_types: dict):
        """
        Read the entire file while checking all data fields.

        Several Borealis field checks are done to insure the integrity of the
        file.

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
        BorealisUtilities
        """
        records = dd.io.load(self.filename)
        BorealisUtilities.check_records(self.filename, records,
                                        attribute_types, dataset_types)

        self._records = OrderedDict(sorted(records.items()))


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
    borealis_filetype
        Borealis filetype. Currently supported:
        - bfiq
        - antennas_iq
        - rawacf
        - rawrf
    record_names: list(str)
    records: OrderedDict{dict}
    arrays: dict
    compression: str
        The type of compression to write the file as. Default None.
        Default is no compression to match site-structure files
        created on site by the Borealis radar. They are not compressed
        as they are appended to record by record.
    """
    def __init__(self, filename: str,
                 borealis_records: OrderedDict,
                 borealis_filetype: str,
                 hdf5_compression: Union[str, None] = None):
        """
        Write borealis records to a file.

        Parameters
        ----------
        filename: str
            Name of the file the user wants to write to
        borealis_records: OrderedDict{dict}
            OrderedDict of borealis records, where keys are the
            record name
        borealis_filetype
            filetype to write as. Currently supported:
                - bfiq
                - rawacf
                - antennas_iq
                - rawrf
        hdf5_compression
            String representing hdf5 compression type. Default None.
        """
        self._records = borealis_records
        self.borealis_filetype = borealis_filetype
        self.filename = filename
        self.compression = hdf5_compression
        self._record_names = sorted(list(borealis_records.keys()))
        # list of group keys for partial write
        self.write_file()

    def __repr__(self):
        """For representation of the class object"""

        return "{class_name}({filename})"\
               "".format(class_name=self.__class__.__name__,
                         filename=self.filename)

    def __str__(self):
        """For printing of the class object"""

        return "Writing to filename: {filename} at record name: "\
               "".format(filename=self.filename)

    @property
    def record_names(self):
        """
        A sorted list of the set of record names in the HDF5 file read.
        These correspond to Borealis file record write times (in ms since
        epoch), and are equal to the group names in the site file types.
        """
        return self._record_names

    @property
    def records(self):
        """
        The Borealis data in a dictionary of records, according to the
        site file format.
        """
        return self._records

    @property
    def arrays(self):
        """
        The Borealis data in a dictionary of arrays, according to the
        restructured array file format.
        """
        return BorealisRestructureUtilities.borealis_site_to_array_dict(
                                            self.filename, self.records,
                                            self.borealis_filetype)

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
        elif self.borealis_filetype == 'rawrf':
            self.write_rawrf()
        else:
            raise borealis_exceptions.\
                    BorealisFileTypeError(self.filename,
                                          self.borealis_filetype)

    def write_bfiq(self) -> str:
        """
        Writes Borealis bfiq file

        Returns
        -------
        filename: str
            Filename of written file.
        """
        pydarn_log.info(
            "Writing Borealis bfiq file: {}".format(self.filename))
        attribute_types = \
            borealis_formats.BorealisBfiq.site_single_element_types()
        dataset_types = borealis_formats.BorealisBfiq.site_array_dtypes()
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
        pydarn_log.info(
            "Writing Borealis rawacf file: {}".format(self.filename))
        attribute_types = \
            borealis_formats.BorealisRawacf.site_single_element_types()
        dataset_types = borealis_formats.BorealisRawacf.site_array_dtypes()
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
        pydarn_log.info(
            "Writing Borealis antennas_iq file: {}".format(self.filename))
        attribute_types = \
            borealis_formats.BorealisAntennasIq.site_single_element_types()
        dataset_types = borealis_formats.BorealisAntennasIq.site_array_dtypes()
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
        pydarn_log.info(
            "Writing Borealis rawrf file: {}".format(self.filename))
        attribute_types = \
            borealis_formats.BorealisRawrf.site_single_element_types()
        dataset_types = borealis_formats.BorealisRawrf.site_array_dtypes()
        self._write_borealis_records(attribute_types, dataset_types)
        return self.filename

    def _write_borealis_records(self, attribute_types: dict,
                                dataset_types: dict):
        """
        Write the file in site style after checking records.

        Several Borealis field checks are done to insure the integrity of the
        file.

        Parameters
        ----------
        attributes_type_dict: dict
            Dictionary with the required types for the attributes in the file.
        datasets_type_dict: dict
            Dictionary with the require dtypes for the numpy arrays in the
            file.

        Raises
        ------
        BorealisFieldMissingError - when a field is missing from the Borealis
                                file/stream type
        BorealisExtraFieldError - when an extra field is present in the
                                Borealis file/stream type
        BorealisDataFormatTypeError - when a field has the incorrect
                                field type for the Borealis file/stream type

        See Also
        --------
        BorealisUtilities
        """
        Path(self.filename).touch()
        BorealisUtilities.check_records(self.filename, self.records,
                                        attribute_types, dataset_types)

        # use external h5copy utility to move new record into 2hr file.
        cp_cmd = 'h5copy -i {newfile} -o {full_file} -s {dtstr} -d {dtstr}'
        warnings.filterwarnings("ignore")
        # Must use temporary file to append to a file; writing entire
        # dictionary at once also doesn't work so this is required.
        tmp_filename = self.filename + '.tmp'
        Path(tmp_filename).touch()
        for group_name, group_dict in self.records.items():
            dd.io.save(tmp_filename, {str(group_name): group_dict},
                       compression=self.compression)
            cmd = cp_cmd.format(newfile=tmp_filename, full_file=self.filename,
                                dtstr='/'+str(group_name))

            sp.call(cmd.split())
            os.remove(tmp_filename)
