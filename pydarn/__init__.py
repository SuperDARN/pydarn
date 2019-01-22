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
from .exceptions import pydmap_exceptions

# Importing pydarn pydmap data structure classes
from .pydmap.datastructures import DmapScalar
from .pydmap.datastructures import DmapArray
from .pydmap.datastructures import DmapRecord
from .pydmap import superdarn_formats

# Importing pydarn pydmap classes
from .pydmap.io import DmapRead

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
