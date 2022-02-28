# (C) Copyright 2021 SuperDARN Canada, University of Saskatchewan
# Author(s): Marina Schmidt
#
# This file is part of the pyDARN Library.
#
# pyDARN is under the LGPL v3 license found in the root directory LICENSE.md
# Everyone is permitted to copy and distribute verbatim copies of this license
# document, but changing it is not allowed.
#
# This version of the GNU Lesser General Public License incorporates the terms
# and conditions of version 3 of the GNU Lesser General Public License,
# supplemented by the additional permissions listed below.
#
# Modifications:
#

"""
coordinates.py is a group of methods that focus on coordinates systems used in
plotting
"""
import datetime as dt
import enum

import aacgm_v2



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

    GEOGRAPHIC = geo_coordinates
    AACGM = aacgm_coordinates
    AACGM_MLT = aacgm_MLT_coordinates


def geo_coordinates(stid: int, beams: tuple = None, gates: tuple = None, **kwargs):
    """
    geographic_coordinates calculates the geographic coordinate for a given set of gates and beams
    parameters
    -----------

    """
    if ranges is None:
        gates = [0, SuperDARNRadars.radars[stid].range_gate_45]
    if beams is None:
        beams = [0, SuperDARNRadars.radars[stid].hardware_info.beams]

    for beam in range(beam[0], beams[1]+1):
        for gate in range(gates[0], gates[1]):
            lat, lon = gate2geographic_location(stid=stid, beam=beam,
                                                range_gate=gate, height=300,
                                                **kwargs)
            beam_corners_lats[gate, beam] = lat
            beam_corners_lons[gate, beam] = lon
    return beam_corners_lats, beam_corners_lons

def aacgm_coordinates(stid: int, beams: tuple = None, gates: tuple = None,
                      date: dt.datetime = dt.datetime.now, **kwargs):
    if ranges is None:
        gates = [0, SuperDARNRadars.radars[stid].range_gate_45]
    if beams is None:
        beams = [0, SuperDARNRadars.radars[stid].hardware_info.beams]

    for beam in range(beam[0], beams[1]+1):
        for gate in range(gates[0], gates[1]):
            lat, lon = gate2geographic_location(stid=stid, beam=beam,
                                                range_gate=gate, height=300,
                                                **kwargs)
            beam_corners_lats[gate, beam] = lat
            beam_corners_lons[gate, beam] = lon

            geomag = np.array(aacgmv2.get_aacgm_coord(glat=lat,
                                                      glon=lon,
                                                      height=250,
                                                      dtime=date))
            beam_corners_lats[gate, beam] = geomag[0]
            beam_corners_lons[gate, beam] = geomag[1]
    return beam_corners_lats, beam_corners_lons


def aacgm_MLT_coordinates(stid: int, beam: int = None, gate:int = None, **kwargs):
    beam_corners_lats, beam_corners_lons = aacgm_coordinates(stid=stid,
                                                             beams=beams,
                                                             gates=gates)
    fan_shape = beam_corners_lons.shape
    # Work out shift due in MLT
    beam_corners_mlts = np.zeros((fan_shape[0], fan_shape[1]))
    mltshift = beam_corners_lons[0, 0] - \
        (aacgmv2.convert_mlt(beam_corners_lons[0, 0], date) * 15)
    beam_corners_mlts = beam_corners_lons - mltshift
    return beam_corners_lats, beam_corners_mlts


def convert2MLT():
    pass

def gate2geographic_location(stid: int):
    pass
