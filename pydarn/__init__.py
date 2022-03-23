#Copyright 2018 SuperDARN Canada, Univeristy Saskatchewan
#Author(s): Marina Schmidt
#
# Disclaimer:
# pyDARN is under the LGPL v3 license found in the root directory LICENSE.md
# Everyone is permitted to copy and distribute verbatim copies of this license
# document, but changing it is not allowed.
#
# This version of the GNU Lesser General Public License incorporates the terms
# and conditions of version 3 of the GNU General Public License,
# supplemented by the additional permissions listed below.
#
# Modifications:
# 2022-03-10 MTS - removed radar_fov from the __init__ file
"""
Init file to setup the logging configuration and linking pyDARN's
module, classes, and functions.
"""
# KEEP THIS FILE AS MINIMAL AS POSSIBLE!

import os

# version file
from .version import __version__

# Import io for pyDARN
from .io.superdarn_io import SuperDARNRead

# Importing pydarn exception classes
from .exceptions import rtp_exceptions
from .exceptions import plot_exceptions
from .exceptions import radar_exceptions
from .exceptions.warning_formatting import standard_warning_format
from .exceptions.warning_formatting import only_message_warning_format
from .exceptions.warning_formatting import citing_warning
from .exceptions.warning_formatting import partial_record_warning
from .exceptions.warning_formatting import cartopy_warning
from .exceptions.warning_formatting import cartopy_print_warning

# importing utils
from .utils.constants import Re
from .utils.constants import EARTH_EQUATORIAL_RADIUS
from .utils.constants import C
from .utils.range_estimations import RangeEstimation
from .utils.virtual_heights import VHModels
from .utils.conversions import dmap2dict
from .utils.plotting import MapParams
from .utils.plotting import check_data_type
from .utils.plotting import time2datetime
from .utils.plotting import find_record
from .utils.superdarn_radars import SuperDARNRadars
from .utils.superdarn_cpid import SuperDARNCpids
from .utils.superdarn_radars import Hemisphere
from .utils.superdarn_radars import read_hdw_file
from .utils.superdarn_radars import get_hdw_files
from .utils.scan import build_scan
from .utils.geo import geocentric_coordinates
from .utils.coordinates import Coords

# import plotting
from .plotting.color_maps import PyDARNColormaps
from .plotting.projections import Projs
from .plotting.rtp import RTP
from .plotting.fan import Fan
from .plotting.grid import Grid
from .plotting.acf import ACF
from .plotting.power import Power
from .plotting.maps import Maps

citing_warning()
