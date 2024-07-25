# Copyright (C) 2020 SuperDARN Canada, Universtiy of Saskatchewan
# Author(s): Daniel Billett
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
#
"""
This module is used for sorting a given dmap_data list of dictionaries
into scans
"""

import datetime
import numpy as np
from typing import List
from pydarn import time2datetime


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
    timestamps = [time2datetime(rec) for rec in dmap_data]
    timestamps_seen = []
    current_scan = 0
    first_time = True
    beam_scan = np.zeros((len(dmap_data)))
    for i in range(len(dmap_data)):
        # Check if this record is concurrent with another record
        if timestamps[i] in timestamps_seen:
            beam_scan[i] = current_scan
        else:
            timestamps_seen.append(timestamps[i])   # Record the timestamp from this file

            # Absolute value used due to some scan flags set as "-1"
            if abs(scan_mark[i]) == 1 and not first_time:
                current_scan += 1
            first_time = False
            beam_scan[i] = current_scan

    return beam_scan


def find_records_by_datetime(dmap_data: List[dict], search: datetime.datetime,
                             tolerance: datetime.timedelta):
    """
    Returns the records which are within a certain timeframe relative to a search time.

    Parameters
    ----------
    dmap_data: List(dict)
        list of records (dictionaries) representing dmap data
    search: datetime.datetime
        datetime to search for records matching this time
    tolerance: datetime.timedelta
        how far off in time the records can be and still be a hit
    Returns
    ----------
    recs: List(dict)
        list of records that are close enough in time to search value
    """
    timestamps = np.array([time2datetime(rec) for rec in dmap_data])
    matches = np.nonzero(np.abs(timestamps - search) < tolerance)[0]
    return [dmap_data[match] for match in matches]


def find_records_by_scan(dmap_data: List[dict], scan_index: int):
    """
    Returns the records which are from the scan corresponding to scan_index
    in the file.

    Parameters
    ----------
    dmap_data: List(dict)
        list of records (dictionaries) representing dmap data
    scan_index: int
        index of scan in file to return
    Returns
    ----------
    recs: List(dict)
        list of records that match the search criteria
    """
    scan_indices = build_scan(dmap_data)
    matches = np.nonzero(scan_indices == scan_index)[0]
    return [dmap_data[match] for match in matches]