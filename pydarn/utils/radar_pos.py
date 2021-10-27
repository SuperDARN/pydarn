# Copyright (C) 2020 SuperDARN Canada, University of Saskatchewan
# Author(s): Daniel Billett, Marina Schmidt
#
# Copyright (C) 2012 Johns Hopkins University/Applied Physics Laboratory
# Author: K.Baker, R.J.Barnes & D. Andre
#
# The following methods:
# - geographic_cell_positions
# - geocentric_coordinates
# - cell_geocentric_coordinates
# - geocentric2flattening
# - geodetic2geocentric
# - geocentric2geodetic
# was copied from
# https://github.com/SuperDARN/rst/superdarn/src.lib/tk/rpos.1.7/src/cnvtcoord.c
# and converted to python for usage in pyDARN
#
# Modifications:
#   2020-04-20 Marina Schmidt converted the above link to python and changed
#              variable and function names to readability
#   2020-09-15 Marina Schmidt removed fov file reading option
#   2021-09-15 Francis Tholley relocated the virtual height models to another file
# Disclaimer:
# pyDARN is under the LGPL v3 license found in the root directory LICENSE.md
# Everyone is permitted to copy and distribute verbatim copies of this license
# document, but changing it is not allowed.
#
# This version of the GNU Lesser General Public License incorporates the terms
# and conditions of version 3 of the GNU General Public License,
# supplemented by the additional permissions listed below.
#
#


"""
This module is used for handling coordinates of a specified radar
in AACGMv2 or geographic coordinates
"""

import datetime as dt
import numpy as np
import os

import aacgmv2

from pydarn import SuperDARNRadars, gate2slant, Coords
from pydarn.utils.constants import EARTH_EQUATORIAL_RADIUS, Re, C

from pydarn.utils.virtual_heights_types import VH_types
from pydarn.utils.virtual_heights import standard_virtual_height, chisham

def radar_fov(stid: int, rsep: int = 45, frang: int = 180,
              ranges: tuple = None, coords: object = Coords.AACGM,
              max_beams: int = None, date: dt.datetime = None, **kwargs):
    """
    Returning beam/gate coordinates of a specified radar's field-of-view

    Parameters
    ----------
    stid: int
        Station ID of radar of choice. See 'superdarn.ca/radar-info'
        for ID numbers.
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
        for range gate corners
    longitudes/mlts: np.array
        n_beams x n_gates array of geographic or AACGMv2 longitudes
        for range gate corners
    """
    # Locate base PyDARN directory
    if ranges is None:
        ranges = [0, SuperDARNRadars.radars[stid].range_gate_45]
    if max_beams is None:
        max_beams = SuperDARNRadars.radars[stid].hardware_info.beams
    # Plus 1 is due to the fact fov files index at 1 so in the plotting
    # of the boundary there is a subtraction of 1 to offset this as python
    # converts to index of 0 which my code already accounts for
    beam_corners_lats = np.zeros((ranges[1], max_beams+1))
    beam_corners_lons = np.zeros((ranges[1], max_beams+1))

    for beam in range(0, max_beams+1):
        for gate in range(ranges[0], ranges[1]):
            lat, lon = geographic_cell_positions(stid, beam, gate, rsep,
                                                 frang, height=300)

            if coords == Coords.AACGM:
                if date is None:
                    date = dt.datetime.now()

                geomag = np.array(aacgmv2. get_aacgm_coord(lat, lon,
                                                           250, date))
                lat = geomag[0]
                lon = geomag[1]
            beam_corners_lats[gate, beam] = lat
            beam_corners_lons[gate, beam] = lon

    # Return geographic coordinates
    return beam_corners_lats, beam_corners_lons


# RPosGeo line 335
def geographic_cell_positions(stid: int, beam: int, range_gate: int,
                              rsep: int = 45, frang: int = 180,
                              height: float = None, elv_angle: float = 0.0,
                              center: bool = True, chisham: bool = False,
                              virtual_height_type: object = VH_types.STANDARD_VIRTUAL_HEIGHT):
    """
    determines the geographic cell position for a given range gate and beam

    parameters
    ----------
        stid: int
            station id of the radar to use
        beam: int
            beam number (indexing at 0)
        range_gate: int
            range gate number (indexing at 0)
        rsep: int
            range seperation, determined by the mode the
            radar is using, in [km]
            default: 45 - normalscan mode
        frang: int
            frequency range from the radar to the front edge of the range gate
            Please note: this definition may be changed, currently defined in
            RST code to keep consistency
        height: float
            transmutation height [km]
            default: none
            if none then it uses elevation angle
        elv_angle: float
            elevation angle in [deg]
            default: 0
        center: bool
            obtain geographic location of the centre of the range gates
            False obtains the front edge of the range gates.
            default: True
        virtual_height_type: object
            use for choosing type of virtual height
            default: VH_types.STANDARD_VIRTUAL_HEIGHT

    returns
    -------
        lat: float
            latitude of the range gate in geographic coordinates [deg]
        lon: float
            longitude of the range gate in geographic coordinates [deg]
    """
    # centre of the field of view
    offset = SuperDARNRadars.radars[stid].hardware_info.beams / 2.0 - 0.5

    # Obtain radar information from hardware files all converted to [rad]
    # radians are needed for numpy geometry calculations and to reduce
    # too much converting back and forth.
    boresight = np.radians(SuperDARNRadars.
                           radars[stid].hardware_info.boresight)
    radar_lat = np.radians(SuperDARNRadars.
                           radars[stid].hardware_info.geographic.lat)
    radar_lon = np.radians(SuperDARNRadars.
                           radars[stid].hardware_info.geographic.lon)
    beam_sep = np.radians(SuperDARNRadars.
                          radars[stid].hardware_info.beam_separation)
    rxrise = SuperDARNRadars.radars[stid].hardware_info.rx_rise_time

    # TODO: fix after slant range change
    if center is True:
        # beam edge in [rad]
        beam_edge = -beam_sep * 0.5
        # range_edge in [km]
    else:
        beam_edge = 0

    # psi [rad] in the angle from the boresight
    psi = beam_sep * (beam - offset) + beam_edge
    # Calculate the slant range [km]
    slant_range = gate2slant(frang, rsep, rxrise, gate=range_gate)

    # If no height is specified then use elevation angle (default 0)
    # to calculate the transmutation height
    if height is None:
        height = -Re + np.sqrt(Re**2 + 2 * slant_range * Re *
                               np.sin(np.radians(elv_angle)) + slant_range**2)

    lat, lon = geocentric_coordinates(radar_lat, radar_lon, slant_range,
                                      height, psi, boresight, virtual_height_type = virtual_height_type)

    # convert back degrees as preferred units to use?
    return np.degrees(lat), np.degrees(lon)


# fldpnth line 90
def geocentric_coordinates(radar_lat: float, radar_lon: float,
                           slant_range: float, cell_height: float,
                           psi: float, boresight: float,
                           virtual_height_type: object = VH_types.STANDARD_VIRTUAL_HEIGHT):
    """
    Calculates the geocentric coordinates of gate cell  point,
    using either the standard or Chisham virtual height model.

    Parameters
    ----------
        radar_lat : float
            radars site latitude [rad]
        radar_lon : float
            radars site longitude [lon]
        slant_range: float
            slant range distance [km]
        cell_height : float
            virtual height of the gate cell [km]
        psi: int
            [rad]
        boresight: float
            boresight of the radar beam [rad]
        virtual_height_type: object
            use for choosing type of virtual height
            default: VH_types.STANDARD_VIRTUAL_HEIGHT

    Returns
    -------
        cell_lat: float
            latitude of the range gate in geographic coordinates [rad]
        cell_lon: float
            longitude of the range gate in geographic coordinates [rad]

    """
    # Gareth Chisham Virtual height model:
    """
    Mapping ionospheric backscatter measured by the SuperDARN HF
    radars – Part 1: A new empirical virtual height model by
    G. Chisham 2008 (https://doi.org/10.5194/angeo-26-823-2008)
    """
    if virtual_height_type == VH_types.CHISHAM:
        x_height = chisham(slant_range)

    if virtual_height_type == VH_types.STANDARD_VIRTUAL_HEIGHT:
        x_height = standard_virtual_height(slant_range, cell_height)

    # calculate the radius over the earth underneath
    # the radar and range gate cell
    rlat, rlon, r_radar, delta = geodetic2geocentric(radar_lat, radar_lon)
    r_cell = r_radar

    psi_cos_2 = np.cos(psi)**2
    psi_sin_2 = np.sin(psi)**2

    while_flag = True
    while while_flag:
        # distance between the gate cell to the earth's centre [km]
        cell_rho = r_cell + x_height
        # elevation angle relative to local horizon [rad]
        rel_elv = np.arcsin(((cell_rho**2) - (r_radar**2) - slant_range**2) /
                            (2.0 * r_radar * slant_range))
        # estimate elevation for multi-hop propagation
        if chisham and slant_range > 2137.5:
            gamma = np.arccos((r_radar**2 + cell_rho**2 - slant_range**2) /
                              (2.0 * r_radar * cell_rho))
            beta = np.arcsin(r_radar * np.sin(gamma/3.0) /
                             (slant_range/3.0))
            # Elevation angle used for estimating off-array normal
            # azimuth [rad]
            xelv = (np.pi/2) - beta - (gamma/3.0)
        else:
            xelv = rel_elv

        # Estimate the off-array-normal azimuth in radians
        elv_sin_2 = np.sin(xelv)**2

        est_azimuth = psi_cos_2 - elv_sin_2
        if est_azimuth < 0:
            tan_azimuth = 1e32
        else:
            # in radians
            tan_azimuth = np.sqrt(psi_sin_2 /
                                  (psi_cos_2 - elv_sin_2))
        # azimuth in [rad]
        if psi > 0:
            azimuth = np.arctan(tan_azimuth)
        else:
            azimuth = -np.arctan(tan_azimuth)

        # azimuth of the gate cell [rad]
        cell_azimuth = azimuth + boresight
        flatten_azimuth = geocentric2flattening(delta, cell_azimuth, xelv)
        cell_rho, cell_lat, cell_lon = \
            cell_geocentric_coordinates(rlat, rlon, r_radar,
                                        flatten_azimuth, rel_elv,
                                        slant_range)

        # recalculate the radius under the gate cell and centre of earth
        r_cell = geocentric2geodetic(cell_lat, cell_lon)
        cell_heightx = cell_rho - r_cell
        # this ensures convergence on the cell point
        while_flag = abs(cell_heightx - x_height) > 0.5

    return cell_lat, cell_lon


# fldpnt
def cell_geocentric_coordinates(lat: float, lon: float, rho: float,
                                azimuth: float, elv: float, r: float):
    """
    Calculates the geocentric coordinates of a gate cell point given the
    angular geocentric coordinates of the point of origin,
    the azimuth, elevation, and slant range.

    parameters
    ----------
        lat: float
            geocentric latitude [rad] of the radar site
        lon : float
            geocentric longitude [rad] of the radar site
        rho: float
            radius from the radar site to the centre of the earth [km]
        azimuth: float
            azimuth with corrected earth flattening in [rad] for the cell
        elv: float
            relative elevation angle [rad]
        r: float
            slant range of the cell [km]

    returns
    -------
        rho: float
            radius from cell point to centre of the earth [km]
        lat: float
            geocentric cell latitude [rad]
        lon: float
            geocentric cell longitude [rad]
    """
    cos_lat = np.cos(np.pi/2 - lat)
    sin_lat = np.sin(np.pi/2 - lat)

    cos_lon = np.cos(lon)
    sin_lon = np.sin(lon)

    cos_azimuth = np.cos(azimuth)
    sin_azimuth = np.sin(azimuth)

    sin_elv = np.sin(elv)
    cos_elv = np.cos(elv)

    # earth centered spherical coordinates [km*rad]
    rx = rho * sin_lat * cos_lon
    ry = rho * sin_lat * sin_lon
    rz = rho * cos_lat

    # earth local Cartesian (x-south, y-east, z-up)

    # [km*rad]
    local_x = -r * cos_elv * cos_azimuth
    local_y = r * cos_elv * sin_azimuth
    local_z = r * sin_elv

    # convert to global Cartesian
    global_x = cos_lat * local_x + sin_lat * local_z
    global_y = local_y
    global_z = -sin_lat * local_x + cos_lat * local_z

    local_x = cos_lon * global_x - sin_lon * global_y
    local_y = sin_lon * global_x + cos_lon * global_y
    local_z = global_z

    # find the global Cartesian coordinates for the new point
    global_x = rx + local_x
    global_y = ry + local_y
    global_z = rz + local_z

    # convert Cartesian back to spherical
    rho = np.sqrt(global_x**2 + global_y**2 + global_z**2)
    lat = np.pi/2 - np.arccos(global_z/rho)
    if global_x == 0 and global_y == 0:
        lon = 0
    else:
        lon = np.arctan2(global_y, global_x)

    return rho, lat, lon


# goecnvrt
def geocentric2flattening(delta: float, azimuth: float, elv: float):
    """
    Adjust azimuth for the oblateness of the Earth

    Parameters
    ----------
        delta: float
            distance before geodetic and geocentric latitude [rad]
        azimuth: float
            azimuth of geocentric cell point [rad]
        elv: float
            elevation angle [rad]

    Returns
    -------
        azimuth_flattening: float
            adjusted azimuth due the earths oblateness

    """
    cos_elv = np.cos(elv)
    sin_elv = np.sin(elv)

    cos_azimuth = np.cos(azimuth)
    sin_azimuth = np.sin(azimuth)

    cos_delta = np.cos(delta)
    sin_delta = np.sin(delta)

    kxg = cos_elv * sin_azimuth
    kyg = cos_elv * cos_azimuth
    kzg = sin_elv

    kxr = kxg
    kyr = kyg * cos_delta + kzg * sin_delta

    azimuth_flattening = np.arctan2(kxr, kyr)

    return azimuth_flattening


# geodtgc, iopt > 0
def geodetic2geocentric(lat: float, lon: float):
    """
    convert geodetic coordinates to geocentric

    parameters
    ----------
        lat: float
            geodetic latitude [rad]
        lon: float
            geodetic longitude [rad]
    returns
    -------
        glat: float
            geocentric latitude [rad]
        glon: float
            geocentric longitude [rad]
        rho: float
            distance from the latitude to the centre of the earth [km]
        delta: float
            difference between geodetic and geocentric latitude [rad]
    """
    # WGS 84 oblate spheroid defining parameters
    # reciprocal flattening
    f = 1.0 / 298.257223563
    # b is in [km] semi minor axis of earth
    b = EARTH_EQUATORIAL_RADIUS * (1.0 - f)
    # e2 is the ellipticity
    e2 = EARTH_EQUATORIAL_RADIUS**2 / b**2 - 1

    glat = np.arctan(b**2 / EARTH_EQUATORIAL_RADIUS**2 * np.tan(lat))
    # glon [rad]
    glon = lon

    if glon > np.pi:
        glon = glon - 2 * np.pi
    # grho is km?
    rho = EARTH_EQUATORIAL_RADIUS / np.sqrt(1 + e2 * np.sin(glat)**2)
    # delta in [rad]
    delta = lat - glat
    return glat, glon, rho, delta


# geodtgc, iopt < 0
def geocentric2geodetic(lat: float, lon: float):
    """
    convert geocentric coordinates to geodetic

    parameters
    ----------
        lat: float
            geocentric latitude [rad]
        lon: float
            geocentric longitude [rad]
    returns
    -------
        dlat: float
            geodetic latitude [rad]
        dlon: float
            geodetic longitude [rad]
        rho: float
            distance from the latitude to the centre of the earth [km]
        delta: float
            difference between geocentric and geodetic latitude [rad]
    """
    # WGS 84 oblate spheroid defining parameters
    f = 1.0 / 298.257223563
    b = EARTH_EQUATORIAL_RADIUS * (1.0 - f)
    e2 = EARTH_EQUATORIAL_RADIUS**2 / b**2 - 1

    rho = EARTH_EQUATORIAL_RADIUS / np.sqrt(1+e2*np.sin(lat)**2)

    return rho
