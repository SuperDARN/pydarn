# Copyright (C) 2023 SuperDARN Canada, University of Saskwatchewan
# Author: Carley Martin
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
import matplotlib.pyplot as plt
import numpy as np
import warnings

from datetime import datetime
from typing import List

from pydarn import (time2datetime, standard_warning_format, find_record, RTP)

warnings.formatwarning = standard_warning_format


class IQ:
    """
    Time-series and specialised plots for IQ data

    Class pattern design: Builder
    This class inherits matplotlib.pyplot to inherit plotting features as well
    build off their builder design pattern.

    Notes
    -----
    This class inherits from matplotlib to generate the figures

    Methods
    -------
    plot_time_series
    plot_iq_sequence
    plot_iq_record
    plot_iq_overview
    """

    def __str__(self):
        return "This class is static class that provides"\
                " the following methods: \n"\
                "   - plot_time_series()\n"\
                "   - plot_iq_sequence()\n"\
                "   - plot_iq_record()\n"\
                "   - plot_iq_overview()\n"

    @staticmethod
    def plot_time_series(dmap_data: List[dict], **kwargs):
        """
        Plots scalar variables from IQ dat files

        SEE ALSO: RTP.plot_time_series() for more information and
        inputs

        Parameters
        ----------
        dmap_data: List[dict]

        Returns
        -------
        time_series_data: Lines, x, y
            standard return values from RTP.plot_time_series
        """
        time_series_info = RTP.plot_time_series(dmap_data, **kwargs)
        return time_series_info

    @staticmethod
    def plot_iq_sequence(dmap_data: List[dict],
                         start_time: datetime = None,
                         channel: int = 0, ax=None, beam_num: int = 0,
                         sequence_num: int = 0, interferometer: bool = False,
                         plot_phase: bool = False):
        """
        Plots a single sequence from a record of IQ data

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
        plot_phase: bool
            Option to plot the phase of the data (True)
            Default False
        """
        # Finds start of minute scan records, then scans the records to
        # find the next record with the correct beam
        if start_time is not None:
            record_num = find_record(dmap_data, start_time)
        else:
            record_num = 0
        # Get the next record with the correct beam
        while (dmap_data[record_num]['bmnum'] != beam_num
                and (dmap_data[record_num]['channel'] != channel
                     and channel != 'all')):
            record_num += 1
            if record_num >= len(dmap_data):
                raise Exception("No matching data found for beam {} "
                                "near time {}"
                                .format(beam_num,
                                        start_time.strftime('%Y-%m-%d' +
                                                            ' %H:%M:%S')))
        dmap_record = dmap_data[record_num]

        # Details from chosen record
        date = time2datetime(dmap_record)
        smpnum = dmap_record['smpnum']
        chnnum = dmap_record['chnnum']
        seqnum = dmap_record['seqnum']

        # Warning to too hihc sequence numberes
        if sequence_num >= seqnum:
            raise ValueError("Sequence numbers available for this record "
                             "range from 0 to {}.".format(seqnum-1))

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
            smp = smp + 1
            iq_imag.append(dmap_record['data'][smp])
            smp = smp + 1

        # Calculate magnitude and phase
        mag = [np.sqrt(i**2 + j**2) for i, j in zip(iq_real, iq_imag)]
        mag_neg = [-np.sqrt(i**2 + j**2) for i, j in zip(iq_real, iq_imag)]

        # Plotting phase if chosen
        if plot_phase:
            phase = np.arctan2(iq_imag, iq_real)
            fig = plt.gcf()
            fig.tight_layout()
            gs = fig.add_gridspec(3, 1)
            ax = fig.add_subplot(gs[0:2, :])
            ax2 = fig.add_subplot(gs[2, :])
            ax2.plot(phase, 'mediumseagreen')
            ax2.grid()
            ax2.set_ylabel('Phase')
            ax2.set_xlabel('Sample Number')
        elif ax is None:
            ax = plt.gca()

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

        return {'ax': ax,
                'ccrs': None,
                'cm': None,
                'cb': None,
                'fig': plt.gcf(),
                'data': {'iq_real': iq_real,
                         'iq_imag': iq_imag,
                         'magnitude': mag}
                }

    @staticmethod
    def plot_iq_record(dmap_data: List[dict],
                       start_time: datetime = None,
                       channel: int = 0, ax=None, beam_num: int = 0,
                       interferometer: bool = False,
                       cmap=plt.colormaps['viridis']):
        """
        Plots all sequences from a record of IQ data

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
        interferometer: bool
            Data from main array (False) or interferometer array (True)
            Default False
        cmap: matplotlib.cm object
            Default: viridis
        """
        # Finds start of minute scan records, then scans the records to
        # find the next record with the correct beam
        if start_time is not None:
            record_num = find_record(dmap_data, start_time)
        else:
            record_num = 0
        # Get the next record with the correct beam
        while (dmap_data[record_num]['bmnum'] != beam_num
                and (dmap_data[record_num]['channel'] != channel
                     and channel != 'all')):
            record_num += 1
            if record_num >= len(dmap_data):
                raise Exception("No matching data found for beam {} "
                                "near time {}"
                                .format(beam_num,
                                        start_time.strftime('%Y-%m-%d' +
                                                            ' %H:%M:%S')))
        dmap_record = dmap_data[record_num]

        # Details from chosen record
        date = time2datetime(dmap_record)
        smpnum = dmap_record['smpnum']
        chnnum = dmap_record['chnnum']
        seqnum = dmap_record['seqnum']

        if interferometer and chnnum < 2:
            raise ValueError("No interferometer data for record chosen.")

        # Calculate starting data position
        # For layout of data and how to access see:
        # https://radar-software-toolkit-rst.readthedocs.io
        # /en/latest/references/general/iqdat/
        iq_real_arr = np.empty([smpnum, seqnum])
        iq_imag_arr = np.empty([smpnum, seqnum])
        for seq in range(0, seqnum):
            if interferometer:
                smp = seq * chnnum * 2 * smpnum + 2 * smpnum
            else:
                smp = seq * chnnum * 2 * smpnum
            iq_real_arr[:, seq] = dmap_record['data'][smp: smp + smpnum]
            iq_imag_arr[:, seq] =\
                dmap_record['data'][smp + smpnum: smp + 2*smpnum]

        # Calculate magnitude
        mag = np.sqrt(iq_real_arr**2 + iq_imag_arr**2)
        # Plot
        if ax is None:
            ax = plt.gca()
        pcol = ax.pcolormesh(mag, vmin=0, vmax=600, cmap=cmap)
        cb = ax.figure.colorbar(pcol, extend='max')
        cb.set_label('Power (AU)')

        # Plot title and axis labels
        if interferometer:
            array_type = 'Interferometer Array'
        else:
            array_type = 'Main Array'
        ax.set_title('IQ Data for ' + array_type + '\n Beam='
                     + str(beam_num) + ' '
                     + date.strftime('%Y-%m-%d %H:%M:%S'))
        ax.set_ylabel('Sample Number')
        ax.set_xlabel('Sequence Number')
        ax.grid()

        return {'ax': ax,
                'ccrs': None,
                'cm': cmap,
                'cb': cb,
                'fig': plt.gcf(),
                'data': {'iq_real': iq_real_arr,
                         'iq_imag': iq_imag_arr,
                         'magnitude': mag}
                }

    @staticmethod
    def __determine_start_end_time(dmap_data, start_time: datetime,
                                   end_time: datetime) -> tuple:
        """
        Sets the start and end time based on import of dmap_data

        Parameter
        ---------
        dmap_data: List[dict]
        start_time: datetime
            Start time is used to check if it was set or not
        end_time: datetime
            End time is used to check if it was set or not

        Returns
        -------
        start_time: datetime
        end_time: datetime
        """
        if not start_time:
            start_time = time2datetime(dmap_data[0])
        if not end_time:
            end_time = time2datetime(dmap_data[-1])
        return start_time, end_time

    @staticmethod
    def plot_iq_overview(dmap_data: List[dict],
                         start_time: datetime = None,
                         end_time: datetime = None,
                         channel: int = 0, ax=None, beam_num: int = 'all',
                         interferometer: bool = False,
                         cmap: object = plt.colormaps['viridis']):
        """
        Plots all sequences from a record of IQ data

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
            Specified start time of interest as a datetime object
        end_time: datetime
            Specified end time of interest as a datetime object
        interferometer: bool
            Data from main array (False) or interferometer array (True)
            Default False
        cmap: matplotlib.cm object
            Default: viridis
        """
        start_time, end_time = IQ.__determine_start_end_time(dmap_data,
                                                             start_time,
                                                             end_time)

        # Assuming the samples and sequences will stay constant
        # over the file
        smpnum = dmap_data[0]['smpnum']
        chnnum = dmap_data[0]['chnnum']
        seqnum = dmap_data[0]['seqnum']

        # Empty lists to append data to
        # TODO: did not work using arrays
        iq_real_arr = []
        iq_imag_arr = []
        for dmap_record in dmap_data:
            if (dmap_record['bmnum'] == beam_num or beam_num == 'all') and\
                    (dmap_record['channel'] == channel or channel == 'all'):
                rec_time = time2datetime(dmap_record)
                if start_time <= rec_time <= end_time:
                    if interferometer and chnnum < 2:
                        raise ValueError("No interferometer data for "
                                         "record chosen.")

                    # Calculate starting data position
                    # For layout of data and how to access see:
                    # https://radar-software-toolkit-rst.readthedocs.io
                    # /en/latest/references/general/iqdat/
                    for seq in range(0, seqnum):
                        if interferometer:
                            smp = seq * chnnum * 2 * smpnum + 2 * smpnum
                        else:
                            smp = seq * chnnum * 2 * smpnum
                        iq_real = dmap_record['data'][smp: smp + smpnum]
                        iq_imag =\
                            dmap_record['data'][smp + smpnum: smp + 2*smpnum]
                        if len(iq_real) == smpnum:
                            iq_real_arr.append(iq_real)
                            iq_imag_arr.append(iq_imag)

        # Convert to arrays, dtype important for mag calc
        iq_real_arr = np.array(iq_real_arr, dtype='float64')
        iq_imag_arr = np.array(iq_imag_arr, dtype='float64')
        # Calculate magnitude
        mag = np.sqrt(np.add(np.square(iq_real_arr), np.square(iq_imag_arr)))

        # Plot
        if ax is None:
            ax = plt.gca()
        pcol = ax.pcolormesh(mag.T, vmin=0, vmax=1000, cmap=cmap)
        cb = ax.figure.colorbar(pcol, extend='max')
        cb.set_label('Power (AU)')

        # Plot title and axis labels
        if interferometer:
            array_type = 'Interferometer Array'
        else:
            array_type = 'Main Array'
        ax.set_title('IQ Data for ' + array_type + ' Beam='
                     + str(beam_num) + '\n'
                     + start_time.strftime('%Y-%m-%d %H:%M:%S') + ' - '
                     + end_time.strftime('%Y-%m-%d %H:%M:%S'))
        ax.set_ylabel('Sample Number')
        ax.set_xlabel('Sequence Number')
        ax.grid()

        return {'ax': ax,
                'ccrs': None,
                'cm': cmap,
                'cb': cb,
                'fig': plt.gcf(),
                'data': {'iq_real': iq_real_arr,
                         'iq_imag': iq_imag_arr,
                         'magnitude': mag}
                }
