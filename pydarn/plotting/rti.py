# Copyright (C) 2019 SuperDARN
# Author: Marian Schmidt
# This code is improvement based on rti.py in the DaVitpy library
# https://github.com/vtsuperdarn/davitpy/blob/master/davitpy

"""
Range-time Intensity plots
"""
import matplotlib
from typing import List
from datetime import datetime

from pydarn import SuperDARNRadars

class RTI(matplotlib.pyplot):
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
    plot
    summaryplot

    """

    parameter_type = {'power': 'pwr',
                      'velocity': 'vel',
                      'sepctral width': 'spect'}

    line_parameter_types = {'frequency': 'freq',
                            'search noise': 'src.noise',
                            'sky noise': 'sky.noise',
                            'control program id': 'cpid',
                            'n averages': 'nave'}

    def plot_parameter(self, *args, dmap_data: List[dict],
                       parameter: str = 'power', **kwargs):

        self.dmap_data = dmap_data


    def plot_line(self, *args, dmap_data: List[dict], **kwargs):
        pass

    def summaryplot(self, *args, dmap_data: List[dict],
                    parameters: str, lines: str, **kwargs):
        pass

    def save_plot(self, filename: str):
        pass

