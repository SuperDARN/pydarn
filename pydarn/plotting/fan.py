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
Fan plots, mapped to AACGM coordinates in a polar format
"""

import datetime as dt
import matplotlib.pyplot as plt
import numpy as np

from matplotlib import ticker, cm, colors
from typing import List

# Third party libraries
import aacgmv2

from pydarn import PyDARNColormaps, build_scan, radar_fov


class Fan():
    """
        Fan plots for SuperDARN data
        This class inherits from matplotlib to generate the figures
        Methods
        -------
        plot_fan
        """

    def __str__(self):
        return "This class is static class that provides"\
                " the following methods: \n"\
                "   - plot_fan()\n"\
                "   - return_beam_pos()\n"

    @classmethod
    def plot_fan(cls, dmap_data: List[dict], ax=None, scan_index: int = 1,
                 ranges: List = [0, 75], boundary: bool = True,
                 parameter: str = 'v', lowlat: int = 30,
                 cmap: str = None, groundscatter: bool = False,
                 zmin: int = None, zmax: int = None,
                 colorbar: bool = True,
                 colorbar_label: str = ''):
        """
        Plots a radar's Field Of View (FOV)
        fan plot for the given data and scan number

        Parameters
        -----------
            dmap_data: List[dict]
                Named list of dictionaries obtained from SDarn_read
            ax: matplotlib.pyplot axis
                Pre-defined axis object to pass in,
                must currently be polar projection
                Default: Generates a polar projection for
                the user with MLT/latitude labels
            scan_index: int
                Scan number from beginning of first record in file
                Default: 1
            parameter: str
                Key name indicating which parameter to plot.
                Default: v (Velocity). Alternatives: 'p_l', 'w_l', 'elv'
            lowlat: int
                Lower AACGM latitude boundary for the polar plot
                Default: 50
            ranges: list
                Set to a two element list of the lower and upper ranges to plot
                Default: [0,75]
            boundary: bool
                Set to false to not plot the outline of the FOV
                Default: True
            cmap: matplotlib.cm
                matplotlib colour map
                https://matplotlib.org/tutorials/colors/colormaps.html
                Default: Official pyDARN colour map for given parameter
            groundscatter : bool
                Set true to indicate if groundscatter should be plotted in grey
                Default: False
            zmin: int
                The minimum parameter value for coloring
                Default: {'p_l': [0], 'v': [-200], 'w_l': [0], 'elv': [0]}
            zmax: int
                The maximum parameter value for  coloring
                Default: {'p_l': [50], 'v': [200], 'w_l': [250], 'elv': [50]}
            colorbar: bool
                Draw a colourbar if True
                Default: True
            colorbar_label: str
                the label that appears next to the colour bar.
                Requires colorbar to be true
                Default: ''
        Returns
        -----------
        beam_corners_aacgm_lats
            n_beams x n_gates numpy array of AACGMv2 latitudes
        beam_corners_aacgm_lons
            n_beams x n_gates numpy array of AACGMv2 longitudes
        scan
            n_beams x n_gates numpy array of the scan data
            (for the selected parameter)
        grndsct
            n_beams x n_gates numpy array of the scan data
            (for the selected parameter)
        dtime
            datetime object for the scan plotted

        """

        # Get scan numbers for each record
        beam_scan = build_scan(dmap_data)

        # Locate scan in loaded data
        plot_beams = np.where(beam_scan == scan_index)

        # Time for coordinate conversion
        dtime = dt.datetime(dmap_data[plot_beams[0][0]]['time.yr'],
                            dmap_data[plot_beams[0][0]]['time.mo'],
                            dmap_data[plot_beams[0][0]]['time.dy'],
                            dmap_data[plot_beams[0][0]]['time.hr'],
                            dmap_data[plot_beams[0][0]]['time.mt'],
                            dmap_data[plot_beams[0][0]]['time.sc'])

        # Get radar beam/gate locations
        beam_corners_aacgm_lats, beam_corners_aacgm_lons = \
            radar_fov(dmap_data[0]['stid'], coords='aacgm', date=dtime)
        fan_shape = beam_corners_aacgm_lons.shape

        # Work out shift due in MLT
        beam_corners_mlts = np.zeros((fan_shape[0], fan_shape[1]))
        mltshift = beam_corners_aacgm_lons[0, 0] - \
            (aacgmv2.convert_mlt(beam_corners_aacgm_lons[0, 0], dtime) * 15)
        beam_corners_mlts = beam_corners_aacgm_lons - mltshift

        # Hold the beam positions
        thetas = np.radians(beam_corners_mlts)
        rs = beam_corners_aacgm_lats

        # Get range-gate data and groundscatter array for given scan
        scan = np.zeros((fan_shape[0] - 1, fan_shape[1]-1))
        grndsct = np.zeros((fan_shape[0] - 1, fan_shape[1]-1))
        for i in np.nditer(plot_beams):
            try:
                # get a list of gates where there is data
                slist = dmap_data[i.astype(int)]['slist']
                # get the beam number for the record
                beam = dmap_data[i.astype(int)]['bmnum']
                scan[slist, beam] = dmap_data[i.astype(int)][parameter]
                grndsct[slist, beam] = dmap_data[i.astype(int)]['gflg']
            # if there is no slist field this means partial record
            except KeyError:
                continue

        # Colour table and max value selection depending on parameter plotted
        # Load defaults if none given
        if cmap is None:
            cmap = {'p_l': 'plasma', 'v': PyDARNColormaps.PYDARN_VELOCITY,
                    'w_l': PyDARNColormaps.PYDARN_VIRIDIS,
                    'elv': PyDARNColormaps.PYDARN}
            cmap = plt.cm.get_cmap(cmap[parameter])

        # Setting zmin and zmax
        defaultzminmax = {'p_l': [0, 50], 'v': [-200, 200],
                          'w_l': [0, 250], 'elv': [0, 50]}
        if zmin is None:
            zmin = defaultzminmax[parameter][0]
        if zmax is None:
            zmax = defaultzminmax[parameter][1]

        # Setup plot
        # This may screw up references
        if ax is None:
            ax = plt.axes(polar=True)
            if beam_corners_aacgm_lats[0, 0] > 0:
                ax.set_ylim(90, lowlat)
                ax.set_yticks(np.arange(lowlat, 90, 10))
            else:
                ax.set_ylim(-90, -abs(lowlat))
                ax.set_yticks(np.arange(-abs(lowlat), -90, -10))
            ax.set_xticklabels(['00', '', '06', '', '12', '', '18', ''])
            ax.set_theta_zero_location("S")

        # Begin plotting by iterating over ranges and beams
        for gates in range(ranges[0], ranges[1] - 1):
            for beams in range(thetas.shape[1] - 2):
                # Index colour table correctly
                cmapindex = (scan[gates, beams] + abs(zmin)) /\
                        (abs(zmin) + abs(zmax))
                if cmapindex < 0:
                    cmapindex = 0

                if cmapindex > 1:
                    cmapindex = 1
                colour_rgba = cmap(cmapindex)

                # Check for zero values (white) and groundscatter (gray)
                if scan[gates, beams] == 0:
                    colour_rgba = (1, 1, 1, 0)

                if groundscatter and grndsct[gates, beams] == 1:
                    colour_rgba = 'gray'

                # Angle for polar plotting
                theta = [thetas[gates, beams], thetas[gates + 1, beams],
                         thetas[gates + 1, beams + 1],
                         thetas[gates, beams + 1]]
                # Radius for polar plotting
                r = [rs[gates, beams], rs[gates + 1, beams],
                     rs[gates + 1, beams + 1], rs[gates, beams + 1]]
                ax.fill(theta, r, color=colour_rgba)

        # Plot FOV outline
        if boundary is True:
            plt.polar(thetas[0:ranges[1], 0], rs[0:ranges[1], 0],
                      color='black', linewidth=0.5)
            plt.polar(thetas[ranges[1] - 1, 0:thetas.shape[1] - 1],
                      rs[ranges[1] - 1, 0:thetas.shape[1] - 1], color='black',
                      linewidth=0.5)
            plt.polar(thetas[0:ranges[1], thetas.shape[1] - 2],
                      rs[0:ranges[1], thetas.shape[1] - 2],
                      color='black', linewidth=0.5)
            plt.polar(thetas[0, 0:thetas.shape[1] - 2],
                      rs[0, 0:thetas.shape[1] - 2], color='black',
                      linewidth=0.5)

        norm = colors.Normalize
        norm = norm(zmin, zmax)
        # Create color bar if True
        if colorbar is True:
            mappable = cm.ScalarMappable(norm=norm, cmap=cmap)
            locator = ticker.MaxNLocator(symmetric=True, min_n_ticks=3,
                                         integer=True, nbins='auto')
            ticks = locator.tick_values(vmin=zmin, vmax=zmax)

            cb = ax.figure.colorbar(mappable, ax=ax,
                                    extend='both', ticks=ticks)

            if colorbar_label != '':
                cb.set_label(colorbar_label)

        return beam_corners_aacgm_lats, beam_corners_aacgm_lons,
