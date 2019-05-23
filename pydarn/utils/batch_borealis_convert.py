import sys
import os
import argparse
import glob
import subprocess

from borealis_converter import borealis_converter

def usage_msg():
    """
    Return the usage message for this process.
     
    This is used if a -h flag or invalid arguments are provided.
     
    :returns: the usage message
    """

    usage_message = """ batch_borealis_convert.py [-h] directory_to_convert
    
    Pass in the directory you wish to convert. Filenames with .bfiq.hdf5 will be attempted to be 
    converted to iqdat dmap. Filenames with .rawacf.hdf5 will be attempted to be converted to 
    rawacf dmap.

    The script will convert the hdf5 files from the directory to file as the given filename,
    with extension replaced with new dmap_filetype."""

    return usage_message


def borealis_conversion_parser():
    parser = argparse.ArgumentParser(usage=usage_msg())
    parser.add_argument("directory_to_convert", help="Path to the files you wish to convert to "
                                                   "SuperDARN dmap type.")

    return parser


def main():
    parser = borealis_conversion_parser()
    args = parser.parse_args()

    rawacf_hdf5_files = glob.glob(args.directory_to_convert + '*.rawacf.hdf5')
    for rawacf_file in rawacf_hdf5_files:
        borealis_converter(rawacf_file, "rawacf")
    print("Successfully converted all rawacf files in directory.")

    bfiq_hdf5_files = glob.glob(args.directory_to_convert + '*bfiq.hdf5')
    for bfiq_file in bfiq_hdf5_files:
        borealis_converter(bfiq_file, "iqdat")
    print("Successfully converted all bfiq files in directory.")


if __name__ == "__main__":
    main()
    