# Copyright (C) 2021 SuperDARN Canada, University of Saskatchewan
# Author: Daniel Billett
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
"""
Code which generates axis objects for use in plotting functions
"""

import matplotlib.pyplot as plt
import numpy as np

from pydarn import Hemisphere


class Projections():
    """
        Methods for generating axis objects for use in plotting functions
        Methods
        -------
        axis_polar
    """

    def __str__(self):
        return "This class is static class that provides"\
                " the following methods: \n"\
                "   - axis_polar()\n"

    @classmethod
    def axis_polar(cls, lowlat: int = 30, hemisphere: object = Hemisphere.North):
        """
        Plots a radar's Field Of View (FOV) fan plot for the given data and
        scan number

        Parameters
        -----------
            lowlat: int
                Lower AACGM latitude boundary for the polar plot
                Default: 30
            hemiphere: enum
                Hemisphere of polar projection. Can be Hemisphere.North or
                Hemisphere.South for northern and southern hemispheres,
                respectively
                Default: Hemisphere.North
        """

        ax = plt.axes(polar=True)

        # Set upper and lower latitude limits (pole and lowlat)
        if hemisphere == Hemisphere.North:
            ax.set_ylim(90, lowlat)
            ax.set_yticks(np.arange(lowlat, 90, 10))
        else:
            # If hemisphere is South, lowlat must be negative
            ax.set_ylim(-90, -abs(lowlat))
            ax.set_yticks(np.arange(-abs(lowlat), -90, -10))

        # Locations of tick marks. Will be customisable in future
        ax.set_xticks([0, np.radians(45), np.radians(90), np.radians(135),
                       np.radians(180), np.radians(225), np.radians(270),
                       np.radians(315)])

        # Tick labels will depend on coordinate system
        ax.set_xticklabels(['00', '', '06', '', '12', '', '18', ''])
        ax.set_theta_zero_location("S")

        return ax
