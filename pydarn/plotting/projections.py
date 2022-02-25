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
from packaging import version

from pydarn import Hemisphere, plot_exceptions
try:
    import cartopy
    from cartopy.mpl import geoaxes
    import cartopy.crs as ccrs
    cartopyInstalled = True
    if version.parse(cartopy.__version__) < version.parse("0.19"):
        cartopyVersion = False
    else:
        cartopyVersion = True
except Exception:
    cartopyInstalled = False



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
    def axis_polar(cls, lowlat: int = 30,
                   hemisphere: object = Hemisphere.North, **kwargs):
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

    @classmethod
    def axis_geological(cls, date, ax: object = None, hemisphere: object = Hemisphere.North,
                        lowlat: int = 30, **kwargs):
        """
        """
        if cartopyInstalled == False:
            raise plot_exceptions.CartopyMissingError()
        if cartopyVersion == False:
            raise plot_exceptions.CartopyVersionError(cartopy.__version__)
        # no need to shift any coords, let cartopy do that
        # however, we do need to figure out
        # how much to rotate the projection
        deg_from_midnight = (date.hour + date.minute / 60) / 24 * 360
        if hemisphere == Hemisphere.North:
            pole_lat = 90
            noon = -deg_from_midnight
            ylocations = -5
        else:
            pole_lat = -90
            noon = 360 - deg_from_midnight
            ylocations = 5
        # handle none types or wrongly built axes
        if type(ax) != geoaxes.GeoAxesSubplot:
            proj = ccrs.Orthographic(noon, pole_lat)
            ax = plt.subplot(111, projection=proj, aspect='auto')
            ax.coastlines()
            #ax.gridlines(ylocs=np.arange(pole_lat, 0, ylocations))
        #        grid_lines = ax.gridlines(draw_labels=True,linewidth=1, color='black',)
        #        grid_lines.xformatter = LONGITUDE_FORMATTER
        #        grid_lines.yformatter = LATITUDE_FORMATTER

            extent = min(45e5,
                         (abs(proj.transform_point(noon, lowlat,
                                                   ccrs.PlateCarree())
                              [1])))
            ax.set_extent(extents=(-extent, extent, -extent, extent),
                          crs=proj)
        else:
            ax.pcolormesh(beam_corners_aacgm_lons,
                          beam_corners_aacgm_lats,
                          np.ma.masked_array(scan, ~scan.astype(bool)),
                          norm=norm, cmap=cmap,
                          transform=ccrs.PlateCarree())
            extent = min(45e5,
                         (abs(proj.transform_point(noon, lowlat,
                                                   ccrs.PlateCarree())
                              [1])))
            ax.set_extent(extents=(-extent, extent, -extent, extent),
                          crs=proj)
        return ax, ccrs
