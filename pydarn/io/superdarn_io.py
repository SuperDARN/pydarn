# Copyright (C) 2020 SuperDARN Canada, University of Saskatchewan
# Author: Marina Schmidt

import bz2
import pydarnio
import os


class SuperDARNRead(pydarnio.SDarnRead):
    """
    A class that reads select SuperDARN files for pyDARN plotting

    Methods
    -------
    read_dmap : reads superDARN DMap formats
    read_borealis: Reads Borealis hdf5 formats and converts
        Borealis' data dictionary to SDARN data dictionary
    """
    def __init__(self, filename: str = None, stream: bool = False):
        if filename is not None:
            super().__init__(filename, stream)

    def read_dmap(self, filename: str):
        """
        Reads select SuperDARN DMap files for pyDARN plotting:
            fitacf
            rawacf
            iqdat
        When more plotting methods are introduced other files
        will be included.

        Parameters
        ----------
            filename: string
                name of the file you are going to read

        Returns
        ------
            data: List[dict]
                data records from the file
        """
        # check if the file  is compressed with
        # bz2
        if 'bz2' in filename:
            with bz2.open(filename) as fp:
                dmap_stream = fp.read()

            super().__init__(dmap_stream, stream=True)
        else:
            super().__init__(filename)

        try:
            # Check which file type it is
            if 'rawacf' in filename:
                data = self.read_rawacf()
            elif 'fitacf' in filename:
                data = self.read_fitacf()
            elif 'iqdat' in filename:
                self.read_iqdat()
            # if not noticeable then just read the file
            else:
                data = self.read_records()
        except Exception as err:
            # sometimes files might fail due to issues with
            # the specific reading methods. This is not a pyDARN
            # issue so we will just read the dmap file if that fails
            # then make an issue on pyDARNio
            print(err)
            print("..... Will try to read DMap file with read_dmap")
            print(" IF THIS FAILS please make an issue on pyDARNio, not "
                  "pyDARN's issue")
            data = self.read_records
        return data

    def read_borealis(self, filename: str, slice_id: int = None):
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
