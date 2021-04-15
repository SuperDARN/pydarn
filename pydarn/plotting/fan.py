# Copyright (C) 2020 SuperDARN Canada, University of Saskatchewan
# Author: Daniel Billett, Marina Schmidt
#
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
# Modifications:
#

"""
Fan plots, mapped to AACGM coordinates in a polar format
"""

import datetime as dt
import matplotlib.pyplot as plt
import numpy as np

from matplotlib import ticker, cm, colors
from typing import List, Union

# Third party libraries
import aacgmv2
from pydarn import (PyDARNColormaps, build_scan, radar_fov, citing_warning,
                    plot_exceptions)
from pydarn.utils.plotting import time2datetime

# handle cartopy ad-hoc
try:
    from cartopy.mpl import geoaxes
    import cartopy.crs as ccrs
    cartopyInstalled = True
except Exception:
    cartopyInstalled = False


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
    def plot_fan(cls, dmap_data: List[dict], ax=None,
                 scan_index: Union[int, dt.datetime] = 1,
                 ranges: List = [0, 75], boundary: bool = True,
                 alpha: int = 0.5, parameter: str = 'v',
                 lowlat: int = 30, cmap: str = None,
                 groundscatter: bool = False,
                 zmin: int = None, zmax: int = None,
                 colorbar: bool = True,
                 colorbar_label: str = '', polar=True):
        """
        Plots a radar's Field Of View (FOV) fan plot for the given data and
        scan number

        Parameters
        -----------
            dmap_data: List[dict]
                Named list of dictionaries obtained from SDarn_read
            ax: matplotlib.pyplot axis
                Pre-defined axis object to pass in, must currently be
                polar projection
                Default: Generates a polar projection for the user
                with MLT/latitude labels

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
            alpha: int
                alpha controls the transparency of
                the fov color
                Default: 0.5
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
            polar: bool
                By default, draw a polar plot in aacgm coordinates
                Setting this to False will generate a plot with cartopy
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

        See Also
        --------
            plot_fov
        """

        # Get scan numbers for each record
        beam_scan = build_scan(dmap_data)

        # Check if scan_index is a datetime, then determine which
        # integer scan to fetch
        if type(scan_index) == dt.datetime:
            # loop through dmap_data records, dump a datetime
            # list where scans start
            scan_datetimes = np.array([dt.datetime(*[record[time_component]
                                                     for time_component in
                                                     ['time.yr', 'time.mo',
                                                      'time.dy', 'time.hr',
                                                      'time.mt', 'time.sc']])
                                       for record in dmap_data
                                       if record['scan'] == 1])
            # find corresponding scan_index
            matching_scan_index = np.argwhere(scan_datetimes ==
                                              scan_index)[..., 0] + 1
            # handle datetimes out of bounds
            if len(matching_scan_index) != 1:
                raise plot_exceptions.IncorrectDateError(scan_datetimes[0],
                                                         scan_index)
            else:
                scan_index = matching_scan_index

        # Locate scan in loaded data
        plot_beams = np.where(beam_scan == scan_index)

        # Time for coordinate conversion
        dtime = time2datetime(dmap_data[plot_beams[0][0]])

        # Get radar beam/gate locations ('aacgm' for polar, 'geo' otherwise)
        if polar:
            beam_corners_aacgm_lats, beam_corners_aacgm_lons = radar_fov(
                stid=dmap_data[0]['stid'], coords='aacgm', date=dtime)
        else:
            beam_corners_aacgm_lats, beam_corners_aacgm_lons = radar_fov(
                stid=dmap_data[0]['stid'], coords='geo', date=dtime)

        # Where in the world are we
        if np.all(beam_corners_aacgm_lats > 0):
            northern_hemisphere = True
        else:
            northern_hemisphere = False
        pole_lat = 90 if northern_hemisphere else -90

        # How many beams and gates do we need
        fan_shape = beam_corners_aacgm_lons.shape

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

        norm = colors.Normalize
        norm = norm(zmin, zmax)

        # Get range-gate data and groundscatter array for given scan
        scan = np.zeros((fan_shape[0] - 1, fan_shape[1] - 1))
        grndsct = np.zeros((fan_shape[0] - 1, fan_shape[1] - 1))
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

        # PLOTTING STUFF ################################################
        # (Maybe this gets put in a separate function call down the road)

        # convert longitudes to mlt shifted radians if using a polar projection
        if polar:
            # determine mlt shift by calling aacgmv2
            mltshift = beam_corners_aacgm_lons[0, 0] - (
                aacgmv2.convert_mlt(beam_corners_aacgm_lons[0, 0], dtime) * 15)
            # implement the lon shift
            beam_corners_mlts = beam_corners_aacgm_lons - mltshift
            # make it something the polar plots can handle
            # by converting to radians
            beam_corners_aacgm_lons = np.radians(beam_corners_mlts)
            # handle creating a new plot axes if neccesary
            if ax is None:
                ax = plt.subplot(111, polar=True)
                ax.set_ylim(pole_lat, lowlat)
                # fix up the rest of the axes details
                ax.set_xticks(np.arange(0, np.radians(360), np.radians(45)))
                ax.set_xticklabels(['00', '', '06', '', '12', '', '18', ''])
                ax.set_theta_zero_location("S")
            # a single* call to pcolormesh to handle all the
            # range gates in the scan
            ax.pcolormesh(beam_corners_aacgm_lons,
                          beam_corners_aacgm_lats,
                          np.ma.masked_array(scan, ~scan.astype(bool)),
                          norm=norm, cmap=cmap)
            # plot the groundscatter as grey fill
            if groundscatter:
                ax.pcolormesh(beam_corners_aacgm_lons,
                              beam_corners_aacgm_lats,
                              np.ma.masked_array(grndsct,
                                                 ~grndsct.astype(bool)),
                              norm=norm, cmap='Greys')
            # *There exists a bug in matplotlib pcolormesh when plotting in
            # polar projections that gets rid of the rgrid. Replot them here:
            for lat in range(pole_lat, lowlat, -10
                             if northern_hemisphere else 10):
                ax.plot(np.linspace(0, np.radians(360), 360),
                        [lat] * 360, 'grey', alpha=0.6)
            for lon in range(0, 360, 45):
                ax.plot([np.radians(lon)] * 2,
                        [pole_lat, lowlat], 'grey', alpha=0.6)

        # the alternative is to plot using catropy
        else:
            # first, check if cartopy is installed:
            if not cartopyInstalled:
                raise plot_exceptions.CartopyMissingError()
            # no need to shift any coords, let cartopy do that
            # however, we do need to figure out
            # how much to rotate the projection
            deg_from_midnight = (dtime.hour + dtime.minute / 60) / 24 * 360
            if northern_hemisphere:
                noon = -deg_from_midnight
            else:
                noon = 360 - deg_from_midnight
            # handle none types or wrongly built axes
            if type(ax) != geoaxes.GeoAxesSubplot:
                proj = ccrs.Orthographic(noon, pole_lat)
                ax = plt.subplot(111, projection=proj, aspect='auto')
                ax.coastlines()
                ax.gridlines(ylocs=np.arange(pole_lat, 0, -5
                                             if northern_hemisphere else 5))
                ax.pcolormesh(beam_corners_aacgm_lons,
                              beam_corners_aacgm_lats,
                              np.ma.masked_array(scan, ~scan.astype(bool)),
                              norm=norm, cmap=cmap,
                              transform=ccrs.PlateCarree())
                if groundscatter:
                    ax.pcolormesh(beam_corners_aacgm_lons,
                                  beam_corners_aacgm_lats,
                                  np.ma.masked_array(grndsct,
                                                     ~grndsct.astype(bool)),
                                  norm=norm, cmap='Greys',
                                  transform=ccrs.PlateCarree())

                # For some reason, cartopy won't allow extents
                # much greater than this
                # - there should probably be an option to allow autscaling
                # - perhaps this is a projection issue?
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

        if boundary:
            # create flat arrays of the lat/lon points for the FOV
            # (bottom, left, -top, -right)
            boundary_lons = np.concatenate(
                (beam_corners_aacgm_lons[ranges[0], :],
                 beam_corners_aacgm_lons[ranges[0]:ranges[1], -1],
                 beam_corners_aacgm_lons[ranges[1], ::-1],
                 beam_corners_aacgm_lons[ranges[1]:ranges[0]:-1, 0],
                 [beam_corners_aacgm_lons[0, 0]]))
            boundary_lats = np.concatenate(
                (beam_corners_aacgm_lats[ranges[0], :],
                 beam_corners_aacgm_lats[ranges[0]:ranges[1], -1],
                 beam_corners_aacgm_lats[ranges[1], ::-1],
                 beam_corners_aacgm_lats[ranges[1]:ranges[0]:-1, 0],
                 [beam_corners_aacgm_lats[0, 0]]))
            # plot the boundary
            ax.plot(boundary_lons, boundary_lats, 'k', linewidth=0.5)

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

        citing_warning()
        return beam_corners_aacgm_lats, beam_corners_aacgm_lons, scan, grndsct

    @classmethod
    def plot_fov(cls, stid: str, dtime: dt.datetime, ax=None,
                 lowlat: int = 30, ranges: List = [0, 75],
                 boundary: bool = True, fov_color: str = None,
                 alpha: int = 0.5):
        """
        plots only the field of view (FOV) for a given radar station ID (stid)

        Parameters
        -----------
            stid: str
                Radar station ID
            ax: matplotlib.pyplot axis
                Pre-defined axis object to pass in, must currently be
                polar projection
                Default: Generates a polar projection for the user
                with MLT/latitude labels
            dtime: datetime datetime object
                sets the datetime used to find the coordinates of the
                FOV
            lowlat: int
                Lower AACGM latitude boundary for the polar plot
                Default: 50
            ranges: list
                Set to a two element list of the lower and upper ranges to plot
                Default: [0,75]
            boundary: bool
                Set to false to not plot the outline of the FOV
                Default: True
            fov_color: str
                fov color to fill in the boundary
                default: None
            alpha: int
                alpha controls the transparency of
                the fov color
                Default: 0.5

        Returns
        -------
            beam_corners_aacgm_lats - list of beam corners AACGM latitudes
            beam_corners_aacgm_lons - list of beam corners AACGM longitudes
            thetas - theta polar coordinates
            rs - radius polar coordinates
        """
        # Get radar beam/gate locations
        beam_corners_aacgm_lats, beam_corners_aacgm_lons = \
            radar_fov(stid, coords='aacgm', date=dtime)
        fan_shape = beam_corners_aacgm_lons.shape

        # Work out shift due in MLT
        beam_corners_mlts = np.zeros((fan_shape[0], fan_shape[1]))
        mltshift = beam_corners_aacgm_lons[0, 0] - \
            (aacgmv2.convert_mlt(beam_corners_aacgm_lons[0, 0], dtime) * 15)
        beam_corners_mlts = beam_corners_aacgm_lons - mltshift

        # Hold the beam positions
        thetas = np.radians(beam_corners_mlts)
        rs = beam_corners_aacgm_lats

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
            ax.set_xticks([0, np.radians(45), np.radians(90), np.radians(135),
                           np.radians(180), np.radians(225), np.radians(270),
                           np.radians(315)])
            ax.set_xticklabels(['00', '', '06', '', '12', '', '18', ''])
            ax.set_theta_zero_location("S")

        if boundary:
            # left boundary line
            plt.polar(thetas[0:ranges[1], 0], rs[0:ranges[1], 0],
                      color='black', linewidth=0.5)
            # top radar arc
            plt.polar(thetas[ranges[1] - 1, 0:thetas.shape[1]],
                      rs[ranges[1] - 1, 0:thetas.shape[1]],
                      color='black', linewidth=0.5)
            # right boundary line
            plt.polar(thetas[0:ranges[1], thetas.shape[1] - 1],
                      rs[0:ranges[1], thetas.shape[1] - 1],
                      color='black', linewidth=0.5)
            # bottom arc
            plt.polar(thetas[0, 0:thetas.shape[1] - 1],
                      rs[0, 0:thetas.shape[1] - 1], color='black',
                      linewidth=0.5)

        if fov_color is not None:
            theta = thetas[0:ranges[1], 0]
            theta = np.append(theta, thetas[ranges[1]-1, 0:thetas.shape[1]-1])
            theta = np.append(theta, np.flip(thetas[0:ranges[1],
                                                    thetas.shape[1]-2]))
            theta = np.append(theta, np.flip(thetas[0, 0:thetas.shape[1]-2]))

            r = rs[0:ranges[1], 0]
            r = np.append(r, rs[ranges[1]-1, 0:thetas.shape[1]-1])
            r = np.append(r, np.flip(rs[0:ranges[1], thetas.shape[1]-2]))
            r = np.append(r, np.flip(rs[0, 0:thetas.shape[1]-2]))
            ax.fill(theta, r, color=fov_color, alpha=alpha)
        citing_warning()
        return beam_corners_aacgm_lats, beam_corners_aacgm_lons, thetas, rs, ax
