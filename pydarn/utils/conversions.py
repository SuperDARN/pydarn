# Copyright 2019 SuperDARN
# Author: Marina Schmidt

"""
This module is to focus on data conversions

All methods in this module are functions for
quick conversions.
"""
from typing import List
import numpy as np
from collections import OrderedDict

from pydarn import DmapArray, DmapScalar

# key is the format char type defined by python, item is the DMAP int value for the type
DMAP_FORMAT_TYPES = {'c': 1,  # character (char)
                     'h': 2,  # short integer
                     'i': 3,  # integer (int)
                     'f': 4,  # float
                     'd': 8,  # double
                     's': 9,  # string
                     'q': 10,  # Long int
                     'B': 16,  # unsigned char
                     'H': 17,  # unsigned short int
                     'I': 18,  # unsigned int
                     'Q': 19}  # unsigned long int

# python possible types that could be the python format type characters
FORMAT_CONVERSION = {chr: 'c',  # Python doesn't actually have chars :/ they are just casted to strings
                     np.char: 'c',  # not sure how to test this, you cannot use np.char() ¯\_(ツ)_/¯
                     np.int8: 'c',  # not sure how a int is a char?
                     np.int16: 'h',
                     int: 'i',
                     np.int32: 'i',
                     float: 'f',
                     np.float32: 'f',
                     np.float64: 'd',
                     str: 's',
                     np.str_: 's',
                     np.str: 's',
                     np.int64: 'q',
                     np.uint8: 'B',
                     np.uint16: 'H',
                     np.uint32: 'I',
                     np.uint64: 'Q'}

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#       WARNING: This converts on best effort
#       python does not have character types, if
#       a string has a length of 1 then it will
#       be treated as a char.
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def dict2dmap(dmap_list: List[dict]) -> List[dict]:
    """
    This method converts list of dictionaries contain keys representing a field
    name for the DMAP format and the item being the value of the field.

    Parameters
    ----------
    dmap_list : List[dict]
        List of dictionaries containing the field names and the
        values of the data

    Return
    ------
    dmap_records : List[dict]
        List of Ordered dictionaries containing dmap data structures
        DmapScalars and DmapArrays.
    """
    dmap_records = []
    for dmap_dict in dmap_list:
        dmap_record = OrderedDict()
        for field, value in dmap_dict.items():
            # if the value is an array then it is a DmapArray
            if isinstance(value, list):
                value = np.array(value)  # keep data structures consistent
            if isinstance(value, np.ndarray):
                shape = np.shape(value)
                dimension = np.ndim(value)
                # I did not implement the string length check to see if
                # it is a list of chars because one would need to look at
                # every element in the array, and it might be better to just
                # store it as a string at this point.
                format_type = FORMAT_CONVERSION[value.dtype.type]
                dmap_type = DMAP_FORMAT_TYPES[format_type]
                dmap_data = DmapArray(field, value, dmap_type,
                                      format_type, dimension, shape)

            # else DmapScalar
            else:
                format_type = FORMAT_CONVERSION[type(value)]
                # check the length and if it equal to one then consider
                # it a char
                if format_type == 's' and len(value) == 1:
                    format_type = 'c'
                dmap_type = DMAP_FORMAT_TYPES[format_type]
                dmap_data = DmapScalar(field, value, dmap_type, format_type)
            dmap_record[field] = dmap_data
        dmap_records.append(dmap_record)
    return dmap_records


def dmap2dict(dmap_records: List[dict]) -> List[dict]:
    """
    This method converts dmap records containing dmap data structures
    to a list of dictionaries.

    Parameters
    ----------
    dmap_records : List[dict]
        a list of dmap records contain dmap data structures

    Return
    ------
    dmap_dict : List[dict]
        a list of dictionaries containing the name of the fields in the keys
        the data value(s) in the items of the dictionary
    """
    dmap_list = []
    for dmap_record in dmap_records:
        dmap_dict = {field: data.value for field, data in dmap_record.items()}
        dmap_list.append(dmap_dict)
    return dmap_list
