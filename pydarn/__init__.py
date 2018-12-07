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
from .exceptions.pydmap_exceptions import EmptyFileError
from .exceptions.pydmap_exceptions import DmapDataError

# Importing pydarn pydmap classes
from .pydmap.io import RawDmapRead
from .pydmap.io import parse_dmap_format_from_file
from .pydmap.io import dicts_to_file
from .pydmap.io import parse_dmap_format_from_stream
from .pydmap.datastructures import Dmapscalar
from .pydmap.datastructures import DmapArray
from .pydmap.datastructures import DmapRecord

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
