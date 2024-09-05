# Copyright (C) 2020 SuperDARN Canada, Universtiy of Saskatchewan
# Author(s): Marina Schmidt
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
"""
This module is utility functions that are useful
for multiple plotting methods
"""
import datetime as dt
import enum
import matplotlib.pyplot as plt
import numpy as np
import warnings

from typing import List

from pydarn import plot_exceptions

class MapParams(enum.Enum):
    """
    """
    FITTED_VELOCITY = "fitted"
    MODEL_VELOCITY = "model.vel.median"
    RAW_VELOCITY = "vector.vel.median"
    POWER = "vector.pwr.median"
    SPECTRAL_WIDTH = "vector.wdt.median"

class TimeSeriesParams(enum.Enum):
        """
        Enum class to hold the parameters that can be plotted
        Members
        ------------
        NUM_VECTORS:
        the number of aviliable vectors in the map
        IMF_BY:
        The magnitude of the IMF By component in nT
        IMF_BZ:
        The magnitude of the IMF Bz component in nT
        KP:
        The Kp index
        HMB_MAX:
        The farthest equatorward extent of the HMB

        """
        NUM_VECTORS = 'num_vectors'
        IMF_BY = 'IMF.By'
        IMF_BZ = 'IMF.Bz'
        IMF_BX = 'IMF.Bx'
        IMF_Vx = 'IMF.Vx'
        IMF_TILT = 'IMF.tilt'
        KP = 'IMF.Kp'
        LATMINN = 'latmin'
        ERR = 'chi.sqr.dat'
        CPP = 'pot.drop'
        POT = 'pot.pos'
        

def find_record(dmap_data: List[dict], start_time: dt.datetime, time_delta:int = 1):
    """
    finds the record number that associates to the start time

    Parameter
    ---------
        dmap_data : List[dict]
            the data to look over for the record number
        start_time : datetime
            the start_time to associate to the record number
        time_delta : int
            the difference between start_time and dmap_data time to determine
            the record number within a region

    Return
    ------
        record_num : int
            the record number associated with the start_time

    Raises
    ------
        NoDataFound
            raises if the start_time is not in the dmap_data list
    """
    record_num = 0
    for record in dmap_data:
        date = time2datetime(record)
        time_diff = date - start_time
        if time_diff.seconds/60 <= time_delta:
            return record_num
        record_num += 1
    raise plot_exceptions.NoDataFoundError('N/A', start_time=start_time)

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


def time2datetime(dmap_record: dict) -> dt.datetime:
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
    try:
        year = dmap_record['time.yr']
        month = dmap_record['time.mo']
        day = dmap_record['time.dy']
        hour = dmap_record['time.hr']
        minute = dmap_record['time.mt']
        second = dmap_record['time.sc']
        micro_sec = dmap_record['time.us']
        return dt.datetime(year=year, month=month, day=day, hour=hour,
                           minute=minute, second=second, microsecond=micro_sec)
    except KeyError:
        year = dmap_record['start.year']
        month = dmap_record['start.month']
        day = dmap_record['start.day']
        hour = dmap_record['start.hour']
        minute = dmap_record['start.minute']
        second = dmap_record['start.second']
        return dt.datetime(year=year, month=month, day=day, hour=hour,
                           minute=minute, second=int(second))


def add_embargo(fig: plt.Figure):
    """
    Adds a watermark to the figure noting that the data is under
    embargo

    Parameter
    ---------
    fig: plt.Figure
    """
    vals = []
    for t in range(0, len(fig.texts)):
        vals.append(fig.texts[t].get_text())
    if not any(item == 'EMBARGOED' for item in vals):
        fig.text(0.5, 0.5, "EMBARGOED", fontsize=70,
                 color='grey', ha='center', va='center',
                 rotation=-20, alpha=0.7)


def determine_embargo(time: dt.datetime, cpid: int, radar: str):
    """
    Determines if the data is under embargo

    Parameter
    ---------
    time: dt.datetime
        Timestamp of the data
    cpid: int
        Control program ID
    radar: str
        Name of the radar which produced the data

    Returns
    -------
    bool: True if data is embargoed, False otherwise
    """
    year_ago = dt.datetime.now() - dt.timedelta(days=365)
    if time > year_ago and cpid < 0:
        warnings.warn(f'The data you are using is under embargo. '
                      f'Please contact the principal investigator '
                      f'of the {radar} radar for authorization to '
                      f'use the data')
        return True
    else:
        return False
