import sys
import os
import argparse

from pydarn.io.borealis import BorealisFileHandler

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
    										  "iqdat.")

    return parser


def main():
	parser = borealis_conversion_parser()
	args = parser.parse_args()

	borealis_data = BorealisFileHandler(args.borealis_hdf5_file)
	print('Read the file {filename}'.format(filename=args.borealis_hdf5_file))
	dmap_filename = borealis_data.write_to_dmap(args.dmap_filetype)

	print("Borealis file {filename} written to {dmap_filename} without errors. "
		  "Exiting.".format(filename=borealis_data.filename, 
		  	                dmap_filename=dmap_filename))


if __name__ == "__main__":
    main()
