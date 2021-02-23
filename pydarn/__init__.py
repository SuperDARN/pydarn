"""
Copyright 2018 SuperDARN Canada, Univeristy Saskatchewan
Author(s): Marina Schmidt

Licensed under GNU v3.0

__init__.py
2018-11-05
Init file to setup the logging configuration and linking pyDARN's
module, classes, and functions.
"""
# KEEP THIS FILE AS MINIMAL AS POSSIBLE!

import os

# Import io for pyDARN
from .io.superdarn_io import SuperDARNRead

# Importing pydarn exception classes
from .exceptions import rtp_exceptions
from .exceptions import plot_exceptions
from .exceptions import radar_exceptions
from .exceptions.warning_formatting import standard_warning_format
from .exceptions.warning_formatting import only_message_warning_format

# importing utils
from .utils.conversions import dmap2dict
from .utils.conversions import gate2slant
from .utils.plotting import check_data_type
from .utils.plotting import time2datetime
from .utils.superdarn_radars import SuperDARNRadars
from .utils.superdarn_cpid import SuperDARNCpids
from .utils.superdarn_radars import Hemisphere
from .utils.superdarn_radars import read_hdw_file
from .utils.superdarn_radars import get_hdw_files
from .utils.scan import build_scan
from .utils.radar_pos import radar_fov

# import plotting
from .plotting.color_maps import PyDARNColormaps
from .plotting.rtp import RTP
from .plotting.fan import Fan
from .plotting.acf import ACF
from .plotting.power import Power
from .plotting.grid import Grid
