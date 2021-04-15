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
from pydarn.utils.const import EARTH_RADIUS


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


# RPosGeo line 335
def geographic_cell_positions(stid: int, beam: int, range_gate: int, rsep: int = 45,
                              frang: int = 180, nrang: int = 75,
                              height: int = None, elv_angle: int = 0,
                              center: bool = True, chisham: bool = False):

    # centre of the field of view units?
    offset = SuperDARNRadars.radars[stid].hardware_info.beams / 2.0 - 0.5
    boresight = SuperDARNRadars.radars[stid].hardware_info.boresight
    radar_lat = SuperDARNRadars.radars[stid].hardware_info.geographic.lat
    radar_lon = SuperDARNRadars.radars[stid].hardware_info.geographic.lon
    beam_sep = SuperDARNRadars.radars[stid].hardware_info.beam_separation

    # TODO: Is this correct?
    if center is True:
        beam_edge = -beam_sep * 0.5
        range_edge = -0.5 * rsep * 20/3
    else:
        beam_edge = 0
        range_edge = 0

    psi = beam_sep * (beam - offset) + beam_edge
    # Calculate the slant range [km]
    # TODO: not sure about this +1 on the range gate?
    slant_range = rst_slant_range(frang, rsep, range_edge, range_gate)

    if height is None and elv_angle < 90:
        height = -EARTH_RADIUS + np.sqrt(EARTH_RADIUS**2 + 2 * slant_range *
                                         EARTH_RADIUS *
                                         np.sin(np.radians(elv_angle)) +
                                         slant_range**2)

    lat, lon = geocentric_coordinates(radar_lat, radar_lon, slant_range,
                                      height, psi, boresight, chisham)
    return lat, lon

def rst_slant_range(frang, rsep, range_edge, range_gate, rxrise=100):
    lagfr = frang * 20/3
    smsep = rsep * 20/3

    return (lagfr - rxrise + (range_gate) * smsep + range_edge) * 0.15

# fldpnth line 90
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
        """
        cell_height, slant_range and x_height are in km
        Default values set in virtual height model described
        Mapping ionospheric backscatter measured by the SuperDARN HF
        radars – Part 1: A new empirical virtual height model by
        G. Chisham 2008
        Equation (1) in the paper
        < 150 km climbing into the E region
        150 - 600 km E region scatter
        (Note in the paper 400 km is the edge of the E region)
        600 - 800 km is F region
        """
        # TODO: why 115?
        # map everything into the E region
        if cell_height <= 150 and slant_range > 150:
            x_height = cell_height
        # virtual height equation (1) from the above paper
        elif slant_range < 150:
            x_height = (slant_range / 150.0) * 115
        elif slant_range >= 150 and slant_range <= 600:
            x_height = 115
        elif slant_range > 600 and slant_range < 800:
            x_height = (slant_range - 600) / 200 * (cell_height - 115) + 115
        # higher than 800 km
        else:
            x_height = cell_height
    # calculate the radius over the earth underneath
    # the radar and range gate cell
    rlat, rlon, r_radar, delta = geodetic2geocentric(radar_lat, radar_lon)
    r_cell = r_radar

    # TODO: turn into a helper do-while loop
    while_flag = True
    #for i in range(0,10):
    while while_flag:
        # distance between the gate cell to the earth's centre [km]
        cell_rho = r_cell + x_height
        # elevation angle relative to local horizon [radians]
        rel_elv = np.arcsin(((cell_rho**2) - (r_radar**2) - slant_range**2) /
                            (2.0 * r_radar * slant_range))
        # TODO: what is 2137.5 km represent?
        if chisham and slant_range > 2137.5:
            gamma = np.arccos((r_radar**2 + cell_rho**2 - slant_range**2) /
                              (2.0 * r_radar * cell_rho))
            beta = np.arcsin(r_radar * np.sin(gamma/3.0) /
                             (slant_range/3.0))
            # Elevation angle used for estimating off-array normal
            # azimuth [radians]
            xelv = (np.pi/2) - beta - (gamma/3.0)
        else:
            xelv = rel_elv

        # Estimate the off-array-normal azimuth in radians
        psi_r = np.radians(psi)
        psi_cos_2 = np.cos(psi_r)**2
        psi_sin_2 = np.sin(psi_r)**2
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

        # azimuth of the gate cell [deg]
        cell_azimuth = np.degrees(azimuth) + boresight
        flatten_azimuth, _ = geocentric2flattening(delta, cell_azimuth, np.degrees(xelv))
        cell_rho , cell_lat, cell_lon = cell_geocentric_coordinates(rlat, rlon,
                                                                    r_radar,
                                                                    flatten_azimuth,
                                                                    np.degrees(rel_elv),
                                                                    slant_range)

        _, _, r_cell, _ = geocentric2geodetic(cell_lat, cell_lon)
        cell_heightx = cell_rho - r_cell
        while_flag = abs(cell_heightx - x_height) > 0.5

    return cell_lat, cell_lon


# fldpnt
def cell_geocentric_coordinates(lat: int, lon: int, rho: int, azimuth: int,
                                elv: int, r: int):

    lat_r = np.radians(lat)
    lon_r = np.radians(lon)
    azimuth_r = np.radians(azimuth)
    elv_r = np.radians(elv)

    sin_theta = np.sin(np.pi/2 - lat_r)

    cos_lat = np.cos(np.pi/2 - lat_r)
    sin_lat = np.sin(np.pi/2 - lat_r)

    cos_lon = np.cos(lon_r)
    sin_lon = np.sin(lon_r)

    # earth centered spherical coordinates [km*rad]
    rx = rho * sin_theta * np.cos(lon_r)
    ry = rho * sin_theta * np.sin(lon_r)
    rz = rho * cos_lat

    # earth local Cartesian (x-south, y-east, z-up)
    cos_azimuth = np.cos(azimuth_r)
    cos_elv = np.cos(elv_r)
    sin_azimuth = np.sin(azimuth_r)
    sin_elv = np.sin(elv_r)

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

    return rho, np.degrees(lat), np.degrees(lon)


# goecnvrt
#TODO clean up function
def geocentric2flattening(delta, azimuth, elv):
    """
    Adjust azimuth and elevation for the oblateness of the Earth
    """
    elv_r = np.radians(elv)
    azimuth_r = np.radians(azimuth)
    delta_r = np.radians(delta)

    cos_xelv = np.cos(elv_r)
    sin_xelv = np.sin(elv_r)

    cos_xal = np.cos(azimuth_r)
    sin_xal = np.sin(azimuth_r)

    cos_delta = np.cos(delta_r)
    sin_delta = np.sin(delta_r)

    kxg = cos_xelv * sin_xal
    kyg = cos_xelv * cos_xal
    kzg = sin_xelv

    kxr = kxg
    kyr = kyg * cos_delta + kzg * sin_delta
    kzr = -kyg * sin_delta + kzg * cos_delta

    azimuth_flattening = np.arctan2(kxr, kyr)

    elv_flattening = np.arctan(kzr / np.sqrt(kxr**2 + kyr**2))

    return np.degrees(azimuth_flattening), np.degrees(elv_flattening)


# geodtgc, iopt > 0
def geodetic2geocentric(lat: int, lon: int):
    """
    """
    # WGS 84 oblate spheroid defining parameters
    # reciprocal flattening
    f = 1.0 / 298.257223563
    # b is in [km] semi minor axis of earth
    b = EARTH_RADIUS * (1.0 - f)
    # e2 is the ellipticity
    e2 = EARTH_RADIUS**2 / b**2 - 1
    lat_r = np.radians(lat)

    glat_r = np.arctan(b**2 / EARTH_RADIUS**2 * np.tan(lat_r))
    # glon is in degress
    glon = lon

    if glon > 180:
        glon = glon - 360
    # grho is km?
    grho = EARTH_RADIUS / np.sqrt(1 + e2 * np.sin(glat_r)**2)
    glat = np.degrees(glat_r)
    delta = lat - glat
    return glat, glon, grho, delta


# geodtgc, iopt < 0
def geocentric2geodetic(lat: int, lon: int):
    # WGS 84 oblate spheroid defining parameters
    f = 1.0 / 298.257223563
    b = EARTH_RADIUS * (1.0 - f)
    lat_r = np.radians(lat)
    e2 = EARTH_RADIUS**2 / b**2 - 1

    r_radar = EARTH_RADIUS / np.sqrt(1+e2*np.sin(lat_r)**2)
    dlat_r = np.arctan(EARTH_RADIUS**2/b**2 * np.tan(lat_r))
    dlon = lon
    dlat = np.degrees(dlat_r)
    delta = dlat - lat

    return dlat, dlon, r_radar, delta
