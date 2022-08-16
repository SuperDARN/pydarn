# Copyright (C) 2021 SuperDARN Canada, University of Saskatchewan
# Author: Daniel Billett
#
# Modifications:
# 2022-03-11 MTS added enums for projection function calls
# 2022-03-22 MTS removed coastline call and added grid lines to cartopy plotting
# 2022-05-20 CJM added options to plot coastlines
# 2022-06-13 Elliott Day don't create new ax if ax passed in to Projs
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
import aacgmv2
import enum
import matplotlib.pyplot as plt
import numpy as np
from packaging import version

from pydarn import Hemisphere, plot_exceptions
try:
    import cartopy
    # from cartopy.mpl import geoaxes
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    cartopyInstalled = True
    if version.parse(cartopy.__version__) < version.parse("0.19"):
        cartopyVersion = False
    else:
        cartopyVersion = True
except Exception:
    cartopyInstalled = False


def convert_geo_coastline_to_mag(geom, date, alt: float = 0.0):
    '''
    Takes the geometry object of coastlines and converts
    the coordinates into AACGM_MLT for convection maps only
    Only required usage is for cartopys NaturalEarthFeature
    at 110m resolution only
    Parameters
    ----------
    geom: Shapely Geometry object
        A list/collection of geometry objects
    date: datetime object
        Date of required plot
    alt: float
        Altitude in km
        Default 0 (sea level) for coastlines
    '''
    # Iterate over the coordinates and convert to MLT
    def convert_to_mag(coords, date, alt):
        for glon, glat in geom.coords:
            [mlat, lon_mag, _] = \
                aacgmv2.convert_latlon_arr(glat, glon, alt,
                                           date, method_code='G2A')
            # Shift to MLT
            shifted_mlts = lon_mag[0] - \
                (aacgmv2.convert_mlt(lon_mag[0], date) * 15)
            shifted_lons = lon_mag - shifted_mlts
            mlon = np.radians(shifted_lons)
            yield (mlon.item(), mlat.item())
    # Return geometry object
    return type(geom)(list(convert_to_mag(geom.coords, date, alt)))


def axis_polar(date, ax: object = None, lowlat: int = 30,
               hemisphere: Hemisphere = Hemisphere.North,
               grid_lines: bool = True, coastline: bool = False,
               **kwargs):

    """
    Plots a radar's Field Of View (FOV) fan plot for the given data and
    scan number

    Parameters
    -----------
        ax: matplotlib.pyplot axis
            Pre-defined axis object to pass in, must be
            polar projection
            Default: Generates a polar projection for the user
            with MLT/latitude labels
        lowlat: int
            Lower AACGM latitude boundary for the polar plot
            Default: 30
        hemiphere: enum
            Hemisphere of polar projection. Can be Hemisphere.North or
            Hemisphere.South for northern and southern hemispheres,
            respectively
            Default: Hemisphere.North
        grid_lines: bool
            required for axis_geological
    """

    if ax is None:
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

    if coastline is True:
        if cartopyInstalled is False:
            raise plot_exceptions.CartopyMissingError()
        if cartopyVersion is False:
            raise plot_exceptions.CartopyVersionError(cartopy.__version__)
        # Read in the geometry object of the coastlines
        cc = cfeature.NaturalEarthFeature('physical', 'coastline', '110m',
                                          color='k', zorder=2.0)
        # Convert geometry object coordinates to MLT
        geom_mag = []
        for geom in cc.geometries():
            geom_mag.append(convert_geo_coastline_to_mag(geom, date))
        cc_mag = cfeature.ShapelyFeature(geom_mag, ccrs.PlateCarree(),
                                         color='k', zorder=2.0)
        # Plot each geometry object
        for geom in cc_mag.geometries():
            plt.plot(*geom.coords.xy, color='k', linewidth=0.5, zorder=2.0)
    return ax, None


def axis_geological(date, ax: object = None,
                    hemisphere: Hemisphere = Hemisphere.North,
                    lowlat: int = 30, grid_lines: bool = True,
                    coastline: bool = False, **kwargs):
    """
    Plots a radar's Field Of View (FOV) fan plot for the given data and
    scan number

    Parameters
    -----------
        ax: matplotlib.pyplot axis
            Pre-defined axis object to pass in, must be
            geological projection
            Default: Generates a geographical projection for the user
            with geographic latitude/longitude labels
        lowlat: int
            Lower geographic latitude boundary for the geographic plot
            Default: 30
        hemiphere: enum
            Hemisphere of geographic projection. Can be Hemisphere.North or
            Hemisphere.South for northern and southern hemispheres,
            respectively
            Default: Hemisphere.North
        grid_lines: bool
            add latitude/longtidue lines with labels to the plot
            Default: True
    """
    if cartopyInstalled is False:
        raise plot_exceptions.CartopyMissingError()
    if cartopyVersion is False:
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
        lowlat = -abs(lowlat)
    # handle none types or wrongly built axes
    proj = ccrs.Orthographic(noon, pole_lat)

    if ax is None:
        ax = plt.subplot(111, projection=proj, aspect='auto')
        if grid_lines:
            ax.gridlines(draw_labels=True)

        extent = abs(proj.transform_point(noon, lowlat, ccrs.PlateCarree())[1])
        ax.set_extent(extents=(-extent, extent, -extent, extent), crs=proj)

    if coastline is True:
        ax.coastlines()
    return ax, ccrs


class Projs(enum.Enum):
    """
    class of projections that pydarn can do

    Enumerators
    ------------
    POLAR: axes_polar
    GEO: axes_geological
    """
    POLAR = (axis_polar, )
    GEO = (axis_geological, )

    # Need this to make the functions callable
    def __call__(self, *args, **kwargs):
        return self.value[0](*args, **kwargs)
