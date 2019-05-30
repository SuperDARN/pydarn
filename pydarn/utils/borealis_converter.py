import sys
import os
import argparse
import bz2

from pydarn import BorealisConvert

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
    parser.add_argument("--dmap_filename", help="The filename you would like to write to. Default will replace "
                                                "the last two extensions of the input file with [dmap_filetype].dmap")

    return parser


def create_dmap_filename(filename_to_convert, dmap_filetype):
    """
    Creates a dmap filename in the same directory as the source .hdf5 file, 
    to write the DARN dmap file to.
    """
    basename = os.path.basename(filename_to_convert)
    basename_without_ext = '.'.join(basename.split('.')[0:-2]) # all but .rawacf.hdf5, for example.
    dmap_filename = os.path.dirname(filename_to_convert) + '/' + basename_without_ext + '.' + dmap_filetype + '.dmap'
    return dmap_filename


def borealis_write_to_dmap(filename, dmap_filetype, dmap_filename):
    """
    Convert the borealis file to Darn dmap filetype.
    """
    borealis_data = BorealisConvert(filename)
    print('Read the file {filename}'.format(filename=filename))
    dmap_filename = borealis_data.write_to_dmap(dmap_filetype, dmap_filename)

    print("Borealis file {filename} written to {dmap_filename} without errors."
          "".format(filename=borealis_data.filename, 
                            dmap_filename=dmap_filename))    


def decompress_bz2(filename):
    basename = os.path.basename(filename) 
    newfilepath = os.path.dirname(filename) + '/' + '.'.join(basename.split('.')[0:-1]) # all but bz2

    with open(newfilepath, 'wb') as new_file, bz2.BZ2File(filename, 'rb') as file:
        for data in iter(lambda : file.read(100 * 1024), b''):
            new_file.write(data)    

    return newfilepath


def compress_bz2(filename):
    bz2_filename = filename + '.bz2'

    with open(filename, 'rb') as file, bz2.BZ2File(bz2_filename, 'wb') as bz2_file:
        for data in iter(lambda : file.read(100 * 1024), b''):
            bz2_file.write(data)   

    return bz2_filename


def borealis_converter(filename, dmap_filetype, dmap_filename=None):
    """
    Checks if the file is bz2, decompresses if necessary, and 
    writes to a dmap file. If the file was bz2, then the resulting dmap
    file will also be compressed to bz2.
    """

    if os.path.basename(filename).split('.')[-1] in ['bz2', 'bzip2']:
        borealis_hdf5_file = decompress_bz2(filename)
        bzip2 = True
    else:
        borealis_hdf5_file = filename
        bzip2 = False

    if dmap_filename is None:
        dmap_filename = create_dmap_filename(borealis_hdf5_file, dmap_filetype)

    borealis_write_to_dmap(borealis_hdf5_file, dmap_filetype, dmap_filename)

    if bzip2:
        # remove the input file from the directory because it was generated.
        os.remove(borealis_hdf5_file)
        # compress the dmap file to bz2 if the input file was given as bz2.
        bz2_filename = compress_bz2(dmap_filename)
        os.remove(dmap_filename)
        dmap_filename = bz2_filename

    return dmap_filename


def main():
    parser = borealis_conversion_parser()
    args = parser.parse_args()

    borealis_converter(args.borealis_hdf5_file, args.dmap_filetype, args.dmap_filename)


if __name__ == "__main__":
    main()
