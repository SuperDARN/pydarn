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
    antipode = [psn[0] - 180, -psn[1]]
    return antipode

def eccentricity_earths_orbit(centuries):
    eccentricity = 0.016708634 - centuries * (0.000042037 + 0.0000001267
                                              * centuries)
    return eccentricity


def mean_obliquity_ecliptic(centuries):
    obliq = (23 + (26 + (21.448 - centuries * (46.8150 + centuries * 
             (0.00059 - centuries * 0.001813))) / 60) / 60) * np.radians
    return obliq


def obliquity_correction(centuries):
    mean_ob = mean_obliquity_ecliptic(centuries)
    obliq = mean_ob + 0.00256 * np.cos((125.04 - 1934.136 * centuries)
                                       * np.radians)
            * np.radians
    return obliq


def solar_true_longitude(centuries):
    true_long = solarGeometricMeanLongitude(centuries)
                + solarEquationOfCenter(centuries)
    return true_long


def solar_apparent_longitude(centuries):
    apparent = solar_true_longitude(centuries) 
               - (0.00569 + 0.00478 * np.sin((125.04 - 1934.136 * centuries) 
                                             * np.radians)) * np.radians
    return apparent


def solar_declination(centuries):
    dec = np.asin(np.sin(obliquityCorrection(centuries))
          * np.sin(solarApparentLongitude(centuries)))
    return dec


def solar_geometric_mean_anomaly(centuries):
    anomaly = (357.52911 + centuries * (35999.05029 - 0.0001537 * centuries))
              * np.radians
    return anomaly


def solar_geometric_mean_longitude(centuries):
    l = (280.46646 + centuries * (36000.76983 + centuries * 0.0003032)) % 360
    # TODO: Convert next line to python
    mean_long = (l < 0 ? l + 360 : l) / 180 * np.pi
    return mean_long


def solar_equation_center(centuries):
    m = solar_geometric_mean_anomaly(centuries):
    solar_center = (np.sin(m) * (1.914602 - centuries * (0.004817 + 0.000014 
                                                         * centuries))
                   + np.sin(m**2) * (0.019993 - 0.000101 * centuries)
                   + np.sin(m**3) * 0.000289) * np.radians


def equation_of_time(centuries):
    # Equation from NOAA subsolar calculator
    # http://www.esrl.noaa.gov/gmd/grad/solcalc/
    e = eccentricity_earths_orbit(centuries)
    m = solar_geometric_mean_anomaly(centuries)
    l = solar_geometric_mean_longitude(centuries)
    y = np.tan(obliquity_correction(centuries) /2)
    time_eq = y * np.sin(2 * l) - 2 * e * np.sin(m) + 4 * e * y * np.sin(m) 
              * np.cos(2 * l) - 0.5 * y * y * np.sin(4 * l)
              - 1.25 * e * e * np.sin(2 * m);
    return time_eq


def solar_position(date):
    """
    """
    #Julian date
    centuries = (date - dateat(2000,1,1,12)) / 864e5/36525
    datefloor = #UTCDate with 0 ,0,0,0
    longitude = datefloor - date /864e5 * 360 - 180
    long = np.degrees(longitude - equation_of_time(centuries))
    lat = np.degrees(solar_declination(centuries))
    return [long, lat]


def antisolar(date):
    antisolar_point - antipode(solar_position(date))
    return antisolar_point


def terminator(date, height):
    # Get the anti-sub-solar point
    antisolar_point = antisolar(date)
    # Calculate the size of the great circle (radius from anti-sub-solar point)
    arc_angle = np.radians(90 - np.degrees(np.acos(Re / (Re + height))))
    # Calculate arc in km
    arc_length = Re * arc_angle
    
    
    
    