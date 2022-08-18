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
# 2022-08-04 CJM added HALF_SLANT option and gate2halfslant method
# 2022-08-18 CJM added functions to convert range to geo, mag or mlt
#

import aacgmv2
import enum
import numpy as np
import datetime as dt


from pydarn import (Re, C, geocentric_coordinates, SuperDARNRadars)


def gate2halfslant(**kwargs):
    """
    Calculate the slant range divided by 2 for each range gate

    Parameters
    ----------
        None

    Returns
    -------
        half_slant : np.array
            returns an array of slant ranges divided by two for the radar
    """
    slant_range = gate2slant(**kwargs)
    half_slant = slant_range / 2
    return half_slant


def gate2groundscatter(reflection_height: float = 250, **kwargs):
    """
    Calculate the ground scatter mapped range (km) for each slanted range
    for SuperDARN data. This function is based on the Ground Scatter equation
    from Bristow paper at https://doi.org/10.1029/93JA01470 on page 325
    Parameters
    ----------
        reflection_height: float
            reflection height
            default:  250

    Returns
    -------
        ground_scatter_mapped_ranges : np.array
            returns an array of ground scatter mapped ranges for the radar
    """
    slant_ranges = gate2slant(**kwargs)
    ground_scatter_mapped_ranges =\
            Re*np.arcsin(np.sqrt((slant_ranges**2/4)-
                                 (reflection_height**2))/Re)

    return ground_scatter_mapped_ranges


def gate2slant(rxrise: int = 0, range_gate: int = 0, frang: int = 180,
               rsep: int = 45, nrang: int = None, center: bool = True,
               **kwargs):
    """
    Calculate the slant range (km) for each range gate for SuperDARN data

    Parameters
    ----------
        frang: int
            range from the edge of first the gate to the radar [km]
            This should be given in fitacf record of the control program
        rsep: int
            Radar seperation of the gates. Determined by control program.
        rxrise: int
            Use hardware value for this, avoid data file values
        gate: int
            range gate to determine the slant range [km], if nrang
            is None
            default: 0
        nrang: int
            max number of range gates in the list of records. If
            not None, will calculate all slant ranges
            default: None
        center: boolean
            Calculate the slant range in the center of range gate
            or edge

    Returns
    -------
        slant_ranges : np.array
            returns an array of slant ranges for the radar
    """
    # lag to the first range gate in microseconds
    # 0.3 - speed of light (km/us)
    # 2 - two times for there and back
    distance_factor = 2.0
    # C - speed of light m/s to km/us
    speed_of_light = C * 0.001 * 1e-6
    lag_first = frang * distance_factor / speed_of_light
    # sample separation in microseconds
    sample_sep = rsep * distance_factor / speed_of_light
    # Range offset
    # If center is true, calculate at the center
    if center:
        # 0.5 off set to the centre of the range gate instead of edge
        range_offset = -0.5 * rsep
    else:
        range_offset = 0.0
    # Now calculate slant range in km
    if nrang is None:
        slant_ranges = (lag_first - rxrise +
                        range_gate * sample_sep) * speed_of_light /\
                distance_factor + range_offset
    else:
        slant_ranges = np.zeros(nrang+1)
        for gate in range(nrang+1):
            slant_ranges[gate] = (lag_first - rxrise +
                                  gate * sample_sep) * speed_of_light /\
                    distance_factor + range_offset
    return slant_ranges


def km2geo(ranges, stid: str, beam: int, **kwargs):
    """
    Convert a value in km from the radar into a geographic
    latitude and longitude

    Parameters
    ----------
        ranges: list
            list of distances from the radar (km)
        stid: str
            the stid of required radar

    Returns
    -------
        latitude: list of floats
            (degrees)
        longitude: list of floats
            (degrees)
    """
    radar_lat = np.radians(SuperDARNRadars.
                           radars[stid].hardware_info.geographic.lat)
    radar_lon = np.radians(SuperDARNRadars.
                           radars[stid].hardware_info.geographic.lon)
    boresight = np.radians(SuperDARNRadars.
                           radars[stid].hardware_info.boresight.physical)
    beam_sep = np.radians(abs(SuperDARNRadars.
                          radars[stid].hardware_info.beam_separation))
    offset = SuperDARNRadars.radars[stid].hardware_info.beams / 2.0 - 0.5
    beam_edge = -beam_sep * 0.5
    # psi [rad] in the angle from the boresight
    psi = beam_sep * (beam - offset) + beam_edge

    lats = []
    lons = []
    for km in ranges:
        lat, lon = geocentric_coordinates(lat=radar_lat, lon=radar_lon,
                                          target_range=km, psi=psi,
                                          boresight=boresight, **kwargs)
        lats.append(np.degrees(lat))
        lons.append(np.degrees(lon))
    return lats, lons


def km2mag(ranges, date: dt.datetime, **kwargs):
    """
    Convert a value in km from the radar into a magnetic
    latitude and longitude

    Parameters
    ----------
        ranges: list
            list of distances from the radar (km)
        date: datetime object
            date from first data

    Returns
    -------
        magnetic latitude: list of floats
            (degrees)
        magnetic longitude: list of floats
            (degrees)
    """
    lats, lons = km2geo(ranges, **kwargs)
    # convert geo to mag
    magpsn = aacgmv2.get_aacgm_coord_arr(glat=lats, glon=lons,
                                         height=250, dtime=date)
    return magpsn[0], magpsn[1]


def km2mlt(ranges, date: dt.datetime, stid: str, beam: int, *kwargs):
    """
    Convert a value in km from the radar into a magnetic local time

    Parameters
    ----------
        ranges: list
            list of distances from the radar (km)

    Returns
    -------
        mlts: list of floats
            magnetic local time
    """
    _, mlons = km2mag(ranges, date=date, stid=stid, beam=beam)
    mlts = aacgmv2.convert_mlt(mlons, date)
    return mlts


class RangeEstimation(enum.Enum):
    """
    Range_Estimation class is to list the current range gate estimations
    a user can pick from

    enumerators:
        RANGE_GATE: range gates
        SLANT_RANGE: slant range (km)
        GSMR: ground scatter mapped range (km)
    """

    RANGE_GATE = enum.auto()
    SLANT_RANGE = (gate2slant,)
    HALF_SLANT = (gate2halfslant,)
    GSMR = (gate2groundscatter,)

    # Need this to make the functions callable
    def __call__(self, *args, **kwargs):
        return self.value[0](*args, **kwargs)
