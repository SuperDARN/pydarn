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
BorealisConversionTypesError
BorealisConvert2IqdatError
BorealisConvert2RawacfError
ConvertFileOverWriteError

Future work
-----------
Update to convert a restructured Borealis file into DMap directly
when Borealis files become restructured to save storage space.

Notes
-----
BorealisConvert makes use of DarnWrite to write to SuperDARN file types

See Also
--------
BorealisSiteRead
BorealisSiteWrite
BorealisArrayRead
BorealisArrayWrite

For more information on Borealis data files and how they convert to dmap,
see: https://borealis.readthedocs.io/en/latest/ 
"""



def read_borealis_file(filename, site=False):
	"""
	Read a Borealis file appropriately given site flag.
	"""

	if site:
		BorealisArrayRead()
	else:
		BorealisSiteRead()


def write_borealis_file(filename, borealis_data, site=False):
	"""
	Write a Borealis file appropriately given a site flag.
	"""

	if site:
		BorealisArrayWrite()
	else:
		BorealisSiteWrite()


def borealis_write_to_dmap(filename, dmap_filetype, dmap_filename):
    """
    Convert the borealis file to DARN dmap filetype.

    Parameters
    ----------
    filename: str
        Name of the file where Borealis hdf5 data is stored, to read from.
    dmap_filetype: str
        Type of DARN dmap filetype you would like to convert to. Possible
        types include 'iqdat' and 'rawacf'. Borealis 'bfiq' can be converted 
        to iqdat, and Borealis 'rawacf' can be converted to DARN rawacf.
    dmap_filename: str
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

    pydarn_log.debug("Borealis file {filename} written to {dmap_filename} "
          "without errors.".format(filename=borealis_data.filename, 
                          dmap_filename=dmap_filename))    


def bfiq2darniqdat(filename, **kwargs):
    """
    Convert the borealis bfiq hdf5 file to DARN iqdat filetype.

    Parameters
    ----------
    filename: str
        Name of the file where Borealis bfiq hdf5 data is stored, to read from.
    dmap_filename: str
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
    ConvertFileOverWriteError

    See Also
    --------
    borealis_write_to_dmap
    """

    settings = {}

    # put dmap in place of hdf5 in each spot (usually just 1)
    dmap_filename = os.path.dirname(filename) + '/'
    basename_partials = os.path.basename(filename).split("hdf5")
    for num, basename_partial in enumerate(basename_partials):
        if num != len(basename_partials) - 1:
            dmap_filename += basename_partial + 'dmap'
        else: # last partial, no 'dmap' after.
            dmap_filename += basename_partial
    
    # set defaults
    settings['dmap_filename'] = dmap_filename
    settings.update(kwargs)

    # verify not converting to the same filename.
    if settings['dmap_filename'] == filename:
        raise ConvertFileOverWriteError(filename)
    
    borealis_write_to_dmap(filename, 'iqdat', settings['dmap_filename'])

    return settings['dmap_filename']


def rawacf2darnrawacf(filename, **kwargs):
    """
    Convert the borealis rawacf hdf5 file to DARN rawacf filetype.

    Parameters
    ----------
    filename: str
        Name of the file where Borealis rawacf hdf5 data is stored, to read from.
    dmap_filename: str
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
    ConvertFileOverWriteError

    See Also
    --------
    borealis_write_to_dmap
    """

    settings = {}

    # put dmap in place of hdf5 in each spot (usually just 1)
    dmap_filename = os.path.dirname(filename) + '/'
    basename_partials = os.path.basename(filename).split("hdf5")
    for num, basename_partial in enumerate(basename_partials):
        if num != len(basename_partials) - 1:
            dmap_filename += basename_partial + 'dmap'
        else: # last partial, no 'dmap' after.
            dmap_filename += basename_partial
    
    # set defaults
    settings['dmap_filename'] = dmap_filename
    settings.update(kwargs)

    # verify not converting to the same filename.
    if settings['dmap_filename'] == filename:
        raise ConvertFileOverWriteError(filename)
    
    borealis_write_to_dmap(filename, 'rawacf', settings['dmap_filename'])

    return settings['dmap_filename']
