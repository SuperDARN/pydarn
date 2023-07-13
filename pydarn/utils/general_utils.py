# Copyright (C) 2023 SuperDARN Canada, University of Saskatchewan
# Author(s): Carley Martin
#
# Modifications:
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
"""
This module contains general calculations used across pyDARN library and may be
useful for the user
"""
import numpy as np

from pydarn import Re


class GeneralUtils():
    """
        General Utility Functions

        Methods
        -------
        great_circle
        new_coordinate
    """
    def __str__(self):
        return "This class is static class that provides"\
                " the following methods: \n"\
                "   - great_circle()\n"

    @classmethod
    def great_circle(cls, lon1, lat1, lon2, lat2):
        '''
        Calculates the great circle distance between two points on a sphere

        Parameters
        -----------
            lon1: float in degrees
                longitude of first point
            lat1: float in degrees
                latitude of first point
            lon2: float in degrees
                longitude of second point
            lat1: float in degrees
                latitude of second point

        Returns
        -------
            distance: float
                assuming radius of sphere is 1 (1 Re)
        '''
        lon1 = np.radians(lon1)
        lat1 = np.radians(lat1)
        lon2 = np.radians(lon2)
        lat2 = np.radians(lat2)
        return (np.arccos(np.sin(lat1) * np.sin(lat2)
                          + np.cos(lat1) * np.cos(lat2)
                          * np.cos(lon1 - lon2)))

    @classmethod
    def new_coordinate(cls, lat, lon, d, bearing, R=Re):
        """
        new coordinate will calculate the new coordinate from a given
        position, distance and bearing

        Parameters
        ----------
        lat: float
            initial latitude, in degrees
        lon: float
            initial longitude, in degrees
        d: target distance from initial
        bearing: (true) heading in degrees
        R: optional radius of sphere, defaults to mean radius of earth

        Returns
        -------
        lat: float
            new latitude, in degrees
        lon: float
            new longitude, in degrees
        """
        lat1 = np.radians(lat)
        lon1 = np.radians(lon)
        a = np.radians(bearing)
        lat2 = np.arcsin(np.sin(lat1) * np.cos(d/R) + np.cos(lat1)
                         * np.sin(d/R) * np.cos(a))
        lon2 = lon1 + np.arctan2(np.sin(a) * np.sin(d/R) * np.cos(lat1),
                                 np.cos(d/R) - np.sin(lat1) * np.sin(lat2))
        return (np.degrees(lat2), np.degrees(lon2))
