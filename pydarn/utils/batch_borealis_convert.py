import sys
import os
import argparse
import glob
from multiprocessing import Pool
import bz2

from borealis_converter import borealis_converter

def usage_msg():
    """
    Return the usage message for this process.
     
    This is used if a -h flag or invalid arguments are provided.
     
    :returns: the usage message
    """

    usage_message = """ batch_borealis_convert.py [-h] -bz2 directory_to_convert 
    
    Pass in the directory you wish to convert. Filenames with .bfiq.hdf5 will be attempted to be 
    converted to iqdat dmap. Filenames with .rawacf.hdf5 will be attempted to be converted to 
    rawacf dmap.

    Filenames with .rawacf.hdf5.bz2 or .bfiq.hdf5.bz2 will be decompressed and then converted. The
    converted file will then be bzipped if the input file was bzipped.

    The script will convert the hdf5 files from the directory to file as the given filename,
    with extension replaced with new dmap_filetype."""

    return usage_message


def borealis_conversion_parser():
    parser = argparse.ArgumentParser(usage=usage_msg())
    parser.add_argument("directory_to_convert", help="Path to the files you wish to convert to "
                                                   "SuperDARN dmap type.")
    return parser


def rawacf_borealis_converter(rawacf_file):

    rawacf_dmap_file = borealis_converter(rawacf_file, "rawacf")


def bfiq_borealis_converter(bfiq_file):

    bfiq_dmap_file = borealis_converter(bfiq_file, "iqdat")


if __name__ == "__main__":
    parser = borealis_conversion_parser()
    args = parser.parse_args()

    rawacf_pool = Pool(processes=4)
    bfiq_pool = Pool(processes=4)

    rawacf_hdf5_files = glob.glob(args.directory_to_convert + '*.rawacf.hdf5')
    rawacf_hdf5_files.extend(glob.glob(args.directory_to_convert + '*.rawacf.hdf5.bz2'))

    bfiq_hdf5_files = glob.glob(args.directory_to_convert + '*bfiq.hdf5')
    bfiq_hdf5_files.extend(glob.glob(args.directory_to_convert + '*bfiq.hdf5.bz2'))
    
    rawacf_pool.map(rawacf_borealis_converter, rawacf_hdf5_files)
    bfiq_pool.map(bfiq_borealis_converter, bfiq_hdf5_files)
