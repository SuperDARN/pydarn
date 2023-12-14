# Copyright (C) 2020 SuperDARN Canada, University of Saskatchewan
# Author: Daniel Billett, Marina Schmidt
#
# Modifications:
# 2021-05-07: CJM - Included radar position and labels in plotting
# 2021-04-01 Shane Coyle added pcolormesh to the code
# 2021-05-19 Marina Schmidt - Added scan index with datetimes
# 2021-09-15 Marina Schmidt - removed fov file options
# 2021-09-09: CJM - Included a channel option for plot_fan
# 2021-09-08: CJM - Included individual gate and beam boundary plotting for FOV
# 2021-11-22: MTS - pass in axes object to plot_fov
# 2021-11-18: MTS - Added Projectsion class for cartopy use
# 2021-02-02: CJM - Included rsep and frang options in plot_fov
#                 - Re-arranged logic for ranges option
#                 - Indexing fixed for give lower ranges that are non-zero
# 2022-03-10: MTS - switched coords involving range estimations to
#                   RangeEstimation
#                 - Removed GEO_COASTALINE, replaced with GEO on projections
#                 - reduced some parameters inputs to kwargs
# 2022-03-22: CJM - Set cmap bad values to transparent
# 2022-03-23: MTS - added the NotImplementedError for AACGM and GEO projection
#                   as this has yet to be figured out
# 2023-02-06: CJM - Added option to plot single beams in a scan or FOV diagram
# 2023-03-01: CJM - Added ball and stick plotting options (merged later in year)
# 2023-08-16: CJM - Corrected for winding order in geo plots
# 2023-06-28: CJM - Refactored return values
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

from matplotlib import ticker, cm, colors, axes
from typing import List, Union

# Third party libraries
import aacgmv2

from pydarn import (PyDARNColormaps, build_scan, partial_record_warning,
                    time2datetime, plot_exceptions, SuperDARNRadars,
                    calculate_azimuth, Projs, Coords, Hemisphere)


class Fan:
    """
    'Fan', or 'Field-of-view' plots for SuperDARN FITACF data
    This class inherits from matplotlib to generate the figures
    Methods
    -------
    plot_fan
    plot_fov
    plot_radar_position
    plot_radar_label
    """

    def __str__(self):
        return "This class is static class that provides"\
                " the following methods: \n"\
                "   - plot_fan()\n"\
                "   - plot_fov()\n"

    @classmethod
    def plot_fan(cls, dmap_data: List[dict], ax=None, ranges=None,
                 scan_index: Union[int, dt.datetime] = 1,
                 parameter: str = 'v', cmap: str = None,
                 groundscatter: bool = False, zmin: int = None,
                 zmax: int = None, colorbar: bool = True,
                 colorbar_label: str = '', title: bool = True,
                 boundary: bool = True, projs: Projs = Projs.POLAR,
                 coords: Coords = Coords.AACGM_MLT,
                 channel: int = 'all', ball_and_stick: bool = False,
                 len_factor: float = 300, beam: int = None, **kwargs):
        """
        Plots a radar's Field Of View (FOV) fan plot for the given data and
        scan number

        Parameters
        -----------
            dmap_data: List[dict]
                Named list of dictionaries obtained from SDarn_read
            ax: axes.Axes
                Pre-defined axis object to pass in, must currently be
                polar projection
                Default: Generates a polar projection for the user
                with MLT/latitude labels
            ranges: List[int]
                Range bounds to plot, as [lower_bound, upper_bound].
                Default: Plots all ranges out to max given in hardware file.
            scan_index: int or datetime
                Scan number starting from the first record in file with
                associated channel number or datetime given first record
                to match the index
                Default: 1
            parameter: str
                Key name indicating which parameter to plot.
                Default: v (Velocity). Alternatives: 'p_l', 'w_l', 'elv'
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
            title: bool
                if true then will create a title, else user
                can define it with plt.title
                default: true
            boundary: bool
                if true then plots the FOV boundaries
                default: true
            projs: Enum
                choice of projection for plot
                default: Projs.POLAR (polar projection)
            coords: Enum
                choice of plotting coordinates
                default: Coords.AACGM_MLT (Magnetic Lat and MLT)
            beam : int or None
                integer indicating if the user would like to plot a single beam
            channel : int or str
                integer indicating which channel to plot or 'all' to
                plot all channels
                Default: 'all'
            ball_and_stick : bool
                plot the data as a vector instead of filling a box
                Default: False
            len_factor : float
                control the length of the ball and stick plot stick length
                Default : 300
            kwargs: key = value
                Additional keyword arguments to be used in projection plotting
                and plot_fov for possible keywords, see: projections.axis_polar

        Returns
        -----------
        beam_corners_aacgm_lats
            n_beams x n_gates numpy array of latitudes
            return values dependent on given coords enum
        beam_corners_aacgm_lons
            n_beams x n_gates numpy array of longitudes or MLT
            return values dependent on given coords enum
        scan
            n_beams x n_gates numpy array of the scan data
            (for the selected parameter)
        grndsct
            n_beams x n_gates numpy array of the scan data
            (for the selected parameter)
        See Also
        --------
            plot_fov
        """
        # Remove all data from dmap_data that is not in chosen channel
        if ranges is None:
            ranges = []
        if channel != 'all':
            # Get the first channel used in case of no data in given channel
            opt_channel = dmap_data[0]['channel']
            dmap_data = [rec for rec in dmap_data if rec['channel'] == channel]
            # If no records exist, advise user that the channel is not used
            if not dmap_data:
                raise plot_exceptions.NoChannelError(channel, opt_channel)

        # Get scan numbers for each record
        beam_scan = build_scan(dmap_data)
        scan_time = None
        if isinstance(scan_index, dt.datetime):
            # loop through dmap_data records, dump a datetime
            # list where scans start
            scan_time = scan_index
            scan_index = 0
            found_match = False
            for rec in dmap_data:
                rec_time = time2datetime(rec)
                if abs(rec['scan']) == 1:
                    scan_index += 1
                # Need the abs since you cannot have negative seconds
                diff_time = abs(scan_time - rec_time)
                if diff_time.seconds < 1:
                    found_match = True
                    break
            # handle datetimes out of bounds
            if found_match is False:
                raise plot_exceptions.IncorrectDateError(rec_time,
                                                         scan_time)
        # Locate scan in loaded data
        plot_beams = np.where(beam_scan == scan_index)
        # Time for coordinate conversion
        if not scan_time:
            date = time2datetime(dmap_data[plot_beams[0][0]])
        else:
            date = scan_time

        # Plot FOV outline
        stid = dmap_data[0]['stid']
        if ranges == [] or ranges is None:
            try:
                # If not given, get ranges from data file
                ranges = [0, dmap_data[0]['nrang']]
            except KeyError:
                # Otherwise, default to [0,75]
                ranges = [0, SuperDARNRadars.radars[stid].range_gate_45]

        # Get rsep and frang from data unless not there then take defaults
        # of 180 km for frang and 45 km for rsep as these are most commonly
        # used
        try:
            frang = dmap_data[0]['frang']
        except KeyError:
            frang = 180

        try:
            rsep = dmap_data[0]['rsep']
        except KeyError:
            rsep = 45

        if coords != Coords.GEOGRAPHIC and projs == Projs.GEO:
            raise plot_exceptions.NotImplemented("AACGM coordinates are"
                                                 " not implemented for "
                                                 " geographic projections"
                                                 " right now, if you would"
                                                 " like to see it sooner"
                                                 " please help out at "
                                                 "https://github.com"
                                                 "/SuperDARN/pyDARN")

        beam_corners_lats, beam_corners_lons =\
            coords(stid=dmap_data[0]['stid'], rsep=rsep, frang=frang,
                   gates=ranges, date=date, **kwargs)

        fan_shape = beam_corners_lons.shape
        if ranges[0] < ranges[1] - fan_shape[0]:
            ranges[0] = ranges[1] - fan_shape[0] + 1
        rs = beam_corners_lats
        if projs != Projs.GEO:
            thetas = np.radians(beam_corners_lons)
        else:
            thetas = beam_corners_lons

        # Get range-gate data and groundscatter array for given scan
        # fan_shape has no -1 as when given ranges we want to include the
        # both ends for the ranges given
        scan = np.zeros((fan_shape[0], fan_shape[1]-1))
        grndsct = np.zeros((fan_shape[0], fan_shape[1]-1))
        # Colour table and max value selection depending on parameter plotted
        # Load defaults if none given
        if cmap is None:
            cmap = {'p_l': PyDARNColormaps.PYDARN_PLASMA,
                    'v': PyDARNColormaps.PYDARN_VELOCITY,
                    'w_l': PyDARNColormaps.PYDARN_VIRIDIS,
                    'elv': PyDARNColormaps.PYDARN_INFERNO}
            cmap = cmap[parameter]

        # Set background to transparent - avoids carry over
        # does not interfere with the fov color if chosen
        cmap.set_bad(alpha=0.0)

        # Setting zmin and zmax
        defaultzminmax = {'p_l': [0, 50], 'v': [-200, 200],
                          'w_l': [0, 250], 'elv': [0, 50]}
        if zmin is None:
            zmin = defaultzminmax[parameter][0]
        if zmax is None:
            zmax = defaultzminmax[parameter][1]
        norm = colors.Normalize
        norm = norm(zmin, zmax)

        for i in np.nditer(plot_beams):
            try:
                # get a list of gates where there is data
                slist = dmap_data[i.astype(int)]['slist']
                # get the beam number for the record
                beami = dmap_data[i.astype(int)]['bmnum']

                # Exclude ranges larger than the expected maximum.
                # This is a temporary fix to manage inconsistencies between the
                # fitacf files and the hardware files. The issue will be
                # fully resolved when the `rpos` code is committed.
                good_data = np.where((slist >= ranges[0]) &
                                     (slist < ranges[1]))
                slist = slist[good_data]
                temp_data = dmap_data[i.astype(int)][parameter][good_data]
                temp_ground = dmap_data[i.astype(int)]['gflg'][good_data]

                scan[slist-ranges[0], beami] = temp_data
                grndsct[slist-ranges[0], beami] = temp_ground
            # if there is no slist field this means partial record
            except KeyError:
                partial_record_warning()
                continue

        # Begin plotting by iterating over ranges and beams
        if beam is not None:
            thetas = thetas[0:ranges[1]-ranges[0]+1, beam:beam+2]
            rs = rs[0:ranges[1]-ranges[0]+1, beam:beam+2]
            scan = scan[0:ranges[1]-ranges[0], beam:beam+1]
            grndsct = grndsct[0:ranges[1]-ranges[0], beam:beam+1]
        else:
            thetas = thetas[0:ranges[1]-ranges[0]+1]
            rs = rs[0:ranges[1]-ranges[0]+1]
            scan = scan[0:ranges[1]-ranges[0]]
            grndsct = grndsct[0:ranges[1]-ranges[0]]

        # Set up axes in correct hemisphere
        stid = dmap_data[0]['stid']
        kwargs['hemisphere'] = SuperDARNRadars.radars[stid].hemisphere

        ax, ccrs = projs(date=date, ax=ax, **kwargs)

        if ccrs is None:
            transform = ax.transData

        else:
            transform = ccrs.PlateCarree()

        if not ball_and_stick:
            ax.pcolormesh(thetas, rs,
                          np.ma.masked_array(scan, ~scan.astype(bool)),
                          norm=norm, cmap=cmap, transform=transform,
                          zorder=2)
        else:
            # Get center of each gate instead of edges
            fan_shape = thetas.shape
            t_center = np.empty([fan_shape[0]-1, fan_shape[1]-1])
            r_center = np.empty([fan_shape[0]-1, fan_shape[1]-1])
            for i in range(0, fan_shape[0]-1):
                for j in range(0, fan_shape[1]-1):
                    t_center = (thetas[i, j] + thetas[i+1, j]
                                + thetas[i, j+1] + thetas[i+1, j+1]) / 4
                    r_center = (rs[i, j] + rs[i+1, j]
                                + rs[i, j+1] + rs[i+1, j+1]) / 4
                    if scan[i, j] != 0.0:
                        col = cmap((scan[i, j] - zmin) / (zmax-zmin))
                        # Plot balls!
                        ax.scatter(t_center, r_center, color=col, s=1.0,
                                   transform=transform, zorder=3.0)
                        # Stick only needed for velocity data
                        if parameter == 'v':
                            # Get azimuth in correct coord system
                            if coords != Coords.GEOGRAPHIC:
                                lat = r_center
                                lon = np.degrees(t_center)
                            else:
                                lat = r_center
                                lon = t_center
                            azm = cls.get_gate_azm(lon, lat, stid,
                                                   coords, date)

                            # Make sure each coordinate is in correct
                            # units again
                            if projs != Projs.GEO:
                                thetas_calc = np.radians(lon)
                                rs_calc = lat
                            else:
                                thetas_calc = np.radians(lon)
                                rs_calc = lat

                            hemisphere = SuperDARNRadars.radars[stid]\
                                                        .hemisphere

                            # Find the end point of the stick to plot
                            # Angle to rotate each vector
                            alpha = thetas_calc

                            # Convert to Cartesian
                            start_pos_x = (90 - abs(rs_calc)) \
                                * np.cos(thetas_calc)
                            start_pos_y = (90 - abs(rs_calc)) \
                                * np.sin(thetas_calc)

                            # Results LOS vector in x and y
                            los_x = -scan[i, j] * np.cos(
                                    np.radians(-azm * hemisphere.value))
                            los_y = -scan[i, j] * np.sin(
                                    np.radians(-azm * hemisphere.value))

                            # Rotate vector into same ref frame
                            vec_x = (los_x * np.cos(alpha)) \
                                - (los_y * np.sin(alpha))
                            vec_y = (los_x * np.sin(alpha)) \
                                + (los_y * np.cos(alpha))

                            # New vector end points
                            end_pos_x = start_pos_x\
                                + (vec_x * hemisphere.value / len_factor)
                            end_pos_y = start_pos_y\
                                + (vec_y * hemisphere.value / len_factor)
                            # Convert back to polar for plotting
                            end_rs = 90 - (np.sqrt(end_pos_x**2
                                                   + end_pos_y**2))
                            end_thetas = np.arctan2(end_pos_y, end_pos_x)
                            end_rs = end_rs * hemisphere.value

                            # Convert to degrees for geo plots
                            if projs == Projs.GEO:
                                end_thetas = np.degrees(end_thetas)
                            # Plot sticks!
                            plt.plot([t_center, end_thetas],
                                     [r_center, end_rs],
                                     color=col, zorder=3.0, linewidth=0.5,
                                     transform=transform)

                    # Plot ground scatter balls (no sticks)
                    if groundscatter and grndsct[i, j] != 0.0:
                        ax.scatter(t_center, r_center, c='grey', s=1.0,
                                   transform=transform, zorder=3.0)

        # plot the groundscatter as grey fill
        if groundscatter and not ball_and_stick:
            ax.pcolormesh(thetas, rs,
                          np.ma.masked_array(grndsct,
                                             ~grndsct.astype(bool)),
                          norm=norm, cmap='Greys',
                          transform=transform, zorder=3)
        if ccrs is None:
            azm = np.linspace(0, 2 * np.pi, 100)
            r, th = np.meshgrid(rs, azm)
            ax.plot(azm, r, color='k', ls='none')
            ax.grid(True)

        if boundary:
            cls.plot_fov(stid=dmap_data[0]['stid'], date=date, ax=ax,
                         ccrs=ccrs, coords=coords, projs=projs, rsep=rsep,
                         frang=frang, ranges=ranges, beam=beam, **kwargs)

        # Create color bar if True
        if colorbar is True:
            mappable = cm.ScalarMappable(norm=norm, cmap=cmap)
            locator = ticker.MaxNLocator(symmetric=True, min_n_ticks=3,
                                         integer=True, nbins='auto')
            ticks = locator.tick_values(vmin=zmin, vmax=zmax)

            if zmin == 0:
                cb = ax.figure.colorbar(mappable, ax=ax, extend='max',
                                        ticks=ticks)
            else:
                cb = ax.figure.colorbar(mappable, ax=ax, extend='both',
                                        ticks=ticks)

            if colorbar_label != '':
                cb.set_label(colorbar_label)
        else:
            cb = None
        if title:
            start_time = time2datetime(dmap_data[plot_beams[0][0]])
            end_time = time2datetime(dmap_data[plot_beams[-1][-1]])
            title = cls.__add_title__(start_time, end_time)
            plt.title(title)
        return {'ax': ax,
                'ccrs': ccrs,
                'cm': cmap,
                'cb': cb,
                'fig': plt.gcf(),
                'data': {'beam_corners_lats': beam_corners_lats,
                         'beam_corners_lons': beam_corners_lons,
                         'scan_data': scan,
                         'ground_scatter': grndsct}
                }

  
    @classmethod
    def plot_fov(cls, stid: int, date: dt.datetime,
                 ax=None, ccrs=None, ranges: List = None, boundary: bool = True,
                 rsep: int = 45, frang: int = 180,
                 projs: Projs = Projs.POLAR,
                 coords: Coords = Coords.AACGM_MLT,
                 fov_color: str = None, alpha: int = 0.5,
                 radar_location: bool = True, radar_label: bool = False,
                 line_color: str = 'black',
                 grid: bool = False, beam: int = None,
                 line_alpha: int = 0.5, **kwargs):
        """
        plots only the field of view (FOV) for a given radar station ID (stid)

        Parameters
        -----------
            stid: int
                Radar station ID
            ax: matplotlib.axes.Axes
                Pre-defined axis object to pass in.
            ccrs:
            date: datetime object
                Sets the datetime used to find the coordinates of the FOV
                Default: Current time
            ranges: list
                Set to a two element list of the lower and upper ranges to plot
                If None, the  max will be obtained by SuperDARNRadars
                Default: None
            boundary: bool
                Set to false to not plot the outline of the FOV
                Default: True
            rsep: int
                Separation between range gates, in kilometers.
                Default: 45
            frang: int
                Kilometers to first range.
                Default: 180
            projs: Projs object
                Sets the projection type for the plot
                Default: Projs.POLAR
            coords: Coords object

            grid: bool
                Set to false to not plot the grid of gates in the FOV
                Default: False
            fov_color: str
                fov color to fill in the boundary
                default: None
            line_color: str
                line color of the fov plot
                default: black
            alpha: int
                alpha controls the transparency of
                the fov color
                Default: 0.5
            line_alpha: int
                line_alpha controls the transparency of
                the boundary and grid lines of the fov
                Default: 0.5
            beam : int or None
                integer indicating if the user would like to plot a single beam
            radar_location: bool
                Add a dot where radar is located if True
                Default: False
            radar_label: bool
                Add a label with the radar abbreviation if True
                Default: False
            kwargs: key = value
                Additional keyword arguments to be used in projection plotting
                For possible keywords, see: projections.axis_polar

        Returns
        -------
            beam_corners_aacgm_lats - list of beam corners AACGM latitudes
            beam_corners_aacgm_lons - list of beam corners AACGM longitudes
            beam_corners_lon - theta polar coordinates
            rs - radius polar coordinates
        """
        if ranges == [] or ranges is None:
            ranges = [0, SuperDARNRadars.radars[stid].range_gate_45]

        if not date:
            date = dt.datetime.now()

        # Get radar beam/gate locations
        beam_corners_lats, beam_corners_lons = \
            coords(stid=stid, gates=ranges, rsep=rsep, frang=frang,
                   date=date, **kwargs)

        # If beam selected then reduce lats and lons array
        if beam is not None:
            beam_corners_lats = beam_corners_lats[:, beam:beam+2]
            beam_corners_lons = beam_corners_lons[:, beam:beam+2]

        if projs == Projs.POLAR:
            beam_corners_lons = np.radians(beam_corners_lons)

        # This section corrects winding order for cartopy plots on a sphere
        # so that the outline is always anti-clockwise and will fill inside
        bmsep = SuperDARNRadars.radars[stid].hardware_info.beam_separation
        if projs == Projs.GEO and bmsep < 0:
            beam_corners_lons = beam_corners_lons[::-1]
            beam_corners_lats = beam_corners_lats[::-1]

        # Setup plot
        # This may screw up references
        hemisphere = SuperDARNRadars.radars[stid].hemisphere
        if ax is None:
            # Get the hemisphere to pass to plotting projection
            kwargs['hemisphere'] = hemisphere
            ax, ccrs = projs(date=date, **kwargs)
        if ccrs is None:
            transform = ax.transData
        else:
            transform = ccrs.Geodetic()

        if boundary:
            # left boundary line
            ax.plot(beam_corners_lons[0:ranges[1]-ranges[0]+1, 0],
                    beam_corners_lats[0:ranges[1]-ranges[0]+1, 0],
                    color=line_color, linewidth=0.5,
                    alpha=line_alpha, transform=transform, zorder=3)
            # top radar arc
            ax.plot(beam_corners_lons[ranges[1]-ranges[0],
                                      0:beam_corners_lons.shape[1]],
                    beam_corners_lats[ranges[1]-ranges[0],
                                      0:beam_corners_lons.shape[1]],
                    color=line_color, linewidth=0.5,
                    alpha=line_alpha, transform=transform, zorder=3)
            # right boundary line
            ax.plot(beam_corners_lons[0:ranges[1]-ranges[0]+1,
                                      beam_corners_lons.shape[1] - 1],
                    beam_corners_lats[0:ranges[1]-ranges[0]+1,
                                      beam_corners_lons.shape[1] - 1],
                    color=line_color, linewidth=0.5,
                    alpha=line_alpha, transform=transform, zorder=3)
            # bottom arc
            ax.plot(beam_corners_lons[0, 0:beam_corners_lons.shape[1]],
                    beam_corners_lats[0, 0:beam_corners_lons.shape[1]],
                    color=line_color, linewidth=0.5, alpha=line_alpha,
                    transform=transform, zorder=3)

        fan_shape = beam_corners_lons.shape

        if grid:
            # This plots lines along the beams
            for bm in range(fan_shape[1]):
                ax.plot(beam_corners_lons[0:ranges[1] + 1, bm - 1],
                        beam_corners_lats[0:ranges[1] + 1, bm - 1],
                        color=line_color, linewidth=0.2,
                        alpha=line_alpha, transform=transform,
                        zorder=3)
            # This plots arcs along the gates
            for g in range(ranges[1] - ranges[0] + 1):
                ax.plot(beam_corners_lons[g - 1,
                                          0:beam_corners_lons.shape[1]],
                        beam_corners_lats[g - 1,
                                          0:beam_corners_lons.shape[1]],
                        color=line_color, linewidth=0.2,
                        alpha=line_alpha, transform=transform,
                        zorder=3)

        if radar_location:
            cls.plot_radar_position(stid, ax, date=date, line_color=line_color,
                                    transform=transform, projs=projs,
                                    coords=coords, ccrs=ccrs, **kwargs)
        if radar_label:
            cls.plot_radar_label(stid, ax, date=date, line_color=line_color,
                                 transform=transform, projs=projs,
                                 coords=coords, ccrs=ccrs, **kwargs)

        if fov_color is not None:
            theta = beam_corners_lons[0:ranges[1] + 1, 0]
            theta =\
                np.append(theta,
                          beam_corners_lons[ranges[1]-ranges[0],
                                            0:beam_corners_lons.shape[1]-1])
            theta =\
                np.append(theta,
                          np.flip(beam_corners_lons[0:ranges[1] -
                                                    ranges[0] + 1,
                                                    beam_corners_lons.
                                                    shape[1] - 1]))
            theta =\
                np.append(theta,
                          np.flip(beam_corners_lons[0,
                                                    0:beam_corners_lons.
                                                    shape[1] - 1]))

            r = beam_corners_lats[0:ranges[1] + 1, 0]
            r =\
                np.append(r, beam_corners_lats[ranges[1]-ranges[0],
                                               0:beam_corners_lons.
                                               shape[1] - 1])
            r =\
                np.append(r,
                          np.flip(beam_corners_lats[0:ranges[1] - ranges[0]+1,
                                                    beam_corners_lons.
                                                    shape[1] - 1]))
            r =\
                np.append(r,
                          np.flip(beam_corners_lats[0,
                                                    0:beam_corners_lons.
                                                    shape[1] - 1]))

            theta = np.flip(theta)
            r = np.flip(r)

            ax.fill(theta, r, color=fov_color, alpha=alpha, zorder=1,
                    transform=transform)

        return {'ax': ax,
                'ccrs': ccrs,
                'cm': None,
                'cb': None,
                'fig': plt.gcf(),
                'data': {'beam_corners_lats': beam_corners_lats,
                         'beam_corners_lons': beam_corners_lons}
                }

    @classmethod
    def get_gate_azm(cls, theta: float, r: float, stid: int, coords, date):
        """
        gets the azimuth of the gate, requires some changes depending on
        coordinates before using calculate_azimuth

        Parameters
        ----------
            theta: float
                longitude
            r: float
                latitude
            stid: int
                station id of radar
            coords: Enum
                enumeration of coordinate system
            date: datetime object
                date of data

        Returns
        -------
            azm: float
                azimuth direction of radar from gate in coordinate system
                given
        """
        # Get position of radar in geographic from hdw files
        radlat = SuperDARNRadars.radars[stid].hardware_info.geographic.lat
        radlon = SuperDARNRadars.radars[stid].hardware_info.geographic.lon
        # Convert radar position to correct coordinate system
        if coords == Coords.AACGM_MLT or coords == Coords.AACGM:
            geomag_radar = aacgmv2.get_aacgm_coord(radlat, radlon, 250, date)
            radlat = geomag_radar[0]
            radlon = geomag_radar[1]
            if coords == Coords.AACGM_MLT:
                mltshift = geomag_radar[1] -\
                        (aacgmv2.convert_mlt(geomag_radar[1], date) * 15)
                radlon = geomag_radar[1] - mltshift[0]
        # Call calculate azimuth function from geo
        azm = calculate_azimuth(r, theta, 300, radlat, radlon, 300)
        return azm

    @classmethod
    def plot_radar_position(cls, stid: int, ax: axes.Axes,
                            date: dt.datetime,

                            transform: object = None,
                            coords: Coords = Coords.AACGM_MLT,
                            projs: Projs = Projs.POLAR,
                            line_color: str = 'black', **kwargs):
        """
        plots only a dot at the position of a given radar station ID (stid)

        Parameters
        -----------
            stid: int
                Radar station ID
            ax: matplotlib.axes.Axes
                Pre-defined axis object to plot on.
            date: datetime datetime object
                sets the datetime used to find the coordinates of the
                FOV
            transform:
            coords: Coords object
            projs: Projs object
            line_color: str
                color of the dot
                default: black

        Returns
        -------
            No variables returned
        """
        # Get location of radar
        lat = SuperDARNRadars.radars[stid].hardware_info.geographic.lat
        lon = SuperDARNRadars.radars[stid].hardware_info.geographic.lon
        # Convert to geomag coords
        if coords == Coords.AACGM_MLT or coords == Coords.AACGM:
            geomag_radar = aacgmv2.get_aacgm_coord(lat, lon, 250, date)
            lat = geomag_radar[0]
            lon = geomag_radar[1]
            if coords == Coords.AACGM_MLT:
                mltshift = geomag_radar[1] -\
                        (aacgmv2.convert_mlt(geomag_radar[1], date) * 15)
                lon = geomag_radar[1] - mltshift
        if projs == Projs.POLAR:
            lon = np.radians(lon)
        # Plot a dot at the radar site
        ax.scatter(lon, lat, c=line_color, s=5, transform=transform)
        return

    @classmethod
    def plot_radar_label(cls, stid: int, ax: axes.Axes,
                         date: dt.datetime,
                         coords: Coords = Coords.AACGM_MLT,
                         projs: Projs = Projs.POLAR,
                         line_color: str = 'black', transform: object = None,
                         **kwargs):
        """
        plots only string at the position of a given radar station ID (stid)

        Parameters
        -----------
            stid: int
                Radar station ID
            ax: matplotlib.axes.Axes
                Pre-defined axis object to plot on.
            coords: Coords object
            projs: Projs object
            date: datetime datetime object
                sets the datetime used to find the coordinates of the
                FOV
            line_color: str
                color of the text
                default: black
            transform:

        Returns
        -------
            No variables returned
        """
        if coords == Coords.AACGM_MLT or coords == Coords.AACGM:
            lat, lon = SuperDARNRadars.radars[stid].mag_label
        else:
            lat, lon = SuperDARNRadars.radars[stid].geo_label
        
        # Label text
        label_str = ' ' + SuperDARNRadars.radars[stid]\
                    .hardware_info.abbrev.upper()

        # Convert to geomag coords
        if coords == Coords.AACGM_MLT:
            mltshift = lon -\
                    (aacgmv2.convert_mlt(lon, date) * 15)
            lon = lon - mltshift
        if projs == Projs.POLAR:
            lon = np.radians(lon)

        theta_text = lon
        r_text = lat
        
        ax.text(theta_text, r_text, label_str, ha='center',
                transform=transform, c=line_color)
        return

    @classmethod
    def __add_title__(cls, first_timestamp: dt.datetime,
                      end_timestamp: dt.datetime):
        title = "{year}-{month}-{day} {start_hour}:{start_minute}:{second} -"\
                " {end_hour}:{end_minute}:{end_second}"\
                "".format(year=first_timestamp.year,
                          month=str(first_timestamp.month).zfill(2),
                          day=str(first_timestamp.day).zfill(2),
                          start_hour=str(first_timestamp.hour).zfill(2),
                          start_minute=str(first_timestamp.minute).zfill(2),
                          second=str(first_timestamp.second).zfill(2),
                          end_hour=str(end_timestamp.hour).
                          zfill(2),
                          end_minute=str(end_timestamp.minute).
                          zfill(2),
                          end_second=str(end_timestamp.second).zfill(2))
        return title
