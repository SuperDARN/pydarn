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

class Coords(enum.Enum):
    """
    This coordinate class is to list the current coordinate systems
    a user can pick from

    enumerators:
        RANGE_GATE: range gates
        SLANT_RANGE: slant range (km)
        GROUND_SCATTER_MAPPED_RANGE: ground scatter mapped range (km)
        GEOGRAPHIC: geographical coordinates lat and longitude (degree)
        AACGM: Magnetic geographical coordinates lat and longitude (degree)
    """

    RANGE_GATE = enum.auto()
    SLANT_RANGE = enum.auto()
    GROUND_SCATTER_MAPPED_RANGE = enum.auto()
    GEOGRAPHIC = enum.auto()
    AACGM = enum.auto()
