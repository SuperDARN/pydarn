# Copyright (C) 2019 SuperDARN
# Author: Marian Schmidt
# This code is improvement based on rti.py in the DaVitpy library
# https://github.com/vtsuperdarn/davitpy/blob/master/davitpy

"""
Range-time Parameter plots (a.k.a Intensity)
"""
import matplotlib.pyplot as plt
import numpy as np
import warnings

from datetime import datetime, timedelta
from matplotlib import dates, colors, cm, ticker
from typing import List

from pydarn import (dmap2dict, DmapArray, DmapScalar,
                    rtp_exceptions, SuperDARNCpids, SuperDARNRadars)


class RTP():
    """
    Range-time Parameter plots SuperDARN data using the following fields:

    Class pattern design: Builder
    This class inherits matplotlib.pyplot to inherit plotting features as well
    build off their builder design pattern.

    Notes
    -----
    This class inherits from matplotlib to generate the figures

    Methods
    -------
    plot_profile
    plot_scalar
    plot_summary
    """

    def __str__(self):
        return "This class is static class that provides"\
                " the following methods: \n"\
                "   - plot_rang_time()\n"\
                "   - plot_time_series()\n"\
                "   - plot_summary()\n"

    @classmethod
    def plot_range_time(cls, dmap_data: List[dict], parameter: str = 'p_l',
                        beam_num: int = 0, ax=None,
                        color_norm=None, **kwargs):
        """
        Plots a range-time parameter plot of the given
        field name in the dmap_data

        Future Work
        -----------
        Support for other data input, like "time"
        dictionary key containing the datetime. However,
        further discussion is needed if this will be the keys
        name or maybe another input.

        Parameters
        -----------
        dmap_data : List[dict]
        parameter : str
            string/key name indicating which parameter to plot.
            Default: p_l
        beam_num : int
        ax: matplotlib.axes
            axes object for another way of plotting
            Default: None
        color_norm: matplotlib.colors.Normalization object
            This object use dependency injection to use any normalization
            method with the zmin and zmax.
            Default: colors.Normalization()
        time_span : [datetime, datetime]
            List containing the start time and end time as datetime objects,
        channel : int or str
            The channel 0, 1, 2, 'all'
            default : 'all'
        groundscatter : boolean
            Flag to indicate if groundscatter should be plotted.
            Default : False
        date_fmt : str
            format of x-axis date ticks, follow datetime format
            Default: '%y/%m/%d\n %H:%M'
        color_bar: boolean
            boolean to indicate if a color bar should be included
            Default: True
        color_bar_label: str
            the label that appears next to the color bar
            Default: ''
        color_map: str
            matplotlib colour map
            https://matplotlib.org/tutorials/colors/colormaps.html
            Default: viridis
            note: to reverse the color just add _r to the string name
        boundary: (int, int)
            min and max values to include in the plot and set for normalization
            of the color map.
            Default: None
                - the min and max values in the data are used instead
        max_array_filter : dict
            dictionary that contains the key parameter names and the values to
            compare against. Will filter out any data points
            that is above this value.
        min_array_filter : dict
            dictionary that contains the key parameter names and the value to
            compare against. Will filter out any data points that is
            below this value.
        max_scalar_filter : dict
            dictionary that contains the key parameter names and the values to
            compare against. Will filter out data sections that is
            above this value.
        min_scalar_filter : dict
            dictionary that contains the key parameter names and the value to
            compare against. Will filter out data sections
            that is below this value.
        equal_scalar_filter : dict
            dictionary that contains the key parameter names and the value to
            compare against. Will filter out data sections
            that is does not equal the value.


        Raises
        ------
        RTPUnknownParameterError
        RTPIncorrectPlotMethodError
        RTPNoDataFoundError
        IndexError

        Returns
        -------
        im: matplotlib.pyplot.pcolormesh
            matplotlib object from pcolormesh
        cb: matplotlib.colorbar
            matplotlib color bar
        cmap: matplotlib.cm
            matplotlib color map object
        time_axis: list
            list representing the x-axis datetime objects
        y_axis: list
            list representing the y-axis range gates
        z_data: 2D numpy array
            2D array of the parameters values at the given time and range gate
        """
        # Settings
        settings = {'groundscatter': False,
                    'channel': 'all',
                    'date_fmt': "%y/%m/%d\n%H:%M",
                    'color_bar': True,
                    'color_bar_label': '',
                    'color_map': 'viridis',
                    'boundary': None,
                    'min_array_filter': dict(),
                    'max_array_filter': dict(),
                    'min_scalar_filter': dict(),
                    'max_scalar_filter': dict(),
                    'equal_scalar_filter': dict()}

        settings.update(kwargs)

        # If an axes object is not passed in then store
        # the equivalent object in matplotlib. This allows
        # for variant matplotlib plotting styles.

        if not ax:
            ax = plt.gca()

        # Determine if a DmapRecord was passed in, instead of a list
        try:
            # because of partial records we need to find the first
            # record that has that parameter
            index_first_match = next(i for i,d in enumerate(dmap_data)
                                     if parameter in d)
            if isinstance(dmap_data[index_first_match][parameter], DmapArray) or\
               isinstance(dmap_data[index_first_match][parameter], DmapScalar):
                dmap_data = dmap2dict(dmap_data)
        except StopIteration:
            raise rtp_exceptions.RTPUnknownParameter(parameter)
        cls.dmap_data = dmap_data
        cls.__check_data_type(parameter, 'array', index_first_match)
        # Calculate the time span range, either passed in or calculated
        # based on the dmap_data records
        # TODO: move this to it's own method
        try:
            if len(kwargs['time_span']) == 2:
                start_time = kwargs['time_span'][0]
                end_time = kwargs['time_span'][1]
                cls.interval_time = None
            elif len(kwargs['time_span']) == 3:
                start_time = kwargs['time_span'][0]
                end_time = kwargs['time_span'][2]
                cls.interval_time = kwargs['time_span'][1]
            else:
                raise IndexError("time_span list must be length of 2 or 3")
        except KeyError:
            start_time = cls.__time2datetime(cls.dmap_data[0])
            end_time = cls.__time2datetime(cls.dmap_data[-1])

        # y-axis coordinates, i.e., range gates,
        # TODO: implement variant other coordinate systems for the y-axis
        y = np.arange(0, cls.dmap_data[0]['nrang']+1, 1)
        y_max = cls.dmap_data[0]['nrang']

        # z: parameter data mapped into the color mesh
        z = np.zeros((1, y_max)) * np.nan

        # x: time date data
        x = []

        # We cannot simply use numpy's built in min and max function
        # because of the groundscatter value
        if settings["boundary"]:
            z_min, z_max = settings["boundary"]
        else:
            z_min = cls.dmap_data[index_first_match][parameter][0]
            z_max = cls.dmap_data[index_first_match][parameter][0]
        for dmap_record in cls.dmap_data:
            # get time difference to test if there is some gap data
            time = cls.__time2datetime(dmap_record)
            diff_time = 0.0
            if time > end_time:
                break
            if x != []:
                # 60.0 seconds in a minute
                delta_diff_time = (time - x[-1])
                diff_time = delta_diff_time.seconds/60.0

            # separation roughly 2 minutes
            if diff_time > 2.0:
                # if there is gap data (no data recorded past 2 minutes)
                # then fill it in with white space
                for _ in range(0, int(np.floor(diff_time/2.0))):
                    x.append(x[-1] + timedelta(0, 120))
                    i = len(x) - 1  # offset since we start at 0 not 1
                    if i > 0:
                        z = np.insert(z, len(z), np.zeros(1, y_max) * np.nan,
                                      axis=0)
            # Get data for the provided beam number
            if (beam_num == 'all' or dmap_record['bmnum'] == beam_num) and\
               (settings['channel'] == 'all' or
                    dmap_record['channel'] == settings['channel']):
                if start_time <= time:
                    # construct the x-axis array
                    # Numpy datetime is used because it properly formats on the
                    # x-axis
                    x.append(time)
                    # I do this to avoid having an extra loop to just count how
                    # many records contain the beam number
                    i = len(x) - 1  # offset since we start at 0 not 1

                    # insert a new column into the z_data
                    if i > 0:
                        z = np.insert(z, len(z), np.zeros(1, y_max) * np.nan,
                                      axis=0)
                    try:
                        # get the range gates that have "good" data in it
                        for j in range(len(dmap_record['slist'])):
                            # if it is groundscatter store a very
                            # low number in that cell
                            if settings['groundscatter'] and\
                               dmap_record['gflg'][j] == 1:
                                # chosen value from davitpy to make the
                                # groundscatter a different color
                                # from the color map
                                z[i][dmap_record['slist'][j]] = -1000000
                            # otherwise store parameter value
                            # TODO: refactor and clean up this code
                            elif cls.__filter_data_check(dmap_record,
                                                         settings, j):
                                z[i][dmap_record['slist'][j]] = \
                                        dmap_record[parameter][j]
                                # calculate min and max value
                                if not settings["boundary"]:
                                    if z[i][dmap_record['slist'][j]] < z_min \
                                       or z_min is None:
                                        z_min = z[i][dmap_record['slist'][j]]
                                    if z[i][dmap_record['slist'][j]] > z_max:
                                        z_max = z[i][dmap_record['slist'][j]]
                    # a KeyError may be thrown because slist is not created
                    # due to bad quality data.
                    except KeyError:
                        continue
        x.append(end_time)
        # Check if there is any data to plot
        if np.all(np.isnan(z)):
            raise rtp_exceptions.RTPNoDataFoundError(parameter, beam_num,
                                                     start_time, end_time)
        time_axis, elev_axis = np.meshgrid(x, y)
        z_data = np.ma.masked_where(np.isnan(z.T), z.T)

        if color_norm is None:
            norm = colors.Normalize(z_min, z_max)
        else:
            norm = color_norm(z_min, z_max)

        cmap = cm.get_cmap(settings['color_map'])

        if settings['groundscatter']:
            cmap.set_under('grey', 1.0)

        cmap.set_bad(color='w', alpha=1.)
        # plot!
        im = ax.pcolormesh(time_axis, elev_axis, z_data, lw=0.01,
                           cmap=cmap, norm=norm)
        # setup some standard axis information
        ax.set_xlim([start_time, end_time])
        ax.xaxis.set_major_formatter(dates.DateFormatter(settings['date_fmt']))
        ax.yaxis.set_ticks(np.arange(0, y_max+1, 15))
        ax.xaxis.set_minor_locator(dates.HourLocator())
        ax.yaxis.set_minor_locator(ticker.MultipleLocator(5))
        # so the plots gets to the ends
        ax.margins(0)

        # create color bar if True
        cb = None
        if settings['color_bar']:
            cb = ax.figure.colorbar(im, ax=ax, extend='both')
            cb.set_label(settings['color_bar_label'])

        return im, cb, cmap, x, y, z_data

    @classmethod
    def plot_time_series(cls, dmap_data: List[dict],
                         parameter: str = 'tfreq', beam_num: int = 0,
                         ax=None, time_span: tuple = None,
                         date_fmt: str = '%y/%m/%d\n %H:%M',
                         channel='all', scale: str = 'linear',
                         cp_name: bool = True, **kwargs):
        """
        Plots the time series of a scalar parameter

        Parameters
        ----------
        dmap_data : List[dict]
            List of dictionaries representing SuperDARN data
        parameter : str
            Scalar parameter to plot
            Default: tfreq
        beam_num : int
            beam number
            Default: 0
        ax : matplotlib axes object
            option to pass in axes object from matplotlib.pyplot
            Default: plt.gca()
        time_span : (datetime, datetime)
            tuple containing the start time and end time
        date_fmt : datetime format string
            Date format for the x-axis
            Default: '%y/%m/%d \n %H:%M'
        channel : int or str
            integer indicating which channel to plot or 'all' to
            plot all channels
            Default: 'all'
        scale: str
            The y-axis scaling. This is not used for plotting the cp ID
            Default: log
        cp_name : bool
            If True, the cp ID name will be printed
            along side the number. Otherwise the cp ID will
            just be printed. This is only used for the parameter cp
            Default: True
        Returns
        -------
        lines: list
            list of matplotlib.lines.Lines2D object representing the
            time-series data if plotting parameter cp then it will be None
        x: list
            list of datetime objects representing x-axis time series
        y: list
            list of scalar values for each datetime object

        Raises
        ------
        RTPUnknownParameterError
        RTPIncorrectPlotMethodError
        RTPNoDataFoundError
        IndexError

        """
        # check if axes object is passed in, if not
        # default to plt.gca()
        if not ax:
            ax = plt.gca()

        # Determine if a DmapRecord was passed in, instead of a list
        try:
            # because of partial records we need to find the first
            # record that has that parameter
            index_first_match = next(i for i,d in enumerate(dmap_data)
                                     if parameter in d)
            if isinstance(dmap_data[index_first_match][parameter], DmapArray) or\
               isinstance(dmap_data[index_first_match][parameter], DmapScalar):
                dmap_data = dmap2dict(dmap_data)
        except StopIteration:
            raise rtp_exceptions.RTPUnknownParameter(parameter)

        cls.dmap_data = dmap_data
        cls.__check_data_type(parameter, 'scalar', index_first_match)
        # Calculate the time span range, either passed in or calculated
        # based on the dmap_data records
        if time_span is None:
            start_time = cls.__time2datetime(cls.dmap_data[0])
            end_time = cls.__time2datetime(cls.dmap_data[-1])
        elif len(time_span) == 2:
            start_time = time_span[0]
            end_time = time_span[1]
        else:
            raise IndexError("time_span list must be length of 2, "
                             "you passed in a time_span list of "
                             "length: {}".format(len(time_span)))

        # initialized here for return purposes
        lines = None
        # parameter data
        y = []
        # date time
        x = []
        # plot CPID
        if parameter == 'cp':
            ax.set_xlim(start_time, end_time)
            old_cpid = 0
            for dmap_record in cls.dmap_data:
                # TODO: this check could be a function call
                if (dmap_record['bmnum'] == beam_num or beam_num == 'all') and\
                   (dmap_record['channel'] == channel or channel == 'all'):
                    time = cls.__time2datetime(dmap_record)
                    if start_time <= time and time <= end_time:
                        if old_cpid != dmap_record['cp']:
                            ax.axvline(x=time, color='black')
                            old_cpid = dmap_record['cp']
                            ax.text(x=time + timedelta(seconds=600), y=0.5,
                                    s=dmap_record['cp'])
                            if cp_name:
                                # Keeping this commented code in to show how
                                # we could get the name from the file; however,
                                # there is not set format for combf field ...
                                # so we will use the dictionary to prevent
                                # errors or incorrect names on the plot.
                                # However, we should get it from the file
                                # not a dictionary that might not be updated
                                # cpid_command = dmap_record['combf'].split(' ')
                                # if len(cpid_command) == 1:
                                #     cp_name = cpid_command[0]
                                # elif len(cpid_command) == 0:
                                #     cp_name = 'unknown'
                                # else:
                                #     cp_name = cpid_command[1]
                                ax.text(x=time + timedelta(seconds=600),
                                        y=0.2,
                                        s=SuperDARNCpids.cpids.get(dmap_record['cp'],
                                                                   'unknown'))

            # Check if the old cp ID change, if not then there was no data
            if old_cpid == 0:
                raise rtp_exceptions.RTPNoDataFoundError(parameter, beam_num,
                                                         start_time, end_time)

            # to get rid of y-axis numbers
            ax.set_yticks([])
        else:
            for dmap_record in cls.dmap_data:
                # TODO: this check could be a function call
                time = cls.__time2datetime(dmap_record)
                if start_time <= time and time <= end_time:
                    if (dmap_record['bmnum'] == beam_num or
                        beam_num == 'all') and \
                       (channel == dmap_record['channel'] or channel == 'all'):
                        # construct the x-axis array
                        x.append(time)
                        if parameter == 'tfreq':
                            # Convert kHz to MHz by dividing by 1000
                            y.append(dmap_record[parameter]/1000)
                        else:
                            y.append(dmap_record[parameter])
                    # else plot missing data
                    elif len(x) > 0:
                        diff_time = time - x[-1]
                        if diff_time.seconds/60 > 2.0:
                            x.append(time)
                            y.append(np.nan)  # for masking the data
            # Check if there is any data to plot
            if np.all(np.isnan(y)) or len(x) == 0:
                raise rtp_exceptions.RTPNoDataFoundError(parameter, beam_num,
                                                         start_time, end_time)

            # using masked arrays to create gaps in the plot
            # otherwise the lines will connect in gapped data
            my = np.ma.array(y)
            my = np.ma.masked_where(np.isnan(my), my)
            lines = ax.plot_date(x, my, fmt='k', tz=None, xdate=True,
                                 ydate=False,
                                 **kwargs)
            ax.set_xlim(start_time, end_time)
            ax.set_yscale(scale)
        # set date format and minor hourly locators
        ax.xaxis.set_major_formatter(dates.DateFormatter(date_fmt))
        ax.xaxis.set_minor_locator(dates.HourLocator())
        ax.margins(x=0)
        ax.tick_params(axis='y', which='minor')
        return lines, x, y

    @classmethod
    def plot_summary(cls, dmap_data: List[dict], beam_num: int = 0,
                     groundscatter: bool = False, channel: int = 'all',
                     figsize: tuple = (11, 8.5), boundary: dict = {},
                     color_maps: dict = {}, plot_elv: bool = True,
                     title=None, **kwargs):
        """
        Plots the summary of the following SuperDARN parameter plots:
            - noise.search : (time-series)
            - noise.sky :  (time-series)
            - tfreq : transmission frequency (time-series)
            - nave : number of averages  (time-series)
            - cp : control program ID (time-series)
            - p_l : Signal to Noise ratio (range-time)
            - v : velocity (range-time)
            - w_l : spectral width (range-time)
            - elv : elevation (optional) (range-time)

        Future Work
        ------------
        day-night terminators
        slant ranges

        Parameters
        ----------
        dmap_data: List[dict]
            List of dictionaries of the data to be plotted containing the
            parameter fields used in the summary plot.
        beam_num : int
        ax: matplotlib.axes
            axes object for another way of plotting
            Default: None
        groundscatter : boolean
            Flag to indicate if groundscatter should be plotted.
            Placed only on the velocity plot.
            default : False
        channel : int
            channel number that will be plotted
            in the summary plot.
            default: 'all'
        figsize : (int,int)
            tuple containing (height, width) figure size
            Default: 11 x 8.5
        color_maps: dict
            dictionary of matplotlib color maps for the summary
            plot parameters.
            https://matplotlib.org/tutorials/colors/colormaps.html
            Default: viridis for all parameter except RdBu for velocity
            note: to reverse the color just add _r to the string name
        boundary: (int, int)
            min and max values to include in the plot and set for normalization
            of the color map.
            Default: None
                - the min and max values in the data are used instead
        plot_elv: boolean
            boolean determines if elevation should be plotted or not.
            If there is no data for elevation data field then elevation is not
            plotted.
            Default: True
        title: str
            title of the plot
            Default: auto-generated by the files details
            {radar name} Fitacf {version} {start_date} - {end_date}  Beam {num}
        Raises
        ------
        IndexError
        RTPUnknownParameterError
        RTPIncorrectPlotMethodError
        RTPNoDataFoundError

        See Also
        --------
        plot_range_time : plots range-time parameter
        plot_time_series : plots time-series

        Return
        ------
        fig: matplotlib.pyplot.figure object
        axes: list
            list of matplotlib.pyplot.axes objects to generate
            the subplots in the summary plot

        """
        # default boundary ranges for the various parameter
        boundary_ranges = {'noise.search': (1e0, 1e6),
                           'noise.sky': (1e0, 1e6),
                           'tfreq': (8, 22),
                           'nave': (0, 80),
                           'p_l': (0, 30),
                           'v': (-200, 200),
                           'w_l': (0, 150),
                           'elv': (0, 50)}
        boundary_ranges.update(boundary)

        # default color maps for the summary plot
        color_map = {'noise.search': 'k',
                     'noise.sky': 'grey',
                     'tfreq': 'k',
                     'nave': 'red',
                     'p_l': 'viridis',
                     'v': 'RdBu',
                     'w_l': 'viridis',
                     'elv': 'viridis'}
        color_map.update(color_maps)


        fig = plt.figure(figsize=figsize)

        # axes objects in order of creation:
        # [noise, tfreq, cp, snr, vel, spect, elv]
        # Check if the radar has elevation information if not
        # do not plot elevation
        try:
            # need to use any because some records at the start
            # can be partial which doesn't mean there is no elv
            # data
            if any('elv' in d for d in dmap_data) and plot_elv:
                num_plots = 7
            else:
                num_plots = 6
        except KeyError:
            num_plots = 6
        axes = []
        # List of parameters plotted in the summary plot, tuples are used
        # for shared plot parameters like noise.search and noise.sky
        axes_parameters = [('noise.search', 'noise.sky'), ('tfreq', 'nave'),
                           ('cp'), ('p_l'), ('v'), ('w_l'), ('elv')]
        # labels to show on the summary plot for each parameter
        labels = [('Search \n Noise', 'Sky\n Noise'),
                  ('Freq\n ($MHz$)', 'Nave'), ('CP ID'), ('SNR ($dB$)'),
                  ('Velocity\n ($m\ s^{-1}$)'),
                  ('Spectral Width\n ($m\ s-1$)'),
                  ('Elevation\n ($\degree$)')]

        for i in range(num_plots):
            # time-series plots
            # position: [left, bottom, width, height]
            if i < 3:
                axes.append(fig.add_axes([0.1, 0.88 - (i*0.08), 0.76, 0.06]))
            # range-time plots
            else:
                axes.append(fig.add_axes([0.1, 1.04 - (i*0.16), 0.95, 0.14]))

        for i in range(num_plots):
            # plot time-series
            if i < 2:
                # for noise.search and frequency plots as they share x-axis
                # with noise.sky and nave
                if i == 0:
                    scale = 'log'
                else:
                    scale = 'linear'

                # plot time-series parameters that share a plot
                if i < 2:
                    with warnings.catch_warnings(record=True) as w:
                        cls.plot_time_series(dmap_data, beam_num=beam_num,
                                             parameter=axes_parameters[i][0],
                                             channel=channel, scale=scale,
                                             color=color_map[axes_parameters[i][0]],
                                             ax=axes[i], linestyle='-',
                                             label=labels[i][0], **kwargs)
                    if len(w) > 0:
                        warnings.warn("Warning: {parameter} raised the"
                                      " following warning: {message}"
                                      "".format(parameter=axes_parameters[i][0],
                                                message=str(w[0].message)))
                    axes[i].set_ylabel(labels[i][0], rotation=0, labelpad=30)
                    axes[i].axhline(y=boundary_ranges[axes_parameters[i][0]][0] + 0.8,
                                    xmin=-0.11, xmax=-0.05,
                                    clip_on=False, color=color_map[axes_parameters[i][0]])
                    axes[i].set_ylim(boundary_ranges[axes_parameters[i][0]][0],
                                     boundary_ranges[axes_parameters[i][0]][1])
                    axes[i].yaxis.set_label_coords(-0.08, 0.085)

                    # plot the shared parameter
                    second_ax = axes[i].twinx()
                    # warnings are not caught with try/except
                    with warnings.catch_warnings(record=True) as w:
                        cls.plot_time_series(dmap_data, beam_num=beam_num,
                                             parameter=axes_parameters[i][0],
                                             color=color_map[axes_parameters[i][1]],
                                             channel=channel,
                                             scale=scale, ax=second_ax,
                                             linestyle='--',
                                             **kwargs)
                    if len(w) > 0:
                        warnings.warn("Warning: {parameter} raised the"
                                      " following warning: {message}"
                                      "".format(parameter=axes_parameters[i][1],
                                                message=str(w[0].message)))
                    second_ax.set_xticklabels([])
                    second_ax.set_ylabel(labels[i][1], rotation=0, labelpad=25)
                    second_ax.axhline(y=boundary_ranges[axes_parameters[i][1]][0] +
                                      0.8, xmin=1.07, xmax=1.13,
                                      clip_on=False, linestyle='--',
                                      color=color_map[axes_parameters[i][1]])
                    second_ax.set_ylim(boundary_ranges[axes_parameters[i][1]][0],
                                       boundary_ranges[axes_parameters[i][1]][1])
                    second_ax.yaxis.set_label_coords(1.1, 0.7)

                    #if scale == 'log':
                    #    axes[i].yaxis.set_minor_locator(ticker.LogLocator())
                    #    second_ax.yaxis.set_minor_locator(ticker.LogLocator())
                    #else:
                    if scale == 'linear':
                        second_ax.set_yticks(boundary_ranges[axes_parameters[i][1]])
                        axes[i].set_yticks(boundary_ranges[axes_parameters[i][0]])
                        axes[i].yaxis.set_minor_locator(ticker.LinearLocator())
                        second_ax.yaxis.set_minor_locator(ticker.LinearLocator())

            # plot cp id
            elif i == 2:
                    cls.plot_time_series(dmap_data, beam_num=beam_num,
                                         parameter=axes_parameters[i],
                                         channel=channel,
                                         ax=axes[i], **kwargs)
                    axes[i].set_ylabel('CPID', rotation=0, labelpad=30)
                    axes[i].yaxis.set_label_coords(-0.08, 0.079)
            # plot range-time
            else:
                # Current standard is to only have groundscatter
                # on the velocity plot. This may change in the future.
                if groundscatter and axes_parameters[i] == 'v':
                    grndflg = True
                else:
                    grndflg = False
                cls.plot_range_time(dmap_data, beam_num=beam_num,
                                    color_bar_label=labels[i],
                                    parameter=axes_parameters[i], ax=axes[i],
                                    groundscatter=grndflg,
                                    channel=channel,
                                    color_map=color_map[axes_parameters[i]],
                                    boundary=boundary_ranges[axes_parameters[i]],
                                    **kwargs)
                axes[i].set_ylabel('Range Gates')
            if i < num_plots-1:
                axes[i].set_xticklabels([])
            # last plot needs the label on the x-axis
            else:
                axes[i].set_xlabel('Date (UTC)')

        if title is None:
            plt.title(cls.__generate_title(beam_num, channel), y=2.4)
        else:
            plt.title(title, y=2.4)
        plt.subplots_adjust(wspace=0, hspace=0)
        return fig, axes

    @classmethod
    def __generate_title(cls, beam_num: int, channel: int):
        start_time = cls.__time2datetime(cls.dmap_data[0])
        end_time = cls.__time2datetime(cls.dmap_data[-1])

        if cls.dmap_data[0]['fitacf.revision.major'] == 5:
            version = "2.5"
        else:
            version = "{major}.{minor}"\
                    "".format(major=cls.dmap_data[0]['fitacf.revision.major'],
                              minor=cls.dmap_data[0]['fitacf.revision.minor'])

        radar_name = SuperDARNRadars.radars[cls.dmap_data[0]['stid']].name
        title_format = "{name} Fitacf {version}"\
                       "  {start_date} - {end_date}  Beam {num}"\
                       "".format(name=radar_name, version=version,
                                 start_date=start_time.strftime("%Y %b %d"),
                                 end_date=end_time.strftime("%Y %b %d"),
                                 num=beam_num)
        if type(channel) is int:
            title_format += " channel {ch_num}".format(ch_num=channel)
        return title_format

    @classmethod
    # TODO: could parallelize this method
    def __filter_data_check(cls, dmap_record: dict,
                            settings: dict, j: int) -> bool:
        """
        checks for data that does not meet the criteria of the filtered
        settings

        Parameters
        ----------
        dmap_record : dict
            dictionary of the dmap record fields
        settings : dict
            dictionary of the settings list
        j : int
            index on the slist or range gate to check the array values

        Returns
        -------
        pass_flg : bool
            boolean indicating if the dmap_record passes all filter checks
        """
        pass_flg = True
        for key, value in settings['min_array_filter'].items():
            if dmap_record[key][j] < value:
                pass_flg = False
                break
        for key, value in settings['max_array_filter'].items():
            if dmap_record[key][j] > value:
                pass_flg = False
                break

        for key, value in settings['min_scalar_filter'].items():
            if dmap_record[key] < value:
                pass_flg = False
                break

        for key, value in settings['max_scalar_filter'].items():
            if dmap_record[key] > value:
                pass_flg = False
                break

        for key, value in settings['equal_scalar_filter'].items():
            if dmap_record[key] != value:
                pass_flg = False
                break

        return pass_flg

    @classmethod
    def __check_data_type(cls, parameter: str, expected_type: str, i: int):
        """
        Checks to make sure the plot type is correct
        for the data structure

        Parameters
        ----------
        parameter: str
            string key word name of the parameter
        expected_type: str
            string describing an array or scalar type
            to determine which one is needed for the type of plot

        Raises
        -------
        RTPIncorrectPlotMethodError
        """
        data_type = cls.dmap_data[i][parameter]
        if expected_type == 'array':
            if not isinstance(data_type, np.ndarray):
                raise rtp_exceptions.RTPIncorrectPlotMethodError(parameter,
                                                                 data_type)
        else:
            if isinstance(data_type, np.ndarray):
                raise rtp_exceptions.RTPIncorrectPlotMethodError(parameter,
                                                                 data_type)

    # TODO: move to a utils or SuperDARN utils
    @classmethod
    def __time2datetime(cls, dmap_record: dict) -> datetime:
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
