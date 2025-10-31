# Copyright (C) 2020 SuperDARN Canada, University of Saskatchewan
# Author: Daniel Billett, Marina Schmidt
#
# Modifications:
#   20220308 MTS added partial record exception
#   20230628 CJM refactored return values
#   20230713 CJM corrected geographic quivers
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
Grid plots
"""

import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import warnings

from matplotlib import ticker, cm, colors
from typing import List

# Third party libraries
import aacgmv2

from pydarn import (PyDARNColormaps, Fan, plot_exceptions, Hemisphere, RadarID,
                    standard_warning_format, Projs, Coords, GeneralUtils)

warnings.formatwarning = standard_warning_format


class Grid():
    """
        Grid plots for SuperDARN data
        This class inherits from matplotlib to generate the figures
        Methods
        -------
        plot_grid
    """
    def __str__(self):
        return "This class is static class that provides"\
                " the following methods: \n"\
                "   - plot_grid()\n"

    @classmethod
    def plot_grid(cls, dmap_data: List[dict], record: int = 0,
                  start_time: dt.datetime = None, time_delta: int = 1,
                  ax=None, parameter: str = 'vel',
                  cmap: str = None, zmin: int = None,
                  zmax: int = None, colorbar: bool = True,
                  colorbar_label: str = '', title: str = '',
                  len_factor: float = 150.0, ref_vector: int = 300,
                  projs: Projs = Projs.POLAR,
                  coords: Coords = Coords.AACGM_MLT,
                  **kwargs):
        """
        Plots a radar's gridded vectors from a GRID file

        Parameters
        -----------
            dmap_data: List[dict]
                Named list of dictionaries obtained from SDarn_read
            record: int
                record number to plot
                default: 0
            start_time: datetime.datetime
                datetime object as the start time of the record to plot
                if none then record will be used
                default: none
            time_delta: int
                How close the start_time has to be start_time of the record
                in minutes
                default: 1
            ax: matplotlib.pyplot axis
                Pre-defined axis object to pass in, must currently
                be polar projection
                Default: Generates a polar projection for the user
                with MLT/latitude labels
            parameter: str
                Key name indicating which parameter to plot.
                Default: vel (Velocity). Alternatives: 'pwr', 'wdt'
            cmap: matplotlib.cm
                matplotlib colour map
                https://matplotlib.org/tutorials/colors/colormaps.html
                Default: Official pyDARN colour map for given parameter
            zmin: int
                The minimum parameter value for coloring
                Default: {'pwr': [0], 'vel': [0], 'wdt': [0]}
            zmax: int
                The maximum parameter value for  coloring
                Default: {'pwr': [50], 'vel': [1000], 'wdt': [250]}
            colorbar: bool
                Draw a colourbar if True
                Default: True
            colorbar_label: str
                The label that appears next to the colour bar.
                Requires colorbar to be true
                Default: ''
            title: str
                Adds a title to the plot. If no title is specified,
                one will be provided
                Default: ''
            len_factor: float
                Normalisation factor for the vectors, to control size on plot
                Larger number means smaller vectors on plot
                Default: 150.0
            ref_vector: int
                Velocity value to be used for the reference vector, in m/s
                Default: 300
            projs: Enum
                choice of projection for plot
                default: Projs.POLAR (polar projection)
            coords: Enum
                choice of plotting coordinates
                default: Coords.AACGM_MLT (Magnetic Lat and MLT)
            kwargs: key=value
                uses the parameters for plot_fov and projections.axis
        See Also
        --------
        plot_fov - plots the field of view found in fan.py

        Returns
        -----------
        If parameter is 'vel':
        thetas - List of gridded data point magnetic local times (degrees)
        end_thetas - List of magnetic local time end points used for vector
                     plotting (degrees)
        rs - List of gridded data point radius' (latitude)
        end_rs - List of radius end points for vector plotting (latitude)
        data - List of magnitudes of line-of-sight velocity
        azm_v -  List of azimuths of line-of-sight velocity
        else:
        thetas - List of gridded data point magnetic local times (degrees)
        rs - List of gridded data point radius' (latitude)
        data - List of data magnitudes plotted, for parameter chosen
        """
        # Short hand for the parameters in GRID files
        if parameter == 'vel' or parameter == 'pwr' or parameter == 'wdt':
            parameter = "vector.{param}.median".format(param=parameter)

        # Find the record corresponding to the start time
        if start_time is not None:
            for record in range(len(dmap_data)):
                date = dt.datetime(dmap_data[record]['start.year'],
                                   dmap_data[record]['start.month'],
                                   dmap_data[record]['start.day'],
                                   dmap_data[record]['start.hour'],
                                   dmap_data[record]['start.minute'])
                time_diff = date - start_time
                if time_diff.seconds/60 <= time_delta:
                    break
            if time_diff.seconds/60 > time_delta:
                raise plot_exceptions.NoDataFoundError(parameter,
                                                       start_time=start_time)
        else:
            # Record is read in or default to 0
            date = dt.datetime(dmap_data[record]['start.year'],
                               dmap_data[record]['start.month'],
                               dmap_data[record]['start.day'],
                               dmap_data[record]['start.hour'],
                               dmap_data[record]['start.minute'])

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # Check for partial records
            if all(dmap_data[record]['nvec'] == 0):
                raise plot_exceptions.PartialRecordsError('~all vectors~')

            data_lons = dmap_data[record]['vector.mlon']
            data_lats = dmap_data[record]['vector.mlat']

            # Hemisphere is not found in grid files so take from latitudes
            hemisphere = Hemisphere(np.sign(
                                    dmap_data[record]['vector.mlat'][0]))
            ax, ccrs = projs(date=date, ax=ax, hemisphere=hemisphere, **kwargs)
            if ccrs is None:
                transform = ax.transData
            else:
                transform = ccrs.Geodetic()

            for stid in dmap_data[record]['stid']:
                fan_rtn = Fan.plot_fov(RadarID(stid), date, ax=ax, ccrs=ccrs,
                                       coords=coords, projs=projs, **kwargs)
                coord_lons = fan_rtn['data']['beam_corners_lons']
                ax = fan_rtn['ax']
                ccrs = fan_rtn['ccrs']

            if coords != Coords.GEOGRAPHIC and projs == Projs.GEO:
                raise plot_exceptions.NotImplemented(
                                        "AACGM coordinates are"
                                        " not implemented for "
                                        " geographic projections right"
                                        " now, if you would like to"
                                        " see it sooner please help"
                                        " out at "
                                        "https://github.com"
                                        "/SuperDARN/pyDARN")
            if coords == Coords.GEOGRAPHIC and projs == Projs.POLAR:
                raise plot_exceptions.NotImplemented(
                                        "Geographic coordinates are"
                                        " not implemented for "
                                        " polar projections in grid plots"
                                        " right now, if you would like to"
                                        " see it sooner please help"
                                        " out at "
                                        "https://github.com"
                                        "/SuperDARN/pyDARN")
            # Thetas in aacgm required for calculating the
            # vectors later, called them theta_calc and rs_calc
            # for later use
            shifted_mlts = coord_lons[0, 0] - \
                (aacgmv2.convert_mlt(coord_lons[0, 0], date) * 15)
            shifted_lons = data_lons - shifted_mlts

            if projs == Projs.POLAR:
                # Convert to radians for polar plots
                thetas_calc = np.radians(shifted_lons)
                thetas = np.radians(shifted_lons)
                rs = data_lats
                rs_calc = data_lats
            elif projs == Projs.MAG:
                thetas_calc = np.radians(shifted_lons)
                thetas = shifted_lons
                rs = data_lats
                rs_calc = data_lats
            else:
                # Convert to geographic coordinates
                glats, glons, _ = aacgmv2.convert_latlon_arr(
                                    data_lats, data_lons, 300,
                                    date, method_code="A2G")
                thetas_calc = np.radians(glons)
                thetas = glons
                rs = glats
                rs_calc = glats

            # Colour table and max value selection depending on
            # parameter plotted Load defaults if none given
            if cmap is None:
                cmap = {'vector.pwr.median': PyDARNColormaps.PYDARN_PLASMA,
                        'vector.vel.median': PyDARNColormaps.PYDARN_PLASMA_R,
                        'vector.wdt.median': PyDARNColormaps.PYDARN_VIRIDIS}
                cmap = cmap[parameter]

            # Setting zmin and zmax
            defaultzminmax = {'vector.pwr.median': [0, 50],
                              'vector.vel.median': [0, 1000],
                              'vector.wdt.median': [0, 250]}
            if zmin is None:
                zmin = defaultzminmax[parameter][0]
            if zmax is None:
                zmax = defaultzminmax[parameter][1]

            norm = colors.Normalize
            norm = norm(zmin, zmax)

            # check to make sure the parameter is present in the file
            # this may not be the case for wdt and pwr as you need -xtd
            # option in make_grid
            try:
                data = dmap_data[record][parameter]
            except KeyError:
                raise plot_exceptions.UnknownParameterError(parameter,
                                                            grid=True)
            # Plot the magnitude of the parameter
            ax.scatter(thetas, rs, c=data, s=2.0, vmin=zmin, vmax=zmax,
                       zorder=5, cmap=cmap, transform=transform)

            # If the parameter is velocity then plot the LOS vectors
            if parameter == "vector.vel.median":

                # Get the mag azimuths from the data
                azm_v = dmap_data[record]['vector.kvect']

                # Azimuth direction needs to be converted to geographic
                if projs == Projs.GEO:
                    # Pole coords in geo for this date
                    gpole_lat = 90 * hemisphere.value
                    gpole_lon = 0
                    mpole_lat, mpole_lon, _ = \
                        aacgmv2.convert_latlon(gpole_lat, gpole_lon, 300,
                                               date, method_code='A2G')

                    # Flatten array to work on
                    a_m_flat = []
                    b_m_flat = []
                    thetas_flat = thetas.flatten()
                    rs_flat = rs.flatten()
                    for i in range(len(rs_flat)):
                        a_m_flat.append(
                            GeneralUtils.great_circle(thetas_flat[i],
                                                      rs_flat[i],
                                                      gpole_lon,
                                                      gpole_lat))
                        b_m_flat.append(
                            GeneralUtils.great_circle(thetas_flat[i],
                                                      rs_flat[i],
                                                      mpole_lon,
                                                      mpole_lat))
                    a_m = np.reshape(a_m_flat, rs.shape)
                    b_m = np.reshape(b_m_flat, rs.shape)
                    c_m_flat = np.ones(len(rs_flat)) * \
                        GeneralUtils.great_circle(gpole_lon, gpole_lat,
                                                  mpole_lon, mpole_lat)
                    c_m = np.reshape(c_m_flat, rs.shape)
                    declination = np.arccos((np.cos(c_m) - np.cos(a_m)
                                             * np.cos(b_m)) /
                                            (np.sin(a_m) * np.sin(b_m)))

                    azm_v = azm_v + np.degrees(declination) * hemisphere.value

                # Number of data points
                num_pts = range(len(data))

                # Angle to "rotate" each vector by to get into same
                # reference frame Controlled by longitude, or "mltitude"
                alpha = thetas_calc

                # Convert initial positions to Cartesian
                start_pos_x = (90 - abs(rs_calc)) * np.cos(thetas_calc)
                start_pos_y = (90 - abs(rs_calc)) * np.sin(thetas_calc)

                # Resolve LOS vector in x and y directions,
                # with respect to mag pole
                # Gives zonal and meridional components of LOS vector
                los_x = -data * np.cos(np.radians(
                                       -azm_v * hemisphere.value))
                los_y = -data * np.sin(np.radians(
                                       -azm_v * hemisphere.value))

                # Rotate each vector into same reference frame
                # following vector rotation matrix
                # https://en.wikipedia.org/wiki/Rotation_matrix
                vec_x = (los_x * np.cos(alpha)) - (los_y * np.sin(alpha))
                vec_y = (los_x * np.sin(alpha)) + (los_y * np.cos(alpha))

                # New vector end points, in Cartesian
                end_pos_x = start_pos_x + (vec_x * hemisphere.value /
                                           len_factor)
                end_pos_y = start_pos_y + (vec_y * hemisphere.value /
                                           len_factor)

                # Convert back to polar for plotting
                end_rs = 90 - (np.sqrt(end_pos_x**2 + end_pos_y**2))
                end_thetas = np.arctan2(end_pos_y, end_pos_x)

                end_rs = end_rs * hemisphere.value

                # Plot the vectors
                if projs == Projs.POLAR:
                    for i in num_pts:
                        ax.plot([thetas[i], end_thetas[i]],
                                 [rs[i], end_rs[i]], c=cmap(norm(data[i])),
                                 linewidth=0.5, transform=transform)
                else:
                    # If proj is geographic
                    end_thetas = np.degrees(end_thetas)
                    for i in num_pts:
                        # If the vector does not cross the meridian
                        if np.sign(thetas[i]) == np.sign(end_thetas[i]):
                            ax.plot([thetas[i], end_thetas[i]],
                                     [rs[i], end_rs[i]],
                                     c=cmap(norm(data[i])),
                                     linewidth=0.5, transform=transform)
                        # If the vector crosses the meridian then amend so that
                        # the start and end are in the same sign
                        else:
                            if abs(end_thetas[i]) > 90:
                                if end_thetas[i] < 0:
                                    end_thetas[i] = end_thetas[i] + 360
                                else:
                                    thetas[i] = thetas[i] + 360
                            # Vector plots correctly over the 0 meridian so
                            # Nothing is done to correct that section
                            ax.plot([thetas[i], end_thetas[i]],
                                     [rs[i], end_rs[i]],
                                     c=cmap(norm(data[i])),
                                     linewidth=0.5, transform=transform)
                # TODO: Add a velocity reference vector

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

        if title == '':
            title = "{year}-{month}-{day} {start_hour}:{start_minute} -"\
                " {end_hour}:{end_minute}"\
                    "".format(year=date.year,
                              month=str(date.month).zfill(2),
                              day=str(date.day).zfill(2),
                              start_hour=str(date.hour).zfill(2),
                              start_minute=str(date.minute).zfill(2),
                              end_hour=str(dmap_data[record]['end.hour']).
                              zfill(2),
                              end_minute=str(dmap_data[record]['end.minute']).
                              zfill(2))
        plt.title(title)
        if parameter != 'vector.vel.median':
            end_thetas = None
            end_rs = None
            azm_v = None
        return {'ax': ax,
                'ccrs': ccrs,
                'cm': cmap,
                'cb': cb,
                'fig': plt.gcf(),
                'data': {'data_position_theta': thetas,
                         'end_stick_position_theta': end_thetas,
                         'data_position_r': rs,
                         'end_stick_position_r': end_rs,
                         'raw_data': data,
                         'raw_azimuths': azm_v}
                }
