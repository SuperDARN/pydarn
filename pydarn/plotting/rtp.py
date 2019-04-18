# Copyright (C) 2019 SuperDARN
# Author: Marian Schmidt
# This code is improvement based on rti.py in the DaVitpy library
# https://github.com/vtsuperdarn/davitpy/blob/master/davitpy

"""
Range-time Intensity plots
"""
import matplotlib.pyplot as plt
from  matplotlib import dates, colors, cm, ticker
import numpy as np
from typing import List
from datetime import datetime, timedelta

from pydarn import DmapArray, DmapScalar, utils, rtp_exceptions


class RTP():
    """
    Range-time intensity plots SuperDARN data using the following fields:

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
    summary_plot

    """
    # Default parameter types that davitpy supports and are usually involved
    # in a summary plot
    parameter_type = {'power': ('p_l', r'Signal to Noise ($dB$)'),
                      'velocity': ('v', r'Velocity ($m/s$)'),
                      'elevation': ('elv', r'Elevation (degrees)'),
                      'spectral width': ('w_l', r'Spectral Width ($m/s$)'),
                      'frequency': ('freq', ''),
                      'search noise': ('noise.search', ''),
                      'sky noise': ('noise.sky', ''),
                      'control program id': ('cpid', ''),
                      'nave': ('nave', '')}


    @classmethod
    def plot_range_time(cls, dmap_data: List[dict], *args,
                        parameter: str = 'power', beam_num: int = 0, ax = None,
                        **kwargs):
        """

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
        beam_num : int
        scalar : boolean
        time_span : [datetime, datetime] or [datetime, datetime, datetime]
            List containing the start time and end time as datetime objects,
            If the list length = 3, then the middle (index=1) value will be
            scale of the time axis (x-axis)
        channel : char
            The channel '1', '2', 'a', 'b', 'c', and 'd' wish to plot
        y_axis : ['gate', '']
        ground_scatter : boolean
            Flag to indicate if ground scatter should be plotted.
            default : False

        Raises
        ------
        """
        # Settings
        settings = {'ground_scatter': False,
                    'date_fmt': "%y/%m/%d\n%H:%M",
                    'color_bar': True,
                    'color_bar_label': '',
                    'color_map': 'jet',
                    'color_bar_label': '',
                    'axes_object': None,
                    'norm_range': None,
                    'boundary': None}


        settings.update(kwargs)
        beam_num = beam_num

        # If an axes object is not passed in then store
        # the equivalent object in matplotlib. This allows
        # for variant matplotlib plotting styles.
        if not ax:
            ax = plt.gca()

        # Determine if it is a supported parameter type
        parameter_tuple = cls.parameter_type.get(parameter, parameter)
        if isinstance(parameter_tuple, tuple):
            settings['color_bar_label'] = parameter_tuple[1]
            parameter = parameter_tuple[0]
        else:
            parameter = parameter_tuple

        # Determine if a DmapRecord was passed in, instead of a list
        try:
            if isinstance(dmap_data[0][parameter], DmapArray) or\
               isinstance(dmap_data[0][parameter], DmapScalar):
                dmap_data = utils.conversions.dmap2dict(dmap_data)
        except KeyError as err:
            raise rtp_exceptions.RTPUnkownParameter(parameter)
        cls.dmap_data = dmap_data
        cls.__check_data_type(parameter, 'array')
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
        y = np.linspace(0, cls.dmap_data[0]['nrang'],
                        cls.dmap_data[0]['nrang'])
        y_max = cls.dmap_data[0]['nrang']

        # z: parameter data mapped into the color mesh
        z = np.zeros((1, y_max)) * np.nan

        # x: time date data
        x = []
        date_list = []

        # We cannot simply use numpy's built in min and max function
        # because of the ground scatter value
        if settings["boundary"]:
            z_min, z_max = settings["value_boundaries"]
        else:
            z_min = cls.dmap_record[0][parameter][0]
            z_max = cls.dmap_record[0][parameter][0]
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
                    x.append(x[-1] + timedelta(0,120))
                    i = len(x) - 1  # offset since we start at 0 not 1
                    if i > 0:
                        z = np.insert(z, len(z), np.zeros(1, y_max) * np.nan,
                                      axis=0)

            # Get data for the provided beam number
            if beam_num == 'all' or dmap_record['bmnum'] == beam_num:
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
                            # if it is ground scatter store a very
                            # low number in that cell
                            if settings['ground_scatter'] and\
                               dmap_record['gflg'][j] == 1:
                                # chosen value from davitpy to make the
                                # ground scatter a different color from the color
                                # map
                                z[i][dmap_record['slist'][j]] = -1000000
                            # otherwise store parameter value
                            else:
                                # check if boundaries have been set
                                if settings["boundary"]:
                                    # see if data within boundaries
                                    if z_min < dmap_record[parameter][j] and\
                                       z_max > dmap_record[parameter][j]:
                                        z[i][dmap_record['slist'][j]] = \
                                                dmap_record[parameter][j]
                                else:
                                    z[i][dmap_record['slist'][j]] = \
                                            dmap_record[parameter][j]
                                    # calculate min and max value
                                    if z[i][dmap_record['slist'][j]] < z_min or z_min is None:
                                        z_min = z[i][dmap_record['slist'][j]]
                                    if z[i][dmap_record['slist'][j]] > z_max:
                                        z_max = z[i][dmap_record['slist'][j]]
                    # a KeyError may be thrown because slist is not created
                    # due to bad quality data.
                    except KeyError as errror:
                        continue

        # Check if there is any data to plot
        if np.all(np.isnan(z)):
            raise rtp_exceptions.RTPNoDataFoundError(parameter, beam_num, start_time, end_time)
        time_axis, elev_axis = np.meshgrid(x, y)
        z_data = np.ma.masked_where(np.isnan(z.T), z.T)

        # Norm_range sets the normalization range
        if settings['norm_range']:
            norm = colors.Normalize(settings['norm_range'][0],
                                    settings['norm_range'][1])
        # otherwise use calculated values
        else:
            norm = colors.Normalize(z_min, z_max)

        cmap = cm.get_cmap(settings['color_map'])
        # set ground scatter to grey
        cmap.set_under('grey', 1.0)

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
            cb = ax.figure.colorbar(im, ax=ax)
            cb.set_label(settings['color_bar_label'])

        return im, cb, cmap

    @classmethod
    def __check_data_type(cls, parameter, expected_type):
        """
        Checks to make sure the plot type is correct
        for the data structure.
        """
        data_type = cls.dmap_data[0][parameter]
        if expected_type == 'array':
            if not isinstance(data_type, np.ndarray):
                raise rtp_exceptions.RTPIncorrectPlotMethodError(parameter,
                                                                 data_type)
        else:
            if isinstance(data_type, np.ndarray):
                raise rtp_exceptions.RTPIncorrectPlotMethodError(parameter,
                                                                 data_type)


    # TODO: move to a utils or superDARN utils
    @classmethod
    def __time2datetime(cls, dmap_record):
        year = dmap_record['time.yr']
        month = dmap_record['time.mo']
        day = dmap_record['time.dy']
        hour = dmap_record['time.hr']
        minute = dmap_record['time.mt']
        second = dmap_record['time.sc']
        micro_sec = dmap_record['time.us']

        return datetime(year=year, month=month, day=day, hour=hour,
                        minute=minute, second=second, microsecond=micro_sec)

    # Needs its own method because it generates vertical lines when
    # the cpid changes
    @classmethod
    def __plot_cpid(cls, *args, **kwargs):
        pass

    @classmethod
    def __plot_scalar(cls, *args, **kwargs):
        pass

    @classmethod
    def summaryplot(cls, *args, dmap_data: List[dict],
                    parameters: str, lines: str, **kwargs):
        pass
