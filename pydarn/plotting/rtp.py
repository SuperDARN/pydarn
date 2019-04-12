# Copyright (C) 2019 SuperDARN
# Author: Marian Schmidt
# This code is improvement based on rti.py in the DaVitpy library
# https://github.com/vtsuperdarn/davitpy/blob/master/davitpy

"""
Range-time Intensity plots
"""
import matplotlib.pyplot as plt
from  matplotlib import dates, colors
import numpy as np
from typing import List
from datetime import datetime, timedelta

from pydarn import DmapArray, DmapScalar, utils, rti_exceptions


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

    parameter_type = {'power': ('pwr0', r'Elevation (degrees)'),
                      'velocity': ('v', r'Velocity ($m/s$)'),
                      'elevation': ('elv', r'Signal to Noise ($dB$)'),
                      'spectral width': ('width', r'Spectral Width ($m/s$)'),
                      'frequency': ('freq', ''),
                      'search noise': ('src.noise', ''),
                      'sky noise': ('sky.noise', ''),
                      'control program id': ('cpid', ''),
                      'nave': ('nave', '')}

    # becuase of the Singleton nature of matplotlib
    # it is written in modules, thus I need to extend the module
    # since I cannot inherit modules :(

    settings = {'ground_scatter': True,
                'date_fmt': "%y/%m/%d\n%H:%M",
                'colour_bar': True,
                'colour_bar_label': '',
                'axes_object': None}

    @classmethod
    def plot_range_time(cls, dmap_data: List[dict], *args,
                        parameter: str = 'power', beamnum: int = 0, ax = None,
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
        beamnum : int
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
        """
        # This is only done because the library support DMAP format
        # it would be better to just require a dictionary
        cls.settings.update(kwargs)
        cls.beamnum = beamnum
        if not ax:
            ax = plt.gca()

        # Determine if it is a supported parameter type
        # TODO: Its own method?
        parameter_tuple = cls.parameter_type.get(parameter, parameter)
        if isinstance(parameter_tuple, tuple):
            cls.settings['color_bar'] = parameter_tuple[1]
            cls.parameter = parameter_tuple[0]
        else:
            cls.parameter = parameter_tuple

        # Determine if a DmapRecord was passed in, instead of a list
        # TODO: Its own method?
        if isinstance(dmap_data[0][cls.parameter], DmapArray) or\
           isinstance(dmap_data[0][cls.parameter], DmapScalar):
            dmap_data = utils.conversions.dmap2dict(dmap_data)

        cls.dmap_data = dmap_data
        cls.__check_data_type(cls.parameter, 'array')
        # TODO: it's own method?
        try:
            if len(kwargs['time_span']) == 2:
                cls.start_time = kwargs['time_span'][0]
                cls.end_time = kwargs['time_span'][1]
                cls.interval_time = None
            elif len(kwargs['time_span']) == 3:
                cls.start_time = kwargs['time_span'][0]
                cls.end_time = kwargs['time_span'][2]
                cls.interval_time = kwargs['time_span'][1]
            else:
                raise IndexError("time_span list must be length of 2 or 3")

        except KeyError:
            cls.start_time = cls.__time2datetime(cls.dmap_data[0])
            cls.end_time = cls.__time2datetime(cls.dmap_data[-1])

        # y-axis coordinates, i.e., range gates,
        # TODO: implement variant other coordinate systems for the y-axis
        y = np.linspace(0, cls.dmap_data[0]['nrang'], cls.dmap_data[0]['nrang'])
        y_max = cls.dmap_data[0]['nrang']

        # z: parameter data mapped into the color mesh
        z = np.zeros((1, y_max)) * np.nan
        x = []
        date_list = []
        # We cannot simply use numpy's built in min and max function
        # because of the ground scatter value
        z_min = 0
        z_max = 0
        for dmap_record in cls.dmap_data:
            time = cls.__time2datetime(dmap_record)
            if x == []:
                diff_time = time - time
            else:
                diff_time = time - x[-1]
            print(diff_time.seconds/60)
            if dmap_record['bmnum'] == cls.beamnum:
                if cls.start_time <= time and time <= cls.end_time:
                    # construct the x-axis array
                    # Numpy datetime is used because it properly formats on the
                    # x-axis
                    x.append(time)
                    # I do this to avoid having an extra loop to just count how
                    # many records contain the beam number
                    i = len(x) - 1  # offset since we start at 0 not 1
                    if i > 0:
                        z = np.insert(z, len(z), np.zeros(1, y_max) * np.nan,
                                      axis=0)
                    try:
                        for j in range(len(dmap_record['slist'])):
                            if cls.settings['ground_scatter'] and\
                               dmap_record['gflg'][j] == 1:
                                # chosen value from davitpy to make the
                                # ground scatter a different colour from the colour
                                # map
                                z[i][dmap_record['slist'][j]] = -1000000
                            else:
                                z[i][dmap_record['slist'][j]] = \
                                        dmap_record[cls.parameter][j]
                                if z[i][dmap_record['slist'][j]] < z_min:
                                    z_min = z[i][dmap_record['slist'][j]]
                                if z[i][dmap_record['slist'][j]] > z_max:
                                    z_max = z[i][dmap_record['slist'][j]]
                    # a KeyError may be thrown because slist is not created
                    # due to bad quality data.
                    except KeyError as errror:
                        continue
            elif diff_time.seconds/60.0 > 2.0:
                print("adding time")
                x.append(time)
                i = len(x) - 1  # offset since we start at 0 not 1
                if i > 0:
                    z = np.insert(z, len(z), np.zeros(1, y_max) * np.nan,
                                  axis=0)

        time_axis, elev_axis = np.meshgrid(x, y)
        z_data = np.ma.masked_where(np.isnan(z.T), z.T)
        norm = colors.Normalize(z_min, z_max)
        pc_kwargs = {'rasterized': True, 'cmap': 'viridis', 'norm': norm}

        im = ax.pcolormesh(time_axis, elev_axis, z_data, lw=0.01, **pc_kwargs)
        ax.xaxis.set_major_formatter(dates.DateFormatter(cls.settings['date_fmt']))
        if cls.settings['colour_bar']:
            cb = ax.figure.colorbar(im, ax=ax)
            cb.set_label(cls.settings['color_bar'])


        #if cls.settings['axes_object'] is not None:
        #    cls.settings['axes_object'].pcolormesh(time_axis, elev_axis,
        #                                           z_data, lw=0.01,
        #                                           **pc_kwargs)
        #    cls.settings['axes_object'].xaxis.set_major_formatter(dates.DateFormatter(cls.settings['date_fmt']))
        #else:
        #    plt.pcolormesh(time_axis, elev_axis, z_data, lw=0.01,  **pc_kwargs)
        #    plt.gca().xaxis.set_major_formatter(dates.DateFormatter(cls.settings['date_fmt']))
        #    if cls.settings['colour_bar']:
        #        cb = plt.colorbar()
        #        cb.set_label(cls.settings['color_bar'])


    @classmethod
    def __check_data_type(cls, parameter, expected_type):
        """
        Checks to make sure the plot type is correct
        for the data structure.
        """
        data_type = cls.dmap_data[0][parameter]
        if expected_type == 'array':
            if not isinstance(data_type, np.ndarray):
                raise rti_exceptions.RTPIncorrectPlotMethodError(parameter,
                                                                 data_type)
        else:
            if isinstance(data_type, np.ndarray):
                raise rti_exceptions.RTPIncorrectPlotMethodError(parameter,
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
