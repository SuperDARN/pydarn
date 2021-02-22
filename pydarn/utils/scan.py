# Copyright (C) 2020 SuperDARN Canada, Universtiy of Saskatchewan
# Author(s): Daniel Billett
"""
This module is used for sorting a given dmap_data list of dictionaries
into scans
"""

import numpy as np
from typing import List


def build_scan(dmap_data: List[dict]):
    """
    Returns list of size equal to number of records in dmap_data,
    with scan number for each record

    Parameters
    ----------
    dmap_data: List(dict)
        list of records (dictionaries) representing dmap data
    Returns
    ----------
    beam_scan: List
        list of size equal to number of records in dmap_data, with scan number
    for each record
    """
    # Set up scans for easy locating
    # Makes a list of size (number of records), with the scan number for each
    scan_mark = [sub['scan'] for sub in dmap_data]
    current_scan = 0
    beam_scan = np.zeros((len(dmap_data)))
    for beam in range(len(dmap_data)):
        # Absoloute value used due to some scan flags set as "-1"
        if abs(scan_mark[beam]) == 1:
            current_scan += 1
            beam_scan[beam] = current_scan
        if scan_mark[beam] == 0:
            beam_scan[beam] = current_scan

    return beam_scan
