# Copyright (C) 2020 SuperDARN Canada, University of Saskatchewan
# Author(s): Daniel Billett, Marina Schmidt
"""
This module is used for handling coordinates of a specified radar
in AACGMv2 or geographic coordinates
"""

import datetime
import numpy as np
import os

import aacgmv2

from pydarn import SuperDARNRadars, gate2slant


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


def geographic_cell_positions(stid: int, beam, range_gate, beam_sep: int,
                              frang: int, height: int, center: bool = True,
                              chisham: bool = False):
    # TODO: Is this correct?
    if center is False:
        beam_edge = -beam_sep * 0.5
        range_edge = -0.5 * beam_sep * 20/3

    offset = SuperDARNRadars.radars[stid].hardware_info.beams / 2.0 - 0.5
    boresight = np.radians(SuperDARNRadars.radars[stid].
                           hardware_info.boresight)
    radar_lat = np.radians(SuperDARNRadars.radars[stid].
                           hardware_info.geographic.lat)
    radar_lon = np.radians(SuperDARNRadars.radars[stid].
                           hardware_info.geographic.lon)

    psi = beam_sep * (beam - offset) + beam_edge

    # Calculate the slant range [km]
    # TODO: not sure about this +1 on the range gate?
    slant_range = gate2slant(frang, beam_sep, range_edge,
                             range_gate+1)

    if height < 90:
        height = Er + np.sqrt(Er**2 + 2 * slant_range * Er * np.sin(height) +
                              slant_range**2)

    lat, lon, rho = geocentric_coordinates(radar_lat, radar_lon, slant_range,
                                           height, psi, boresight, chisham)
    return np.degrees(lat), np.degrees(lon)


def geocentric_coordinates(radar_lat, radar_lon, slant_range: int,
                           cell_height: int, psi: int, boresight: int,
                           chisham: bool = False):
    """
     Parameters:
         slant_range: int
            slant range distance (km)
    """
    if chisham:
        A_const = (108.974, 384.416, 1098.28)
        B_const = (0.0191271, -0.178640, -0.354557)
        C_const = (6.68283e-5, 1.81405e-4, 9.39961e-5)

        if slant_range < 115:
            x_height = (slant_range / 115.0) * 112.0
        elif slant_range < 787.5:
            x_height = A_const[0] + B_const[0] * slant_range + C_const[0] *\
                    slant_range**2
        elif slant_range <= 2137.5:
            x_height = A_const[1] + B_const[1] * slant_range + C_const[1] *\
                    slant_range**2
        else:
            x_height = A_const[2] + B_const[2] * slant_range + C_const[2] *\
                    slant_range**2
    else:
        if cell_height <= 150:
            x_height = 115
        elif slant_range > 600 and slant_range < 800:
            x_height = (slant_range - 600) / 200 * (cell_height - 115) + 115
        else:
            x_height = cell_height
        if slant_range < 150:
            x_height = (slant_range / 150.0) * 115

    # calculate the radius over the earth underneath
    # the radar and range gate cell
    rlat, rlon, r_radar, delta = geodetic2geocentric(radar_lat, radar_lon)

    # TODO: will this happen with determined frang?
    if slant_range == 0:
        slant_range = 0.1

    # TODO: turn into a helper do-while loop
    while abs(cell_hieghtx - x_height) > 0.5:
        # distance between the gate cell to the earth's centre
        cell_rho = r_radar + x_height

        # elevation angle relative to local horizon
        rel_elv = np.arcsin(((cell_rho**2) - (r_radar**2) - slant_range**2) /
                            (2.0 * r_radar * slant_range))

        # TODO: what is 2137.5 represent?
        rad_3deg = np.radians(3)
        if chisham and slant_range > 2137.5:
            gamma = np.arccos((r_radar**2 + cell_rho**2 - slant_range**2) /
                              (np.radians(2.0) * r_radar * cell_rho))
            beta = np.arcsin(r_radar * np.sin(gamma/rad_3deg) /
                             (slant_range/rad_3deg))
            rel_elv = (np.pi/2) - beta - (gamma/rad_3deg)

        # Estimate the off-array-normal azimuth
        psi = np.radians(psi)
        psi_cos_2 = np.cos(psi)**2
        psi_sin_2 = np.sin(psi)**2
        est = psi_cos_2 - psi_sin_2
        if est < 0:
            tan_azimuth = 1e32
        else:
            tan_azimuth = np.sqrt(psi_sin_2 /
                                  (psi_cos_2 - np.sin(rel_elv)**2))

        if psi > 0:
            azimuth = np.arctan(tan_azimuth) * -np.radians(1.0)
        else:
            azimuth = np.arctan(tan_azimuth) * -np.radians(1.0)

        cell_azimuth = azimuth + boresight

        ral, _ = geocentric_convert(radar_lat, radar_lon, cell_azimuth, xel)

        cell_lat, cell_lon, cell_rho = cell_geocentric_coordinates(rlat, rlon,
                                                                   r_radar,
                                                                   ral, rel,
                                                                   slant_range)

        celld_lat, celld_lon, delta = geocentric2geodetic(cell_lat, cell_lon)

        cell_hightx = cell_azimuth - r_radar

    return celld_lat, celld_lon


def cell_geocentric_coordinates(lat: int, lon: int, rho: int, ral: int,
                                rel: int, r: int):

    sinteta = np.sin(np.pi/2-lat)

    cos_lat = np.cos(np.pi/2 - lat)
    sin_lat = np.sin(np.pi/2 - lat)

    cos_lon = np.cos(lon)
    sin_lon = np.sin(lon)

    # earth centered spherical coordinates [deg]
    sx = rho * sinteta * np.cos(lon)
    sy = rho * sinteta * np.sin(lon)
    sz = rho * cos_lat

    # earth local Cartesian (x-south, y-east, z-up)
    cos_ral = np.cos(ral)
    cos_rel = np.cos(rel)
    sin_ral = np.sin(ral)
    sin_rel = np.sin(rel)
    local_x = -r * cos_rel * cos_ral
    local_y = r * sin_rel * sin_ral
    local_z = r * sin_rel

    # convert to global Cartesian
    global_x = cos_lat * local_x + sin_lat * local_z
    global_y = local_y
    global_z = -sin_lat * local_x + cos_lat * local_z

    local_x = cos_lon * global_x - sin_lon * global_y
    local_y = sin_lon * global_x + cos_lon * global_y
    local_z = global_z

    # find the global Cartesian coordinates for the new point
    global_x = sx + local_x
    global_y = sy + local_y
    global_z = sz + local_z

    # concert Cartesian back to spherical
    rho = np.sqrt(global_x**2 + global_y**2 + global_z**2)
    lat = np.pi/2 - np.arccos(global_z/rho)
    if global_x == 0 and global_y == 0:
        lon = 0
    else:
        lon = np.arctan2(global_y, global_x)

    return rho, lat, lon


def geocentric_convert(lat, lon, xal, xel):

    cos_xel = np.cos(xel)
    sin_xel = np.sin(xel)
    cos_xal = np.cos(xal)
    sin_xal = np.sin(xal)

    kxg = cos_xel * sin_xal
    kyg = cos_xel * cos_xal
    kzg = sin_xel

    _, _, _, delta = geodetic2geocentric(lat, lon)

    cos_delta = np.cos(delta)
    sin_delta = np.sin(delta)

    kxr = kxg
    kyr = kyg * cos_delta + kzg * sin_delta
    kzr = -kyg * sin_delta + kzg * cos_delta

    ral = np.arctan2(kxr, kyr)
    rel = np.arctan(kzr / np.sqrt(kxr**2 + kyr**2))

    return ral, rel


def geodetic2geocentric(lat: int, lon: int):
    # WGS 84 oblate spheroid defining parameters
    f = 1.0 / 298.257223563
    b = Er * (1.0 - f)
    e2 = Er**2 / b**2 - 1

    glat = np.arctan(b**2 / Er**2) * np.tan(lat)
    glon = lon

    if glon > 180:
        glon = glon-360
    grho = Er / np.sqrt(1+e2*np.sin(glat)**2)
    delta = lat - glat
    return glat, glon, grho, delta


def geocentric2geodetic(lat: int, lon: int):
    # WGS 84 oblate spheroid defining parameters
    f = 1.0 / 298.257223563
    b = Er * (1.0 - f)

    dlat = np.arctan(b**2/Er**2) * np.tan(lat)
    dlon = lon
    delta = dlat - lat

    return dlat, dlon, delta
