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
    def axis_polar(cls, ax=None):
        """
        Plots a radar's Field Of View (FOV) fan plot for the given data and
        scan number

        Parameters
        -----------
            dmap_data: List[dict]
                asda
        """                
             
        pdb.set_trace()  
        
        
        return ax       
                 
                 
                 