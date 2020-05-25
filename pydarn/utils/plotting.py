# Copyright (C) 2020 SuperDARN Canada, Universtiy of Saskatchewan
# Author(s): Marina Schmidt
"""
This module is utility functions that are useful
for multiple plotting methods
"""

import numpy as np

from datetime import datetime
from typing import List

from pydarn import plot_exceptions


def check_data_type(dmap_data: List[dict], parameter: str,
                    expected_type: str, index: int):
    """
    Checks to make sure the plot type is correct
    for the data structure

    Parameters
    ----------
    dmap_data: List(dict)
        list of records (dictionaries) representing
        DNap data
    parameter: str
        string key word name of the parameter
    expected_type: str
        string describing an array or scalar type
        to determine which one is needed for the type of plot
    index: int
        record number to check
    Raises
    -------
    RTPIncorrectPlotMethodError
    """
    data_type = dmap_data[index][parameter]
    if expected_type == 'array':
        if not isinstance(data_type, np.ndarray):
            raise plot_exceptions.IncorrectPlotMethodError(parameter,
                                                           data_type)
    else:
        if isinstance(data_type, np.ndarray):
            # TODO: make into a general plotting exception
            raise plot_exceptions.IncorrectPlotMethodError(parameter,
                                                           data_type)


def time2datetime(dmap_record: dict) -> datetime:
    """
    Converts DMAP time parameter fields into a datetime object

    Parameter
    ---------
    dmap_record: dict
        dictionary of the DMAP data contains the time data

    Returns
    -------
    datetime object
        returns a datetime object of the records time stamp
    """
    year = dmap_record['time.yr']
    month = dmap_record['time.mo']
    day = dmap_record['time.dy']
    hour = dmap_record['time.hr']
    minute = dmap_record['time.mt']
    second = dmap_record['time.sc']
    micro_sec = dmap_record['time.us']

    return datetime(year=year, month=month, day=day, hour=hour,
                    minute=minute, second=second, microsecond=micro_sec)
