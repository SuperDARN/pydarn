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
BorealisVersionError
BorealisStructureError
BorealisRestructureError

See Also
--------
BorealisUtilities
BorealisArrayRead
BorealisArrayWrite

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

pydarn_log = logging.getLogger('pydarn')


class BorealisSiteRead():
    """
    Class for reading Borealis 'site' filetypes. Site files are stored in
    a record-by-record style.

    See Also
    --------
    BaseFormat
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
    software_version : str
        The Borealis software version that created the file.
    format: subclass of borealis_formats.BaseFormat
        The format class used to read/write the file.
    """

    def __init__(self, filename: str, borealis_filetype: str):
        """
        Reads Borealis site file types into a dictionary. First determines
        the correct format class from borealis_formats module to use to verify
        the file fields before proceeding with the read.

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
        BorealisFileTypeError
            Filetype not recognized
        BorealisStructureError
            Cannot read the software version; file is incorrect structure
        BorealisVersionError
            Borealis software version format does not exist in pydarn
        """
        warnings.simplefilter('once', PendingDeprecationWarning)
        warnings.warn("BorealisSiteRead method will be removed from pyDARN v 1.2,"
                      " please use pyDARNio: "
                      "https://github.com/SuperDARN/pyDARNio",
                      PendingDeprecationWarning)

        self.filename = filename
        if borealis_filetype not in ['bfiq', 'antennas_iq', 'rawacf', 'rawrf']:
            raise borealis_exceptions.BorealisFileTypeError(
                self.filename, borealis_filetype)
        self.borealis_filetype = borealis_filetype

        with h5py.File(self.filename, 'r') as f:
            self._record_names = sorted(list(f.keys()))
            # list of group names in the HDF5 file, to allow partial read.

        # get the version of the file - split by the dash, first part should be
        # 'vX.X'

        try:
            version = dd.io.load(self.filename,
                                 group='/'+self._record_names[0]
                                 )['borealis_git_hash'].split('-')[0]
        except (IndexError, ValueError) as err:
            # if this is an array style file, it will raise
            # IndexError on the array.
            raise borealis_exceptions.BorealisStructureError(
                ' {} Could not find the borealis_git_hash required to '
                'determine read version (file may be array style): {}'
                ''.format(self.filename, err)) from err

        if version not in borealis_formats.borealis_version_dict:
            raise borealis_exceptions.BorealisVersionError(self.filename,
                                                           version)
        else:
            self._borealis_version = version

        self._format = borealis_formats.borealis_version_dict[
                self.software_version][self.borealis_filetype]

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

        Raises
        ------
        BorealisRestructureError
            Errors in restructuring to arrays style file.
        """

        if self.format.is_restructureable():
            try:
                arrays = self.format._site_to_array(self.records)
                BorealisUtilities.check_arrays(
                    self.filename, arrays,
                    self.format.array_single_element_types(),
                    self.format.array_array_dtypes(),
                    self.format.unshared_fields())
            except Exception as err:
                raise borealis_exceptions.BorealisRestructureError(
                    'Records from {}: Error restructuring {} from site to '
                    'array style: {}'
                    ''.format(self.filename, self.format.__name__, err)) \
                    from err
        else:
            raise borealis_exceptions.BorealisRestructureError(
                'Records from {}: File format {} not recognized as '
                'restructureable from site to array style'
                ''.format(self.filename, self.format.__name__))

        return arrays

    @property
    def software_version(self):
        """
        The version of the file, taken from the 'borealis_git_hash' in the
        first record, in the init.
        """
        return self._borealis_version

    @property
    def format(self):
        """
        The format class used for the file, from the borealis_formats module.
        """
        return self._format

    def read_file(self) -> dict:
        """
        Reads the specified Borealis file using the other functions for
        the proper file type. Reads the entire file.

        See Also
        --------
        BaseFormat

        Returns
        -------
        records: OrderedDict{dict}
            records of Borealis rawacf data. Keys are first sequence timestamp
            (in ms since epoch).
        """
        pydarn_log.info("Reading Borealis {} {} file: {}"
                        "".format(self.software_version,
                                  self.borealis_filetype, self.filename))

        attribute_types = self.format.site_single_element_types()
        dataset_types = self.format.site_array_dtypes()

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
    BaseFormat
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
    software_version : str
        The Borealis software version that created the file.
    format: subclass of borealis_formats.BaseFormat
        The format class used to read/write the file.
    """
    def __init__(self, filename: str,
                 borealis_records: OrderedDict,
                 borealis_filetype: str,
                 hdf5_compression: Union[str, None] = None):
        """
        Write Borealis records to a file.

        Parameters
        ----------
        filename: str
            Name of the file the user wants to write to
        borealis_records: OrderedDict{dict}
            OrderedDict of Borealis records, where keys are the
            record name
        borealis_filetype
            filetype to write as. Currently supported:
                - bfiq
                - rawacf
                - antennas_iq
                - rawrf
        hdf5_compression
            String representing hdf5 compression type. Default None.

        Raises
        ------
        BorealisFileTypeError
            Filetype not recognized
        BorealisStructureError
            Cannot read the software version; file is incorrect structure
        BorealisVersionError
            Borealis software version format does not exist in pydarn
        """
        warnings.simplefilter('once', PendingDeprecationWarning)
        warnings.warn("BorealisSiteWrite method will be removed from pyDARN v 1.2,"
                      " please use pyDARNio: "
                      "https://github.com/SuperDARN/pyDARNio",
                      PendingDeprecationWarning)

        self._records = borealis_records
        if borealis_filetype not in ['bfiq', 'antennas_iq', 'rawacf', 'rawrf']:
            raise borealis_exceptions.BorealisFileTypeError(
                self.filename, borealis_filetype)
        self.borealis_filetype = borealis_filetype
        self.filename = filename
        self.compression = hdf5_compression
        self._record_names = sorted(list(borealis_records.keys()))

        # get the version of the file - split by the dash, first part should be
        # 'vX.X'
        try:
            version = self._records[self.record_names[0]][
                'borealis_git_hash'].split('-')[0]
        except (IndexError, ValueError) as err:
            # if this is an array style file, it will raise
            # IndexError on the array.
            raise borealis_exceptions.BorealisStructureError(
                ' {} Could not find the borealis_git_hash required to '
                'determine read version (data may be array style) {}'
                ''.format(self.filename, err)) from err

        if version not in borealis_formats.borealis_version_dict:
            raise borealis_exceptions.BorealisVersionError(self.filename,
                                                           version)
        else:
            self._borealis_version = version

        self._format = borealis_formats.borealis_version_dict[
                self.software_version][self.borealis_filetype]

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

        Raises
        ------
        BorealisRestructureError
            Errors in restructuring to arrays style file.
        """

        if self.format.is_restructureable():
            try:
                arrays = self.format._site_to_array(self.records)
                BorealisUtilities.check_arrays(
                    self.filename, arrays,
                    self.format.array_single_element_types(),
                    self.format.array_array_dtypes(),
                    self.format.unshared_fields())
            except Exception as err:
                raise borealis_exceptions.BorealisRestructureError(
                    'Records for {}: Error restructuring {} from site to array'
                    ' style: {}'
                    ''.format(self.filename, self.format.__name__, err)) \
                    from err
        else:
            raise borealis_exceptions.BorealisRestructureError(
                'Records for {}: File format {} not recognized as '
                'restructureable from site to array style'
                ''.format(self.filename, self.format.__name__))

        return arrays

    @property
    def software_version(self):
        """
        The version of the file, taken from the 'borealis_git_hash' in the
        first record, in the init.
        """
        return self._borealis_version

    @property
    def format(self):
        """
        The format class used for the file, from the borealis_formats module.
        """
        return self._format

    def write_file(self) -> str:
        """
        Write Borealis records to a file given filetype.

        See Also
        --------
        BaseFormat

        Returns
        -------
        filename
            The filename written to.
        """
        pydarn_log.info("Writing Borealis {} {} file: {}"
                        "".format(self.software_version,
                                  self.borealis_filetype, self.filename))

        attribute_types = self.format.site_single_element_types()
        dataset_types = self.format.site_array_dtypes()

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

        warnings.filterwarnings("ignore")
        # Must use temporary file to append to a file; writing entire
        # dictionary at once also doesn't work so this is required.
        tmp_filename = self.filename + '.tmp'
        Path(tmp_filename).touch()
        for group_name, group_dict in self.records.items():
            dd.io.save(tmp_filename, {str(group_name): group_dict},
                       compression=self.compression)
            cp_cmd = 'h5copy -i {newfile} -o {full_file} -s {dtstr} -d {dtstr}'
            cmd = cp_cmd.format(newfile=tmp_filename, full_file=self.filename,
                                dtstr='/'+str(group_name))
            sp.call(cmd.split())
            os.remove(tmp_filename)
