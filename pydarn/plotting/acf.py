# Copyright (C) 2020 SuperDARN Canada, University of Saskatchewan
# Author: Marina Schmidt
# This code is based on acf.py in the DaVitpy library
# https://github.com/vtsuperdarn/davitpy/blob/master/davitpy
#
# Modifications:
# 2022-05-03: CJM - Added options to plot power and phase of acf
#                 - change defaults to fit needs
# 2023-06-28: CJM - Refactored return values
# 2023-12-15: RAR - Made helper function for plotting ACF values
#                 - Refactored plot_acfs() to use helper function for plotting
#
# Disclaimer:
# pyDARN is under the LGPL v3 license found in the root directory LICENSE.md
# Everyone is permitted to copy and distribute verbatim copies of this license
# document, but changing it is not allowed.
#
# This version of the GNU Lesser General Public License incorporates the terms
# and conditions of version 3 of the GNU General Public License,
# supplemented by the additional permissions listed below.


import matplotlib.markers
import matplotlib.pyplot as plt
import numpy as np
import warnings
import matplotlib.ticker as ticker

from datetime import datetime
from typing import List

from pydarn import (plot_exceptions, SuperDARNRadars,
                    standard_warning_format, time2datetime,
                    check_data_type, RadarID)

warnings.formatwarning = standard_warning_format


class ACF:
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


    @staticmethod
    def plot_acfs(dmap_data: List[dict], beam_num: int = 0,
                  gate_num: int = 15, parameter: str = 'acfd',
                  scan_num: int = 0, start_time: datetime = None,
                  ax: matplotlib.axes.Axes = None,
                  normalized: bool = False, real_color: str = 'red',
                  plot_blank: bool = True, blank_marker: str = 'o',
                  imaginary_color: str = 'blue', legend: bool = True,
                  pwr_and_phs: bool = True, pwr_color: str = 'tab:orange',
                  phs_color: str = 'tab:purple',
                  real_marker: str = 'o', imaginary_marker: str = 'o',
                  pwr_marker: str = 'o', phs_marker: str = 'o',
                  **kwargs):
        """
        Plots the parameter ACF/XCF field from SuperDARN file,
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
        scan_num: int
            will plot the scan number for the provided beam
        start_time: datetime object
            datetime object containing the record to plot for
            the given beam
        ax: matplotlib.axes.Axes
            axes object for another way of plotting. **WILL BE OVERWRITTEN IF PLOTTING POWER AND PHASE**
            Default: None
        normalized: bool
            normalizes the parameter data with the associated
            power 0 value for the given gate number
            default: False
        real_color: str
            line color of the real part of the parameter
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
        pwr_color: str
            the color of line and symbol of power
            default: tab:orange
        phs_color: str
            the color of line and symbol of phase
            default: tab:purple
        real_marker: str
            the marker symbol of real lags
            default: o - dot
        imaginary_marker: str
            the marker symbol of imaginary lags
            default: o - dot
        pwr_marker: str
            the marker symbol of power
            default: o - dot
        phs_marker: str
            the marker symbol of phase
            default: o - dot
        kwargs: dict
            are applied to the plots

        Notes
        -----
        plot blanked lags as hollow circles

        Raises
        ------
        UnknownParameterError
        IncorrectPlotMethodError
        OutOfRangeGateError

        Returns
        -------
        dict of standard parameters, including:
            ax: list of axes that were plotted on
            fig: Figure that contains plot
            ccrs: None,
            cm: None,
            cb: None,
            data: dict of parameters plotted.
                real: real component of ACF,
                imaginary: imaginary component of ACF,
                power: Power of ACF,
                phase: Phase of ACF,
                blanked: Blanked lags of the ACF
        """
        # Determine if a DmapRecord was passed in, instead of a list
        try:
            # because of partial records we need to find the first
            # record that has that parameter
            index_first_match = next(i for i, d in enumerate(dmap_data)
                                     if parameter in d)
        except StopIteration:
            raise plot_exceptions.UnknownParameterError(parameter)
        check_data_type(dmap_data, parameter, 'array', index_first_match)

        # search over the records to find the correct beam and scan/time
        # to plot the corresponding ACF/XCF plot
        scan_count = 0
        re = []
        im = []
        for record in dmap_data:
            if record['bmnum'] == beam_num:
                time = time2datetime(record)
                if start_time is not None:
                    if time.day != start_time.day or \
                       time.month != start_time.month or \
                       time.year != start_time.year:
                        raise plot_exceptions.IncorrectDateError(time,
                                                                 start_time)

                if ACF.__found_scan(scan_num, scan_count, start_time, time):
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
                    blanked_lags = ACF.__blanked_lags(record, lags, gate_num)
                    lag_num = 0
                    lag_idx = 0

                    # Create a mask for hiding missing or blanked lags
                    mask = [0] * len(lags)

                    # Search for missing lags
                    # Note: had to use while loop do to insert method
                    while lag_idx < len(lags):
                        if lag_num in blanked_lags:
                            mask[lag_idx] = 1   # This lag is blanked, mask it
                        if lags[lag_idx] != lag_num:
                            lags.insert(lag_num, lag_num)
                            mask.insert(lag_num, 1) # this lag is missing, mask it
                            # Adding in nan's for missing lags (won't be plotted)
                            re.insert(lag_num, np.nan)
                            im.insert(lag_num, np.nan)

                        lag_idx += 1
                        if lag_idx < len(lags):
                            if lag_num != lags[lag_idx]:
                                if lag_num > lags[lag_idx]:
                                    lag_num = lags[lag_idx]
                                else:
                                    lag_num += 1
                    # once we find the data break free!!
                    break
                scan_count += 1
        if record['cp'] == 503:
            warnings.warn("Please note that this data is from Tauscan "
                          "which has different lag properties compared "
                          "to other control programs. The ACF plot may "
                          "not be correct. Please contact the PI of the "
                          "radar to confirm if the data looks correct.")
        if re == [] or im == []:
            if 0 < gate_num < record['nrang']:
                raise plot_exceptions.\
                    NoDataFoundError(parameter, beam_num,
                                     opt_beam_num=record['bmnum'])
            else:
                raise plot_exceptions.OutOfRangeGateError(parameter, gate_num,
                                                          record['nrang'])

        if normalized is True:
            re /= record['pwr0'][gate_num]
            im /= record['pwr0'][gate_num]

        # generates gaps where there are missing or blanked lags
        masked_re = np.ma.array(re, mask=mask)
        masked_im = np.ma.array(im, mask=mask)

        # Calculate pwr and phs regardless of choice as they are returned
        pwr = np.sqrt(np.square(re) + np.square(im))
        phs = np.rad2deg(np.arctan2(im, re))
        masked_pwr = np.ma.array(pwr, mask=mask)
        masked_phs = np.ma.array(phs, mask=mask)

        # plot real and imaginary with power
        if pwr_and_phs is True:
            fig = plt.gcf()
            gs = fig.add_gridspec(2, 2)
            ax = fig.add_subplot(gs[0, :])
            ax_pwr = fig.add_subplot(gs[1, 0])
            ax_phs = fig.add_subplot(gs[1, 1])
            axes = [ax, ax_pwr, ax_phs]
        else:
            if ax is not None:
                ax = ax
            else:
                ax = plt.gca()
            axes = [ax]

        real_dict = ACF.plot_acf_param(lags, masked_re, ax,
                                       plot_blank=plot_blank,
                                       marker=real_marker,
                                       color=real_color,
                                       blank_marker=blank_marker,
                                       **kwargs)
        imag_dict = ACF.plot_acf_param(lags, masked_im, ax,
                                       plot_blank=plot_blank,
                                       marker=imaginary_marker,
                                       color=imaginary_color,
                                       blank_marker=blank_marker,
                                       **kwargs)
        # Set parameters (axis labels, line labels, etc.) of main plot
        ax.set_ylabel(parameter)
        ax.set_xlabel('Lag Number')
        real_dict['data']['line'].set_label('Real')
        imag_dict['data']['line'].set_label('Imag')
        if plot_blank:
            real_dict['data']['blank_line'].set_label('Real Blanked')
            imag_dict['data']['blank_line'].set_label('Imag Blanked')
            lim_val = 1.1 * max(np.nanmax(np.abs(re)), np.nanmax(np.abs(im)))
        else:
            lim_val = 1.1 * max(np.abs(masked_re).max(),
                                np.abs(masked_im).max())
        ax.set_ylim([-lim_val, lim_val])
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

        # Plot the power and phase, if specified
        if pwr_and_phs is True:
            power_dict = ACF.plot_acf_param(lags, masked_pwr, ax_pwr,
                                            plot_blank=plot_blank,
                                            marker=pwr_marker,
                                            color=pwr_color,
                                            blank_marker=blank_marker,
                                            **kwargs)
            ax_pwr.set_ylabel('Power')
            ax_pwr.set_xlabel('Lag Number')
            ax_pwr.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
            ax_pwr.set_ylim([0, 1.1 * np.nanmax(pwr)])
            ax_pwr.set_title('Power')

            phase_dict = ACF.plot_acf_param(lags, masked_phs, ax_phs,
                                            plot_blank=plot_blank,
                                            marker=phs_marker,
                                            color=phs_color,
                                            blank_marker=blank_marker,
                                            **kwargs)
            ax_phs.set_ylabel('Phase (degrees)')
            ax_phs.set_xlabel('Lag Number')
            ax_phs.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
            ax_phs.set_ylim([-180, 180])
            ax_phs.set_title('Phase')

            # Set labels on the plots
            power_dict['data']['line'].set_label('Power')
            phase_dict['data']['line'].set_label('Phase')
            if plot_blank:
                power_dict['data']['blank_line'].set_label('Power Blanked')
                phase_dict['data']['blank_line'].set_label('Phase Blanked')

        # Make legend on right side of figure
        if legend is True:
            fig = plt.gcf()
            fig.legend(loc=5)
            plt.subplots_adjust(right=0.8)

        # Set title of Plot
        radar_name = SuperDARNRadars.radars[RadarID(dmap_data[0]['stid'])].name
        title = "{date} UT {radar} Beam {beam}, Gate {gate}, Control "\
                "Program: {cpid}"\
                "".format(radar=radar_name, beam=beam_num, gate=gate_num,
                          date=time.strftime("%Y %b %d %H:%M"),
                          cpid=record['cp'])
        ax.set_title(title)

        return {'ax': axes,
                'ccrs': None,
                'cm': None,
                'cb': None,
                'fig':  plt.gcf(),
                'data': {'real': masked_re,
                         'imaginary': masked_im,
                         'power': masked_pwr,
                         'phase':  masked_phs,
                         'blanked': blanked_lags}
                }

    @staticmethod
    def plot_acf_param(x, y, ax,
                       plot_blank: bool = True,
                       blank_marker: str = 'o',
                       **kwargs):
        """
        plots the parameter ACF/XCF field from SuperDARN file,
        typically RAWACF format for a given beam and gate number

        Parameters
        ----------
        x: np.array
            X coordinates of values to plot
        y: np.ma.array
            Y coordinates of values to plot
        ax: matplotlib.Axes
            Axes object for another way of plotting
            Default: None
        plot_blank: bool
            boolean to determine if blanked lags should be plotted
            default: False
        blank_marker: str
            the marker symbol of blanked lags
            default: o - circle
        kwargs: dict
            keyword arguments for setting plot features


        Notes
        -----
        plot blanked lags as hollow circles

        Returns
        -------

        """
        line = ax.plot(x, y, **kwargs)

        # Plot blanked lags
        if plot_blank:
            mask = y.mask

            # Invert the mask so the blanked data is plotted
            blank_mask = ~mask
            y.mask = blank_mask

            # Use blank_marker as marker
            kwargs['marker'] = blank_marker

            # Check if blank_marker is a filled marker like circle or square, and set face white if so
            if blank_marker in matplotlib.markers.MarkerStyle.filled_markers:
                kwargs['facecolors'] = (1, 1, 1, 0)     # Make the marker face white
                kwargs['edgecolors'] = kwargs.get('color', None)
            # For unfilled markers like 'x', just set the color
            else:
                kwargs['color'] = kwargs.get('color', None)

            # Plot the blanks as scatter points
            blank_scatter = ax.scatter(x, y, **kwargs)

            # Now put the mask back!
            y.mask = mask
        else:
            blank_scatter = None

        return {'ax': ax,
                'ccrs': None,
                'cm': None,
                'cb': None,
                'fig': plt.gcf(),
                'data': {'x': x,
                         'y': y,
                         'line': line[0],
                         'blank_line': blank_scatter}
                }

    @staticmethod
    def __found_scan(scan_num: int, count_num: int,
                     start_time: datetime, time: datetime):
        """
        Method to help do the complicated if statement
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

    @staticmethod
    def __blanked_lags(record: dict, lags: list, gate: int):
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
