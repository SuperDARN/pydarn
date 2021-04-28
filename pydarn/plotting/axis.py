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

import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
from typing import List
import pdb

# Third party libraries
import aacgmv2

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
    def axis_polar(cls, lowlat: int = 30, hem: str='N'):
        """
        Plots a radar's Field Of View (FOV) fan plot for the given data and
        scan number

        Parameters
        -----------
            lowlat: int
                Lower AACGM latitude boundary for the polar plot
                Default: 30
            hem: str
                Hemisphere of polar projection. Can be 'N' or 'S' for
                northern and southern hemispheres, respectively
                Default: 'N'
                
        """                    
        
        ax = plt.axes(polar=True)

        # Set upper and lower latitude limits (pole and lowlat)
        if hem is 'N':
            ax.set_ylim(90, lowlat)
            ax.set_yticks(np.arange(lowlat, 90, 10))
        else:
            ax.set_ylim(-90, -abs(lowlat)) # If hem is 'S', lowlat must be negative
            ax.set_yticks(np.arange(-abs(lowlat), -90, -10))
         
        # Locations of tick marks. Will be customisable in future    
        ax.set_xticks([0, np.radians(45), np.radians(90), np.radians(135),
                       np.radians(180), np.radians(225), np.radians(270),
                       np.radians(315)])
                       
        # Tick labels will depend on coordinate system               
        ax.set_xticklabels(['00', '', '06', '', '12', '', '18', ''])
        ax.set_theta_zero_location("S")
        
        return ax       
                 
                 
                 