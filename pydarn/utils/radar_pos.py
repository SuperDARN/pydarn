# Copyright (C) 2020 SuperDARN Canada, University of Saskatchewan
# Author(s): Daniel Billett
"""
This module is used for handling coordinates of a specified radar
in AACGMv2 or geographic coordinates
"""

import datetime
import numpy as np
import os

import aacgmv2


def radar_fov(stid: int, coords: str = 'aacgm', date: datetime = None):
    """
    Returning beam/gate coordinates of a specified radar's field-of-view

    Parameters
    ----------
    stid: int
        Station ID of radar of choice. See 'superdarn.ca/radar-info'
        for ID numbers.
    coords: str
        Type of coordinates returned. 'geo' = Geographic, 'aacgm' = AACGMv2
        Default: 'aacgm'
    date: datetime
        datetime object date to be used for AACGMv2 conversion
        Default: Current day

    Returns
    ----------
    latitudes: np.array
        n_beams x n_gates array of geographic or AACGMv2 latitudes
        for range gate corners
    longitudes/mlts: np.array
        n_beams x n_gates array of geographic or AACGMv2 longitudes
        for range gate corners
    """
    # Locate base PyDARN directory
    my_path = os.path.abspath(os.path.dirname(__file__))
    base_path = os.path.join(my_path, '..')

    # Find files holding radar beam/gate locations
    beam_lats = base_path+'/radar_fov_files/' + \
        str(stid).zfill(3)+'_lats.txt'
    beam_lons = base_path+'/radar_fov_files/' + \
        str(stid).zfill(3)+'_lons.txt'

    # Read in geographic coordinates
    beam_corners_lats = np.loadtxt(beam_lats)
    beam_corners_lons = np.loadtxt(beam_lons)

    # AACGMv2 conversion
    if coords == 'aacgm':
        if not date:
            date = datetime.datetime.now()

        # Initialise arrays
        fan_shape = beam_corners_lons.shape
        beam_corners_aacgm_lons = \
            np.zeros((fan_shape[0], fan_shape[1]))
        beam_corners_aacgm_lats = \
            np.zeros((fan_shape[0], fan_shape[1]))

        for x in range(fan_shape[0]):
            for y in range(fan_shape[1]):
                # Conversion
                geomag = np.array(aacgmv2.
                                  get_aacgm_coord(beam_corners_lats[x, y],
                                                  beam_corners_lons[x, y],
                                                  250, date))
                beam_corners_aacgm_lats[x, y] = geomag[0]
                beam_corners_aacgm_lons[x, y] = geomag[1]

        # Return AACGMv2 latitudes and longitudes
        return beam_corners_aacgm_lats, beam_corners_aacgm_lons
    else:
        # Return geographic coordinates
        return beam_corners_lats, beam_corners_lons
