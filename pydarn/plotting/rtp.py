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

class RTP(matplotlib.pyplot):
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
    def __str__(self):
        return "This class is static class that provides"\
                " the following methods: \n"\
                "   - plot_rang_time()\n"\
                "   - plot_time_series()\n"\
                "   - plot_summary()\n"

    def plot_range_time(cls):
        pass

    def plot_time_series(cls):
        pass

    def plot_summary(cls):
        pass
