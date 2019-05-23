import sys
import os
import argparse

from pydarn.borealis_io.borealis import BorealisConvert

def usage_msg():
    """
    Return the usage message for this process.
     
    This is used if a -h flag or invalid arguments are provided.
     
    :returns: the usage message
    """

    usage_message = """ borealis_converter.py [-h] borealis_hdf5_file dmap_filetype
    
    Pass in the filename you wish to convert as borealis_hdf5_file, and the type that you wish
    to convert to as dmap_filetype (ex. iqdat). 

    The script will convert the records to a dmap dictionary and then write to file as the given filename,
    with extension replaced with new dmap_filetype."""

    return usage_message


def borealis_conversion_parser():
    parser = argparse.ArgumentParser(usage=usage_msg())
    parser.add_argument("borealis_hdf5_file", help="Path to the file that you wish to convert to a "
                                                   "SuperDARN dmap type. (e.g. 20190327.2210.38.sas.0.bfiq.hdf5)")
    parser.add_argument("dmap_filetype", help="SuperDARN dmap type to convert to. Possible types include "
                                              "iqdat and rawacf.")

    return parser


def create_dmap_filename(filename_to_convert, dmap_filetype):
    """
    Creates a dmap filename in the same directory as the source file, to
    write the DARN dmap file to.
    """
    basename = os.path.basename(filename_to_convert)
    basename_without_ext = '.'.join(basename.split('.')[0:-2]) # all but .rawacf.hdf5, for example.
    dmap_filename = os.path.dirname(filename_to_convert) + basename_without_ext + '.' + dmap_filetype + '.dmap'
    return dmap_filename


def borealis_converter(filename, dmap_filetype, dmap_filename):
    """
    Convert the borealis file to Darn dmap filetype.
    """
    borealis_data = BorealisConvert(filename)
    print('Read the file {filename}'.format(filename=filename))
    dmap_filename = borealis_data.write_to_dmap(dmap_filetype, dmap_filename)

    print("Borealis file {filename} written to {dmap_filename} without errors."
          "".format(filename=borealis_data.filename, 
                            dmap_filename=dmap_filename))    


def main():
    parser = borealis_conversion_parser()
    args = parser.parse_args()

    dmap_filename = create_dmap_filename(args.borealis_hdf5_file, args.dmap_filetype)
    borealis_converter(args.borealis_hdf5_file, args.dmap_filetype, dmap_filename)


if __name__ == "__main__":
    main()
