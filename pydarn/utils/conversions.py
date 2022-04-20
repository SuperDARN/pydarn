# Copyright 2019 SuperDARN Canada, University of Saskatchewan
# Author: Marina Schmidt
#
# Disclaimer:
# pyDARN is under the LGPL v3 license found in the root directory LICENSE.md
# Everyone is permitted to copy and distribute verbatim copies of this license
# document, but changing it is not allowed.
#
# This version of the GNU Lesser General Public License incorporates the terms
# and conditions of version 3 of the GNU General Public License,
# supplemented by the additional permissions listed below.
#
# Modification:
# 2022-03-10 MTS removed gate2slant and gate2groundscatter
#                to range_estimations.py
"""
This module is to focus on data conversions

All methods in this module are functions for
quick conversions.
"""
from typing import List
import numpy as np
from collections import OrderedDict


# key is the format char type defined by python,
# item is the DMAP int value for the type
DMAP_FORMAT_TYPES = {'c': 1,  # char = int8 by RST rtypes.h definition
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
# python doesn't have char types, instead it converts them to strings.
# This conversion is okay because RST treats chars as only int8 types.
FORMAT_CONVERSION = {np.int8: 'c',  # RST defines char as an int8 in rtypes.h
                     np.int16: 'h',
                     int: 'i',
                     np.int32: 'i',
                     float: 'f',
                     np.float32: 'f',
                     np.float64: 'd',
                     str: 's',
                     str: 's',
                     str: 's',
                     np.int64: 'q',
                     np.uint8: 'B',
                     np.uint16: 'H',
                     np.uint32: 'I',
                     np.uint64: 'Q'}

DMAP_CASTING_TYPES = {'c': np.int8,  # RST defined char
                      'h': np.int16,  # Short
                      'i': int,  # int
                      'f': float,  # Float
                      'd': np.float64,  # Double
                      's': str,  # String
                      'q': np.int64,  # long int
                      'B': np.uint8,  # Unsigned char
                      'H': np.uint16,  # Unsigned short
                      'I': np.uint32,  # Unsigned int
                      'Q': np.uint64}  # Unsigned long int


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
        dmap_dict = {field: (data.value if isinstance(data.value, np.ndarray)
                     else DMAP_CASTING_TYPES[data.data_type_fmt](data.value))
                     for field, data in dmap_record.items()}
        dmap_list.append(OrderedDict(dmap_dict))
    return dmap_list
