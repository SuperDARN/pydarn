# Copyright (C) 2021 SuperDARN Canada, University of Saskatchewan
# Author: Daniel Billett
#
# Modifications:
# 2022-03-11 MTS added enums for projection function calls
# 2022-03-22 MTS removed coastline call and added grid lines to cartopy
#                plotting
# 2022-05-20 CJM added options to plot coastlines
# 2022-06-13 Elliott Day don't create new ax if ax passed in to Projs
# 2023-02-22 CJM added options for nightshade
# 2023-08-11 RR added crude check for unmodified axes, handle both hemispheres
# 2024-05-15 CJM refactored geographic axes to add plot zoom and center, 
#            and added the geomagnetic version to do the same
# 2024-07-10 CJM removed cartopy logic to allow full dependency
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
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.feature.nightshade import Nightshade
import enum
import matplotlib.pyplot as plt
from matplotlib import axes
import matplotlib.ticker as mticker
import numpy as np

from pydarn import (Hemisphere, Re, nightshade_warning)


def convert_geo_coastline_to_mag(geom, date, alt: float = 0.0, mag_lon: bool = False):
    """
    Takes the geometry object of coastlines and converts
    the coordinates into AACGM_MLT
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
    mag_lon: bool
        Set true to return magnetic longitude, not MLT
    """
    [mlats, lon_mag, _] = \
        aacgmv2.convert_latlon_arr(geom.coords.xy[1], geom.coords.xy[0], alt,
                                       date, method_code='G2A')

    # Finds the first not nan value to calculate the mlt shift
    # Substitutes NaN if not found which results in no data to plot
    # aacgmv2 will return NaNs as there are some lat/lon combinations that
    # do not correspond to a geomagnetic position.
    notnan_lon = next((x for x in lon_mag if x == x), float('NaN'))

    # Shift to MLT
    shifted_mlts = notnan_lon - \
                    (aacgmv2.convert_mlt(notnan_lon, date) * 15)
    shifted_lons = lon_mag - shifted_mlts

    if mag_lon:
        mlons = shifted_lons
    else:
        mlons = np.radians(shifted_lons)
    # Return geometry object
    return type(geom)(list(zip(mlons, mlats)))


def axis_geomagnetic(date, ax: axes.Axes = None, lowlat: int = 30,
                    hemisphere: Hemisphere = Hemisphere.North,
                    coastline: bool = False, cartopy_scale: str = '110m',
                    coastline_color: str = 'k',
                    coastline_linewidth: float = 0.5,
                    nightshade: int = 0, grid_lines: bool = True,
                    plot_center: list = None,
                    plot_extent: list = None, **kwargs):
    """
    Sets up the cartopy orthographic plot axis object, for use in
    various other functions. This plot assumes you are giving geoMAGNETIC
    values for plotting, so extra additional cartopy functions such as
    coastlines do not work in this context, you must convert to geomagnetic.
    
    Parameters
    ----------
        date: datetime object
            Date of required plot
        ax: matplotlib.axes.Axes
            Pre-defined axis object to pass in, must be
            geological projection
            Default: Generates a geographical projection for the user
            with geographic latitude/longitude labels
        lowlat: int
            Lower geographic latitude boundary for the geographic plot
            Default: 30
        hemisphere: enum
            Hemisphere of geographic projection. Can be Hemisphere.North or
            Hemisphere.South for northern and southern hemispheres,
            respectively
            Default: Hemisphere.North
        grid_lines: bool
            add latitude/longtitude lines with labels to the plot
            Default: True
        coastline: bool
            Set to true to overlay coastlines with cartopy
        nightshade: int
            Altitude above surface for calculating regions shadowed from Sun.
        plot_center: list [float, float]
            Longitude and Latitude of the desired center of the plot
            Plot will still plot even if data is on the other side of the Earth
            Remember to include negative latitude for Southern Hemisphere
            Setting this option will change the rotation and 12 MLT may no
            longer be at the bottom of the plot
            Default: None
            Example: [-90, 60] will show the Earth centered on Canada
        plot_extent: list [float, float]
            Plotting extent in terms of a percentage of Earth shown in
            the x and y plotting field 
            Default: None
            Example: [30, 50] shows a plot centered on the pole or specified
                     plot_center coord that shows 30% of the Earth in x and 
                     50% of the Earth in y. See tutorials for plotted example.
    """
    if plot_center is None:
        # If no center for plotting is given, default to pole
        if hemisphere == Hemisphere.North:
            pole_lat = 90
            # Keep 0 MLT at the bottom of plot by default
            lon = 0
            lat = abs(lowlat)
        else:
            pole_lat = -90
            # Keep 0 MLT at the bottom of plot by default
            lon = 180
            lat = -abs(lowlat)
        if ax is None:
            proj = ccrs.Orthographic(lon, pole_lat)
            ax = plt.axes(projection=proj)
            if plot_extent is not None and len(plot_extent) == 2:
                # Padding in % of Earth radius
                padx = (plot_extent[0] / 100) * Re*1000
                pady = (plot_extent[1] / 100) * Re*1000
                ax.set_extent(extents=(-padx, padx, -pady, pady), crs=proj)
            else:
                extent = abs(proj.transform_point(lon, lat, ccrs.PlateCarree())[1])
                ax.set_extent(extents=(-extent, extent, -extent, extent), crs=proj)

    else:
        # If the center of the plot is given- shift it around
        lon = plot_center[0]
        lat = plot_center[1]
        if ax is None:
            proj = ccrs.Orthographic(lon, lat)
            ax = plt.axes(projection=proj)
            if plot_extent is not None and len(plot_extent) == 2:
                # Padding in % of Earth radius
                padx = (plot_extent[0] / 100) * Re*1000
                pady = (plot_extent[1] / 100) * Re*1000
                ax.set_extent(extents=(-padx, padx, -pady, pady), crs=proj)
            else:
                # If size is not set or set incorrectly, show  whole
                # hemisphere centered on plot_center
                ax.set_global()

    def mlt_ticklabels(x, pos):
        ''' function for converting mlon to MLT for sole use in tick labels
            for a FuncFormatter operation
        '''
        # Calculate MLT from the mlon values (already shifted)
        MLT = aacgmv2.convert_mlt(x, date)
        # Undo the original shift done to the MLT values to get back to 0-23
        unshiftedMLT = MLT + shift
        # Make sure it is cyclical from 0-24
        if unshiftedMLT < 0:
            unshiftedMLT = unshiftedMLT + 24
        elif unshiftedMLT >= 24:
            unshiftedMLT = unshiftedMLT - 24
        return str(int(np.round(unshiftedMLT))) + ' MLT'

    if grid_lines:
        # Mag Lon gridlines
        gl = ax.gridlines(draw_labels=True)
        # Positions of gridl ines required in MLT
        MLT = [0, 3, 6, 9, 12, 15, 18, 21]
        # Shift MLT to plotting position
        MLT_gridlines = MLT - (MLT[0] - aacgmv2.convert_mlt(MLT[0], date))
        shift = MLT[0] - aacgmv2.convert_mlt(MLT[0], date)
        # Convert shifted MLT to mlon
        mlon_gridlines = aacgmv2.convert_mlt(MLT_gridlines, date, m2a=True)
        # Put grid lines on the MLT positions
        gl.xlocator = mticker.FixedLocator(mlon_gridlines)
        # format the labels to show MLT values
        gl.xformatter = plt.FuncFormatter(mlt_ticklabels)

    if coastline:
        # Read in the geometry object of the coastlines
        cc = cfeature.NaturalEarthFeature('physical', 'coastline',
                                          cartopy_scale, color='k',
                                          zorder=2.0)
        # Convert geometry object coordinates to MLT
        geom_mag = []
        for geom in cc.geometries():
            if geom.__class__.__name__ == 'MultiLineString':
                for g in geom.geoms:
                    geom_mag.append(convert_geo_coastline_to_mag(g, date, mag_lon=True))
            else:
                geom_mag.append(convert_geo_coastline_to_mag(geom, date, mag_lon=True))
        cc_mag = cfeature.ShapelyFeature(geom_mag, ccrs.Geodetic(),
                                         color='k', zorder=2.0)

        # Plot each geometry object
        for geom in cc_mag.geometries():
            plt.plot(*geom.coords.xy, color=coastline_color,
                     linewidth=coastline_linewidth, zorder=2.0,
                     transform = ccrs.Geodetic())

    if nightshade:
        nightshade_warning()

    return ax, ccrs


def axis_geomagnetic_polar(date, ax: axes.Axes = None, lowlat: int = 30,
                    hemisphere: Hemisphere = Hemisphere.North,
                    coastline: bool = False, cartopy_scale: str = '110m',
                    coastline_color: str = 'k',
                    coastline_linewidth: float = 0.5,
                    nightshade: int = 0, **kwargs):
    """
    Sets up the polar plot matplotlib axis object, for use in
    various other functions. Magnetic latitude - magnetic local
    time projection.

    This projection is defunct now MAG exists, however is kept available for
    compatibility and non-cartopy options. 

    Parameters
    -----------
        date: datetime object
            Date of required plot. Only required if using coastlines
            (for AACGM conversion)
        ax: matplotlib.axes.Axes
            Pre-defined axis object to pass in, must be
            polar projection
            Default: Generates a polar projection for the user
            with MLT/latitude labels
        lowlat: int
            Lower AACGM latitude boundary for the polar plot
            Default: 30
        hemisphere: enum
            Hemisphere of polar projection. Can be Hemisphere.North or
            Hemisphere. South for northern and southern hemispheres,
            respectively
            Default: Hemisphere.North
        coastline: bool
            Set to true to overlay coastlines with cartopy. Requires
            date.
        nightshade: int
            Altitude above surface for calculating regions shadowed from Sun.
            Not supported for this projection.
        cartopy_scale: str
            string corresponding with the scale to plot the coastlines at
            options: '110m', '50m', '10m'
        coastline_color: str
            color of the coastline outline
        coastline_linewidth: float
            linewidth of the coastline feature
            default 0.5
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
    else:
        if ax.get_ylim() == (0.0, 1.0):
            # Set upper and lower latitude limits (pole and lowlat)
            if hemisphere == Hemisphere.North:
                ax.set_ylim(90, lowlat)
                ax.set_yticks(np.arange(lowlat, 90, 10))
            else:
                # If hemisphere is South, lowlat must be negative
                ax.set_ylim(-90, -abs(lowlat))
                ax.set_yticks(np.arange(-abs(lowlat), -90, -10))

    if coastline:
        # Read in the geometry object of the coastlines
        cc = cfeature.NaturalEarthFeature('physical', 'coastline',
                                          cartopy_scale, color='k',
                                          zorder=2.0)
        # Convert geometry object coordinates to MLT
        geom_mag = []
        for geom in cc.geometries():
            if geom.__class__.__name__ == 'MultiLineString':
                for g in geom.geoms:
                    geom_mag.append(convert_geo_coastline_to_mag(g, date))
            else:
                geom_mag.append(convert_geo_coastline_to_mag(geom, date))
        cc_mag = cfeature.ShapelyFeature(geom_mag, ccrs.PlateCarree(),
                                         color='k', zorder=2.0)
        # Plot each geometry object
        for geom in cc_mag.geometries():
            plt.plot(*geom.coords.xy, color=coastline_color,
                     linewidth=coastline_linewidth, zorder=2.0)

    if nightshade:
        nightshade_warning()

    return ax, None


def axis_geographic(date, ax: axes.Axes = None,
                    hemisphere: Hemisphere = Hemisphere.North,
                    lowlat: int = 30, grid_lines: bool = True,
                    coastline: bool = False, nightshade: int = 0,
                    cartopy_scale: str = '110m', coastline_color: str = 'k',
                    coastline_linewidth: float = 0.5,
                    plot_center: list = None,
                    plot_extent: list = None, **kwargs):

    """

    Sets up the cartopy orthographic plot axis object, for use in
    various other functions. Geographic projection.

    Parameters
    -----------
        date: datetime object
            Date of required plot
        ax: matplotlib.axes.Axes
            Pre-defined axis object to pass in, must be
            geological projection
            Default: Generates a geographical projection for the user
            with geographic latitude/longitude labels
        lowlat: int
            Lower geographic latitude boundary for the geographic plot
            Default: 30
        hemisphere: enum
            Hemisphere of geographic projection. Can be Hemisphere.North or
            Hemisphere.South for northern and southern hemispheres,
            respectively
            Default: Hemisphere.North
        grid_lines: bool
            add latitude/longtidue lines with labels to the plot
            Default: True
        coastline: bool
            Set to true to overlay coastlines with cartopy
        nightshade: int
            Altitude above surface for calculating regions shadowed from Sun.

        cartopy_scale: str
            string corresponding with the scale to plot the coastlines at
            options: '110m', '50m', '10m'
        coastline_color: str
            color of the coastline outline
        coastline_linewidth: float
            linewidth of the coastline feature
            default 0.5
        plot_center: list [float, float]
            Longitude and Latitude of the desired center of the plot
            Plot will still plot if data is on the other side of the Earth
            Remember to include negative latitude for Southern Hemisphere
            Default: None
            Example: [-90, 60] will show the Earth centered on Canada
        plot_extent: list [float, float]
            Plotting extent in terms of a percentage of Earth shown in
            the x and y plotting field 
            Default: None
            Example: [30, 50] shows a plot centered on the pole or specified
                     plot_center coord that shows 30% of the Earth in x and 
                     50% of the Earth in y. See tutorials for plotted example.
    """
    if plot_center is None:
        # If no center for plotting is given, default to pole and rotate for 0
        # degrees longitude
        if hemisphere == Hemisphere.North:
            pole_lat = 90
            lon = 0
            lat = abs(lowlat)
        else:
            pole_lat = -90
            lon = 0
            lat = -abs(lowlat)
        if ax is None:
            proj = ccrs.Orthographic(lon, pole_lat)
            ax = plt.axes(projection=proj)
            if plot_extent is not None and len(plot_extent) == 2:
                # Padding in % of Earth radius
                padx = (plot_extent[0] / 100) * Re*1000
                pady = (plot_extent[1] / 100) * Re*1000
                ax.set_extent(extents=(-padx, padx, -pady, pady), crs=proj)
            else:
                extent = abs(proj.transform_point(lon, lat, ccrs.PlateCarree())[1])
                ax.set_extent(extents=(-extent, extent, -extent, extent), crs=proj)
    else:
        # If the center of the plot is given- shift it around
        lon = plot_center[0]
        lat = plot_center[1]
        if ax is None:
            proj = ccrs.Orthographic(lon, lat)
            ax = plt.axes(projection=proj)
            if plot_extent is not None and len(plot_extent) == 2:
                # Padding in % of Earth radius
                padx = (plot_extent[0] / 100) * Re*1000
                pady = (plot_extent[1] / 100) * Re*1000
                ax.set_extent(extents=(-padx, padx, -pady, pady), crs=proj)
            else:
                # If size is not set or set incorrectly, show  whole
                # hemisphere centered on plot_center
                ax.set_global()

    if grid_lines:
        ax.gridlines(draw_labels=True)

    if coastline:
        ax.coastlines(resolution=cartopy_scale, color=coastline_color,
                      linewidth=coastline_linewidth)

    if nightshade:
        refraction_value = -np.degrees(np.arccos(Re / (Re + nightshade)))
        ns = Nightshade(date, refraction=refraction_value, alpha=0.1)
        ax.add_feature(ns)

    return ax, ccrs


class Projs(enum.Enum):
    """
    class of projections that pydarn can do

    Enumerators
    ------------
    POLAR: axes_polar
    GEO: axes_geological
    """
    POLAR = (axis_geomagnetic_polar, )
    GEO = (axis_geographic, )
    MAG = (axis_geomagnetic, )

    # Need this to make the functions callable
    def __call__(self, *args, **kwargs):
        return self.value[0](*args, **kwargs)
