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
# 2022-03-10: MTS - switched coords involving range estimations to RangeEstimation
#                 - Removed GEO_COASTALINE, replaced with GEO on projections
#                 - reduced some parameters inputs to kwargs
# 2022-03-22: CJM - Set cmap bad values to transparent
# 2022-03-23: MTS - added the NotImplementedError for AACGM and GEO projection as this has yet to be figured out
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
from typing import List, Union

# Third party libraries
import aacgmv2

from pydarn import (PyDARNColormaps, build_scan, partial_record_warning,
                    time2datetime, plot_exceptions, SuperDARNRadars,
                    Projs, Coords, Hemisphere, RangeEstimation)


class Fan():
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
    def plot_fan(cls, dmap_data: List[dict], ax=None, ranges: List = [],
                 scan_index: Union[int, dt.datetime] = 1,
                 parameter: str = 'v', cmap: str = None,
                 groundscatter: bool = False, zmin: int = None,
                 zmax: int = None, colorbar: bool = True,
                 colorbar_label: str = '', title: bool = True,
                 boundary: bool = True, projs: Projs = Projs.POLAR,
                 coords: Coords = Coords.AACGM_MLT,
                 channel: int = 'all', **kwargs):
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
            fov_files: bool
                boolean if the fov data should be read in by a file
                pyDARN supplies. If false then it uses radar position
                code.
                default: False
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
            channel : int or str
                integer indicating which channel to plot or 'all' to
                plot all channels
                Default: 'all'
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
            raise plot_exceptions.NotImplemented("AACGM coordinates are"\
                                                 " not implemented for "\
                                                 " geographic projections right"\
                                                 " now, if you would like to"\
                                                 " see it sooner please help"\
                                                 " out at "\
                                                 "https://github.com"\
                                                 "/SuperDARN/pyDARN")

        beam_corners_lats, beam_corners_lons =\
                coords(stid=dmap_data[0]['stid'],
                       rsep=rsep, frang=frang,
                       gates=ranges, date=date,
                       **kwargs)

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
            cmap = {'p_l': 'plasma', 'v': PyDARNColormaps.PYDARN_VELOCITY,
                    'w_l': PyDARNColormaps.PYDARN_VIRIDIS,

                    'elv': PyDARNColormaps.PYDARN}
            cmap = plt.cm.get_cmap(cmap[parameter])

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
                beam = dmap_data[i.astype(int)]['bmnum']

                # Exclude ranges larger than the expected maximum.
                # This is a temporary fix to manage inconsistencies between the
                # fitacf files and the hardware files. The issue will be
                # fully resolved when the `rpos` code is committed.
                good_data = np.where((slist >= ranges[0]) &
                                     (slist < ranges[1]))
                slist = slist[good_data]
                temp_data = dmap_data[i.astype(int)][parameter][good_data]
                temp_ground = dmap_data[i.astype(int)]['gflg'][good_data]

                scan[slist-ranges[0], beam] = temp_data
                grndsct[slist-ranges[0], beam] = temp_ground
            # if there is no slist field this means partial record
            except KeyError:
                partial_record_warning()
                continue

        # Begin plotting by iterating over ranges and beams

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
        ax.pcolormesh(thetas, rs,
                      np.ma.masked_array(scan, ~scan.astype(bool)),
                      norm=norm, cmap=cmap, transform=transform,
                      zorder=2)

        # plot the groundscatter as grey fill
        if groundscatter:
            ax.pcolormesh(thetas, rs,
                          np.ma.masked_array(grndsct,
                                             ~grndsct.astype(bool)),
                          norm=norm, cmap='Greys',
                          transform=transform, zorder=3)
        if ccrs is None:
            azm = np.linspace(0, 2 * np.pi, 100)
            r, th = np.meshgrid(rs, azm)
            plt.plot(azm, r, color='k', ls='none')
            plt.grid()

        if boundary:
            cls.plot_fov(stid=dmap_data[0]['stid'], date=date, ax=ax,
                         ccrs=ccrs, coords=coords, projs=projs, rsep=rsep,
                         frang=frang, ranges=ranges, **kwargs)

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
        if title:
            start_time = time2datetime(dmap_data[plot_beams[0][0]])
            end_time = time2datetime(dmap_data[plot_beams[-1][-1]])
            title = cls.__add_title__(start_time, end_time)
            plt.title(title)
        return ax, beam_corners_lats, beam_corners_lons, scan, grndsct

    @classmethod
    def plot_fov(cls, stid: str, date: dt.datetime,
                 ax=None, ccrs=None, ranges: List = [], boundary: bool = True,
                 rsep: int = 45, frang: int = 180,
                 projs: object = Projs.POLAR,
                 coords: Coords = Coords.AACGM_MLT,
                 fov_color: str = None, alpha: int = 0.5,
                 radar_location: bool = True, radar_label: bool = False,
                 line_color: str = 'black',
                 grid: bool = False,
                 line_alpha: int = 0.5, **kwargs):
        """
        plots only the field of view (FOV) for a given radar station ID (stid)

        Parameters
        -----------
            stid: int
                Radar station ID
            ax: matplotlib.pyplot axis
                Pre-defined axis object to pass in, must currently be
                polar projection
                Default: Generates a polar projection for the user
                with MLT/latitude labels
            date: datetime object
                Sets the datetime used to find the coordinates of the FOV
                Default: Current time
            ranges: list
                Set to a two element list of the lower and upper ranges to plot
                If None, the  max will be obtained by SuperDARNRadars
                Default: None
            projs: Pojs object
                Sets the projection type for the plot
                Default: Projs.POLAR
            boundary: bool
                Set to false to not plot the outline of the FOV
                Default: True
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

        if projs == Projs.POLAR:
            beam_corners_lons = np.radians(beam_corners_lons)

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
            plt.plot(beam_corners_lons[0:ranges[1]-ranges[0]+1, 0],
                     beam_corners_lats[0:ranges[1]-ranges[0]+1, 0],
                     color=line_color, linewidth=0.5,
                     alpha=line_alpha, transform=transform, zorder=3)
            # top radar arc
            plt.plot(beam_corners_lons[ranges[1]-ranges[0],
                                       0:beam_corners_lons.shape[1]],
                     beam_corners_lats[ranges[1]-ranges[0],
                                       0:beam_corners_lons.shape[1]],
                     color=line_color, linewidth=0.5,
                     alpha=line_alpha, transform=transform, zorder=3)
            # right boundary line
            plt.plot(beam_corners_lons[0:ranges[1]-ranges[0]+1,
                                       beam_corners_lons.shape[1] - 1],
                     beam_corners_lats[0:ranges[1]-ranges[0]+1,
                                       beam_corners_lons.shape[1] - 1],
                     color=line_color, linewidth=0.5,
                     alpha=line_alpha, transform=transform, zorder=3)
            # bottom arc
            plt.plot(beam_corners_lons[0, 0:beam_corners_lons.shape[1]],
                     beam_corners_lats[0, 0:beam_corners_lons.shape[1]],
                     color=line_color, linewidth=0.5, alpha=line_alpha,
                     transform=transform, zorder=3)

        fan_shape = beam_corners_lons.shape

        if grid:
            # This plots lines along the beams
            for bm in range(fan_shape[1]):
                plt.plot(beam_corners_lons[0:ranges[1] + 1, bm - 1],
                         beam_corners_lats[0:ranges[1] + 1, bm - 1],
                         color=line_color, linewidth=0.2,
                         alpha=line_alpha, transform=transform,
                         zorder=3)
            # This plots arcs along the gates
            for g in range(ranges[1] - ranges[0] + 1):
                plt.plot(beam_corners_lons[g - 1,
                                           0:beam_corners_lons.shape[1]],
                         beam_corners_lats[g - 1,
                                           0:beam_corners_lons.shape[1]],
                         color=line_color, linewidth=0.2,
                         alpha=line_alpha, transform=transform,
                         zorder=3)

        if radar_location:
            cls.plot_radar_position(stid, date=date, line_color=line_color,
                                    transform=transform, projs=projs,
                                    coords=coords, ccrs=ccrs, **kwargs)
        if radar_label:
            cls.plot_radar_label(stid, date=date, line_color=line_color,
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

        return beam_corners_lats, beam_corners_lons, ax, ccrs

    @classmethod
    def plot_radar_position(cls, stid: int, date: dt.datetime,
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
            date: datetime datetime object
                sets the datetime used to find the coordinates of the
                FOV
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
        plt.scatter(lon, lat, c=line_color, s=5, transform=transform)
        return

    @classmethod
    def plot_radar_label(cls, stid: int, date: dt.datetime,
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
            date: datetime datetime object
                sets the datetime used to find the coordinates of the
                FOV
            line_color: str
                color of the text
                default: black

        Returns
        -------
            No variables returned
        """
        # Label text
        label_str = ' ' + SuperDARNRadars.radars[stid]\
                    .hardware_info.abbrev.upper()
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

        theta_text = lon
        # Shift in latitude (dependent on hemisphere)
        if SuperDARNRadars.radars[stid].hemisphere == Hemisphere.North:
            r_text = lat - 5
        else:
            r_text = lat + 5
        plt.text(theta_text, r_text, label_str, ha='center',
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
