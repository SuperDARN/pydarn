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
import logging.config
import yaml

# Importing pydarn exception classes
from .exceptions import dmap_exceptions
from .exceptions import superdarn_exceptions
from .exceptions import rtp_exceptions
from .exceptions import borealis_exceptions
from .exceptions import radar_exceptions
from .exceptions.warning_formatting import standard_warning_format
from .exceptions.warning_formatting import only_message_warning_format

# Importing pydarn pydmap data structure classes
from .io.datastructures import DmapScalar
from .io.datastructures import DmapArray
from .io import superdarn_formats

# importing utils
from .utils.conversions import dict2dmap
from .utils.conversions import dmap2dict
from .utils.superdarn_radars import SuperDARNRadars
from .utils.superdarn_cpid import SuperDARNCpids
from .utils.superdarn_radars import Hemisphere
from .utils.superdarn_radars import read_hdw_file

# Importing pydarn dmap classes
from .io.dmap import DmapRead
from .io.dmap import DmapWrite

# Importing pydarn superdarn classes
from .io.superdarn import SDarnRead
from .io.superdarn import SDarnWrite
from .io.superdarn import SDarnUtilities

# Importing pydarn borealis classes
from .io.borealis import borealis_formats
from .io.borealis.borealis import BorealisRead
from .io.borealis.borealis import BorealisWrite
from .io.borealis.borealis_convert import BorealisConvert

# import plotting
from .plotting.color_maps import PyDARNColormaps
from .plotting.rtp import RTP

"""
pyDARN uses yaml for logging configuration because its legibility
makes it the preferred configuration file format.
"""
# real path is needed because path imports from where it is ran and the
# logging config will not be in the users current path.
real_path = os.path.realpath(__file__)
dirname = os.path.dirname(real_path)

# setting the logging configuration.
log_path = dirname + "/logging_config.yaml"
with open(log_path, 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)
