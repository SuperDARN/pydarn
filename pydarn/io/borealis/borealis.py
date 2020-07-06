# Copyright 2019 SuperDARN Canada, University of Saskatchewan
# Author: Marci Detwiller
"""
This file contains classes and functions for
converting of Borealis file types.

Classes
-------
BorealisRead: Uses BorealisSiteRead and BorealisArrayRead
    to read a Borealis HDF5 file
BorealisWrite: Uses BorealisSiteWrite and BorealisArrayWrite
    to write a Borealis HDF5 file

Exceptions
----------
BorealisFileTypeError
BorealisFieldMissingError
BorealisExtraFieldError
BorealisDataFormatTypeError
BorealisNumberOfRecordsError
BorealisConversionTypesError
BorealisConvert2IqdatError
BorealisConvert2RawacfError
BorealisRestructureError
BorealisStructureError
ConvertFileOverWriteError

See Also
--------
BorealisSiteRead
BorealisSiteWrite
BorealisArrayRead
BorealisArrayWrite
BorealisConvert

For more information on Borealis data files and how they convert to SDARN
filetypes, see: https://borealis.readthedocs.io/en/latest/
"""

import logging
import warnings

from collections import OrderedDict
from typing import Union

from pydarn import borealis_exceptions
from .borealis_site import BorealisSiteRead, BorealisSiteWrite
from .borealis_array import BorealisArrayRead, BorealisArrayWrite

pydarn_log = logging.getLogger('pydarn')


class BorealisRead():
    """
    Class for reading Borealis filetypes of both array and site
    structure. This class abstracts and redirects the file being read to
    the correct class (BorealisSiteRead or BorealisArrayRead).

    See Also
    --------
    BorealisSiteRead
    BorealisArrayRead
    BaseFormat
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
    reader: Union[BorealisSiteWrite, BorealisArrayWrite]
        the wrapped BorealisSiteRead or BorealisArrayRead instance
    borealis_file_structure: Union[str, None]
        The structure of the data. 'site' structure means record-by-record
        style, as is written by the Borealis radar on-site. 'array'
        structure means a restructured file where parameters
        that are consistent throughout the whole file are provided
        once and data is restructured into arrays where the
        first dimension is num_records. 'array' structure is
        intended for downstream users to more easily read and use
        the data.
    records: dict
    arrays: dict
    record_names: list[str]
    software_version : str
        The Borealis software version that created the file.
    format: subclass of borealis_formats.BaseFormat
        The format class used to read/write the file.
    """

    def __init__(self, filename: str, borealis_filetype: str,
                 borealis_file_structure: Union[str, None] = None):
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
        borealis_file_structure: Union[str, None]
            The write structure of the file provided. Possible types are
            'site', 'array', or None. If None (default), array will be
            attempted first followed by site.

        Raises
        ------
        OSError
            Unable to open file
        BorealisStructureError
            Unknown structure type.
        """
        warnings.simplefilter('once', PendingDeprecationWarning)
        warnings.warn("BorealisRead method will be removed from pyDARN v 1.2,"
                      " please use pyDARNio: "
                      "https://github.com/SuperDARN/pyDARNio",
                      PendingDeprecationWarning)

        self.filename = filename

        if borealis_filetype not in ['bfiq', 'antennas_iq', 'rawacf', 'rawrf']:
            raise borealis_exceptions.BorealisFileTypeError(
                self.filename, borealis_filetype)
        self.borealis_filetype = borealis_filetype

        if borealis_file_structure is None:
            self._reader, self._borealis_file_structure = \
                self.return_reader(self.filename, self.borealis_filetype)
        elif borealis_file_structure == 'site':
            self._reader = BorealisSiteRead(self.filename,
                                            self.borealis_filetype)
            self._borealis_file_structure = 'site'
        elif borealis_file_structure == 'array':
            self._reader = BorealisArrayRead(self.filename,
                                             self.borealis_filetype)
            self._borealis_file_structure = 'array'
        else:  # unknown structure
            raise borealis_exceptions.\
                BorealisStructureError("Unknown structure type: {}"
                                       "".format(borealis_file_structure))

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
    def borealis_file_structure(self):
        """
        The structure of the file read, 'site' or 'array'. Default None.
        """
        return self._borealis_file_structure

    @property
    def record_names(self):
        """
        A sorted list of the set of record names in the HDF5 file read.
        These correspond to Borealis file record write times (in ms since
        epoch), and are equal to the group names in the site file types.
        """
        return self._reader.record_names

    @property
    def records(self):
        """
        The Borealis data in a dictionary of records, according to the
        site file format.
        """
        return self._reader.records

    @property
    def arrays(self):
        """
        The Borealis data in a dictionary of arrays, according to the
        restructured array file format.
        """
        return self._reader.arrays

    @property
    def software_version(self):
        """
        The Borealis software version that created the data.

        Note:
            May impact the fields included in the file
            as each version has a different field structure/format
        """
        return self._reader.software_version

    @property
    def format(self):
        """
        The format class used for the file, from the borealis_formats module.
        """
        return self._reader.format

    @staticmethod
    def return_reader(borealis_hdf5_file: str, borealis_filetype: str) -> \
                     (Union[BorealisArrayRead, BorealisSiteRead], str):
        """
        Attempts to read a file as array and then as site. Returns if
        any read is successful.

        Parameters
        ----------
        borealis_hdf5_file
            Borealis file to read. Either array or site style.
        borealis_filetype
            Borealis filetype. Possible types include antennas_iq,
            bfiq, rawacf.

        Returns
        -------
        reader
            instance of BorealisArrayRead or BorealisSiteRead, depending on
            reader success
        reader_type
            'array' or 'site', depending on which read was successful

        Raises
        ------
        BorealisExtraFieldError
        BorealisMissingFieldError
        BorealisDataFormatTypeError

        See Also
        --------
        BorealisArrayRead
        BorealisSiteRead
        """
        try:
            reader = BorealisArrayRead(borealis_hdf5_file, borealis_filetype)
            return reader, 'array'
        except (borealis_exceptions.BorealisExtraFieldError,
                borealis_exceptions.BorealisFieldMissingError,
                borealis_exceptions.BorealisStructureError):
            pydarn_log.info('{} is not array restructured. Attempting site'
                            ' read.'.format(borealis_hdf5_file))
            try:
                reader = BorealisSiteRead(borealis_hdf5_file,
                                          borealis_filetype)
                return reader, 'site'
            except Exception as err:
                pydarn_log.info('{} is not site structured. Raising reader'
                                ' errors.'.format(borealis_hdf5_file))
                raise err


class BorealisWrite():
    """
    Class for writing Borealis filetypes of both array and site
    structure. This class abstracts and redirects the file write to
    the correct class (BorealisSiteWrite or BorealisArrayWrite).

    See Also
    --------
    BorealisSiteWrite
    BorealisArrayWrite
    BaseFormat
    BorealisRawacf
    BorealisBfiq
    BorealisAntennasIq
    BorealisRawrf

    Attributes
    ----------
    filename: str
        The filename of the Borealis HDF5 file being written.
    borealis_filetype: str
        The type of Borealis file. Types include:
        'bfiq'
        'antennas_iq'
        'rawacf'
        'rawrf'
    writer: Union[BorealisSiteWrite, BorealisArrayWrite]
        the wrapped BorealisSiteWrite or BorealisArrayWrite instance
    borealis_file_structure: Union[str, None]
        The structure of the data. 'site' structure means record-by-record
        style, as is written by the Borealis radar on-site. 'array'
        structure means a restructured file where parameters
        that are consistent throughout the whole file are provided
        once and data is restructured into arrays where the
        first dimension is num_records. 'array' structure is
        intended for downstream users to more easily read and use
        the data.
    compression: Union[str, None]
        The type of compression the file is written with. Default is
        None for site structure, and 'zlib' for array structure.
        Site structured files will have no compression to match
        files actually written on-site, where records are constantly
        appended so there is no compression. Array structured files
        will have 'zlib' compression to enable a faster read time
        for downstream users.
    arrays: dict
        The Borealis data in a dictionary of arrays, according to the
        restructured array file format.
    software_version : str
        The Borealis software version that created the file.
    format: subclass of borealis_formats.BaseFormat
        The format class used to read/write the file.
    """

    def __init__(self, filename: str, borealis_data: Union[dict, OrderedDict],
                 borealis_filetype: str,
                 borealis_file_structure: Union[str, None] = None,
                 **kwargs):
        """
        Write Borealis records to a file.

        Parameters
        ----------
        filename: str
            Name of the file the user wants to write to
        data: Union[dict, OrderedDict]
            Borealis data dictionary. Can be arrays or records.
        borealis_filetype: str
            The type of Borealis file. Restructured types include:
            'bfiq'
            'antennas_iq'
            'rawacf'
        borealis_file_structure: Union[str, None]
            The structure of the data provided. Possible types are
            'site', 'array', or None. If None (default), array write will be
            attempted first followed by site.
        hdf5_compression: str
            A kwarg key name, giving a string representing compression type.
        """
        warnings.simplefilter('once', PendingDeprecationWarning)
        warnings.warn("BorealisWrite method will be removed from pyDARN v 1.2,"
                      " please use pyDARNio: "
                      "https://github.com/SuperDARN/pyDARNio",
                      PendingDeprecationWarning)

        self.filename = filename
        self.data = borealis_data
        self.borealis_filetype = borealis_filetype

        if borealis_file_structure is None:
            self._writer, self._borealis_file_structure = \
                self.return_writer(self.filename, self.data,
                                   self.borealis_filetype, **kwargs)
        elif borealis_file_structure == 'site':
            self._writer = BorealisSiteWrite(self.filename, self.data,
                                             self.borealis_filetype,
                                             **kwargs)
            self._borealis_file_structure = 'site'
        elif borealis_file_structure == 'array':
            self._writer = BorealisArrayWrite(self.filename, self.data,
                                              self.borealis_filetype, **kwargs)
            self._borealis_file_structure = 'array'
        else:  # unknown structure
            raise borealis_exceptions.\
                BorealisStructureError('Unknown structure type: {}'
                                       ''.format(borealis_file_structure))

    def __repr__(self):
        """For representation of the class object"""

        return "{class_name}({filename}, {current_record_name})"\
               "".format(class_name=self.__class__.__name__,
                         filename=self.filename,
                         current_record_name=self.current_record_name)

    def __str__(self):
        """For printing of the class object"""

        return "Writing to filename: {filename} at record name: "\
               "{current_record_name}"\
               "".format(filename=self.filename,
                         current_record_name=self.current_record_name)

    @property
    def borealis_file_structure(self):
        """
        The structure of the file read, 'site' or 'array'. Default None.
        """
        return self._borealis_file_structure

    @property
    def compression(self):
        """
        The type of compression the file is written with. Default is
        None for site structure, and 'zlib' for array structure.
        Site structured files will have no compression to match
        files actually written on-site, where records are constantly
        appended so there is no compression. Array structured files
        will have 'zlib' compression to enable a faster read time
        for downstream users.
        """
        return self._writer.compression

    @property
    def record_names(self):
        """
        A sorted list of the set of record names in the HDF5 file read.
        These correspond to Borealis file record write times (in ms since
        epoch), and are equal to the group names in the site file types.
        """
        return self._writer.record_names

    @property
    def records(self):
        """
        The Borealis data in a dictionary of records, according to the
        site file format.
        """
        return self._writer.records

    @property
    def arrays(self):
        """
        The Borealis data in a dictionary of arrays, according to the
        restructured array file format.
        """
        return self._writer.arrays

    @property
    def software_version(self):
        """
        The Borealis software version that created the data.

        Note:
            May impact the fields included in the file
            as each version has a different field structure/format
        """
        return self._writer.software_version

    @property
    def format(self):
        """
        The format class used for the file, from the borealis_formats module.
        """
        return self._writer.format

    @staticmethod
    def return_writer(filename: str, data: Union[dict, OrderedDict],
                      borealis_filetype: str, **kwargs) -> \
            (Union[BorealisArrayRead, BorealisSiteRead], str):
        """
        Attempts to write a file as array and then site. Returns if any writer
        is successful.

        Parameters
        ----------
        filename
            Filename to write to. Either array or site style.
        data
            Data to write out. Can be arrays dictionary or OrderedDict of
            records.
        borealis_filetype
            Borealis filetype. Possible types include antennas_iq,
            bfiq, rawacf, rawrf (site only).
        kwargs:
            keyword arguments for writer call. Only supported is
            'hdf5_compression'

        Returns
        -------
        writer
            instance of BorealisArrayWrite or BorealisSiteWrite, depending on
            writer success
        writer_type
            'array' or 'site', depending on which write was successful

        Raises
        ------
        BorealisExtraFieldError
        BorealisMissingFieldError
        BorealisDataFormatTypeError

        See Also
        --------
        BorealisArrayWrite
        BorealisSiteWrite
        """
        try:
            writer = BorealisArrayWrite(filename, data,
                                        borealis_filetype, **kwargs)
            return writer, 'array'
        except (borealis_exceptions.BorealisExtraFieldError,
                borealis_exceptions.BorealisFieldMissingError,
                borealis_exceptions.BorealisStructureError):
            pydarn_log.info('Data provided is not array restructured. '
                            'Attempting site write to file {}.'
                            ''.format(filename))
            try:
                writer = BorealisSiteWrite(filename, data,
                                           borealis_filetype, **kwargs)
                return writer, 'site'
            except Exception as err:
                pydarn_log.info('Data provided is not site structured. '
                                'Raising writer error.')
                raise err
