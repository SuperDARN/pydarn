# Copyright 2019 SuperDARN Canada, University of Saskatchewan
# Author: Marina Schmidt

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
                     np.str_: 's',
                     np.str: 's',
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


def gate2slant(record, nrang, center=True):
    """
    Calculate the slant range (km) for each range gate for SuperDARN data

    Parameters
    ----------
        record: dict
            dictionary of superdarn data records
        nrang: int
            max number of range gates in the list of records
        center: boolean
            Calculate the slant range in the center of range gate
            or edge

    Returns
    -------
        slant_ranges : np.array
            returns an array of slant ranges for the radar
    """

    # lag to the first range gate in microseconds
    # 0.3 - speed of light (km/us)
    # 2 - two times for there and back
    speed_of_light = 0.3  # TODO: should this be more accurate?
    distance_factor = 2.0
    lag_first = record['frang'] * distance_factor / speed_of_light

    # sample separation in microseconds
    sample_sep = record['rsep'] * distance_factor / speed_of_light
    # Range offset
    # If center is true, calculate at the center
    if center:
        # 0.5 off set to the centre of the range gate instead of edge
        range_offset = -0.5 * record['rsep']
    else:
        range_offset = 0.0

    # Now calculate slant range in km
    slant_ranges = np.zeros(nrang+1)
    for gate in range(nrang+1):
        slant_ranges[gate] = (lag_first - record['rxrise'] +
                              gate * sample_sep) * speed_of_light /\
                distance_factor + range_offset
    return slant_ranges
