# Copyright (C) 2020 SuperDARN Canada, University of Saskatchewan
# Author(s): Daniel Billett, Marina Schmidt
#
# The following methods:
# - radar_fov
#
# Modifications:
#   2020-04-20 Marina Schmidt converted the above link to python and changed
#              variable and function names to readability
#   2020-09-15 Marina Schmidt removed fov file reading option
#   2021-09-15 Francis Tholley relocated the virtual height
#              models to another file
#              statement
#   2022-02-02 CJM - radar_fov updated to correctly use lower limit for ranges
#   2022-03-03 MTS - removed geographic methods to other modules
#              abstraction
# Disclaimer:
# pyDARN is under the LGPL v3 license found in the root directory LICENSE.md
# Everyone is permitted to copy and distribute verbatim copies of this license
# document, but changing it is not allowed.
#
# This version of the GNU Lesser General Public License incorporates the terms
# and conditions of version 3 of the GNU General Public License,
# supplemented by the additional permissions listed below.
#
"""
This module is used for handling radar field-of-view
"""
import datetime as dt
import numpy as np

import aacgmv2

from pydarn import (SuperDARNRadars, Coords, Re,
                    EARTH_EQUATORIAL_RADIUS, Range_Estimation,
                    radar_exceptions)


def radar_fov(coords: object = Coords.AACGM_MLT,
              **kwargs):
    """
    Returning beam/gate coordinates of a specified radar's field-of-view

    Parameters
    ----------
    stid: int
        Station ID of radar of choice. See 'superdarn.ca/radar-info'
        for ID numbers.
    max_beams : int
        max number of beams to generate coordinates for
    coords: Coords object
        Type of coordinates returned
        Default: Coords.AACGM
    date: datetime
        datetime object date to be used for AACGMv2 conversion
        Default: Current day

    Returns
    ----------
    latitudes: np.array
        n_beams x n_gates array of geographic or AACGMv2 latitudes
        for range gate corners in degrees
    longitudes/mlts: np.array
        n_beams x n_gates array of geographic or AACGMv2 longitudes
        for range gate corners in degrees

    TODO: make max_beams a range so you can show the fov of a single beam
    """
    return coords(**kwargs)
