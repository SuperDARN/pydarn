# (C) Copyright 2021 SuperDARN Canada, University of Saskatchewan
# Author(s): Marina Schmidt
#
# This file is part of the pyDARN Library.
#
# pyDARN is under the LGPL v3 license found in the root directory LICENSE.md
# Everyone is permitted to copy and distribute verbatim copies of this license
# document, but changing it is not allowed.
#
# This version of the GNU Lesser General Public License incorporates the terms
# and conditions of version 3 of the GNU Lesser General Public License,
# supplemented by the additional permissions listed below.
#
# Modifications:
#

"""
coordinates.py is a group of methods that focus on coordinates systems used in
plotting
"""
import enum

class Projs(enum.Enum):
    """
    Projection class is a list of enums for the various
    projects supported by pyDARN.

    enumerators:
    """

    POLAR = enum.auto()
    GEO_COASTALINE = enum.auto()
