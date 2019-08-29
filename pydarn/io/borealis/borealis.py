# Copyright 2019 SuperDARN Canada, University of Saskatchewan
# Author: Marci Detwiller
"""
This file contains classes and functions for 
converting of Borealis file types. 

Classes
-------
BorealisConvert: Writes Borealis SuperDARN files types to
SuperDARN DARN files with DMap record structure

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
ConvertFileOverWriteError

Functions
---------
read_borealis_file: uses BorealisArrayRead or BorealisSiteRead
    and returns records or arrays (as requested)
write_borealis_file: uses BorealisArrayWrite or BorealisSiteWrite
    to write a file
return_reader: attempts to read first as BorealisArrayRead and 
    then as BorealisSiteRead and returns the reader class if one is 
    successful
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
BorealisSiteRead
BorealisSiteWrite
BorealisArrayRead
BorealisArrayWrite
BorealisConvert

For more information on Borealis data files and how they convert to DARN 
filetypes, see: https://borealis.readthedocs.io/en/latest/ 
"""

import os
import sys

from collections import OrderedDict

from pydarn import BorealisSiteRead, BorealisSiteWrite, BorealisArrayRead, \
                   BorealisArrayWrite, BorealisConvert


def read_borealis_file(borealis_hdf5_file: str, borealis_filetype: str, 
                       site: bool = False, records: bool = False) ->
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
    site: bool 
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

    if site:
        reader = BorealisSiteRead(borealis_hdf5_file, borealis_filetype)
    else:
        reader = BorealisArrayRead(borealis_hdf5_file, borealis_filetype)

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
        writer = BorealisSiteWrite(borealis_hdf5_file, data_dict,
                                   borealis_filetype)
    else:
        writer = BorealisArrayWrite(borealis_hdf5_file, data_dict,
                                   borealis_filetype)

    return writer.filename


def return_reader(borealis_hdf5_file: str, borealis_filetype: str) -> 
                    Union[BorealisArrayRead, BorealisSiteRead], str:
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
    BorealisRestructureUtilities
    """
    try:
        reader = BorealisArrayRead(borealis_hdf5_file, borealis_filetype)
        return reader, 'array'
    except borealis_exceptions.BorealisExtraFieldError, 
           borealis_exceptions.BorealisFieldMissingError:
        try:
            pydarn_log.debug('{} is not array restructured. Attempting site'\
                ' read.'.format(borealis_hdf5_file))
            reader = BorealisSiteRead(borealis_hdf5_file, borealis_filetype)
            return reader, 'site'
        except:
            raise 


def borealis_site_to_array_file(read_data_path: str, write_data_path: str):
    """
    Restructure the data from site style (record by record) to array style,
    where unshared fields across records are formed into arrays where the 
    first dimension = the number of records. 

    Shared fields that do not change between records will be
    stored as fields in one metadata record within the file. 
    
    Parameters
    ----------
    read_data_path: str
        string containing the path to the data file for restructuring
    write_data_path: str
        string containing the path of where to write the restructured data
    
    Raises
    ------

    BorealisFileTypeError
        if cannot determine the borealis filetype
    """

    if read_data_path == write_data_path:
        raise ConvertFileOverWriteError(read_data_path)

    if 'antennas_iq' in read_data_path:
        borealis_filetype = 'antennas_iq'
    elif 'bfiq' in read_data_path:
        borealis_filetype = 'bfiq'
    elif 'rawacf' in read_data_path:
        borealis_filetype = 'rawacf'
    else:
        raise BorealisFileTypeError(read_data_path, read_data_path[-2:])

    pydarn_log.debug("Reading {} site file: {}".format(borealis_filetype, read_data_path))
    site_reader = BorealisSiteRead(read_data_path, borealis_filetype)
    pydarn_log.debug("Restructuring to array and writing to file: {}"\
        "".format(write_data_path))
    array_writer = BorealisArrayWrite(write_data_path, site_reader.arrays, 
                                      borealis_filetype)
    pydarn_log.debug("Successfully restructured {} to {}"\
                     "".format(read_data_path, write_data_path))


def borealis_array_to_site_file(read_data_path: str, write_data_path: str):
    """
    Converts a restructured and compressed hdf5 borealis datafile
    back to its original, record based format.
    
    Parameters
    ----------
    read_data_path: str
        string containing the path to the array data file
    write_data_path: str
        string containing the path of where to write the record-by-record data
    
    Raises
    ------
    ConvertFileOverWriteError
        if read path = write path
    BorealisFileTypeError
        if cannot determine the borealis filetype
    """

    if read_data_path == write_data_path:
        raise ConvertFileOverWriteError(read_data_path)

    warnings.simplefilter('ignore')

    if 'antennas_iq' in read_data_path:
        borealis_filetype = 'antennas_iq'
    elif 'bfiq' in read_data_path:
        borealis_filetype = 'bfiq'
    elif 'rawacf' in read_data_path:
        borealis_filetype = 'rawacf'
    else:
        raise BorealisFileTypeError(read_data_path, read_data_path[-2:])

    pydarn_log.debug("Reading {} array file: {}".format(borealis_filetype, 
                                             read_data_path))
    array_reader = BorealisArrayRead(read_data_path, borealis_filetype)
    pydarn_log.debug("Restructuring to site and writing to file: {}"\
        "".format(write_data_path))
    site_writer = BorealisSiteWrite(write_data_path, array_reader.records, 
                                    borealis_filetype)
    pydarn_log.debug("Successfully restructured {} to {}"\
                     "".format(read_data_path, write_data_path))


def borealis_write_to_dmap(borealis_hdf5_file: str, borealis_filetype: str, 
                           darn_filename: str, site: bool = False):
    """
    Convert a Borealis hdf5 file to a DARN filetype.

    Parameters
    ----------
    borealis_hdf5_file: str
        A Borealis file to convert to DARN DMap filetype. File may contain
        site records or the Borealis arrays format, according to the site 
        flag.
    darn_filename
        The filename to save the converted file to
    borealis_filetype
        The Borealis filetype to convert from, if not the default of the
        second last extension in the filename. This determines the darn
        filetype to convert to according to the mapping:
        'rawacf' -> 'rawacf'
        'bfiq' -> 'iqdat'
    site: bool 
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
    read_borealis_file
    BorealisConvert
    """

    if borealis_hdf5_file == darn_filename:
        raise ConvertFileOverWriteError(borealis_hdf5_file)

    records = read_borealis_file(borealis_hdf5_file, borealis_filetype, 
                                 site=site, records=True)
    converter = BorealisConvert(records, borealis_filetype, darn_filename)

    pydarn_log.debug("Borealis file {filename} written to {darn_filename} "
          "without errors.".format(filename=borealis_hdf5_file, 
                          darn_filename=darn_filename))    


def bfiq2darniqdat(borealis_hdf5_file: str, darn_filename: str, 
                   site: bool = False):
    """
    Convert a Borealis bfiq file to DARN iqdat.

    Parameters
    ----------
    borealis_hdf5_file: str
        A Borealis file to convert to DARN DMap filetype. File may contain
        site records or the Borealis arrays format, according to the site 
        flag.
    darn_filename
        The filename to save the converted file to
    site: bool 
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
    borealis_write_to_dmap(borealis_hdf5_file, 'bfiq', darn_filename, 
                           site=site)


def rawacf2darnrawacf(borealis_hdf5_file: str, darn_filename: str, 
                      site: bool = False):
    """
    Convert a Borealis rawacf file to DARN rawacf.

    Parameters
    ----------
    borealis_hdf5_file: str
        A Borealis file to convert to DARN DMap filetype. File may contain
        site records or the Borealis arrays format, according to the site 
        flag.
    darn_filename
        The filename to save the converted file to
    site: bool 
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
    borealis_write_to_dmap(borealis_hdf5_file, 'rawacf', darn_filename, 
                           site=site)
