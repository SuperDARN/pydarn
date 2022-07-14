# Copyright (C) 2020 SuperDARN Canada, University of Saskatchewan
# Author: Marina Schmidt
# This code is based on acf.py in the DaVitpy library
# https://github.com/vtsuperdarn/davitpy/blob/master/davitpy
# Modifications:
# 2022-05-03: CJM - Added options to plot power and phase of acf
#                 - change defaults to fit needs
#
# Disclaimer:
# pyDARN is under the LGPL v3 license found in the root directory LICENSE.md
# Everyone is permitted to copy and distribute verbatim copies of this license
# document, but changing it is not allowed.
#
# This version of the GNU Lesser General Public License incorporates the terms
# and conditions of version 3 of the GNU General Public License,
# supplemented by the additional permissions listed below.


import copy
import matplotlib.pyplot as plt
import numpy as np
import warnings
import matplotlib.ticker as ticker

from datetime import datetime
from typing import List

from pydarn import (plot_exceptions, SuperDARNRadars,
                    standard_warning_format, time2datetime,
                    check_data_type)

warnings.formatwarning = standard_warning_format


class ACF():
    """
    ACF class plots SuperDARN RAWACF data

    Class pattern design: Builder
    This class inherits matplotlib.pyplot to inherit plotting features as well
    build off their builder design pattern.

    Notes
    -----
    This class extends from matplotlib to generate the figures

    Methods
    -------
    plot
    plot_amplitude (not implemented yet)
    """

    def __str__(self):
        return "This class is static class that provides"\
                " the following methods: \n"\
                "   - plot_acfs()\n"\


    @classmethod
    def plot_acfs(cls, dmap_data: List[dict], beam_num: int = 0,
                  gate_num: int = 15, parameter: str = 'acfd',
                  scan_num: int = 0, start_time: datetime = None,
                  normalized: bool = False, real_color: str = 'red',
                  plot_blank: bool = True, blank_marker: str = 'o',
                  imaginary_color: str = 'blue', legend: bool = True,
                  pwr_and_phs: bool = True, **kwargs):
        """
        plots the parameter ACF/XCF field from SuperDARN file,
        typically RAWACF format for a given beam and gate number

        Parameters
        ----------
        dmap_data : list[dict]
            records from a dmap file
        beam_num : int
            the beam number to plot, default: 0
        gate_num : int
            the gate number to plot, default: 15
        parameter : str
            the parameter to plot, default: acfd
        scan_number: int
            will plot the scan number for the provided beam
        start_time: datetime object
            datetime object containing the record to plot for
            the given beam
        ax: matplotlib.axes
            axes object for another way of plotting
            Default: None
        normalized: bool
            normalizes the parameter data with the associated
            power 0 value for the given gate number
            default: False
        real_color: str
            line color of the real part of the paramter
            default: red
        plot_blank: bool
            boolean to determine if blanked lags should be plotted
            default: False
        blank_marker: str
            the marker symbol of blanked lags
            default: o - dot
        imaginary_color: str
            line color of the imaginary part of the parameter
            default: blue
        legend: bool
            produces a standard legend
            default: True
        pwr_and_phs: bool
            plots the power and phase of the ACF
            default: True
        kwargs: dict
            are applied to the real and imaginary plots


        Notes
        -----
        plot blanked lags as hollow circles

        Raises
        ------
        UnkownParameterError
        IncorrectPlotMethodError
        OutOfRangeGateError

        Returns
        -------

        """
        # Determine if a DmapRecord was passed in, instead of a list
        try:
            # because of partial records we need to find the first
            # record that has that parameter
            index_first_match = next(i for i, d in enumerate(dmap_data)
                                     if parameter in d)
        except StopIteration:
            raise plot_exceptions.UnknownParameterError(parameter)
        cls.dmap_data = dmap_data
        check_data_type(cls.dmap_data, parameter, 'array', index_first_match)

        # search over the records to find the correct beam, and scan/time
        # to plot the corresponding ACF/XCF plot
        scan_count = 0
        re = []
        im = []
        for record in cls.dmap_data:
            if record['bmnum'] == beam_num:
                time = time2datetime(record)
                if start_time is not None:
                    if time.day != start_time.day or \
                       time.month != start_time.month or \
                       time.year != start_time.year:
                        raise plot_exceptions.IncorrectDateError(time,
                                                                 start_time)

                if cls.__found_scan(scan_num, scan_count, start_time, time):
                    if gate_num >= record['nrang'] or gate_num < 0:
                        raise plot_exceptions.\
                                OutOfRangeGateError(parameter, gate_num,
                                                    record['nrang'])
                    # get the difference to get the lag number
                    lags = [lag[1] - lag[0] for lag in record['ltab']]
                    # remove the last lag as it is the zeroth lag
                    lags = lags[:-1]

                    # grab corresponding real and imaginary parts
                    # of the ACF/XCF field for a given gate number
                    re = [x[0] for x in record[parameter][gate_num]]
                    im = [x[1] for x in record[parameter][gate_num]]

                    # calculate the blank lags for this record and gate
                    blanked_lags = cls.__blanked_lags(record, lags, gate_num)
                    # Need to deep clone so we keep the values
                    blank_re = copy.deepcopy(re)
                    blank_im = copy.deepcopy(im)
                    lag_num = 0
                    lag_idx = 0
                    lags_len = len(lags)
                    # Search for missing lags
                    # Note: had to use while loop do to insert method
                    while lag_idx < lags_len:
                        if lag_num in blanked_lags:
                            # to remove lines going through the points
                            re[lag_idx] = np.nan
                            im[lag_idx] = np.nan
                        if lags[lag_idx] != lag_num:
                            lags.insert(lag_num, lag_num)
                            # increase length by one due to insert
                            lags_len += 1
                            # masking the values so it can create
                            # gaps in the data
                            re.insert(lag_num, np.nan)
                            im.insert(lag_num, np.nan)
                            # ensures the points line up on the plot
                            blank_re.insert(lag_num, np.nan)
                            blank_im.insert(lag_num, np.nan)

                        lag_idx += 1
                        if lag_idx < lags_len:
                            if lag_num != lags[lag_idx]:
                                if lag_num > lags[lag_idx]:
                                    lag_num = lags[lag_idx]
                                else:
                                    lag_num += 1
                    # once we got the data break free!!
                    break
                scan_count += 1
        if record['cp'] == 503:
            warnings.warn("Please note that this data is from Tauscan "
                          "which has different lag properties compared "
                          "to other control programs. The ACF plot may "
                          "not be correct. Please contact the PI of the "
                          "radar to confirm if the data looks correct.")
        if re == [] or im == []:
            if gate_num > 0 and gate_num < record['nrang']:
                time = time2datetime(record)
                raise plot_exceptions.\
                    NoDataFoundError(parameter, beam_num,
                                     opt_beam_num=record['bmnum'])
            else:
                raise plot_exceptions.OutOfRangeGateError(parameter, gate_num,
                                                          record['nrang'])

        # generates gaps where there are nan's
        masked_re = np.ma.array(re)
        masked_re = np.ma.masked_where(np.isnan(masked_re), masked_re)

        masked_im = np.ma.array(im)
        masked_im = np.ma.masked_where(np.isnan(masked_im), masked_im)

        # Calculate pwr and phs regardless of choice as
        # in return statement
        pwr = np.sqrt(np.square(masked_re) + np.square(masked_im))
        phs = np.arctan2(masked_im, masked_re)

        masked_pwr = np.ma.array(pwr)
        masked_pwr = np.ma.masked_where(np.isnan(masked_pwr), masked_pwr)
        masked_phs = np.ma.array(phs)
        masked_phs = np.ma.masked_where(np.isnan(masked_phs), masked_phs)

        if normalized is True:
            masked_re /= record['pwr0'][gate_num]
            masked_im /= record['pwr0'][gate_num]

            blank_re_n = blank_re / record['pwr0'][gate_num]
            blank_im_n = blank_im / record['pwr0'][gate_num]

        # plot real and imaginary with power
        if pwr_and_phs is True:
            fig = plt.gcf()
            gs = fig.add_gridspec(2, 2)
            ax = fig.add_subplot(gs[0, :])
            ax_pwr = fig.add_subplot(gs[1, 0])
            ax_phs = fig.add_subplot(gs[1, 1])

            ax_pwr.scatter(lags, masked_pwr, marker='o', color='tab:orange',
                           label='Power', **kwargs)
            ax_pwr.set_ylabel('Power')
            ax_pwr.set_xlabel('Lag Number')
            ax_pwr.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
            ax_pwr.set_ylim([0, abs(max(masked_pwr))
                             + 0.1*abs(max(masked_pwr))])
            ax_pwr.set_title('Power')

            ax_phs.scatter(lags, np.degrees(masked_phs), marker='o',
                           color='tab:purple', label='Phase', **kwargs)
            ax_phs.set_ylabel('Phase (degrees)')
            ax_phs.set_xlabel('Lag Number')
            ax_phs.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
            ax_phs.set_ylim([-180, 180])
            ax_phs.set_title('Phase')
        else:
            ax = plt.gca()

        ax.plot(lags, masked_im, marker='o', color=imaginary_color,
                label='Imaginary', **kwargs)
        ax.plot(lags, masked_re, marker='o', color=real_color,
                label='Real', **kwargs)

        # Plot blanked lags
        if plot_blank:
            print("Blanked lags:", blanked_lags)
            for blank in blanked_lags:
                # I use scatter here to make points not lines
                # also shows up in the legend nicer
                if pwr_and_phs is True:
                    blank_pwr = np.sqrt(np.square(blank_re)
                                        + np.square(blank_im))
                    blank_phs = np.arctan2(blank_im, blank_re)
                    line_pwr = ax_pwr.scatter(blank,
                                              blank_pwr[lags.index(blank)],
                                              edgecolors='tab:orange',
                                              facecolors=(1, 1, 1, 0),
                                              marker='o')
                    line_phs = ax_phs.scatter(blank,
                                              np.degrees(
                                                blank_phs[lags.index(blank)]),
                                              edgecolor='tab:purple',
                                              marker='o',
                                              facecolor=(1, 1, 1, 0))

                if normalized is True:
                    line_im = ax.scatter(blank, blank_im_n[lags.index(blank)],
                                         edgecolors=imaginary_color,
                                         facecolors=(1, 1, 1, 0),
                                         marker=blank_marker)
                    line_re = ax.scatter(blank, blank_re_n[lags.index(blank)],
                                         edgecolors=real_color,
                                         facecolors=(1, 1, 1, 0),
                                         marker=blank_marker)
                else:
                    line_im = ax.scatter(blank, blank_im[lags.index(blank)],
                                         edgecolors=imaginary_color,
                                         facecolors=(1, 1, 1, 0),
                                         marker=blank_marker)
                    line_re = ax.scatter(blank, blank_re[lags.index(blank)],
                                         edgecolors=real_color,
                                         facecolors=(1, 1, 1, 0),
                                         marker=blank_marker)

            # generate generic legend
            if legend and blanked_lags != []:
                line_re.set_label('Real Blanked')
                line_im.set_label('Imaginary Blanked')
                if pwr_and_phs is True:
                    line_pwr.set_label('Power Blanked')
                    line_phs.set_label('Phase Blanked')

        # Make legend on right side of figure
        if legend is True:
            fig = plt.gcf()
            fig.legend(loc=5)
            plt.subplots_adjust(right=0.8)
        # Set labels of main plot
        ax.set_ylabel(parameter)
        ax.set_xlabel('Lag Number')
        # Calc and set limit of main plot
        lim_val = max(abs(masked_re + masked_im))\
            + 0.1 * max(abs(masked_re + masked_im))
        ax.set_ylim([-lim_val, lim_val])
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

        # Set title of Plot
        radar_name = SuperDARNRadars.radars[cls.dmap_data[0]['stid']].name
        title = "{date} UT {radar} Beam {beam}, Gate {gate}, Control "\
                "Program: {cpid}"\
                "".format(radar=radar_name, beam=beam_num, gate=gate_num,
                          date=time.strftime("%Y %b %d %H:%M"),
                          cpid=record['cp'])
        ax.set_title(title)

        return masked_re, masked_im, masked_pwr, masked_phs, blanked_lags

    @classmethod
    def __found_scan(cls, scan_num: int, count_num: int,
                     start_time: datetime, time: datetime):
        """
            method to help do the complicated if statement
            for scan/time check

            Parameter
            ---------
                scan_num: int
                    scan number the user passed in
                count_num: int
                    the current scan count
                start_time: datetime
                    a datetime object the user passes in
                time: datetime
                    current time the record is at

            Return:
            ------
                Bool
                If the scan is found return True
                else False
        """
        if start_time is None:
            if scan_num == count_num:
                return True
        elif start_time < time:
            return True

        return False

    @classmethod
    def __blanked_lags(cls, record: dict, lags: list, gate: int):
        """
        Determines the blanked lags in the data record
        Lags contaminated by transmit pulse overlap

        Parameters
        ----------
        record : dict
            data record containing the lag and ACF/SCF data
        lags : list
            the lag number list where elments are: ltab[i][1] - ltab[i][0]
        gate : int
            gate number
        """
        sorted_lags = lags
        lags_pair = [lag for lags in record['ltab'] for lag in lags]
        sorted_lags.sort()
        lags_pair.sort()
        tau_per_txpl = record['mpinc'] / record['txpl']
        blanked_samples = [lag_pair * tau_per_txpl for lag_pair in lags_pair]
        blanked_lags = []
        for blank in blanked_samples:
            blanked_lags.extend([blank, blank + 1])

        blanked_lag_numbers = []
        for s_lag in sorted_lags:
            for pair in record['ltab']:
                # find which lags didn't get changed
                # in the sorting
                if s_lag == (pair[1] - pair[0]):
                    sample1 = tau_per_txpl * pair[0] + gate + 1 * \
                        record['lagfr'] / record['txpl']
                    sample2 = tau_per_txpl * pair[1] + gate + 1 * \
                        record['lagfr'] / record['txpl']
                    if sample1 in blanked_lags or sample2 in blanked_lags:
                        blanked_lag_numbers.append(s_lag)

        return blanked_lag_numbers
