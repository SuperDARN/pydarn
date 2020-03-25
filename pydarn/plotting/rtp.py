# Copyright (C) 2019 SuperDARN
# Author: Marian Schmidt
# This code is improvement based on rti.py in the DaVitpy library
# https://github.com/vtsuperdarn/davitpy/blob/master/davitpy

"""
Range-Time Parameter (aka Intensity) plots
"""
import matplotlib.pyplot as plt
import numpy as np
import warnings

from datetime import datetime, timedelta
from matplotlib import dates, colors, cm, ticker
from typing import List

from pydarn import (dmap2dict, DmapArray, DmapScalar,
                    rtp_exceptions, SuperDARNCpids, SuperDARNRadars,
                    standard_warning_format, PyDARNColormaps)

warnings.formatwarning = standard_warning_format


class RTP():
    """
    Range-Time Parameter plots SuperDARN data using the following fields:

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
    def plot_range_time(cls, dmap_data: List[dict], parameter: str = 'v',
                        beam_num: int = 0, channel: int = 'all', ax=None,
                        background: str = 'w', groundscatter: bool = False,
                        zmin: int = None, zmax: int = None,
                        start_time: datetime = None, end_time: datetime = None,
                        colorbar: plt.colorbar = None, ymax: int = None,
                        colorbar_label: str = '', norm=colors.Normalize,
                        cmap: str = PyDARNColormaps.PYDARN_VELOCITY,
                        filter_settings: dict = {},
                        date_fmt: str = '%y/%m/%d\n %H:%M', **kwargs):
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
        dmap_data: List[dict]
        parameter: str
            key name indicating which parameter to plot.
            Default: v (Velocity)
        beam_num : int
            The beam number of data to plot
            Default: 0
        channel : int or str
            The channel 0, 1, 2, 'all'
            Default : 'all'
        ax: matplotlib.axes
            axes object for another way of plotting
            Default: None
        groundscatter : boolean or str
            Flag to indicate if groundscatter should be plotted. If string
            groundscatter will be represented by that color else grey.
            Default : False
        background : str
            color of the background in the plot
            default: white
        zmin: int
            Minimum normalized value
            Default: minimum parameter value in the data set
        zmax: int
            Maximum normalized value
            Default: maximum parameter value in the data set
        ymax: int
            Sets the maximum y value
            Default: None, uses 'nrang' from data
        norm: matplotlib.colors.Normalization object
            This object use dependency injection to use any normalization
            method with the zmin and zmax.
            Default: colors.Normalization()
        start_time: datetime
            Start time of the plot x-axis as a datetime object
            Default: rounded to nearest hour-30 minutes from the first
                     record containing the chosen parameters data
        end_time: datetime
            End time of the plot x-axis as a datetime object
            Default: last record of the chosen parameters data
        date_fmt : str
            format of x-axis date ticks, follow datetime format
            Default: '%y/%m/%d\n %H:%M' (Year/Month/Day Hour:Minute)
        colorbar: matplotlib.pyplot.colorbar
            Setting a predefined colorbar for the range-time plot
            If None, then a colorbar will be created for the plot
            Default: None
        colorbar_label: str
            the label that appears next to the color bar
            Default: ''
        cmap: str or matplotlib.cm
            matplotlib colour map
            https://matplotlib.org/tutorials/colors/colormaps.html
            Default: PyDARNColormaps.PYDARN_VELOCITY
            note: to reverse the color just add _r to the string name
        plot_filter: dict
            dictionary of the following keys for filtering data out:
            max_array_filter : dict
                dictionary that contains the key parameter names and the values
                to compare against. Will filter out any data points
                that is above this value.
            min_array_filter : dict
                dictionary that contains the key parameter names and the value
                to compare against. Will filter out any data points that is
                below this value.
            max_scalar_filter : dict
                dictionary that contains the key parameter names and the values
                to compare against. Will filter out data sections that is
                above this value.
            min_scalar_filter : dict
                dictionary that contains the key parameter names and the value
                to compare against. Will filter out data sections
                that is below this value.
            equal_scalar_filter : dict
                dictionary that contains the key parameter names and the value
                to compare against. Will filter out data sections
                that is does not equal the value.
        kwargs:
            key names of variable settings of pcolormesh:
            https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.pyplot.pcolormesh.html

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

        See Also
        ---------
        colors: https://matplotlib.org/2.0.2/api/colors_api.html
        color maps: PyDARNColormaps or
                    https://matplotlib.org/tutorials/colors/colormaps.html
        normalize:
            https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.colors.Normalize.html
        colorbar:
            https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.pyplot.colorbar.html
        pcolormesh:
            https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.pyplot.pcolormesh.html

        """
        # Settings
        plot_filter = {'min_array_filter': dict(),
                       'max_array_filter': dict(),
                       'min_scalar_filter': dict(),
                       'max_scalar_filter': dict(),
                       'equal_scalar_filter': dict()}

        plot_filter.update(filter_settings)

        # If an axes object is not passed in then store
        # the equivalent object in matplotlib. This allows
        # for variant matplotlib plotting styles.
        if not ax:
            ax = plt.gca()

        # Determine if a DmapRecord was passed in, instead of a list
        try:
            # because of partial records we need to find the first
            # record that has that parameter
            index_first_match = next(i for i, d in enumerate(dmap_data)
                                     if parameter in d)
            if isinstance(dmap_data[index_first_match][parameter],
                          DmapArray) or\
               isinstance(dmap_data[index_first_match][parameter],
                          DmapScalar):
                dmap_data = dmap2dict(dmap_data)
        except StopIteration:
            raise rtp_exceptions.RTPUnknownParameterError(parameter)
        cls.dmap_data = dmap_data
        cls.__check_data_type(parameter, 'array', index_first_match)
        start_time, end_time = cls.__determine_start_end_time(start_time,
                                                              end_time)

        # y-axis coordinates, i.e., range gates,
        # TODO: implement variant other coordinate systems for the y-axis
        # y shape needs to be +1 longer as requirement of how pcolormesh
        # draws the pixels on the grid

        # because nrang can change based on mode we need to look
        # for the largest value
        y_max = max(record['nrang'] for record in cls.dmap_data)
        y = np.arange(0, y_max+1, 1)

        # z: parameter data mapped into the color mesh
        z = np.zeros((1, y_max)) * np.nan

        # x: time date data
        x = []

        # We cannot simply use numpy's built in min and max function
        # because of the groundscatter value :(

        # These flags indicate if zmin and zmax should change
        set_zmin = True
        set_zmax = True
        if zmin is None:
            zmin = cls.dmap_data[index_first_match][parameter][0]
            set_zmin = False
        if zmax is None:
            zmax = cls.dmap_data[index_first_match][parameter][0]
            set_zmax = False

        for dmap_record in cls.dmap_data:
            # get time difference to test if there is some gap data
            rec_time = cls.__time2datetime(dmap_record)
            diff_time = 0.0
            if rec_time > end_time:
                break
            if x != []:
                # 60.0 seconds in a minute
                delta_diff_time = (rec_time - x[-1])
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
               (channel == 'all' or
                    dmap_record['channel'] == channel):
                if start_time <= rec_time:
                    # construct the x-axis array
                    # Numpy datetime is used because it properly formats on the
                    # x-axis
                    x.append(rec_time)
                    # I do this to avoid having an extra loop to just count how
                    # many records contain the beam number
                    i = len(x) - 1  # offset since we start at 0 not 1

                    # insert a new column into the z_data
                    if i > 0:
                        z = np.insert(z, len(z), np.zeros(1, y_max) * np.nan,
                                      axis=0)
                    try:
                        if len(dmap_record[parameter]) == dmap_record['nrang']:
                            good_gates = range(len(dmap_record[parameter]))
                        else:
                            good_gates = dmap_record['slist']

                        # get the range gates that have "good" data in it
                        for j in range(len(good_gates)):
                            # if it is groundscatter store a very
                            # low number in that cell
                            if groundscatter and\
                               dmap_record['gflg'][j] == 1:
                                # chosen value from davitpy to make the
                                # groundscatter a different color
                                # from the color map
                                z[i][good_gates[j]] = -1000000
                            # otherwise store parameter value
                            # TODO: refactor and clean up this code
                            elif cls.__filter_data_check(dmap_record,
                                                         plot_filter, j):
                                z[i][good_gates[j]] = \
                                        dmap_record[parameter][j]
                                # calculate min and max value
                                if not set_zmin and\
                                   z[i][good_gates[j]] < zmin:
                                    zmin = z[i][good_gates[j]]
                                if not set_zmax and \
                                   z[i][good_gates[j]] > zmax:
                                    zmax = z[i][good_gates[j]]
                    # a KeyError may be thrown because slist is not created
                    # due to bad quality data.
                    except KeyError:
                        continue
        x.append(end_time)
        # Check if there is any data to plot
        if np.all(np.isnan(z)):
            raise rtp_exceptions.RTPNoDataFoundError(parameter, beam_num,
                                                     start_time, end_time,
                                                     cls.dmap_data[0]['bmnum'])
        time_axis, y_axis = np.meshgrid(x, y)
        z_data = np.ma.masked_where(np.isnan(z.T), z.T)
        norm = norm(zmin, zmax)
        if isinstance(cmap, str):
            cmap = cm.get_cmap(cmap)

        if isinstance(groundscatter, str):
            cmap.set_under(groundscatter, 1.0)
        elif groundscatter:
            cmap.set_under('grey', 1.0)

        # set the background color, this needs to happen to avoid
        # the overlapping problem that occurs
        # cmap.set_bad(color=background, alpha=1.)
        # plot!
        im = ax.pcolormesh(time_axis, y_axis, z_data, lw=0.01,
                           cmap=cmap, norm=norm, **kwargs)
        # setup some standard axis information
        # Upon request of Daniel Billet and others, I am rounding
        # the time down so the plotting x-axis will show the origin
        # time label
        # TODO: may need to be its own function
        rounded_down_start_time = x[0] -\
            timedelta(minutes=x[0].minute % 15,
                      seconds=x[0].second,
                      microseconds=x[0].microsecond)
        ax.set_xlim([rounded_down_start_time, x[-1]])
        ax.xaxis.set_major_formatter(dates.DateFormatter(date_fmt))
        if ymax is None:
            ymax = y_max
        ax.set_ylim(0, ymax)
        ax.yaxis.set_ticks(np.arange(0, ymax+1, (ymax)/5))

        # SuperDARN file typically are in 2hr or 24 hr files
        # to make the minute ticks sensible, the time length is detected
        # then a interval is picked. 30 minute ticks for 24 hr plots
        # and 5 minute ticks for 2 hour plots.
        data_time_length = end_time - start_time
        # 3 hours * 60 minutes * 60 seconds
        if data_time_length.total_seconds() > 3*60*60:
            tick_interval = 30
        else:
            tick_interval = 1
        ax.xaxis.set_minor_locator(dates.MinuteLocator(interval=tick_interval))
        ax.yaxis.set_minor_locator(ticker.MultipleLocator(5))
        # so the plots gets to the ends
        ax.margins(0)

        # create color bar if True
        if not colorbar:
            with warnings.catch_warnings():
                warnings.filterwarnings('error')
                try:
                    locator = ticker.MaxNLocator(symmetric=True, min_n_ticks=3,
                                                 integer=True, nbins='auto')
                    ticks = locator.tick_values(vmin=zmin, vmax=zmax)
                    cb = ax.figure.colorbar(im, ax=ax, extend='both',
                                            ticks=ticks)

                except (ZeroDivisionError, Warning):
                    raise rtp_exceptions.RTPZeroError(parameter, beam_num,
                                                      zmin, zmax,
                                                      norm) from None
        if colorbar_label != '':
            cb.set_label(colorbar_label)

        return im, cb, cmap, x, y, z_data

    @classmethod
    def plot_time_series(cls, dmap_data: List[dict],
                         parameter: str = 'tfreq', beam_num: int = 0,
                         ax=None, start_time: datetime = None,
                         end_time: datetime = None,
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
            The beam number of data to plot
            Default: 0
        ax : matplotlib axes object
            option to pass in axes object from matplotlib.pyplot
            Default: plt.gca()
        start_time: datetime
            Start time of the plot x-axis as a datetime object
            Default: first record date
        end_time: datetime
            End time of the plot x-axis as a datetime object
            Default: last record date
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
        kwargs
            kwargs passed into plot_date

        Raises
        ------
        RTPUnknownParameterError
        RTPIncorrectPlotMethodError
        RTPNoDataFoundError
        IndexError

        Returns
        -------
        lines: list
            list of matplotlib.lines.Lines2D object representing the
            time-series data if plotting parameter cp then it will be None
        x: list
            list of datetime objects representing x-axis time series
        y: list
            list of scalar values for each datetime object

        See Also
        --------
        yscale:
            https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.pyplot.yscale.html
        plot_date:
            https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.axes.Axes.plot_date.html
        colors: https://matplotlib.org/2.0.2/api/colors_api.html
        """
        # check if axes object is passed in, if not
        # Default to plt.gca()
        if not ax:
            ax = plt.gca()

        # Determine if a DmapRecord was passed in, instead of a list
        try:
            # because of partial records we need to find the first
            # record that has that parameter
            index_first_match = next(i for i, d in enumerate(dmap_data)
                                     if parameter in d)
            if isinstance(dmap_data[index_first_match][parameter],
                          DmapArray) or\
               isinstance(dmap_data[index_first_match][parameter],
                          DmapScalar):
                dmap_data = dmap2dict(dmap_data)
        except StopIteration:
            raise rtp_exceptions.RTPUnknownParameterError(parameter)

        cls.dmap_data = dmap_data
        cls.__check_data_type(parameter, 'scalar', index_first_match)
        start_time, end_time = cls.__determine_start_end_time(start_time,
                                                              end_time)

        # initialized here for return purposes
        lines = None
        # parameter data
        y = []
        # date time
        x = []
        # plot CPID
        if parameter == 'cp':
            old_cpid = None
            for dmap_record in cls.dmap_data:
                # TODO: this check could be a function call
                x.append(cls.__time2datetime(dmap_record))

                if (dmap_record['bmnum'] == beam_num or beam_num == 'all') and\
                   (dmap_record['channel'] == channel or channel == 'all'):
                    rec_time = cls.__time2datetime(dmap_record)
                    if start_time <= rec_time and rec_time <= end_time:
                        if old_cpid != dmap_record['cp'] or old_cpid is None:
                            ax.axvline(x=rec_time, color='black')
                            old_cpid = dmap_record['cp']
                            ax.text(x=rec_time + timedelta(seconds=600), y=0.7,
                                    s=dmap_record['cp'])
                            if cp_name:
                                # Keeping this commented code in to show how
                                # we could get the name from the file; however,
                                # there is not set format for combf field ...
                                # so we will use the dictionary to prevent
                                # errors or incorrect names on the plot.
                                # However, we should get it from the file
                                # not a dictionary that might not be updated
                                # cpid_command =
                                #   dmap_record['combf'].split(' ')
                                # if len(cpid_command) == 1:
                                #     cp_name = cpid_command[0]
                                # elif len(cpid_command) == 0:
                                #     cp_name = 'unknown'
                                # else:
                                #     cp_name = cpid_command[1]
                                if dmap_record['cp'] < 0:
                                    cpID_name = 'discretionary \n{}'\
                                            ''.format(SuperDARNCpids.cpids.
                                                      get(abs(dmap_record['cp']),
                                                          'unknown'))
                                else:
                                    cpID_name =\
                                            SuperDARNCpids.cpids.\
                                            get(abs(dmap_record['cp']),
                                                'unknown')
                                ax.text(x=rec_time + timedelta(seconds=600),
                                        y=0.1, s=cpID_name)

            # Check if the old cp ID change, if not then there was no data
            if old_cpid is None:
                raise rtp_exceptions.\
                        RTPNoDataFoundError(parameter, beam_num,
                                            start_time, end_time,
                                            cls.dmap_data[0]['bmnum'])

            # to get rid of y-axis numbers
            ax.set_yticks([])
        else:
            for dmap_record in cls.dmap_data:
                # TODO: this check could be a function call
                rec_time = cls.__time2datetime(dmap_record)
                if start_time <= rec_time and rec_time <= end_time:
                    if (dmap_record['bmnum'] == beam_num or
                        beam_num == 'all') and \
                       (channel == dmap_record['channel'] or channel == 'all'):
                        # construct the x-axis array
                        x.append(rec_time)
                        if parameter == 'tfreq':
                            # Convert kHz to MHz by dividing by 1000
                            y.append(dmap_record[parameter]/1000)
                        else:
                            y.append(dmap_record[parameter])
                    # else plot missing data
                    elif len(x) > 0:
                        diff_time = rec_time - x[-1]
                        # if the time difference is greater than 2 minutes
                        # meaning no data was collected for that time period
                        # then plot nothing.
                        if diff_time.total_seconds() > 2.0 * 60.0:
                            x.append(rec_time)
                            y.append(np.nan)  # for masking the data
            # Check if there is any data to plot
            if np.all(np.isnan(y)) or len(x) == 0:
                raise rtp_exceptions.\
                        RTPNoDataFoundError(parameter, beam_num,
                                            start_time, end_time,
                                            cls.dmap_data[0]['bmnum'])

            # using masked arrays to create gaps in the plot
            # otherwise the lines will connect in gapped data
            my = np.ma.array(y)
            my = np.ma.masked_where(np.isnan(my), my)
            lines = ax.plot_date(x, my, fmt='k', tz=None, xdate=True,
                                 ydate=False,
                                 **kwargs)
            rounded_down_start_time = x[0] -\
                timedelta(minutes=x[0].minute % 15,
                          seconds=x[0].second,
                          microseconds=x[0].microsecond)
            ax.set_xlim([rounded_down_start_time, x[-1]])
            ax.set_yscale(scale)

        # set date format and minor hourly locators
        # Rounded the time down to show origin label upon
        # Daniel Billet and others request.
        # TODO: may move this to its own function
        rounded_down_start_time = x[0] -\
            timedelta(minutes=x[0].minute % 15,
                      seconds=x[0].second,
                      microseconds=x[0].microsecond)
        ax.set_xlim([rounded_down_start_time, x[-1]])

        ax.xaxis.set_major_formatter(dates.DateFormatter(date_fmt))
        ax.xaxis.set_minor_locator(dates.HourLocator())
        # SuperDARN file typically are in 2hr or 24 hr files
        # to make the minute ticks sensible, the time length is detected
        # then a interval is picked. 30 minute ticks for 24 hr plots
        # and 5 minute ticks for 2 hour plots.
        data_time_length = end_time - start_time
        # 3 hours * 60 minutes * 60 seconds
        if data_time_length.total_seconds() > 3*60*60:
            tick_interval = 30
        else:
            tick_interval = 1
        ax.xaxis.set_minor_locator(dates.MinuteLocator(interval=tick_interval))

        ax.margins(x=0)
        ax.tick_params(axis='y', which='minor')
        return lines, x, y

    @classmethod
    def plot_summary(cls, dmap_data: List[dict], beam_num: int = 0,
                     groundscatter: bool = True, channel: int = 'all',
                     figsize: tuple = (11, 8.5), watermark: bool = True,
                     boundary: dict = {}, background_color: str = 'w',
                     cmaps: dict = {}, lines: dict = {},
                     plot_elv: bool = True, title=None):
        """
        Plots the summary of several SuperDARN parameters using time-series and
        range-time plots. Please see Notes for further description
        on what is plotted.

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
            beam number to plot
            default: 0
        ax: matplotlib.axes
            axes object for another way of plotting
            Default: None
        groundscatter : boolean
            Flag to indicate if groundscatter should be plotted.
            Placed only on the velocity plot.
            Default : True
        channel : int
            channel number that will be plotted
            in the summary plot.
            Default: 'all'
        figsize : (int,int)
            tuple containing (height, width) figure size
            Default: 11 x 8.5
        watermark : boolean
            text that runs across the plot stating "Not for Publication Use"
            default: True
        cmaps: dict or str
            dictionary of matplotlib color maps for the summary
            range time parameter plots.
            https://matplotlib.org/tutorials/colors/colormaps.html
            Default: {'p_l': 'plasma',
                      'v': PyDARNColormaps.PYDARN_VELOCITY,
                      'w_l': PyDARNColormaps.PYDARN_VIRIDIS,
                      'elv': PyDARNColormaps.PYDARN}
            note: to reverse the color just add _r to the string name
        lines: dict or str
            dictionary of time-series line colors.
            Default: black
        background_color: str
            changes the color of the background in the plots.
            Default: white
        boundary: dict
            tuple as the value (zmin, zmax) for the plots
            Default: {'noise.sky': (1e0, 1e5),
                      'tfreq': (8, 22),
                      'nave': (0, 60),
                      'p_l': (0, 45),
                      'v': (-200, 200),
                      'w_l': (0, 250),
                      'elv': (0, 45)}
        plot_elv: boolean
            boolean determines if elevation should be plotted or not.
            If there is no data for elevation data field then elevation is not
            plotted.
            Default: True
        title: str
            title of the plot
            Default: auto-generated by the files details
            {radar name} {Radar system (if applicable)} Fitacf {version}
            {start hour/date} - {end hour/date}  Beam {number}

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

        Notes
        -----
        These are the following parameters in the SuperDARN FitACF file that is
        plotted in a summary plot:
            - noise.sky :  (time-series)
            - tfreq : transmission frequency (time-series)
            - nave : number of averages  (time-series)
            - cp : control program ID (time-series)
            - p_l : Signal to Noise ratio (range-time)
            - v : velocity (range-time)
            - w_l : spectral width (range-time)
            - elv : elevation (optional) (range-time)
        """
        message = "WARNING: matplotlib Default dpi may cause distortion"\
                  " in range gates and time period. The figure size can"\
                  " be adjusted with the option figsize and dpi can be"\
                  " adjusted when saving the file."
        warnings.warn(message)

        # Default boundary ranges for the various parameter
        boundary_ranges = {'noise.search': (1e0, 1e5),
                           'noise.sky': (1e0, 1e5),
                           'tfreq': (8, 22),
                           'nave': (0, 60),
                           'p_l': (0, 45),
                           'v': (-200, 200),
                           'w_l': (0, 250),
                           'elv': (0, 45)}
        boundary_ranges.update(boundary)

        # Default color maps for the summary plot
        line = {'noise.search': 'k',
                'noise.sky': 'k',
                'tfreq': 'k',
                'nave': 'k'}

        if isinstance(lines, dict):
            line.update(lines)
        else:
            line.update({k: lines for k, v in line.items()})
        cmap = {'p_l': 'plasma',
                'v': PyDARNColormaps.PYDARN_VELOCITY,
                'w_l': PyDARNColormaps.PYDARN_VIRIDIS,
                'elv': PyDARNColormaps.PYDARN}
        if isinstance(cmaps, dict):
            cmap.update(cmaps)
        else:
            cmap.update({k: cmaps for k, v in cmap.items()})

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
        # Removing search noise from the summary plot due to too much
        # overlapping, however, if confirmed as undesired parameter to
        # plot, will remove it from the code.
        # TODO: remove search noise completely if not wanted in summary plot
        axes_parameters = [('noise.sky', 'noise.search'), ('tfreq', 'nave'),
                           ('cp'), ('p_l'), ('v'), ('w_l'), ('elv')]
        # labels to show on the summary plot for each parameter
        labels = [('Sky \n Noise', 'Search\n Noise'),
                  ('Freq\n ($MHz$)', 'Nave'), ('CP ID'), ('SNR ($dB$)'),
                  ('Velocity\n ($m\ s^{-1}$)'),
                  ('Spectral Width\n ($m\ s^{-1}$)'),
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
                                             color=line[axes_parameters[i][0]],
                                             ax=axes[i], linestyle='-',
                                             label=labels[i][0])
                    if len(w) > 0:
                        warnings.\
                            warn("Warning: {parameter} raised the"
                                 " following warning: {message}"
                                 "".format(parameter=axes_parameters[i][0],
                                           message=str(w[0].message)))
                    axes[i].set_ylabel(labels[i][0], rotation=0, labelpad=30)
                    axes[i].\
                        axhline(y=boundary_ranges[axes_parameters[i][0]][0] +
                                0.8, xmin=-0.11, xmax=-0.05, clip_on=False,
                                color=line[axes_parameters[i][0]])
                    axes[i].set_ylim(boundary_ranges[axes_parameters[i][0]][0],
                                     boundary_ranges[axes_parameters[i][0]][1])
                    # For better y-axis ticks
                    if scale == 'log':
                        axes[i].yaxis.set_major_locator(ticker.
                                                        LogLocator(numticks=3))
                    else:
                        axes[i].yaxis.\
                                set_major_locator(ticker.
                                                  MaxNLocator(integer=True,
                                                              nbins=3))
                    axes[i].yaxis.set_label_coords(-0.08, 0.085)

                    if i == 1:
                        # plot the shared parameter
                        second_ax = axes[i].twinx()
                        # warnings are not caught with try/except
                        with warnings.catch_warnings(record=True) as w:
                            cls.plot_time_series(dmap_data, beam_num=beam_num,
                                                 parameter=axes_parameters[i][1],
                                                 color=line[axes_parameters[i][1]],
                                                 channel=channel,
                                                 scale=scale, ax=second_ax,
                                                 linestyle='--')
                        if len(w) > 0:
                            warnings.\
                                warn("Warning: {parameter} raised the"
                                     " following warning: {message}"
                                     "".format(parameter=axes_parameters[i][1],
                                               message=str(w[0].message)))
                        second_ax.set_xticklabels([])
                        second_ax.set_ylabel(labels[i][1], rotation=0,
                                             labelpad=25)
                        second_ax.\
                            axhline(y=boundary_ranges[axes_parameters[i][1]][0]
                                    + 0.8, xmin=1.07, xmax=1.13,
                                    clip_on=False, linestyle='--',
                                    color=line[axes_parameters[i][1]])
                        second_ax.\
                            set_ylim(boundary_ranges[axes_parameters[i][1]][0],
                                     boundary_ranges[axes_parameters[i][1]][1])
                        second_ax.yaxis.set_label_coords(1.1, 0.7)
                        if scale == 'log':
                            second_ax.yaxis.\
                                    set_major_locator(ticker.
                                                      LogLocator(numticks=4))

                        else:
                            second_ax.yaxis.\
                                    set_major_locator(ticker.
                                                      MaxNLocator(integer=True,
                                                                  nbins=3))

                axes[i].set_facecolor(background_color)
            # plot cp id
            elif i == 2:
                cls.plot_time_series(dmap_data, beam_num=beam_num,
                                     parameter=axes_parameters[i],
                                     channel=channel,
                                     ax=axes[i])
                axes[i].set_ylabel('CPID', rotation=0, labelpad=30)
                axes[i].yaxis.set_label_coords(-0.08, 0.079)
                axes[i].set_facecolor(background_color)
            # plot range-time
            else:
                # Current standard is to only have groundscatter
                # on the velocity plot. This may change in the future.
                if groundscatter and axes_parameters[i] == 'v':
                    grndflg = True
                else:
                    grndflg = False
                _, cbar, _, x, _, _ =\
                    cls.plot_range_time(dmap_data,
                                        beam_num=beam_num,
                                        colorbar_label=labels[i],
                                        parameter=axes_parameters[i],
                                        ax=axes[i],
                                        groundscatter=grndflg,
                                        channel=channel,
                                        cmap=cmap[axes_parameters[i]],
                                        zmin=boundary_ranges[axes_parameters[i]][0],
                                        zmax=boundary_ranges[axes_parameters[i]][1],
                                        ymax=75,
                                        background=background_color)
                # Overwriting velocity ticks to get a better pleasing
                # look on the colorbar
                # Preference by Marina Schmidt
                if axes_parameters[i] == 'v':
                    locator = ticker.LinearLocator(numticks=5)
                    ticks =\
                        locator.tick_values(vmin=boundary_ranges[axes_parameters[i]][0],
                                            vmax=boundary_ranges[axes_parameters[i]][1])
                    if ticks[0] < boundary_ranges[axes_parameters[i]][0]:
                        ticks[0] = boundary_ranges[axes_parameters[i]][0]

                    if ticks[-1] > boundary_ranges[axes_parameters[i]][1]:
                        ticks[-1] = boundary_ranges[axes_parameters[i]][1]
                    cbar.set_ticks(ticks)
                axes[i].set_ylabel('Range Gates')
            if i < num_plots-1:
                axes[i].set_xticklabels([])
            # last plot needs the label on the x-axis
            else:
                axes[i].set_xlabel('Date (UTC)')

        if title is None:
            plt.title(cls.__generate_title(x[0], x[-1], beam_num,
                                           channel), y=2.4)
        else:
            plt.title(title, y=2.4)
        plt.subplots_adjust(wspace=0, hspace=0)
        if watermark:
            fig.text(0.90, 0.99, "Not for Publication Use", fontsize=75,
                     color='gray', ha='right', va='top',
                     rotation=-38, alpha=0.3)

        return fig, axes

    @classmethod
    def __generate_title(cls, start_time: datetime, end_time: datetime,
                         beam_num: int, channel: int) -> str:
        if cls.dmap_data[0]['fitacf.revision.major'] == 5:
            version = "2.5"
        else:
            version = "{major}.{minor}"\
                    "".format(major=cls.dmap_data[0]['fitacf.revision.major'],
                              minor=cls.dmap_data[0]['fitacf.revision.minor'])
        if cls.dmap_data[0]['origin.code'] == 100:
            radar_system = " (Borealis)"
        else:
            # I would put ROS but Alaska and AGILE DARN might have their own
            # systems and not sure how to decipher between them. If something
            # changes in the file structure, then I can add it here.
            radar_system = ""
        radar_name = SuperDARNRadars.radars[cls.dmap_data[0]['stid']].name
        # Date time formats:
        #   %Y - year
        #   %b - month abbreviation
        #   %d - day
        #   %H - Hour
        #   %M - 2-digit minutes
        if end_time.day == start_time.day:
            end_format = "%H:%M"
        elif end_time.month == start_time.month:
            end_format = "%d %H:%M"
        elif end_time.year == start_time.year:
            end_format = "%b %d %H:%M"
        else:
            end_format = "%Y %b %d %H:%M"
        title_format =\
            "{name}{system} Fitacf {version}"\
            "{system} {start_date} - {end_date}  Beam {num}"\
            "".format(name=radar_name, version=version,
                      system=radar_system,
                      start_date=start_time.strftime("%Y %b %d %H:%M"),
                      end_date=end_time.strftime(end_format),
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

    # TODO: if used in other plotting methods then this should moved to
    #       utils
    @classmethod
    def __determine_start_end_time(cls, start_time: datetime,
                                   end_time: datetime) -> tuple:
        """
        Sets the start and end time based on import of dmap_data

        Parameter
        ---------
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
            start_time = cls.__time2datetime(cls.dmap_data[0])
        if not end_time:
            end_time = cls.__time2datetime(cls.dmap_data[-1])
        return start_time, end_time
