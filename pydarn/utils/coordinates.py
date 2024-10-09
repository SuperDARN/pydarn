# (C) Copyright 2021 SuperDARN Canada, University of Saskatchewan
# Author(s): Marina Schmidt
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
# Modifications:
# 2022-03-10 MTS added 4 new methods to generate coordinates for the various
#                enums
# 2023-08-26 CJM corrected calculations to use bmoff and removed abs()
#

"""
coordinates.py is a group of methods that focus on coordinates systems used in
plotting
"""
import datetime as dt
import enum
import numpy as np

import aacgmv2

import pydarn
from pydarn import (geocentric_coordinates, SuperDARNRadars, RangeEstimation,
                    radar_exceptions, Re, RadarID)


def geo_coordinates(stid: RadarID, beams: int = None,
                    gates: tuple = None, **kwargs):
    """
    geographic_coordinates calculates the geographic coordinate for a given
    set of gates and beams
    parameters
    -----------

    """
    if gates is None:
        gates = [0, SuperDARNRadars.radars[stid].range_gate_45]
    if beams is None:
        beams = SuperDARNRadars.radars[stid].hardware_info.beams

    # Plus 1 is due to the fact fov files index at 1 so in the plotting
    # of the boundary there is a subtraction of 1 to offset this as python
    # converts to index of 0 which my code already accounts for
    beam_corners_lats = np.zeros((gates[1]-gates[0]+1, beams+1))
    beam_corners_lons = np.zeros((gates[1]-gates[0]+1, beams+1))

    for beam in range(0, beams+1):
        for gate in range(gates[0], gates[1]+1):
            lat, lon = gate2geographic_location(stid=stid, beam=beam,
                                                range_gate=gate, height=300,
                                                **kwargs)
            beam_corners_lats[gate-gates[0], beam] = lat
            beam_corners_lons[gate-gates[0], beam] = lon
    y0inx = np.min(np.where(np.isfinite(beam_corners_lats[:,0]))[0])
    return beam_corners_lats[y0inx:], beam_corners_lons[y0inx:]


def aacgm_coordinates(stid: pydarn.RadarID, beams: int = None, gates: tuple = None,
                      date: dt.datetime = dt.datetime.now, **kwargs):
    if gates is None:
        gates = [0, SuperDARNRadars.radars[stid].range_gate_45]
    if beams is None:
        beams = SuperDARNRadars.radars[stid].hardware_info.beams

    # Plus 1 is due to the fact fov files index at 1 so in the plotting
    # of the boundary there is a subtraction of 1 to offset this as python
    # converts to index of 0 which my code already accounts for
    beam_corners_lats = np.zeros((gates[1]-gates[0]+1, beams+1))
    beam_corners_lons = np.zeros((gates[1]-gates[0]+1, beams+1))

    for beam in range(0, beams+1):
        for gate in range(gates[0], gates[1]+1):
            lat, lon = gate2geographic_location(stid=stid, beam=beam,
                                                range_gate=gate, height=300,
                                                **kwargs)
            geomag = np.array(aacgmv2.get_aacgm_coord(glat=lat,
                                                      glon=lon,
                                                      height=250,
                                                      dtime=date))
            beam_corners_lats[gate-gates[0], beam] = geomag[0]
            beam_corners_lons[gate-gates[0], beam] = geomag[1]
    y0inx = np.min(np.where(np.isfinite(beam_corners_lats[:,0]))[0])
    return beam_corners_lats[y0inx:], beam_corners_lons[y0inx:]


def aacgm_MLT_coordinates(**kwargs):
    beam_corners_lats, beam_corners_lons = aacgm_coordinates(**kwargs)
    beam_corners_mlts = convert2MLT(beam_corners_lons, **kwargs)
    return beam_corners_lats, beam_corners_mlts


def convert2MLT(lons: float, date: object, **kwargs):
    fan_shape = lons.shape
    # Work out shift due in MLT
    beam_corners_mlts = np.zeros((fan_shape[0], fan_shape[1]))
    mltshift = lons[0, 0] - (aacgmv2.convert_mlt(lons[0, 0], date) * 15)
    beam_corners_mlts = lons - mltshift
    return beam_corners_mlts


def gate2geographic_location(stid: pydarn.RadarID, beam: int, height: float = None,
                             elv_angle: float = 0.0, center: bool = False,
                             range_estimation: RangeEstimation =
                             RangeEstimation.SLANT_RANGE, **kwargs):
    """
    determines the geographic cell position for a given range gate and beam
    Notes: From RPosGeo line 335

    parameters
    ----------
        stid: pydarn.RadarID
            station id of the radar to use
        beam: int
            beam number (indexing at 0)
        height: float
            transmutation height [km]
            default: none
            if none then it uses elevation angle
        elv_angle: float
            elevation angle in [deg]
            default: 0
        center: bool
            obtain geographic location of the centre of the range gates
            False obtains the near-left corner of the range gates.
            See also: gate2slant in range_estimation module
            default: False (return corner values)

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
                           radars[stid].hardware_info.boresight.physical)
    bmoff = np.radians(SuperDARNRadars.
                       radars[stid].hardware_info.boresight.electronic)
    radar_lat = np.radians(SuperDARNRadars.
                           radars[stid].hardware_info.geographic.lat)
    radar_lon = np.radians(SuperDARNRadars.
                           radars[stid].hardware_info.geographic.lon)
    # Note that some beam separations are negative
    beam_sep = np.radians(SuperDARNRadars.
                          radars[stid].hardware_info.beam_separation)
    rxrise = SuperDARNRadars.radars[stid].hardware_info.rx_rise_time

    # If the user wants the edge corner of the range gate:
    # Radar outwards direction center value is corrected in
    # range_estimation module
    if center:
        beam_edge = 0
    else:
        beam_edge = -beam_sep * 0.5

    # psi [rad] in the angle from the boresight
    psi = beam_sep * (beam - offset) + beam_edge + bmoff
    # Calculate the slant range [km]
    if range_estimation == RangeEstimation.RANGE_GATE:
        raise radar_exceptions.RangeEstimationError("Range gates cannot be "
                                                    "used in to estimate "
                                                    "distance. Try SLANT_RANGE"
                                                    " instead.")
    elif range_estimation == RangeEstimation.TIME_OF_FLIGHT:
        raise radar_exceptions.RangeEstimationError("Time of flight cannot be "
                                                    "used in to estimate "
                                                    "distance. Try SLANT_RANGE"
                                                    " instead.")
    else:
        target_range = range_estimation(rxrise=rxrise, **kwargs)

    # If no height is specified then use elevation angle (default 0)
    # to calculate the transmutation height
    if height is None:
        height = -Re + np.sqrt(Re**2 + 2 * target_range * Re *
                               np.sin(np.radians(elv_angle)) + target_range**2)

    lat, lon = geocentric_coordinates(lat=radar_lat,
                                      lon=radar_lon,
                                      target_range=target_range,
                                      cell_height=height,
                                      psi=psi,
                                      boresight=boresight, **kwargs)
    # convert back degrees as preferred units to use?
    return np.degrees(lat), np.degrees(lon)


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

    GEOGRAPHIC = (geo_coordinates, )
    AACGM = (aacgm_coordinates, )
    AACGM_MLT = (aacgm_MLT_coordinates, )

    # Need this to make the functions callable
    def __call__(self, *args, **kwargs):
        return self.value[0](*args, **kwargs)
