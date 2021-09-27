# Copyright (C) 2020 SuperDARN Canada, University of Saskatchewan
# Author: Daniel Billett, Marina Schmidt
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
Grid plots, mapped to AACGM coordinates in a polar format
"""

import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import warnings

from matplotlib import ticker, cm, colors
from typing import List

# Third party libraries
import aacgmv2

from pydarn import (PyDARNColormaps, Grid, plot_exceptions, citing_warning,
                    standard_warning_format)

warnings.formatwarning = standard_warning_format


class Maps():
    """
    Maps plots for SuperDARN data

    Methods
    -------
    plot_maps
    """

    def __str__(self):
        return "This class is static class that provides"\
                " the following methods: \n"\
                "   - plot_maps()\n"

    @classmethod
    def plot_map(cls, dmap_data, parameter="vector.vel.median",
                 alpha=1.0, **kwargs):
        """
        """

        # If the parameter is velocity then plot the LOS vectors
        if parameter == "vector.vel.median":
            record = 0
            data = dmap_data[0]['vector.vel.median']
            # Get the azimuths from the data
            azm_v = dmap_data[record]['vector.kvect']

            # Number of data points
            num_pts = range(len(data))

            # Angle to "rotate" each vector by to get into same
            # reference frame Controlled by longitude, or "mltitude"
            alpha = thetas

            # Convert initial positions to Cartesian
            start_pos_x = (90 - rs) * np.cos(thetas)
            start_pos_y = (90 - rs) * np.sin(thetas)

            # Resolve LOS vector in x and y directions,
            # with respect to mag pole
            # Gives zonal and meridional components of LOS vector
            los_x = -data * np.cos(np.radians(-azm_v))
            los_y = -data * np.sin(np.radians(-azm_v))

            # Rotate each vector into same reference frame
            # following vector rotation matrix
            # https://en.wikipedia.org/wiki/Rotation_matrix
            vec_x = (los_x * np.cos(alpha)) - (los_y * np.sin(alpha))
            vec_y = (los_x * np.sin(alpha)) + (los_y * np.cos(alpha))

            # New vector end points, in Cartesian
            end_pos_x = start_pos_x + (vec_x / len_factor)
            end_pos_y = start_pos_y + (vec_y / len_factor)

            # Convert back to polar for plotting
            end_rs = 90 - (np.sqrt(end_pos_x**2 + end_pos_y**2))
            end_thetas = np.arctan2(end_pos_y, end_pos_x)

            # Plot the vectors
            for i in num_pts:
                plt.plot([thetas[i], end_thetas[i]],
                         [rs[i], end_rs[i]], c=cmap(norm(data[i])),
                         linewidth=0.5)
        else:
            Grid.plot_grid(dmap_data, parameter, alpha, **kwargs)
