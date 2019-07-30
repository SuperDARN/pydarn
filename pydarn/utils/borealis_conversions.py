# Copyright 2019 SuperDARN Canada, University of Saskatchewan
# Author: Marci Detwiller
"""
This file contains a function to convert Borealis hdf5 files to DARN dmap files,
using the BorealisConvert class from the pydarn io borealis module. 

Notes
-----
BorealisConvert uses both BorealisRead and DarnWrite classes to convert files. 

"""
import logging

from pydarn import BorealisConvert

pydarn_log = logging.getLogger('pydarn')

def borealis_write_to_dmap(filename, dmap_filetype, dmap_filename):
    """
    Convert the borealis file to DARN dmap filetype.

    Parameters
    ----------
    filename : str
        Name of the file where Borealis hdf5 data is stored, to read from.
    dmap_filetype : str
        Type of DARN dmap filetype you would like to convert to. Possible
        types include 'iqdat' and 'rawacf'. Borealis 'bfiq' can be converted 
        to iqdat, and Borealis 'rawacf' can be converted to DARN rawacf.
    dmap_filename : str
        Name of the file that you want to save the DARN dmap file to. 

    Raises
    ------
    BorealisFileTypeError
    BorealisFieldMissingError
    BorealisExtraFieldError
    BorealisDataFormatTypeError
    BorealisConversionTypesError
    BorealisConvert2IqdatError
    BorealisConvert2RawacfError

    See Also
    --------
    BorealisConvert 
        Class that is used to convert
    BorealisRead
        BorealisConvert uses this
    DarnWrite
        BorealisConvert uses this
    """
    borealis_data = BorealisConvert(filename)
    pydarn_log.debug('Read the file {filename}'.format(filename=filename))
    dmap_filename = borealis_data.write_to_dmap(dmap_filetype, dmap_filename)

    pydarn_log.debug("Borealis file {filename} written to {dmap_filename} without "
          "errors.".format(filename=borealis_data.filename, 
                          dmap_filename=dmap_filename))    
