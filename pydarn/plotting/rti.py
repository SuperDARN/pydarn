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
from datetime import datetime

from pydarn import DmapArray, utils


class RTI():
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

    parameter_type = {'power': ('pwr0', 'array'),
                      'velocity': ('v', 'array'),
                      'spectral width': ('spect', 'array'),
                      'frequency': ('freq', 'scalar'),
                      'search noise': ('src.noise', 'scalar'),
                      'sky noise': ('sky.noise', 'scalar'),
                      'control program id': ('cpid', 'scalar'),
                      'n averages': ('nave', 'scalar')}

    # becuase of the Singleton nature of matplotlib
    # it is written in modules, thus I need to extend the module
    # since I cannot inherit modules :(
    plt = plt

    settings = {'ground_scatter': True}

    @classmethod
    def plot_profile(cls, dmap_data: List[dict], *args,
                     parameter: str = 'power', beamnum: int = 0, **kwargs):
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
        if isinstance(dmap_data[0]['ptab'], DmapArray):
            dmap_list = utils.conversions.dmap2dict(dmap_data)

        cls.settings.update(kwargs)
        cls.beamnum = beamnum
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
            cls.start_time = cls.__time2datetime(dmap_list[0])
            cls.end_time = cls.__time2datetime(dmap_list[-1])
        cls.dmap_data = dmap_list
        param_tuple = cls.parameter_type.get(parameter, None)
        if param_tuple is None:
            data_type = cls.dmap_data[0][parameter]
            if isinstance(data_type, np.ndarray):
                data_type = 'array'
            else:
                data_type = 'scalar'
        else:
            data_type = param_tuple[1]
            cls.parameter = param_tuple[0]

        if data_type == 'array':
            cls.__plot_array(*args, **kwargs)
        else:
            cls.__plot_scalar(*args, **kwargs)

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
    def __plot_array(cls, *args, **kwargs):
        print("made it here")
        # y-axis coordinates, i.e., range gates,
        # TODO: implement variant other coordinate systems for the y-axis
        y = np.linspace(0, cls.dmap_data[0]['nrang'], cls.dmap_data[0]['nrang'])
        y_max = cls.dmap_data[0]['nrang']

        # z: parameter data mapped into the color mesh
        z = np.zeros((1, y_max)) * np.nan
        x = []
        # We cannot simply use numpy's built in min and max function
        # because of the ground scatter value
        z_min = 0
        z_max = 0
        for dmap_record in cls.dmap_data:
            if dmap_record['bmnum'] == cls.beamnum:
                time = cls.__time2datetime(dmap_record)
                if cls.start_time <= time and time <= cls.end_time:
                    # construct the x-axis array
                    x.append(dates.date2num(time))
                    # I do this to avoid having an extra loop to just count how
                    # many records contain the beam number
                    i = len(x) - 1  # offset since we start at 0 not 1
                    if len(x) > 1:
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
        time_axis, elev_axis = np.meshgrid(x, y)
        z_data = np.ma.masked_where(np.isnan(z.T), z.T)
        norm = colors.Normalize(z_min, z_max)
        pc_kwargs = {'rasterized': True, 'cmap': 'viridis', 'norm': norm}
        plt.pcolormesh(time_axis,
                       elev_axis, z_data, lw=0.01,  **pc_kwargs)
        plt.gca().format_xdata = dates.DateFormatter("%H:%M")
        plt.colorbar()
        plt.show()

    @classmethod
    def summaryplot(cls, *args, dmap_data: List[dict],
                    parameters: str, lines: str, **kwargs):
        pass
