# Copyright 2019 SuperDARN Canada, University of Saskatchewan
# Author: Marci Detwiller
"""
This file contains some functions that could be useful with 
Borealis file types.

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

Functions
---------
read_borealis_file: uses BorealisRead and returns records or 
    arrays (as requested)
write_borealis_file: uses BorealisWrite to write a file
borealis_site_to_array_file: uses BorealisSiteRead and BorealisArrayWrite
    to convert a site file and write it to an array file.
borealis_array_to_site_file: uses BorealisArrayRead and BorealisSiteWrite
    to convert an array file and write it to a site file.
borealis_write_to_dmap: uses read_borealis_file to read a file
    and BorealisConvert to then write a DARN file.
bfiq2darniqdat: reads a Borealis bfiq file and converts to DARN iqdat.
rawacf2darnrawacf: reads a Borealis rawacf file and converts
    to DARN rawacf.

See Also
--------
BorealisRead
BorealisWrite
BorealisSiteRead
BorealisSiteWrite
BorealisArrayRead
BorealisArrayWrite
BorealisConvert

For more information on Borealis data files and how they convert to DARN
filetypes, see: https://borealis.readthedocs.io/en/latest/
"""

import logging
import os
import sys
import warnings

from collections import OrderedDict
from typing import Union, List

from pydarn import (borealis_exceptions, BorealisRead,
                   BorealisWrite, BorealisConvert)

pydarn_log = logging.getLogger('pydarn')


def read_borealis_file(borealis_hdf5_file: str, borealis_filetype: str,
                       site_flag: bool = False, records: bool = False) -> \
                       Union[dict, OrderedDict]:
    """
    Read a Borealis file appropriately given site flag. Returns either
    arrays or records according to records flag.

    Parameters
    ----------
    borealis_hdf5_file
        Borealis file to read. Either array or site style.
    borealis_filetype
        Borealis filetype. Possible types include antennas_iq,
        bfiq, rawacf, rawrf.
    site_flag: bool
        True if for reading as a site file (record by record), False for
        reading as an array file. Default False.
    records: bool
        True for returning a record dictionary, False for arrays dictionary.
        Default False.

    Returns
    -------
    data_dict : Union[dict, OrderedDict]
        The records dictionary or arrays dictionary, as requested.

    See Also
    --------
    BorealisArrayRead
    BorealisSiteRead
    BorealisRestructureUtilities
    """

    if site_flag:
        reader = BorealisRead(borealis_hdf5_file, borealis_filetype,
                              borealis_file_structure='site')
    else:
        reader = BorealisRead(borealis_hdf5_file, borealis_filetype,
                              borealis_file_structure='array')

    if records:
        data_dict = reader.records
    else:
        data_dict = reader.arrays

    return data_dict


def write_borealis_file(data_dict: Union[dict, OrderedDict],
                        borealis_hdf5_file: str, borealis_filetype: str,
                        records=False) -> str:
    """
    Write a Borealis file appropriately given site flag.

    Parameters
    ----------
    data_dict: Union[dict, OrderedDict]
        Borealis dictionary to write. Either records or arrays.
    borealis_hdf5_file
        Borealis filename to write to.
    borealis_filetype
        Borealis filetype. Possible types include antennas_iq,
        bfiq, rawacf, rawrf.
    records: bool
        To be passed in True if data_dict is records, False for arrays
        dictionary. Default False. If True, will write a site file. If
        False, will write arrays file.

    Returns
    -------
    filename: str
        The filename that was successfully written to.

    See Also
    --------
    BorealisArrayWrite
    BorealisSiteWrite
    BorealisRestructureUtilities
    """

    if records:
        writer = BorealisWrite(borealis_hdf5_file, data_dict,
                               borealis_filetype,
                               borealis_file_structure='site')
    else:
        writer = BorealisWrite(borealis_hdf5_file, data_dict,
                               borealis_filetype,
                               borealis_file_structure='array')

    return writer.filename

def borealis_site_to_array_file(read_filename: str, write_filename: str):
    """
    Restructure the data from site style (record by record) to array style,
    where unshared fields across records are formed into arrays where the
    first dimension = the number of records.

    Shared fields that do not change between records will be
    stored as fields in one metadata record within the file.

    Parameters
    ----------
    read_filename: str
        string containing the path to the data file for restructuring
    write_filename: str
        string containing the path of where to write the restructured data

    Raises
    ------
    BorealisFileTypeError
        if cannot determine the borealis filetype
    ConvertFileOverWriteError
        if reading and writing to the same file
    """

    if read_filename == write_filename:
        raise borealis_exceptions.ConvertFileOverWriteError(read_filename)

    if 'antennas_iq' in read_filename:
        borealis_filetype = 'antennas_iq'
    elif 'bfiq' in read_filename:
        borealis_filetype = 'bfiq'
    elif 'rawacf' in read_filename:
        borealis_filetype = 'rawacf'
    else:
        raise borealis_exceptions.BorealisFileTypeError(read_filename,
            read_filename[-2:])

    pydarn_log.info("Reading {} site file: {}".format(borealis_filetype, read_filename))
    site_reader = BorealisRead(read_filename, borealis_filetype,
                               borealis_file_structure='site')
    pydarn_log.info("Restructuring to array and writing to file: {}"\
        "".format(write_filename))
    array_writer = BorealisWrite(write_filename, site_reader.arrays,
                                 borealis_filetype,
                                 borealis_file_structure='array')
    pydarn_log.info("Successfully restructured {} to {}"\
                     "".format(read_filename, write_filename))


def borealis_array_to_site_file(read_filename: str, write_filename: str):
    """
    Converts a restructured and compressed hdf5 borealis datafile
    back to its original, record based format.

    Parameters
    ----------
    read_filename: str
        string containing the path to the array data file
    write_filename: str
        string containing the path of where to write the record-by-record data

    Raises
    ------
    ConvertFileOverWriteError
        if read file = write file
    BorealisFileTypeError
        if cannot determine the borealis filetype
    """

    if read_filename == write_filename:
        raise borealis_exceptions.ConvertFileOverWriteError(read_filename)

    warnings.simplefilter('ignore')

    if 'antennas_iq' in read_filename:
        borealis_filetype = 'antennas_iq'
    elif 'bfiq' in read_filename:
        borealis_filetype = 'bfiq'
    elif 'rawacf' in read_filename:
        borealis_filetype = 'rawacf'
    else:
        raise borealis_exceptions.BorealisFileTypeError(read_filename,
            read_filename[-2:])

    pydarn_log.info("Reading {} array file: {}".format(borealis_filetype,
                                             read_filename))
    array_reader = BorealisRead(read_filename, borealis_filetype,
                                borealis_file_structure='array')
    pydarn_log.info("Restructuring to site and writing to file: {}"\
        "".format(write_filename))
    site_writer = BorealisWrite(write_filename, array_reader.records,
                                borealis_filetype,
                                borealis_file_structure='site')
    pydarn_log.info("Successfully restructured {} to {}"\
                     "".format(read_filename, write_filename))


def borealis_write_to_dmap(borealis_hdf5_file: str, borealis_filetype: str,
                           slice_id: int, sdarn_filename: str, 
                           site_flag: bool = False):
    """
    Convert a Borealis hdf5 file to a DARN filetype.

    Parameters
    ----------
    borealis_hdf5_file: str
        A Borealis file to convert to DARN DMap filetype. File may contain
        site records or the Borealis arrays format, according to the site
        flag.
    borealis_filetype: str
        The Borealis filetype to convert from, if not the default of the
        second last extension in the filename. This determines the darn
        filetype to convert to according to the mapping:
        'rawacf' -> 'rawacf'
        'bfiq' -> 'iqdat'
    slice_id: int
        The borealis slice identifier code for this data.
    sdarn_filename: str
        The filename to save the converted file to
    site_flag: bool
        Type of the Borealis file supplied. If True, will read as a site file.
        If False, will read as an array file. Default False.

    Raises
    ------
    BorealisFileTypeError
    BorealisFieldMissingError
    BorealisExtraFieldError
    BorealisDataFormatTypeError
    BorealisNumberOfRecordsError
    BorealisConversionTypesError
    BorealisConvert2IqdatError
    BorealisConvert2RawacfError
    BorealisRestructureError
    ConvertFileOverWriteError

    See Also
    --------
    BorealisConvert
    """

    if site_flag:
        structure = 'site'
    else:
        structure = 'array'

    converter = BorealisConvert(borealis_hdf5_file, borealis_filetype, 
                                sdarn_filename, slice_id, 
                                borealis_file_structure=structure)

    pydarn_log.info("Borealis file {filename} written to {sdarn_filename} "
          "without errors.".format(filename=borealis_hdf5_file,
                          sdarn_filename=sdarn_filename))


def bfiq2darniqdat(borealis_hdf5_file: str, sdarn_filename: str,
                   slice_id: int, site_flag: bool = False):
    """
    Convert a Borealis bfiq file to DARN iqdat.

    Parameters
    ----------
    borealis_hdf5_file: str
        A Borealis bfiq file to convert to DARN DMap filetype. File may contain
        site records or the Borealis arrays format, according to the site
        flag.
    sdarn_filename
        The filename to save the converted file to
    slice_id: int
        The borealis slice identifier code for this data.
    site_flag: bool
        Type of the Borealis file supplied. If True, will read as a site file.
        If False, will read as an array file. Default False.

    Raises
    ------
    BorealisFileTypeError
    BorealisFieldMissingError
    BorealisExtraFieldError
    BorealisDataFormatTypeError
    BorealisNumberOfRecordsError
    BorealisConversionTypesError
    BorealisConvert2IqdatError
    BorealisConvert2RawacfError
    BorealisRestructureError
    ConvertFileOverWriteError

    See Also
    --------
    borealis_write_to_dmap
    """
    borealis_write_to_dmap(borealis_hdf5_file, 'bfiq', slice_id, 
                           sdarn_filename, site_flag=site_flag)


def rawacf2darnrawacf(borealis_hdf5_file: str, sdarn_filename: str,
                      slice_id: int, site_flag: bool = False):
    """
    Convert a Borealis rawacf file to DARN rawacf.

    Parameters
    ----------
    borealis_hdf5_file: str
        A Borealis rawacf file to convert to DARN DMap filetype. File may contain
        site records or the Borealis arrays format, according to the site
        flag.
    sdarn_filename
        The filename to save the converted file to
    slice_id: int
        The borealis slice identifier code for this data.
    site_flag: bool
        Type of the Borealis file supplied. If True, will read as a site file.
        If False, will read as an array file. Default False.

    Raises
    ------
    BorealisFileTypeError
    BorealisFieldMissingError
    BorealisExtraFieldError
    BorealisDataFormatTypeError
    BorealisNumberOfRecordsError
    BorealisConversionTypesError
    BorealisConvert2IqdatError
    BorealisConvert2RawacfError
    BorealisRestructureError
    ConvertFileOverWriteError

    See Also
    --------
    borealis_write_to_dmap
    """
    borealis_write_to_dmap(borealis_hdf5_file, 'rawacf', slice_id, 
                           sdarn_filename, site_flag=site_flag)
