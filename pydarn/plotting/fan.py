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
from typing import List, Union

# Third party libraries
import aacgmv2

from pydarn import (PyDARNColormaps, build_scan, radar_fov, citing_warning,
                    time2datetime, plot_exceptions, SuperDARNRadars,
                    Hemisphere, Projections)



class Fan():
    """
        'Fan', or 'Field-of-view' plots for SuperDARN FITACF data
        This class inherits from matplotlib to generate the figures
        Methods
        -------
        plot_fan
        plot_fov
        """

    def __str__(self):
        return "This class is static class that provides"\
                " the following methods: \n"\
                "   - plot_fan()\n"\
                "   - plot_fov()\n"

    @classmethod
    def plot_fan(cls, dmap_data: List[dict], ax=None,
                 scan_index: Union[int, dt.datetime] = 1,
                 ranges: List = [0, 75], boundary: bool = True,
                 alpha: int = 0.5, parameter: str = 'v',
                 lowlat: int = 30, cmap: str = None,
                 groundscatter: bool = False,
                 zmin: int = None, zmax: int = None,
                 colorbar: bool = True,
                 colorbar_label: str = '', title: bool = True,
                 **kwargs):

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
                Scan number from beginning of first record in file
                or datetime given first record to match the index
                Default: 1
            parameter: str
                Key name indicating which parameter to plot.
                Default: v (Velocity). Alternatives: 'p_l', 'w_l', 'elv'
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
            title: bool
                if true then will create a title, else user
                can define it with plt.title
                default: true
            kwargs: key = value
                Additional keyword arguments to be used in projection plotting
                For possible keywords, see: projections.axis_polar

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
        See Also
        --------
            plot_fov
        """

        # Get scan numbers for each record
        beam_scan = build_scan(dmap_data)

        if isinstance(scan_index, dt.datetime):
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

        # Plot FOV outline
        beam_corners_aacgm_lats, beam_corners_aacgm_lons, thetas, rs, ax = \
            cls.plot_fov(stid=dmap_data[0]['stid'], date=date, ranges=ranges, 
                        boundary=boundary, alpha=alpha, ax=ax, **kwargs)
        fan_shape = beam_corners_aacgm_lons.shape

        # Get range-gate data and groundscatter array for given scan
        scan = np.zeros((fan_shape[0] - 1, fan_shape[1]-1))
        grndsct = np.zeros((fan_shape[0] - 1, fan_shape[1]-1))

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

        # Begin plotting by iterating over ranges and beams
        for gates in range(ranges[0], ranges[1] - 1):
            for beams in range(thetas.shape[1] - 1):
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
        if title:
            start_time = time2datetime(dmap_data[plot_beams[0][0]])
            end_time = time2datetime(dmap_data[plot_beams[-1][-1]])
            title = cls.__add_title__(start_time, end_time)
            plt.title(title)
        citing_warning()
        return beam_corners_aacgm_lats, beam_corners_aacgm_lons, scan, grndsct

    @classmethod
    def plot_fov(cls, stid: str, date: dt = None, ax=None, ranges: List = [0, 75],
                boundary: bool = True, fov_color: str = None, alpha: int = 0.5,
                **kwargs):
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
            date: datetime object
                Sets the datetime used to find the coordinates of the FOV
                Default: Current time
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
            kawrgs: key = value
                Additional keyword arguments to be used in projection plotting
                For possible keywords, see: projections.axis_polar

        Returns
        -------
            beam_corners_aacgm_lats - list of beam corners AACGM latitudes
            beam_corners_aacgm_lons - list of beam corners AACGM longitudes
            thetas - theta polar coordinates
            rs - radius polar coordinates
        """
        
        #Set datetime object to current computer time if not given
        if not date:
            date = dt.datetime.now()     
        
        # Get radar beam/gate locations
        beam_corners_aacgm_lats, beam_corners_aacgm_lons = \
            radar_fov(stid, coords='aacgm', date=date)
        fan_shape = beam_corners_aacgm_lons.shape

        # Work out shift due in MLT
        beam_corners_mlts = np.zeros((fan_shape[0], fan_shape[1]))
        mltshift = beam_corners_aacgm_lons[0, 0] - \
            (aacgmv2.convert_mlt(beam_corners_aacgm_lons[0, 0], date) * 15)
        beam_corners_mlts = beam_corners_aacgm_lons - mltshift

        # Hold the beam positions
        thetas = np.radians(beam_corners_mlts)
        rs = beam_corners_aacgm_lats   

        # Setup plot
        # This may screw up references
        if ax is None:
            # Get the hemisphere to pass to plotting projection
            kwargs['hem'] = SuperDARNRadars.radars[stid].hemisphere
            # Get a polar projection using any kwarg input
            ax = Projections.axis_polar(**kwargs)

        if boundary:
            # left boundary line
            plt.plot(thetas[0:ranges[1], 0], rs[0:ranges[1], 0],
                     color='black', linewidth=0.5)
            # top radar arc
            plt.plot(thetas[ranges[1] - 1, 0:thetas.shape[1]],
                     rs[ranges[1] - 1, 0:thetas.shape[1]],
                     color='black', linewidth=0.5)
            # right boundary line
            plt.plot(thetas[0:ranges[1], thetas.shape[1] - 1],
                     rs[0:ranges[1], thetas.shape[1] - 1],
                     color='black', linewidth=0.5)
            # bottom arc
            plt.plot(thetas[0, 0:thetas.shape[1] - 1],
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
                          end_second=str(end_timestamp.second).zfill(2)
                         )
        return title
