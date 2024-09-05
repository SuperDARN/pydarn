# Copyright 2023 SuperDARN Canada, University of Saskatchewan
# Author: Carley Martin
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
# This code to calculate the solar terminator at given height in the ionosphere
# is converted from Carley Martin's JavaScript terminator.js code
#
# Modification:
# 

import numpy as np
import datetime as dt

from pydarn import Re

"""
terminator.py is a group of methods used to calculated the part of a map where
the ionosphere is in the earth's shadow
"""


def antipode(psn):
    """
    antipode calculates the opposite side of the Earth to the sub-solar 
    point

    Parameters
    ----------
    psn : list
        list containing the longitude/latitude of the sub solar point

    Returns
    -------
    antipode: lise
        list containing the logitude/latitude of the opposite side of the 
        sub-solar position
    """
    antipode = [psn[0] + 180, -psn[1]]
    return antipode


def eccentricity_earths_orbit(centuries):
    """
    eccentricity of Earths orbit calculates the ellipse created by Earth in
    it's orbit

    Parameters
    ----------
    centuries: float
        decimal value of centuries passed since Julian base

    Returns
    -------
    eccentricity: float
        eccentricity of Earth's orbit, likely small number as all dates in
        SuperDARN operations are around 2000
    """
    # Eccentricity of Earth's orbit (unitless) = 0.016708634
    eccentricity = 0.016708634 - centuries * (0.000042037 + 0.0000001267
                                              * centuries)
    return eccentricity


def mean_obliquity_ecliptic(centuries):
    """
    mean obliquity ecliptic calculates the effect caused by the tilt of the
    Earth on its axis

    Parameters
    ----------
    centuries: float
        decimal value of centuries passed since Julian base

    Returns
    -------
    oblic: float (radians)
        obliquity of Earths axis
    """
    obliq = np.radians(23 + (26 + (21.448 - centuries * (46.8150 + centuries *
                (0.00059 - centuries * 0.001813))) / 60) / 60)
    return obliq


def obliquity_correction(centuries):
    """
    obliquity correction corrects the obliquity of Earths axis, includes small
    perturbations in obliquity over time

    Parameters
    ----------
    centuries: float
        decimal value of centuries passed since Julian base

    Returns
    -------
    oblic: float (radians)
        obliquity of Earths axis
    """
    mean_ob = mean_obliquity_ecliptic(centuries)
    obliq = mean_ob + np.radians(0.00256) * np.cos(np.radians(125.04 - 1934.136
                                                              * centuries))
    return obliq


def solar_geometric_mean_anomaly(centuries):
    """
    solar geometric mean anomaly calculates the apparent motion of the sun and
    along the plane of the ecliptic

    Parameters
    ----------
    centuries: float
        decimal value of centuries passed since Julian base

    Returns
    -------
    anomaly: float (radians)
        angular distance from perihelion which Earth would have moved around
        Sun if using constant angular velocity
    """
    anomaly = np.radians(357.52911 + centuries
                         * (35999.05029 - 0.0001537 * centuries))
    return anomaly


def solar_geometric_mean_longitude(centuries):
    """
    solar geometric mean longitude calculates where the mean Sun was at given
    date time in reference to Julian base date

    Parameters
    ----------
    centuries: float
        decimal value of centuries passed since Julian base

    Returns
    -------
    mean_long: float (radians)
        solar meal longitude
    """
    # Mean longitude of sun at base julian date = 280.46646 degrees
    # Corrections from J.Meeus Astronomical Algorithms book
    el = (280.46646 + centuries * (36000.76983 + centuries * 0.0003032)) % 360
    # Give value between 0 and 360
    if el < 0:
        el = el + 360
    mean_long = np.radians(el)
    return mean_long


def solar_equation_center(centuries):
    """
    solar equation center calculates the angular difference between the
    actual position of a body and it's position if it's motion was uniform in
    a circular orbit - approx from Keppler's equation allowed as the
    eccentricity is very small

    Parameters
    ----------
    centuries: float
        decimal value of centuries passed since Julian base

    Returns
    -------
    solar_center: float (radians)
        solar center angle
    """
    m = solar_geometric_mean_anomaly(centuries)
    solar_center = np.radians(np.sin(m)
                   * (1.914602 - centuries * (0.004817 + 0.000014 * centuries))
                   + np.sin(m + m) * (0.019993 - 0.000101 * centuries)
                   + np.sin(m + m + m) * 0.000289)
    return solar_center


def solar_true_longitude(centuries):
    """
    solar true longitude calculates the true longitude of the Sun

    Parameters
    ----------
    centuries: float
        decimal value of centuries passed since Julian base

    Returns
    -------
    true_long: float (radians)
        the true longitude
    """
    true_long = solar_geometric_mean_longitude(centuries)\
                + solar_equation_center(centuries)
    return true_long


def solar_apparent_longitude(centuries):
    """
    solar apparent longitude calculates the true longitude including
    extra perturbations from the Moon etc. 

    Parameters
    ----------
    centuries: float
        decimal value of centuries passed since Julian base

    Returns
    -------
    apparent: float (radians)
        the true apparent longitude
    """
    apparent = solar_true_longitude(centuries) - np.radians(0.00569 + 0.00478
                    * np.sin(np.radians(125.04 - 1934.136 * centuries)))
    return apparent


def solar_declination(centuries):
    dec = np.arcsin( np.sin(obliquity_correction(centuries))\
          * np.sin(solar_apparent_longitude(centuries)))
    return dec


def equation_of_time(centuries):
    # Equation from NOAA subsolar calculator
    # http://www.esrl.noaa.gov/gmd/grad/solcalc/
    e = eccentricity_earths_orbit(centuries)
    m = solar_geometric_mean_anomaly(centuries)
    el = solar_geometric_mean_longitude(centuries)
    y = np.tan(obliquity_correction(centuries) /2)
    time_eq = y * np.sin(2 * el) - 2 * e * np.sin(m) + 4 * e * y * np.sin(m)\
              * np.cos(2 * el) - 0.5 * y * y * np.sin(4 * el)\
              - 1.25 * e * e * np.sin(2 * m)
    return time_eq


def solar_position(date):
    """
    solar position calculates the latitude and longitude of the sub-solar
    position on Earth for a given date time

    Parameters
    ----------
    date : datetime object
            date time of interest

    Returns
    -------
    psn: list
        list containing the logitude/latitude of the 
        sub-solar position
    """
    # Convert Greg date to Julian date (given in partial centuries)
    # 86400 seconds = 1 days
    # 36525 days = 100 years (a century)
    centuries = (date - dt.datetime(2000,1,1,12,0)).total_seconds() / 86400 / 36525
    # Given days date but at midnight
    datefloor = date.replace(hour=0, minute=0, second=0)
    # Calculate the longitude at given time
    longitude = (datefloor - date).total_seconds() / 86400 * 360 - 180
    # Calculate long lat of sub-solar position in degrees
    long = longitude - np.degrees(equation_of_time(centuries))
    lat = np.degrees(solar_declination(centuries))
    return [long, lat]


def antisolar(date):
    """
    antisolar calculates the latitude and longitude of the anti-sub-solar
    position on Earth for a given date time

    Parameters
    ----------
    date : datetime object
            date time of interest

    Returns
    -------
    antisolar_point: list
        list containing the logitude/latitude of the 
        anti-sub-solar position
    """
    antisolar_point = antipode(solar_position(date))
    return antisolar_point


def terminator(date, height):
    # Get the anti-sub-solar point
    antisolar_point = antisolar(date)
    # Calculate the size of the great circle (radius from anti-sub-solar point)
    arc_angle = 90 - np.degrees(np.arccos(Re / (Re + height)))
    # Calculate arc in km
    arc_length = Re * np.radians(arc_angle)
    
    return antisolar_point, arc_length, arc_angle

