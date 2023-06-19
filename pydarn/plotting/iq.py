# Copyright (C) 2023 SuperDARN Canada, University of Saskwatchewan
# Author: Carley Martin
# This code is improvement based on rti.py in the DaVitpy library
# https://github.com/vtsuperdarn/davitpy/blob/master/davitpy
#
# Modifications:
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

"""
IQ plots
"""
import copy
import matplotlib.pyplot as plt
import numpy as np
import warnings

from datetime import datetime, timedelta
from matplotlib import dates, colors, cm, ticker
from typing import List

from pydarn import (RangeEstimation, check_data_type,
                    time2datetime, rtp_exceptions, plot_exceptions,
                    SuperDARNCpids, SuperDARNRadars,
                    standard_warning_format, PyDARNColormaps)

warnings.formatwarning = standard_warning_format

class IQ():
    """
    Time-series and range-time plots for IQ data
    
    Class pattern design: Builder
    This class inherits matplotlib.pyplot to inherit plotting features as well
    build off their builder design pattern.
    
    Notes
    -----
    This class inherits from matplotlib to generate the figures
    
    Methods
    -------
    plot_iq_time_series
    plot_iq
    """
    
    def __str__(self):
        return "This class is static class that provides"\
                " the following methods: \n"\
                "   - plot_time_series()\n"\
                "   - plot_iq()\n"


    @classmethod
    def plot_iq(cls, dmap_data: List[dict], beam_num: int=0,
                channel: int=0, ax=None, spec_time: datetime = None,
                sequence: int=0):
        """
        Plots IQ data
        
        Parameters
        -----------
        dmap_data: List[dict]
        beam_num : int
            The beam number of data to plot
            Default: 0
        channel : int or str
            The channel 0, 1, 2 ...
            Default : 0
        ax: matplotlib.axes
            axes object for another way of plotting
            Default: None
        spec_time: datetime
            Specified time of interest as a datetime object
        """
        # If an axes object is not passed in then store
        # the equivalent object in matplotlib. This allows
        # for variant matplotlib plotting styles.
        if not ax:
            ax = plt.gca()
        cls.dmap_data = dmap_data

        # If time is given, then find the record with the nearest time
        for i, record in enumerate(cls.dmap_data):
            rec_time = time2datetime(record)
            if record['bmnum'] == beam_num and record['channel'] == channel:
                
        
        # If beam and channel given then find the 
        
        # for a single record
        dmap_record = cls.dmap_data[0]
        smpnum = dmap_record['smpnum']
        chnnum = dmap_record['chnnum']
        seqnum = dmap_record['seqnum']
        
        iq_real = []
        iq_imag = []
        smp_count = 0
        psn_in_data = 0
        smp = 0
        while smp < smp_count + 2*smpnum:
            iq_real.append(dmap_record['data'][smp])
            smp=smp+1
            iq_imag.append(dmap_record['data'][smp])
            smp=smp+1
        smp_count = smp


        mag = [np.sqrt(i**2 + j**2) for i,j in zip(iq_real, iq_imag)]
        mag_neg = [-np.sqrt(i**2 + j**2) for i,j in zip(iq_real, iq_imag)]
        phase = np.arctan2(iq_imag,iq_real)
        plt.plot(mag, 'grey', linestyle='--')
        plt.plot(mag_neg, 'grey', linestyle='--')
        plt.plot(iq_real, 'r')
        plt.plot(iq_imag, 'b')
        
        #plt.plot(phase, 'y')
        plt.title('Raw Data in each Sample in one Sequence')
        plt.ylabel('Raw Data')
        plt.xlabel('Sample Number')
        plt.show()
#        # Set data shapes
#         y_max = max(record['smpnum'] for record in cls.dmap_data)
#         y = np.arange(0, y_max+1, 1)
#         z: parameter data mapped into the color mesh
#         z = np.zeros((1, y_max)) * np.nan
#         Start time data
#         x = []
# 
#         for dmap_record in cls.dmap_data:
#             rec_time =time2datetime(dmap_record)
#             diff_time = 0.0
#             if rec_time > end_time:
#                 break
#             if x != []:
#                 delta_diff_time = abs(rec_time - x[-1])
#                 diff_time = delta_diff_time.seconds/60.0
#                 if (rec_time - x[-1]) < timedelta(0):
#                     warn.warning("Please be aware that the data for timestamp {}"
#                           " contains a record that is not"
#                           " in time order. As such the plot of the"
#                           " data may not be correct, you can solve"
#                           " this by sorting the data stream by date"
#                           " before plotting.".format(rec_time))
# 
#             if diff_time > 2.0:
#                 for _ in range(0, int(np.floor(diff_time/2.0))):
#                     x.append(x[-1] + timedelta(0,120))
#                     i = len(x) - 1
#                     if i > 0:
#                         z = np.insert(z, len(z), np.zeros(1, y_max) * np.nan,
#                                       axis=0)
#             if (beam_num = 'all' or dmap_record['bmnum'] == beam_num):
#                 if start_time <= rec_time:
#                     x.append(rec_time)
#                     i = len(x - 1)
#                     if i > 0:
#                         z = np.insert(z, len(z), np.zeros(1, y_max) * np.nan,
#                                       axis=0)
#                     try:
                        
                
                
                
                
                
                