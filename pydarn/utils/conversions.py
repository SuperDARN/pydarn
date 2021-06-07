# Copyright 2019 SuperDARN Canada, University of Saskatchewan
# Author: Marina Schmidt
# Copyright 2021 University of Scranton
# Author: Francis Tholley and Dr. Nathaniel Frissel for gate2groundscatter
"""
This module is to focus on data conversions

All methods in this module are functions for
quick conversions.
"""
from typing import List
import numpy as np
from collections import OrderedDict

from pydarn import (Re, C)


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


def gate2GroundScatter(slant_ranges: List[float],
                       reflection_height: float = 250):
    """
    Calculate the ground scatter mapped range (km) for each slanted range
    for SuperDARN data. This function is based on the Ground Scatter equation
    from Bristow paper at https://doi.org/10.1029/93JA01470 on page 325
    Parameters
    ----------
        slant_ranges : List[float]
            list of slant ranges
        reflection_height: float
            reflection height
            default:  250

    Returns
    -------
        ground_scatter_mapped_ranges : np.array
            returns an array of ground scatter mapped ranges for the radar
    """

    ground_scatter_mapped_ranges =\
        Re*np.arcsin(np.sqrt((slant_ranges**2/4)-(reflection_height**2))/Re)

    return ground_scatter_mapped_ranges


def gate2slant(frang:int, rsep:int, rxrise:int, gate: int = 0,
               nrang: int = None, center: bool = True):
    """
    Calculate the slant range (km) for each range gate for SuperDARN data

    Parameters
    ----------
        frang: int
            range from the edge of first the gate to the radar [km]
            This should be given in fitacf record of the control program
        rsep: int
            Radar seperation of the gates. Determined by control program.
        rxrise: int
            Use hardware value for this, avoid data file values
        gate: int
            range gate to determine the slant range [km], if nrang
            is None
            default: 0
        nrang: int
            max number of range gates in the list of records. If
            not None, will calculate all slant ranges
            default: None
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
    distance_factor = 2.0
    # C - speed of light m/s to km/us
    speed_of_light = C * 0.001 * 1e-6
    lag_first = frang * distance_factor / speed_of_light

    # sample separation in microseconds
    sample_sep = rsep * distance_factor / speed_of_light
    # Range offset
    # If center is true, calculate at the center
    if center:
        # 0.5 off set to the centre of the range gate instead of edge
        range_offset = -0.5 * rsep
    else:
        range_offset = 0.0
    # Now calculate slant range in km
    if nrang is None:
             slant_ranges = (lag_first - rxrise +
                                  gate * sample_sep) * speed_of_light /\
                    distance_factor + range_offset
    else:
        slant_ranges = np.zeros(nrang+1)
        for gate in range(nrang+1):
            slant_ranges[gate] = (lag_first - rxrise +
                                  gate * sample_sep) * speed_of_light /\
                    distance_factor + range_offset
    return slant_ranges
