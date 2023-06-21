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

from pydarn import (time2datetime, standard_warning_format, find_record)

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
    def plot_iq(cls, dmap_data: List[dict], start_time: datetime = None,
                channel: int=0, ax=None, beam_num: int=0,
                sequence_num: int=0, interferometer: bool=False):
        """
        Plots IQ data
        
        Parameters
        -----------
        dmap_data: List[dict]
        beam_num : int
            The beam number of data to plot
            Default: 0
        channel : int or str
            The frequency channel 0, 1, 2 ...
            Default : 0
        ax: matplotlib.axes
            axes object for another way of plotting
            Default: None
        start_time: datetime
            Specified time of interest as a datetime object
        sequence_num: int
            Sequence in the record to be plotted
            Default: 0
        interferometer: bool
            Data from main array (False) or interferometer array (True)
            Default False
        """
        if not ax:
            ax = plt.gca()
        cls.dmap_data = dmap_data

        # Finds start of minute scan records, then scans the records to 
        # find the next record with the correct beam
        if start_time is not None:
            record_num = find_record(cls.dmap_data, start_time)
        else:
            record_num = 0
        # Get the next record with the correct beam
        while dmap_data[record_num]['bmnum'] != beam_num:
            record_num += 1
            if record_num >= len(dmap_data):
                raise Exception("No matching data found for beam {} "
                                "near time {}".format(beam_num,
                                start_time.strftime('%Y-%m-%d %H:%M:%S')))
        dmap_record = dmap_data[record_num]

        # Details from chosen record
        date = time2datetime(dmap_record)
        smpnum = dmap_record['smpnum']
        chnnum = dmap_record['chnnum']
        seqnum = dmap_record['seqnum']

        # Warning to too hihc sequence numberes
        if sequence_num >= seqnum:
            raise ValueError("Sequence numbers available for this record range "
                         "from 0 to {}.".format(seqnum-1))

        if interferometer and chnnum < 2:
            raise ValueError("No interferometer data for record chosen.")
        
        # Calculate starting data position
        # For layout of data and how to access see:
        # https://radar-software-toolkit-rst.readthedocs.io
        # /en/latest/references/general/iqdat/
        if interferometer:
            smp = sequence_num * chnnum * 2 * smpnum + 2 * smpnum
        else:
            smp = sequence_num * chnnum * 2 * smpnum
        iq_real = []
        iq_imag = []
        smp_initial = smp
        while smp < smp_initial + 2*smpnum:
            iq_real.append(dmap_record['data'][smp])
            smp=smp+1
            iq_imag.append(dmap_record['data'][smp])
            smp=smp+1

        # Calculate magnitude and phase
        mag = [np.sqrt(i**2 + j**2) for i,j in zip(iq_real, iq_imag)]
        mag_neg = [-np.sqrt(i**2 + j**2) for i,j in zip(iq_real, iq_imag)]
        phase = np.arctan2(iq_imag,iq_real)

        # Plot lines
        real_line, = ax.plot(iq_real, 'r')
        imag_line, = ax.plot(iq_imag, 'b')
        mag_line, = ax.plot(mag, 'grey', linestyle='--', linewidth=0.5)
        ax.plot(mag_neg, 'grey', linestyle='--', linewidth=0.5)

        # Plot legend and labels
        real_line.set_label('Real')
        imag_line.set_label('Imaginary')
        mag_line.set_label('Magnitude')
        ax.legend()

        # Plot title and axis labels
        #plt.plot(phase, 'y')
        if interferometer:
            array_type = 'Interferometer Array'
        else:
            array_type = 'Main Array'
        ax.set_title('IQ Data for ' + array_type + '\n Beam='
                     + str(beam_num) + ' '
                     + ' Sequence=' + str(sequence_num) + '\n '
                     + date.strftime('%Y-%m-%d %H:%M:%S'))
        ax.set_ylabel('Raw Data')
        ax.set_xlabel('Sample Number')
        ax.grid()
