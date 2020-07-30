# Copyright (C) 2020 SuperDARN Canada, Universtiy of Saskatchewan
# Author(s): Daniel Billett
"""
This module is is used for sorting a given dmap_data list of dictionaries
into scans
"""

import numpy as np
from typing import List

def build_scan(dmap_data: List[dict]):
    """
    Returns list of size equal tonumber of records in dmap_data, with scan number
    for each record

    Parameters
    ----------
    dmap_data: List(dict)
        list of records (dictionaries) representing dmap data
    """ 
    # Setup scans for easy locating
    # Makes a list of size (number of records), with the scan number for each
    scan_mark = [sub['scan'] for sub in dmap_data]
    no_scans = 0
    beam_scan = np.zeros((len(dmap_data)))
    for beam in range(len(dmap_data)):
        if abs(scan_mark[beam]) == 1:
            no_scans += 1
            beam_scan[beam] = no_scans
        if scan_mark[beam] == 0:
            beam_scan[beam] = no_scans
    no_scans += 1
    
    return beam_scan