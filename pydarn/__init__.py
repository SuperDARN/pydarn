"""
Copyright 2018 SuperDARN

__init__.py
2018-11-05
Init file to setup the logging configuration and linking pydarn's
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

# Importing pydarn pydmap data structure classes
from .io.datastructures import DmapScalar
from .io.datastructures import DmapArray
from .io.datastructures import DmapRecord
from .io import superdarn_formats


# Importing pydarn dmap classes
from .io.dmap import DmapRead
from .io.dmap import DmapWrite

# Importing pydarn superdarn classes
from .io.superdarn import DarnRead
from .io.superdarn import DarnWrite
from .io.superdarn import DarnUtilities

# Importing pydarn borealis classes
from .io.borealis import borealis_formats
from .io.borealis.borealis_utilities import BorealisUtilities
from .io.borealis.borealis_site import BorealisSiteRead
from .io.borealis.borealis_site import BorealisSiteWrite
from .io.borealis.borealis_array import BorealisArrayRead
from .io.borealis.borealis_array import BorealisArrayWrite
from .io.borealis.borealis_convert import BorealisConvert
from .io.borealis.restructure_borealis import BorealisRestructureUtilities
from .io.borealis.borealis import read_borealis_file
from .io.borealis.borealis import write_borealis_file
from .io.borealis.borealis import return_reader
from .io.borealis.borealis import borealis_site_to_array_dict
from .io.borealis.borealis import borealis_array_to_site_dict
from .io.borealis.borealis import borealis_array_to_site_file
from .io.borealis.borealis import borealis_site_to_array_file
from .io.borealis.borealis import borealis_write_to_dmap
from .io.borealis.borealis import bfiq2darniqdat
from .io.borealis.borealis import rawacf2darnrawacf
from .io.borealis import bfiq_to_rawacf

# importing utils
from .utils.conversions import dict2dmap
from .utils.conversions import dmap2dict

# import plotting
from .plotting.superdarn_radars import SuperDARNRadars
from .plotting.superdarn_cpid import SuperDARNCpids
from .plotting.rtp import RTP

"""
Pydarn uses yaml for logging configuration because it is the
preferred configuration file format because of its readability.

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
