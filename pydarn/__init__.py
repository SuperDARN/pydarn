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
# 2023-06-20 PXP - added TimeSeriesParams to the __init__ file
"""
Init file to setup the logging configuration and linking pyDARN's
module, classes, and functions.
"""
# KEEP THIS FILE AS MINIMAL AS POSSIBLE!
# ruff: noqa: F401
# version file
from .version import __version__

# Import io for pyDARN
from .io.superdarn_io import SuperDARNRead

# Importing pydarn exception classes
from .exceptions import rtp_exceptions, plot_exceptions, radar_exceptions
from .exceptions.warning_formatting import (standard_warning_format,
    only_message_warning_format, partial_record_warning, nightshade_warning)

# importing utils
from .utils.constants import Re, EARTH_EQUATORIAL_RADIUS, C
from .utils.citations import Citations
from .utils.range_estimations import RangeEstimation
from .utils.virtual_heights import VHModels
from .utils.conversions import dmap2dict
from .utils.plotting import (MapParams, TimeSeriesParams, check_data_type,
    time2datetime, find_record, determine_embargo, add_embargo)
from .utils.general_utils import GeneralUtils
from .utils.superdarn_radars import RadarID, SuperDARNRadars
from .utils.superdarn_cpid import SuperDARNCpids
from .utils.superdarn_radars import Hemisphere, read_hdw_file, get_hdw_files
from .utils.scan import find_records_by_datetime, find_records_by_scan
from .utils.geo import geocentric_coordinates, calculate_azimuth
from .utils.coordinates import Coords
from .utils.terminator import terminator
from .utils.recalculate_elevation import recalculate_elevation
from .utils.filters import Boxcar

# import plotting
from .plotting.color_maps import PyDARNColormaps
from .plotting.projections import Projs
from .plotting.rtp import RTP
from .plotting.fan import Fan
from .plotting.grid import Grid
from .plotting.acf import ACF
from .plotting.power import Power
from .plotting.maps import Maps
from .plotting.iq import IQ
