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
# Modified from the DaVit IDL rad_fit_calculate_elevation.pro which is from
# the make_fit C function in RST. THIS CODE IS DESIGNED TO AMEND ELEVATION
# AFTER FITACF FITTING (AT THE VISUALIZATION STEP TO QUICKLY CHECK THE EFFECTS
# OF DIFFERENT TDIFF VALUES) NOT TO REPLACE THE FITTING ITSELF
#
# Modifications:
#

import numpy as np

from datetime import datetime
from typing import List
from copy import deepcopy

from pydarn import (SuperDARNRadars, C)


def recalculate_elevation(dmap_data: List[dict], tdiff: float,
                          scan_boresight_offset: float = 0.0,
                          overwrite: bool = False):
    """
    Recalculates elevation values for a given tdiff Value
    
    Parameters
    -----------
    dmap_data: list of dictionaries
        fitacf data 
    tdiff: float
        propagation time from interferometer array to phasing matrix
        input minus propagation time from main array antenna, microseconds
    scan_boresight_offset: float
        offset between the physical boresight and scanning boresight
        Generally do not differ (=0.0) except at Blackstone
    overwrite: bool
        If true then return a new dmap_data with new elevation to plot with
        if false then return dictionary of new elevations for further use
        
    
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

    # For each record in data, recalculate the elevation
    for ind in range(0, len(dmap_data)):
        # If there is no elevation data, append empty list and skip
        if 'phi0' not in dmap_data[ind]:
            if not overwrite:
                elv_amended[ind] = []
            continue
        # Fitacf Phi0 Data
        phi0 = dmap_data[ind]['phi0']
        size_phi0 = len(phi0)
    
        # Hardware config for radar
        radar_hdw = SuperDARNRadars.radars[dmap_data[0]['stid']].hardware_info
        phase_sign = radar_hdw.phase_sign
        int_pos = radar_hdw.interferometer_offset

        # Antenna separation in meters
        antenna_sep = np.sqrt(int_pos[0]**2 + int_pos[1]**2 + int_pos[2]**2)

        # Elevation angle correction
        elv_corr = phase_sign * np.arcsin( int_pos[2] / antenna_sep)
        # If inteferometer is infront (+1) or behind (-1) main array
        if int_pos[1] > 0:
            phi_sign = 1.0
        else:
            phi_sign = -1.0
        elv_corr = elv_corr * -phi_sign

        # Calculate offset in beam widths to edge of array
        offset = radar_hdw.beams/2.0 - 0.5

        # Beam direction off boresight in RADIANS
        phi = np.radians(radar_hdw.beam_separation * (dmap_data[ind]['bmnum'] - offset)
                         + scan_boresight_offset)

        # Cos of phi in shape of phi0
        c_phi = np.ones(size_phi0) * np.cos(phi)

        # wave number : k = 2pi*f/C
        k = np.ones(size_phi0) *\
            (2.0 * np.pi * (dmap_data[ind]['tfreq'] * 1000.0) / C)

        # phase shift caused by cables - rad
        dchi_cable = np.ones(size_phi0) *\
            (-2.0 * np.pi * (dmap_data[ind]['tfreq']) * 1000.0 * tdiff * 1.0e-6)

        # max phase shift possible - rad
        chi_max = np.ones(size_phi0) *\
            (phi_sign * k * antenna_sep * c_phi + dchi_cable)

        # Actual phase angle + cable
        phi_temp = phi0 + 2.0 * np.pi * np.floor((chi_max - phi0) / (2.0 * np.pi))

        if phi_sign < 0.0:
            phi_temp = phi_temp + 2.0 * np.pi

        # Remove cable effect
        phi = phi_temp - dchi_cable

        # Calculate angle of arrival for horizontal antennas
        theta = phi / (k * antenna_sep)
        theta = (c_phi * c_phi - theta * theta)

        # Where theta is < 0 or > 1 is an invalid elevation so set data to NaN
        theta[theta < 0.0] = np.nan
        theta[theta > 1.0] = np.nan
        phi_temp[theta < 0.0] = np.nan
        phi_temp[theta > 1.0] = np.nan
        phi[theta < 0.0] = np.nan
        phi[theta > 1.0] = np.nan

        # Convert theta back to degrees
        if overwrite:
            dmap_amended[ind].update({'elv': np.degrees(theta)})
        else:
            elv_amended[ind] = np.degrees(theta)

    if overwrite:
        return dmap_amended
    else:
        return elv_amended
