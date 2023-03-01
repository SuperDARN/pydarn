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
# 2022-03-10 MTS added kwargs to the functions just to avoid errors when
#                extra keys are passed in from other functions
# 2023-01-03 CJM added functions to calculate azimuth from XS and SC existing
#                codebase, can be expanded and added to when required
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
This module focuses on geographic calculations used for converting gate
information to geographic location
"""
import numpy as np
from pydarn import VHModels, EARTH_EQUATORIAL_RADIUS


def geocentric_coordinates(target_range: float, psi: float, boresight: float,
                           virtual_height_model: VHModels =
                           VHModels.STANDARD,
                           **kwargs):
    """
    Calculates the geocentric coordinates of gate cell  point,
    using either the standard or Chisham virtual height model.

    Parameters
    ----------
        radar_lat : float
            radars site latitude [rad]
        radar_lon : float
            radars site longitude [lon]
        target_range: float
            The range from the instrument to the target (echo) [km]
        cell_height : float
            virtual height of the gate cell [km]
        psi: int
            [rad]
        boresight: float
            boresight of the radar beam [rad]
        virtual_height_model: VHModels
            use for choosing type of virtual height
            default: VHModels.STANDARD

    Returns
    -------
        cell_lat: float
            latitude of the range gate in geographic coordinates [rad]
        cell_lon: float
            longitude of the range gate in geographic coordinates [rad]

    """
    """
    Mapping ionospheric backscatter measured by the SuperDARN HF
    radars – Part 1: A new empirical virtual height model by
    G. Chisham 2008 (https://doi.org/10.5194/angeo-26-823-2008)
    """
    x_height = virtual_height_model(target_range=target_range, **kwargs)

    # calculate the radius over the earth underneath
    # the radar and range gate cell
    rlat, rlon, r_radar, delta = geodetic2geocentric(**kwargs)
    r_cell = r_radar

    psi_cos_2 = np.cos(psi)**2
    psi_sin_2 = np.sin(psi)**2

    while_flag = True
    while while_flag:
        # distance between the gate cell to the earth's centre [km]
        cell_rho = r_cell + x_height
        # elevation angle relative to local horizon [rad]
        rel_elv = np.arcsin(((cell_rho**2) - (r_radar**2) - target_range**2) /
                            (2.0 * r_radar * target_range))
        # estimate elevation for multi-hop propagation
        if virtual_height_model == VHModels.CHISHAM and target_range > 2137.5:
            gamma = np.arccos((r_radar**2 + cell_rho**2 - target_range**2) /
                              (2.0 * r_radar * cell_rho))
            beta = np.arcsin(r_radar * np.sin(gamma/3.0) /
                             (target_range/3.0))
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
        flatten_azimuth = geocentric2flattening(delta=delta,
                                                azimuth=cell_azimuth,
                                                elv=xelv)
        cell_rho, cell_lat, cell_lon = \
            cell_geocentric_coordinates(lat=rlat, lon=rlon,
                                        rho=r_radar,
                                        azimuth=flatten_azimuth,
                                        elv=rel_elv,
                                        r=target_range)

        # recalculate the radius under the gate cell and centre of earth
        r_cell = geocentric2geodetic(lat=cell_lat, lon=cell_lon)
        cell_heightx = cell_rho - r_cell
        # this ensures convergence on the cell point
        while_flag = abs(cell_heightx - x_height) > 0.5

    return cell_lat, cell_lon


# fldpnt
def cell_geocentric_coordinates(lat: float, lon: float, rho: float,
                                azimuth: float, elv: float, r: float,
                                **kwargs):
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
def geocentric2flattening(delta: float, azimuth: float, elv: float, **kwargs):
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
def geodetic2geocentric(lat: float, lon: float, **kwargs):
    """
    convert geodetic coordinates to geocentric
    radian version

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
def geocentric2geodetic(lat: float, lon: float, **kwargs):
    """
    convert geocentric coordinates to geodetic
    radian version

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


def geod2geoc(lat, lon, inverse=False):
    """Converts position from geodetic to geocentric or vice-versa.
    Based on the IAU 1964 oblate spheroid model of the Earth.
    Parameters
    ----------
    lat : float
        latitude [degree]
    lon : float
        longitude [degree]
    inverse : Optional[bool]
        inverse conversion (geocentric to geodetic).  Default is false.
    Returns
    -------
    lat_out : float
        latitude [degree] (geocentric/detic if inverse=False/True)
    lon_out : float
        longitude [degree] (geocentric/detic if inverse=False/True)
    rade : float
        Earth radius [km] (geocentric/detic if inverse=False/True)
    """
    a = 6378.16
    f = 1.0 / 298.25
    b = a * (1.0 - f)
    e2 = (a**2 / b**2) - 1.0

    if not inverse:
        # geodetic into geocentric
        lat_out = np.degrees(np.arctan(b**2 / a**2 * np.tan(np.radians(lat))))
        lon_out = lon
    else:
        # geocentric into geodetic
        lat_out = np.degrees(np.arctan(a**2 / b**2 * np.tan(np.radians(lat))))
        lon_out = lon

    rade = a / np.sqrt(1.0 + e2 * np.sin(np.radians(lat_out)) ** 2)

    return lat_out, lon_out, rade


def globalspherical2globalcartesian(xin, yin, zin, inverse=False):
    """Converts a position from global spherical (geocentric) to global
    cartesian (and vice-versa).

    Parameters
    ----------
    xin : float
        latitude [degree] or global cartesian X [km]
    yin : float
        longitude [degree] or global cartesian Y [km]
    zin : float
        distance from center of the Earth [km] or global cartesian Z [km]
    inverse : Optional[bool]
        inverse conversion

    Returns
    -------
    xout : float
        global cartesian X [km] (inverse=False) or latitude [degree]
    yout : float
        global cartesian Y [km] (inverse=False) or longitude [degree]
    zout : float
        global cartesian Z [km] (inverse=False) or distance from the center of
        the Earth [km]

    Notes
    -------
    The global cartesian coordinate system is defined as:
        - origin: center of the Earth
        - x-axis in the equatorial plane and through the prime meridian.
        - z-axis in the direction of the rotational axis and through the North
          pole
    The meaning of the input (x,y,z) depends on the direction of the conversion
    (to global cartesian or to global spherical).
    """

    if not inverse:
        # Global spherical to global cartesian
        xout = zin * np.cos(np.radians(xin)) * np.cos(np.radians(yin))
        yout = zin * np.cos(np.radians(xin)) * np.sin(np.radians(yin))
        zout = zin * np.sin(np.radians(xin))
    else:
        # Calculate latitude (xout), longitude (yout) and distance from center
        # of the Earth (zout)
        zout = np.sqrt(xin**2 + yin**2 + zin**2)
        xout = np.degrees(np.arcsin(zin / zout))
        yout = np.degrees(np.arctan2(yin, xin))

    return xout, yout, zout


def globalcartesian2localcartesian(X, Y, Z, lat, lon, rho, inverse=False):
    """Converts a position from global cartesian to local cartesian
    (or vice-versa).

    Parameters
    ----------
    X : float
        global cartesian X [km] or local cartesian X [km]
    Y : flaot
        global cartesian Y [km] or local cartesian Y [km]
    Z : float
        global cartesian Z [km] or local cartesian Z [km]
    lat : float
        geocentric latitude [degree] of local cartesian system origin
    lon : float
        geocentric longitude [degree] of local cartesian system origin
    rho : float
        distance from center of the Earth [km] of local cartesian system origin
    inverse : Optional[bool]
        inverse conversion

    Returns
    -------
    X : float
        local cartesian X [km] or global cartesian X [km]
    Y : float
        local cartesian Y [km] or global cartesian Y [km]
    Z : float
        local cartesian Z [km] or global cartesian Z [km]

    Notes
    -------
    The global cartesian coordinate system is defined as:
        - origin: center of the Earth
        - Z axis in the direction of the rotational axis and through the North
          pole
        - X axis in the equatorial plane and through the prime meridian.
    The local cartesian coordinate system is defined as:
        - origin: local position
        - X: East
        - Y: North
        - Z: up
    The meaning of the input (X,Y,Z) depends on the direction of the conversion
    (to global cartesian or to global spherical).
    """
    # First get global cartesian coordinates of local origin
    (goX, goY, goZ) = globalspherical2globalcartesian(lat, lon, rho)

    if not inverse:
        # Translate global position to local origin
        tx = X - goX
        ty = Y - goY
        tz = Z - goZ
        # Then, rotate about global-Z to get local-X pointing eastward
        rot = -np.radians(lon + 90.0)
        sx = tx * np.cos(rot) - ty * np.sin(rot)
        sy = tx * np.sin(rot) + ty * np.cos(rot)
        sz = tz
        # Finally, rotate about X axis to align Z with upward direction
        rot = -np.radians(90.0 - lat)
        xOut = sx
        yOut = sy * np.cos(rot) - sz * np.sin(rot)
        zOut = sy * np.sin(rot) + sz * np.cos(rot)
    else:
        # First rotate about X axis to align Z with Earth rotational axis
        # direction
        rot = np.radians(90.0 - lat)
        sx = X
        sy = Y * np.cos(rot) - Z * np.sin(rot)
        sz = Y * np.sin(rot) + Z * np.cos(rot)
        # Rotate about global-Z to get global-X pointing to the prime meridian
        rot = np.radians(lon + 90.0)
        xOut = sx * np.cos(rot) - sy * np.sin(rot)
        yOut = sx * np.sin(rot) + sy * np.cos(rot)
        zOut = sz
        # Finally, translate local position to global origin
        xOut = xOut + goX
        yOut = yOut + goY
        zOut = zOut + goZ

    return xOut, yOut, zOut


def localspherical2localcartesian(X, Y, Z, inverse=False):
    """Convert a position from local spherical to local cartesian,
        or vice-versa

    Parameters
    ----------
    X : float
        azimuth [degree, N] or local cartesian X [km]
    Y : float
        elevation [degree] or local cartesian Y [km]
    Z : float
        distance origin [km] or local cartesian Z [km]
    inverse : Optional[bool]
        inverse conversion

    Returns
    -------
    X : float
        local cartesian X [km] or azimuth [degree, N]
    Y : float
        local cartesian Y [km] or elevation [degree]
    Z : float
        local cartesian Z [km] or distance from origin [km]

    Notes
    ------
    The local spherical coordinate system is defined as:
        - origin: local position
        - azimuth (with respect to North)
        - Elevation (with respect to horizon)
        - Altitude
    The local cartesian coordinate system is defined as:
        - origin: local position
        - X: East
        - Y: North
        - Z: up
    The meaning of the input (X,Y,Z) depends on the direction of the conversion
    (to global cartesian or to global spherical).
    """
    if not inverse:
        # local spherical into local cartesian
        r = Z
        el = Y
        az = X
        xOut = r * np.cos(np.radians(el)) * np.sin(np.radians(az))
        yOut = r * np.cos(np.radians(el)) * np.cos(np.radians(az))
        zOut = r * np.sin(np.radians(el))
    else:
        # local cartesian into local spherical
        r = np.sqrt(X**2 + Y**2 + Z**2)
        el = np.degrees(np.arcsin(Z / r))
        az = np.degrees(np.arctan2(X, Y))
        xOut = az
        yOut = el
        zOut = r

    return xOut, yOut, zOut


def geodetic2geocAzEl(lat, lon, az, el, inverse=False):
    """Converts pointing azimuth and elevation measured with respect to the
    local horizon to azimuth and elevation with respect to the horizon defined
    by the plane perpendicular to the Earth-centered radial vector drawn
    through a user defined point.

    Parameters
    ----------
    lat : float
        latitude [degree]
    lon : float
        longitude [degree]
    az : float
        azimuth [degree, N]
    el : float
        elevation [degree]
    inverse : Optional[bool]
        inverse conversion

    Returns
    -------
    lat : float
        latitude [degree]
    lon : float
        longitude [degree]
    Re : float
        Earth radius [km]
    az : float
        azimuth [degree, N]
    el : float
        elevation [degree]
    """
    taz = np.radians(az)
    tel = np.radians(el)

    # In this transformation x is east, y is north and z is up
    if not inverse:
        # Calculate deviation from vertical (in radians)
        (geocLat, geocLon, Re) = geod2geoc(lat, lon)
        devH = np.radians(lat - geocLat)
        # Calculate cartesian coordinated in local system
        kxGD = np.cos(tel) * np.sin(taz)
        kyGD = np.cos(tel) * np.cos(taz)
        kzGD = np.sin(tel)
        # Now rotate system about the x axis to align local vertical vector
        # with Earth radial vector
        kxGC = kxGD
        kyGC = kyGD * np.cos(devH) + kzGD * np.sin(devH)
        kzGC = -kyGD * np.sin(devH) + kzGD * np.cos(devH)
        # Finally calculate the new azimuth and elevation in the geocentric
        # frame
        azOut = np.degrees(np.arctan2(kxGC, kyGC))
        elOut = np.degrees(np.arctan(kzGC / np.sqrt(kxGC**2 + kyGC**2)))
        latOut = geocLat
        lonOut = geocLon
    else:
        # Calculate deviation from vertical (in radians)
        (geodLat, geodLon, Re) = geod2geoc(lat, lon, inverse=True)
        devH = np.radians(geodLat - lat)
        # Calculate cartesian coordinated in geocentric system
        kxGC = np.cos(tel) * np.sin(taz)
        kyGC = np.cos(tel) * np.cos(taz)
        kzGC = np.sin(tel)
        # Now rotate system about the x axis to align local vertical vector
        # with Earth radial vector
        kxGD = kxGC
        kyGD = kyGC * np.cos(-devH) + kzGC * np.sin(-devH)
        kzGD = -kyGC * np.sin(-devH) + kzGC * np.cos(-devH)
        # Finally calculate the new azimuth and elevation in the geocentric
        # frame
        azOut = np.degrees(np.arctan2(kxGD, kyGD))
        elOut = np.degrees(np.arctan(kzGD / np.sqrt(kxGD**2 + kyGD**2)))
        latOut = geodLat
        lonOut = geodLon

    return latOut, lonOut, Re, azOut, elOut


def calculate_azimuth(slat, slon, salt, elat, elon, ealt):
    """
    calculates the azimuth between two given points
    Only one method used and only azimuth returned, this can be expanded
    using XS and SC existing codebase

    Parameters
    ----------
    slat : float
        origin latitude [degree]
    slon : float
        origin longitude [degree]
    salt : float
        origin altitude [km]
    elat : float
        distant latitude [degree]
    elon : float
        distant longitude [degree]
    ealt : float
        distant altitude [km]

    Returns
    -------
    azm : float
        azimuth between origin location and distant location [degrees]
        in reference to North
    """
    # Convert point of origin from geodetic to geocentric
    gclat, gclon, srho = geod2geoc(slat, slon)
    # Convert distant point from geodetic to geocentric
    gcelat, gcelon, erho = geod2geoc(elat, elon)
    # Convert distant point from geocentric to global cartesian
    (pX, pY, pZ) = globalspherical2globalcartesian(gcelat, gcelon, erho + ealt)
    # Convert pointing direction from global cartesian to local cartesian
    (dX, dY, dZ) = globalcartesian2localcartesian(pX, pY, pZ, gclat,
                                                  gclon, srho + salt)
    # Convert pointing direction from local cartesian to local spherical
    (gaz, gel, rho) = localspherical2localcartesian(dX, dY, dZ, inverse=True)
    # Convert pointing azimuth and elevation to geodetic
    (_, _, _, azm, _) = geodetic2geocAzEl(gclat, gclon, gaz, gel, inverse=True)
    return azm
