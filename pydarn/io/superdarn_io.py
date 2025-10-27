# Copyright (C) 2020 SuperDARN Canada, University of Saskatchewan
# Author: Marina Schmidt
# Modifications:
# 20230623 - CJM - Removed checks for read_dmap, will read in any dmap

import pydarnio
import os


def read_borealis(filename: str, slice_id: int = None):
    """
    Reads RAWACF or BFIQ borealis files and converts them to
    an SDARN data format dictionary for plotting.

    Parameters
    ----------
        filename: str
            string name of the file, make sure "rawacf" or "bfiq" is in
            the name
        slice_id: int
            the Borealis slice id of the file, required if reading Borealis
            data produced prior to when Borealis v0.5 was released

    Post
    ----
        Produces a file named: dmap_file.rawacf, this should be deleted
        at the end of the file. Requirements for BorealisConvert.

    Raises
    -----
        ValueError - if the file type is not determined in the filename
        then it raises an error that it cannot convert the file.
    """
    new_filename = 'dmap_file.rawacf'

    if 'rawacf' in filename:
        file_type = 'rawacf'
    elif 'bfiq' in filename:
        file_type = 'bfiq'
    else:
        raise ValueError("The filetype of {} cannot  be determined,"
                         " please make sure the filename has rawacf"
                         " or bfiq in the name or look up the accepted"
                         " file in pyDARNio's"
                         " documentation".format(filename))

    converter = pydarnio.BorealisConvert(filename, file_type,
                                         new_filename, slice_id)
    os.remove(new_filename)
    return converter.sdarn_dict
