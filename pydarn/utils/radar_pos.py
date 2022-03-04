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

from pydarn import (SuperDARNRadars, Coords, Re, VH_types,
                    EARTH_EQUATORIAL_RADIUS, Range_Estimation,
                    radar_exceptions)


def radar_fov(stid: int, coords: object = Coords.AACGM_MLT,
              date: dt.datetime = None, **kwargs):
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
    # Locate base PyDARN directory
    # Plus 1 is due to the fact fov files index at 1 so in the plotting
    # of the boundary there is a subtraction of 1 to offset this as python
    # converts to index of 0 which my code already accounts for
    beam_corners_lats = np.zeros((ranges[1]-ranges[0]+1, max_beams+1))
    beam_corners_lons = np.zeros((ranges[1]-ranges[0]+1, max_beams+1))
    for beam in range(0, max_beams+1):
        for gate in range(ranges[0], ranges[1]):
            lat, lon = geographic_cell_positions(stid=stid, beam=beam,
                                                 range_gate=gate, height=300,
                                                 **kwargs)
            if coords in [Coords.AACGM_MLT, Coords.AACGM]:
                if date is None:
                    date = dt.datetime.now()

                geomag = np.array(aacgmv2.get_aacgm_coord(glat=lat,
                                                          glon=lon,
                                                          height=250,
                                                          dtime=date))
                lat = geomag[0]
                lon = geomag[1]
            beam_corners_lats[gate-ranges[0], beam] = lat
            beam_corners_lons[gate-ranges[0], beam] = lon
    if coords == Coords.AACGM_MLT:
        fan_shape = beam_corners_lons.shape
        # Work out shift due in MLT
        beam_corners_mlts = np.zeros((fan_shape[0], fan_shape[1]))
        mltshift = beam_corners_lons[0, 0] - \
            (aacgmv2.convert_mlt(beam_corners_lons[0, 0], date) * 15)
        beam_corners_mlts = beam_corners_lons - mltshift
        return beam_corners_lats, beam_corners_mlts
    else:
        # Return geographic coordinates
        return beam_corners_lats, beam_corners_lons
