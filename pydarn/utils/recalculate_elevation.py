# (C) Copyright SuperDARN Canada, University of Saskatchewan 2022
# Author: Carley Martin 20221101
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
# About:
# Modified from the RST elevation_v2.c code (Simon Shepherd's code).
# Method: https://agupubs.onlinelibrary.wiley.com/doi/full/10.1002/2017RS006348
# THIS CODE IS DESIGNED TO AMEND ELEVATION
# AFTER FITACF FITTING (AT THE VISUALIZATION STEP TO QUICKLY CHECK THE EFFECTS
# OF DIFFERENT TDIFF VALUES) NOT TO REPLACE THE FITTING ITSELF
#
# Modifications:
# 20221221 - Bharat Kunduri: Updated to RST elevation code

import numpy as np

from typing import List
from copy import deepcopy

from pydarn import (SuperDARNRadars, C, RadarID)


def recalculate_elevation(dmap_data: List[dict], tdiff: float,
                          overwrite: bool = False,
                          interferometer_offset: list = None):
    """
    Recalculates elevation values for a given tdiff Value

    Parameters
    -----------
    dmap_data: list of dictionaries
        fitacf data
    tdiff: float
        propagation time from interferometer array to phasing matrix
        input minus propagation time from main array antenna, microseconds
    overwrite: bool
        If true then return a new dmap_data with new elevation to plot with
        if false then return dictionary of new elevations for further use
    interferometer_offset: list
        select position of interferometer array wrt the main array
        needs to be list of [X, Y, Z] e.g. [0.0, 100.0, 1.0]

    Raises
    ------

    Returns
    -------
    elv_amended: dictionary of lists
        amended elevation values for each record given
    """
    if not overwrite:
        # Make phi1 output into dictionary
        elv_amended = {}
    else:
        dmap_amended = deepcopy(dmap_data)

    # Hardware config for radar
    # Doesn't have to be in the loop, since we're accessing only the first rec
    radar_hdw = SuperDARNRadars.radars[RadarID(dmap_data[0]['stid'])].hardware_info
    if interferometer_offset is not None:
        int_pos = interferometer_offset
    else:
        int_pos = radar_hdw.interferometer_offset

    # If inteferometer is infront (+1) or behind (-1) main array
    if int_pos[1] < 0:
        sgn = -1.0
    else:
        sgn = 1.0

    boff = (radar_hdw.beams / 2.0) - 0.5

    # For each record in data, recalculate the elevation
    for ind in range(0, len(dmap_data)):
        # If there is no elevation data, append empty list and skip
        if 'phi0' not in dmap_data[ind]:
            print("No elevation data. 'phi0' parameter missing"
                  " from the record")
            if not overwrite:
                elv_amended[ind] = []
            continue

        # Beam direction off boresight in RADIANS
        phi0 = np.radians(radar_hdw.beam_separation
                          * (dmap_data[ind]['bmnum'] - boff))
        # Cos and Sin of phi in shape of phi0
        cp0 = np.cos(phi0)
        sp0 = np.sin(phi0)

        # Phase delay [radians] due to electrical path difference.
        psi_ele = (-2.0 * np.pi * (dmap_data[ind]['tfreq'])
                   * 1000.0 * tdiff * 1.0e-6)
        # Elevation angle (a0) where psi (phase difference) is maximum
        a0 = np.arcsin(sgn * int_pos[2] * cp0
                       / np.sqrt(int_pos[1]**2 + int_pos[2]**2))
        if a0 < 0:
            a0 = 0
        ca0 = np.cos(a0)
        sa0 = np.sin(a0)

        # maximum phase = psi_ele + psi_geo(a0)
        psi_max = psi_ele + 2.0 * np.pi * (dmap_data[ind]['tfreq']) *\
            (1e3 / C) * (int_pos[0] * sp0 + int_pos[1]
                         * np.sqrt(ca0*ca0 - sp0*sp0) + int_pos[2] * sa0)

        # compute the number of 2pi factors necessary to map to correct region
        dpsi = (psi_max - dmap_data[ind]['phi0'])
        if int_pos[1] > 0:
            n2pi = np.floor(dpsi / (2.0 * np.pi))
        else:
            n2pi = np.ceil(dpsi / (2.0 * np.pi))
        d2pi = n2pi * 2.0 * np.pi
        # map observed phase to correct extended phase
        psi_obs = dmap_data[ind]['phi0'] + d2pi
        # solve for the elevation angle
        E = (psi_obs / (2.0*np.pi*dmap_data[ind]['tfreq']*1.0e3)
             + tdiff*1e-6) * C - int_pos[0] * sp0

        alpha = np.arcsin((E*int_pos[2]
                           + np.sqrt(E*E * int_pos[2]**2
                           - (int_pos[1]**2 + int_pos[2]**2)
                           * (E*E - int_pos[1]*int_pos[1]*cp0*cp0)))
                          / (int_pos[1]*int_pos[1] + int_pos[2]*int_pos[2]))

        # Convert theta back to degrees
        if overwrite:
            dmap_amended[ind].update({'elv': np.degrees(alpha)})
        else:
            elv_amended[ind] = np.degrees(alpha)

    if overwrite:
        return dmap_amended
    else:
        return elv_amended
