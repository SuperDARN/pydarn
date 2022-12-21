# Copyright (C) 2021 SuperDARN Canada, University of Saskatchewan
# Author: Marina Schmidt
# Copyright (C) 2012  VT SuperDARN Lab
# Modifications:
# 2022-03-08: MTS - added partial records exception
# 2022-03-18: CJM - Included contour plotting and HMB
# 2022-03-31: CJM - Map info included
# 2022-03-31: CJM - IMF clock angle dial added
# 2022-04-01: CJM - Bug fix for lon shifting to MLT
# 2022-04-28: CJM - Added option to have single color vectors with reference
#                   vector
# 2022-08-15: CJM - Removed plot_FOV call for default uses
# 2022-12-13: CJM - Limited reference vectors to only velocity use
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

from enum import Enum
from matplotlib import ticker, cm, colors
from mpl_toolkits.axes_grid1.inset_locator import InsetPosition
from scipy import special
from typing import List

# Third party libraries
import aacgmv2

from pydarn import (PyDARNColormaps, plot_exceptions,
                    standard_warning_format, Re, Hemisphere,
                    time2datetime, find_record, Fan, Projs, MapParams)

warnings.formatwarning = standard_warning_format


class Maps():
    """
    Maps plots for SuperDARN data

    Methods
    -------
    plot_maps
    calculated_fitted_velocities
    """

    def __str__(self):
        return "This class is static class that provides"\
                " the following methods: \n"\
                "   - plot_maps()\n"


    @classmethod
    def plot_mapdata(cls, dmap_data: List[dict], ax=None,
                     parameter: Enum = MapParams.FITTED_VELOCITY,
                     record: int = 0, start_time: dt.datetime = None,
                     time_delta: float = 1,  alpha: float = 1.0,
                     len_factor: float = 150, color_vectors: bool = True,
                     cmap: str = None, colorbar: bool = True,
                     colorbar_label: str = '', title: str = '',
                     zmin: float = None, zmax: float = None,
                     hmb: bool = True, boundary: bool = False,
                     radar_location: bool = False, map_info: bool = True,
                     imf_dial: bool = True, reference_vector: int = 500,
                     projs: Projs = Projs.POLAR, **kwargs):
        """
        Plots convection maps data points and vectors

        Parameters
        ----------
            dmap_data : dict[List]
                DMAP data returned from pyDARN.SuperDARNRead or pyDARNio
            ax: object
                matplotlib axis object
            parameters: enum
                enum object to determine what to plot
                default: MapParams.FITTED_VELOCITY
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
            color_vectors: bool
                If True, color the vectors by color map chosen
                If False, color dark grey and include vector reference
                Default: True
            cmap: matplotlib.cm
                matplotlib colour map
                https://matplotlib.org/tutorials/colors/colormaps.html
                Default: Official pyDARN colour map for given parameter
                    MapParams.FITTED_VELOCITY: 'plasma',
                    MapParams.MODEL_VELOCITY: 'plasma',
                    MapParams.RAW_VELOCITY: 'plasma',
                    MapParams.POWER: 'plasma_r',
                    MapParams.SPECTRAL_WIDTH: PyDARNColormaps.PYDARN_VIRIDIS
            zmin: int
                The minimum parameter value for coloring
                Default: MapParams.FITTED_VELOCITY: [0],
                         MapParams.MODEL_VELOCITY: [0],
                         MapParams.RAW_VELOCITY: [0],
                         MapParams.POWER: [0],
                         MapParams.SPECTRAL_WIDTH: [0]
            zmax: int
                The maximum parameter value for  coloring
                Default: MapParams.FITTED_VELOCITY: [1000],
                         MapParams.MODEL_VELOCITY: [1000],
                         MapParams.RAW_VELOCITY: [1000],
                         MapParams.POWER: [250],
                         MapParams.SPECTRAL_WIDTH: [250]
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
            imf_dial: bool
                If True, draw an IMF dial of the magnetic field clock angle.
                Default: True
            reference_vector: int
                If a value is given, a reference velocity vector with
                magnitude of given value, drawn in lower right corner.
                Vector can be turned off by setting this value to False or 0.
                Will not plot for power or spectral width options.
                Default: 500 (vector plotted)
            projs: Enum
                choice of projection for plot
                default: Projs.POLAR (polar projection)
                There is no support for other projections currently
            kwargs: key=value
                uses the parameters for plot_fov and projections.axis

        """
        # Find the record corresponding to the start time
        if start_time is not None:
            record = find_record(dmap_data, start_time, time_delta)
        date = time2datetime(dmap_data[record])

        if cmap is None:
            cmap = {MapParams.FITTED_VELOCITY: 'plasma_r',
                    MapParams.MODEL_VELOCITY: 'plasma_r',
                    MapParams.RAW_VELOCITY: 'plasma_r',
                    MapParams.POWER: 'plasma',
                    MapParams.SPECTRAL_WIDTH: PyDARNColormaps.PYDARN_VIRIDIS}
            cmap = plt.cm.get_cmap(cmap[parameter])
        # Setting zmin and zmax
        defaultzminmax = {MapParams.FITTED_VELOCITY: [0, 1000],
                          MapParams.MODEL_VELOCITY: [0, 1000],
                          MapParams.RAW_VELOCITY: [0, 1000],
                          MapParams.POWER: [0, 250],
                          MapParams.SPECTRAL_WIDTH: [0, 250]}
        if zmin is None:
            zmin = defaultzminmax[parameter][0]
        if zmax is None:
            zmax = defaultzminmax[parameter][1]

        hemisphere = Hemisphere(dmap_data[record]['hemisphere'])
        norm = colors.Normalize
        norm = norm(zmin, zmax)

        if projs != Projs.POLAR:
            raise plot_exceptions.NotImplemented(" Only polar projections"
                                                 " are implemented for"
                                                 " convection maps."
                                                 " Please set"
                                                 " projs=Projs.POLAR"
                                                 " to plot a convection map.")

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # If the user wants to plot a FOV boundary or radar location
            # Needs to find the positions for each
            # Else just call the axis maker: proj
            if boundary or radar_location:
                for stid in dmap_data[record]['stid']:
                    _, _, ax, _ =\
                            Fan.plot_fov(stid, date, ax=ax, boundary=boundary,
                                         radar_location=radar_location,
                                         **kwargs)
            else:
                ax, _ = projs(date, ax=ax, hemisphere=hemisphere, **kwargs)

        if parameter == MapParams.MODEL_VELOCITY:
            try:
                data_lons = dmap_data[record]['model.mlon']
                data_lats = dmap_data[record]['model.mlat']
            except KeyError:
                raise plot_exceptions.PartialRecordsError('model.mlon')
        else:
            try:
                data_lons = dmap_data[record]['vector.mlon']
                data_lats = dmap_data[record]['vector.mlat']
            except KeyError:
                raise plot_exceptions.PartialRecordsError('model.mlat')

        # Arbitrary lon used to calculate the shift required
        shifted_mlts = 0 - (aacgmv2.convert_mlt(0, date) * 15)
        shifted_lons = data_lons - shifted_mlts
        # Note that this "mlons" is adjusted for MLT
        mlons = np.radians(shifted_lons)
        mlats = data_lats

        # If the parameter is velocity then plot the LOS vectors
        # Actual mlons used here, not adjusted mlons (np.radians(data_lons))
        if parameter == MapParams.FITTED_VELOCITY:
            v_mag, azm_v =\
                    cls.calculated_fitted_velocities(mlats=mlats,
                                                     mlons=np.radians(
                                                         data_lons),
                                                     hemisphere=hemisphere,
                                                     fit_coefficient=dmap_data[
                                                         record]['N+2'],
                                                     fit_order=dmap_data[
                                                         record]['fit.order'],
                                                     lat_min=dmap_data[
                                                         record]['latmin'],
                                                     len_factor=len_factor)

        elif parameter == MapParams.MODEL_VELOCITY:
            v_mag = dmap_data[record]['model.vel.median']
            azm_v = np.radians(dmap_data[record]['model.kvect'])
        elif parameter == MapParams.RAW_VELOCITY:
            v_mag = dmap_data[record]['vector.vel.median']
            azm_v = np.radians(dmap_data[record]['vector.kvect'])
        elif parameter == MapParams.POWER:
            v_mag = dmap_data[record]['vector.pwr.median']
            azm_v = np.radians(dmap_data[record]['vector.kvect'])

        elif parameter == MapParams.SPECTRAL_WIDTH:
            v_mag = dmap_data[record]['vector.wdt.median']
            azm_v = np.radians(dmap_data[record]['vector.kvect'])

        if parameter in [MapParams.FITTED_VELOCITY, MapParams.MODEL_VELOCITY,
                         MapParams.RAW_VELOCITY]:
            # Make reference vector and add it to the array to
            # be calculated too
            reflat = (np.abs(plt.gca().get_ylim()[1]) - 5) * hemisphere.value
            reflon = np.radians(45)
            v_mag = np.append(v_mag, reference_vector)
            if hemisphere == Hemisphere.North:
                azm_v = np.append(azm_v, np.radians(135))
            else:
                azm_v = np.append(azm_v, np.radians(45))

            # Angle to "rotate" each vector by to get into same
            # reference frame Controlled by longitude, or "mltitude"
            alpha = np.append(mlons, reflon)
            mlons = np.append(mlons, reflon)
            mlats = np.append(mlats, reflat)

            # Convert initial positions to Cartesian
            start_pos_x = (90 - abs(mlats)) * np.cos(mlons)
            start_pos_y = (90 - abs(mlats)) * np.sin(mlons)

            # Resolve LOS vector in x and y directions,
            # with respect to mag pole
            # Gives zonal and meridional components of LOS vector
            x = -v_mag * np.cos(-azm_v * hemisphere.value)
            y = -v_mag * np.sin(-azm_v * hemisphere.value)

            # Rotate each vector into same reference frame
            # following vector rotation matrix
            # https://en.wikipedia.org/wiki/Rotation_matrix
            vec_x = (x * np.cos(alpha)) - (y * np.sin(alpha))
            vec_y = (x * np.sin(alpha)) + (y * np.cos(alpha))

            # New vector end points, in Cartesian
            end_pos_x = start_pos_x + (vec_x * hemisphere.value / len_factor)
            end_pos_y = start_pos_y + (vec_y * hemisphere.value / len_factor)

            # Convert back to polar for plotting
            end_mlats = 90.0 - (np.sqrt(end_pos_x**2 + end_pos_y**2))
            end_mlons = np.arctan2(end_pos_y, end_pos_x)

            end_mlats = end_mlats * hemisphere.value

            # Plot the vector socks (final vector is the reference
            # vector to be plotted later if required)
            if color_vectors is True:
                for i in range(len(v_mag) - 1):
                    plt.plot([mlons[i], end_mlons[i]],
                             [mlats[i], end_mlats[i]], c=cmap(norm(v_mag[i])),
                             linewidth=0.5, zorder=5.0)
            else:
                for i in range(len(v_mag) - 1):
                    plt.plot([mlons[i], end_mlons[i]],
                             [mlats[i], end_mlats[i]], c='#292929',
                             linewidth=0.5, zorder=5.0)

        # Plot the sock start dots and reference vector if known
        if color_vectors is True:
            if parameter in [MapParams.FITTED_VELOCITY,
                             MapParams.MODEL_VELOCITY,
                             MapParams.RAW_VELOCITY]:
                if reference_vector > 0:
                    plt.scatter(mlons[:], mlats[:], c=v_mag[:], s=2.0,
                                vmin=zmin, vmax=zmax,  cmap=cmap, zorder=5.0,
                                clip_on=False)
                    plt.plot([mlons[-1], end_mlons[-1]],
                             [mlats[-1], end_mlats[-1]], c=cmap(norm(v_mag[-1])),
                             linewidth=0.5, zorder=5.0, clip_on=False)
                    plt.figtext(0.675, 0.15, str(reference_vector) + ' m/s',
                                fontsize=8)
                else:
                    plt.scatter(mlons[:-1], mlats[:-1], c=v_mag[:-1], s=2.0,
                                vmin=zmin, vmax=zmax,  cmap=cmap, zorder=5.0)
            else:
                plt.scatter(mlons[:], mlats[:], c=v_mag[:], s=2.0,
                            vmin=zmin, vmax=zmax,  cmap=cmap, zorder=5.0)

        else:
            # no color so make sure colorbar is turned off
            colorbar = False
            if parameter in [MapParams.FITTED_VELOCITY,
                             MapParams.MODEL_VELOCITY,
                             MapParams.RAW_VELOCITY]:
                if reference_vector > 0:
                    plt.scatter(mlons[:], mlats[:], c='#292929', s=2.0,
                                zorder=5.0, clip_on=False)
                    plt.plot([mlons[-1], end_mlons[-1]],
                             [mlats[-1], end_mlats[-1]], c='#292929',
                             linewidth=0.5, zorder=5.0, clip_on=False)
                    plt.figtext(0.675, 0.15, str(reference_vector) + ' m/s',
                                fontsize=8)
                else:
                    plt.scatter(mlons[:-1], mlats[:-1], c='#292929', s=2.0,
                                zorder=5.0)
            else:
                plt.scatter(mlons[:], mlats[:], c='#292929', s=2.0,
                                zorder=5.0)

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
                if parameter in [MapParams.FITTED_VELOCITY,
                                 MapParams.MODEL_VELOCITY,
                                 MapParams.RAW_VELOCITY]:
                    cb.set_label('Velocity (m s$^{-1}$)')
                elif parameter is MapParams.SPECTRAL_WIDTH:
                    cb.set_label('Spectral Width (m s$^{-1}$)')
                elif parameter is MapParams.POWER:
                    cb.set_label('Power')

        # Plot potential contours
        fit_coefficient = dmap_data[record]['N+2']
        fit_order = dmap_data[record]['fit.order']
        lat_shift = dmap_data[record]['lat.shft']
        lon_shift = dmap_data[record]['lon.shft']
        lat_min = dmap_data[record]['latmin']

        cls.plot_potential_contours(fit_coefficient, lat_min, date, ax,
                                    lat_shift=lat_shift, lon_shift=lon_shift,
                                    fit_order=fit_order, hemisphere=hemisphere,
                                    **kwargs)

        if hmb is True:
            # Plot the HMB
            mlats_hmb = dmap_data[record]['boundary.mlat']
            mlons_hmb = dmap_data[record]['boundary.mlon']
            cls.plot_heppner_maynard_boundary(mlats_hmb, mlons_hmb, date)

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

        if map_info is True:
            model = dmap_data[record]['model.name']
            num_points = len(dmap_data[record]['vector.mlat'])
            pol_cap_pot = dmap_data[record]['pot.drop']
            cls.add_map_info(fit_order, pol_cap_pot, num_points, model)

        if imf_dial is True:
            # Plot the IMF dial
            bx = dmap_data[record]['IMF.Bx']
            by = dmap_data[record]['IMF.By']
            bz = dmap_data[record]['IMF.Bz']
            delay = dmap_data[record]['IMF.delay']
            bt = np.sqrt(bx**2 + by**2 + bz**2)
            cls.plot_imf_dial(ax, by, bz, bt, delay)

        return mlats, mlons, v_mag


    @classmethod
    def index_legendre(cls, l: int, m: int):
        """
        not a 100% how this works some black magic

        parameter
        ---------
            l : int
                doping level
            m : int
                fit order

        return
        ------
            legendre index?
        """
        return (m == 0 and l**2) or ((l != 0)
                                     and (m != 0) and l**2 + 2 * m - 1) or 0


    @classmethod
    def calculated_fitted_velocities(cls, mlats: list, mlons: list,
                                     fit_coefficient: list,
                                     hemisphere: Enum = Hemisphere.North,
                                     fit_order: int = 6, lat_min: int = 60,
                                     len_factor: int = 150):
        """
        Calculates the fitted velocities using Legrendre polynomial

        Parameters
        ----------
            mlats: List[float]
                Magnetic Latitude in degrees
            mlons: List[float]
                Magnetic Longitude in radians
            fit_coefficient: List[float]
                Value of the coefficient
            hemisphere: int
                1 or -1 for hemisphere North or South
                default: 1 - North
            fit_order: int
                order of the fit
                default: 6
            lat_min: int
                Lower latitude boundary of data in degrees
                default: 60
            len_factor: int
                length of the vector socks multiplied by
                default: 150
        """
        # convert earth radius to meters
        Re_meters = Re * 1000.0
        # theta values in radians
        thetas = np.radians(90.0 - abs(mlats))
        thetas_max = np.radians(90.0 - abs(lat_min))

        # Angle to "rotate" each vector by to get into same
        # reference frame Controlled by longitude, or "mltitude"
        alpha = np.pi / thetas_max
        thetas_prime = alpha * thetas
        x = np.cos(thetas_prime)

        # i is the index of the list
        # x_i is the element of x at ith index
        for i, x_i in enumerate(x):
            temp_poly = special.lpmn(fit_order, fit_order, x_i)
            if i == 0:
                legendre_poly = np.append([temp_poly[0]], [temp_poly[0]],
                                          axis=0)
            else:
                legendre_poly = np.append(legendre_poly, [temp_poly[0]],
                                          axis=0)
        legendre_poly = np.delete(legendre_poly, 0, 0)
        phi = mlons

        # now do the index legender part,
        # We are doing Associated Legendre Polynomials but
        # for each polynomial we have two coefficients one
        # for cos(phi) and the other for sin(phi),
        # so we do spherical harmonics for a real valued function using
        # sin(phi) and cos(phi) rather than exp(i*phi).
        # we place an inner function to copying code

        # max index value
        k_max = cls.index_legendre(fit_order, fit_order)

        # set up arrays and small stuff for the E field
        # coefficients calculation
        thetas_ecoeffs = np.zeros((k_max + 2, len(thetas)))
        phi_ecoeffs = np.zeros((k_max + 2, len(thetas)))

        q_prime = np.array(np.where(thetas_prime != 0.0))
        q_prime = q_prime[0]
        q = np.array(np.where(thetas != 0.0))
        q = q[0]

        # finally get to converting coefficients for the potential into
        # coefficients for elec. Field
        fit_coefficient_flat = fit_coefficient.flatten()
        for m in range(fit_order + 1):
            for l in range(m, fit_order + 1):
                k3 = cls.index_legendre(l, m)
                k4 = cls.index_legendre(l, m)

                if k3 >= 0:
                    thetas_ecoeffs[k4, q_prime] =\
                            thetas_ecoeffs[k4, q_prime] -\
                            fit_coefficient_flat[k3] * alpha * l *\
                            np.cos(thetas_prime[q_prime]) / \
                            np.sin(thetas_prime[q_prime]) / Re_meters
                    phi_ecoeffs[k4, q] = phi_ecoeffs[k4, q] - \
                        fit_coefficient_flat[k3 + 1] * m /\
                        np.sin(thetas[q]) / Re_meters
                    phi_ecoeffs[k4 + 1, q] = phi_ecoeffs[k4 + 1, q] + \
                        fit_coefficient_flat[k3] * m /\
                        np.sin(thetas[q]) / Re_meters

                if l < fit_order:
                    k1 = cls.index_legendre(l+1, m)
                else:
                    k1 = -1

                k2 = cls.index_legendre(l, m)

                if k1 >= 0:
                    thetas_ecoeffs[k2, q_prime] =\
                        thetas_ecoeffs[k2, q_prime] + \
                        fit_coefficient_flat[k1] * alpha * (l + 1 + m) / \
                        np.sin(thetas_prime[q_prime]) / Re_meters

                if m > 0:
                    if k3 >= 0:
                        k3 = k3 + 1
                    k4 = k4 + 1

                    if k1 >= 0:
                        k1 = k1 + 1
                    k2 = k2 + 1

                    if k3 >= 0:
                        thetas_ecoeffs[k4, q_prime] =\
                                thetas_ecoeffs[k4, q_prime] \
                                - fit_coefficient_flat[k3] * alpha * l * \
                                np.cos(thetas_prime[q_prime]) / \
                                np.sin(thetas_prime[q_prime]) / Re_meters

                    if k1 >= 0:
                        thetas_ecoeffs[k2, q_prime] = \
                            thetas_ecoeffs[k2, q_prime] \
                            + fit_coefficient_flat[k1] * alpha *\
                            (l + 1 + m) / np.sin(thetas_prime[q_prime]) /\
                            Re_meters

        # Calculate the Electric field positions
        thetas_ecomp = np.zeros(thetas.shape)
        phi_ecomp = np.zeros(thetas.shape)

        for m in range(fit_order + 1):
            for l in range(m, fit_order + 1):
                k = cls.index_legendre(l, m)
                # Now in the IDL code we use
                # legendre_poly[:,l,m] instead of
                # legendre_poly[:,m,l] like here, this is
                # because we have a different
                # organization of legendre_poly due to the
                # way scipy.special.lpmn
                # stores values in arrays...
                if m == 0:
                    thetas_ecomp = thetas_ecomp + thetas_ecoeffs[k, :] * \
                            legendre_poly[:, m, l]
                    phi_ecomp = phi_ecomp + phi_ecoeffs[k, :] * \
                        legendre_poly[:, m, l]
                else:
                    thetas_ecomp = thetas_ecomp + thetas_ecoeffs[k, :] * \
                        legendre_poly[:, m, l] * np.cos(m * phi) + \
                        thetas_ecoeffs[k+1, :] * legendre_poly[:, m, l] * \
                        np.sin(m * phi)
                    phi_ecomp = phi_ecomp + phi_ecoeffs[k, :] * \
                        legendre_poly[:, m, l] * np.cos(m * phi) + \
                        phi_ecoeffs[k+1, :] * legendre_poly[:, m, l] * \
                        np.sin(m * phi)

        # Store the two components of Efield into a single array
        E_field_fit = np.append([thetas_ecomp], [phi_ecomp], axis=0)

        # We'll calculate Bfield magnitude now, need to initialize some more
        # stuff
        # F-region altitude 300 km * 1000 to convert to meteres
        F_altitude = 300.0 * 1000.0
        # dipole earth field in Tesla
        B_field_polar = -0.62e-4
        B_field = B_field_polar * (1.0 - 3.0 * F_altitude / Re_meters) \
            * np.sqrt(3.0 * np.square(np.cos(thetas)) + 1.0) / 2

        # get the velocity components from E-field
        velocity_fit_vectors = np.zeros(E_field_fit.shape)
        velocity_fit_vectors[0, :] = E_field_fit[1, :] / B_field
        velocity_fit_vectors[1, :] = -E_field_fit[0, :] / B_field
        velocity = np.sqrt(np.square(velocity_fit_vectors[0, :]) +
                           np.square(velocity_fit_vectors[1, :]))
        velocity_chk_zero_inds = np.where(velocity != 0.0)
        velocity_chk_zero_inds = velocity_chk_zero_inds[0]

        azm_v = np.zeros(velocity.shape)

        if len(velocity_chk_zero_inds) == 0:
            velocity = np.array([0.0])
            azm_v = np.array([0.0])
        else:
            if hemisphere == Hemisphere.South:
                azm_v[velocity_chk_zero_inds] =\
                        np.arctan2(
                            velocity_fit_vectors[1, velocity_chk_zero_inds],
                            velocity_fit_vectors[0, velocity_chk_zero_inds])
            else:
                azm_v[velocity_chk_zero_inds] =\
                        np.arctan2(
                            velocity_fit_vectors[1, velocity_chk_zero_inds],
                            -velocity_fit_vectors[0, velocity_chk_zero_inds])

        return velocity, azm_v


    @classmethod
    def add_map_info(cls, fit_order: float, pol_cap_pot: float,
                     num_points: float, model: str):
        """
        Annotates the plot with information about the map plotting

        Parameters
        ----------
            ax: object
                matplotlib axis object
            fit_order: int
                order of the fit
            pol_cap_pot: float
                value of the polar cap potential in kV
            num_points: int
                number of vectors plotted
            model: str
                model used to fit data
        """
        text_string = r'$\phi_{PC}$' + ' = ' + str(round(pol_cap_pot/1000))\
                      + ' kV\n' \
                      + 'N = ' + str(num_points) + '\n' \
                      + 'Order: ' + str(fit_order) + '\n' \
                      + 'Model: ' + model + '\n'
        plt.figtext(0.1, 0.1, text_string)


    @classmethod
    def plot_heppner_maynard_boundary(cls, mlats: list, mlons: list,
                                      date: object, line_color: str = 'black',
                                      **kwargs):
        # TODO: No evaluation of coordinate system made! May need if in
        # plotting to plot in radians/geo ect.
        """
        Plots the position of the Heppner-Maynard Boundary

        Parameters
        ----------
            ax: object
                matplotlib axis object
            mlats: List[float]
                Magnetic Latitude in degrees
            mlons: List[float]
                Magnetic Longitude in radians
            date: datetime object
                Date from record
            line_color: str
                Color of the Heppner-Maynard boundary
                Default: black

        """
        # Shift mlon to MLT
        shifted_mlts = mlons[0] - \
            (aacgmv2.convert_mlt(mlons[0], date) * 15)
        shifted_lons = mlons - shifted_mlts
        mlon = np.radians(shifted_lons)

        plt.plot(mlon, mlats, c=line_color, zorder=4.0, **kwargs)


    @classmethod
    def plot_imf_dial(cls, ax: object, by: float = 0, bz: float = 0,
                      bt: float = 0, delay: float = 0):
        """
        Plots an IMF clock angle dial on the existing plot
        Defaults all to 0 if no IMF data available to plot

        Parameters
        ----------
            ax: object
                matplotlib axis object
            by: Float
                Value of the magnetic field in the y-direction (nT)
                Default = 0 nT
            bz: Float
                Value of the magnetic field in the z-direction (nT)
                Default = 0 nT
            bt: Float
                Magnitude of the magnetic field (nT)
                Default = 0 nT
            delay: Float
                Time delay of magnetic field between the
                measuring satellite and the ionosphere (minutes)
                Default = 0 minutes
        """
        # Create new axes inside existing axes
        ax_imf = plt.axes([0, 0, 1, 1])
        ip = InsetPosition(ax, [-0.2, 0.7, 0.4, 0.4])
        ax_imf.set_axes_locator(ip)
        ax_imf.axis('off')

        ax_imf.set_xlim([-20.2, 20.2])
        ax_imf.set_ylim([-20.2, 20.2])

        # Plot a Circle
        limit_circle = plt.Circle((0, 0), 10, facecolor='w',
                                  edgecolor='k')
        ax_imf.add_patch(limit_circle)
        # Plot axis lines
        plt.plot([-10, 10], [0, 0], color='k', linewidth=0.5)
        plt.plot([0, 0], [-10, 10], color='k', linewidth=0.5)

        # Plot line for magnetic field
        plt.plot([0, by], [0, bz], color='r')

        # Add axis labels
        ax_imf.annotate('+Z', xy=(-2.5, 11))
        ax_imf.annotate('+Y', xy=(11, -1))

        # Add annotations for delay and Btot
        ax_imf.annotate('|B| = ' + str(round(bt)) + ' nT', xy=(-16, -13),
                        fontsize=7)
        ax_imf.annotate('Delay = -' + str(delay) + ' min', xy=(-16, -17),
                        fontsize=7)


    @classmethod
    def calculate_potentials(cls, fit_coefficient: list, lat_min: list,
                             lat_shift: int = 0, lon_shift: int = 0,
                             fit_order: int = 6, lowlat: int = 60,
                             hemisphere: Enum = Hemisphere.North,
                             **kwargs):
        # TODO: No evaluation of coordinate system made! May need if in
        # plotting to plot in radians/geo ect.
        '''
        Calculates potential across a magnetic lat/lon grid for
        plotting later

        Parameters
        ----------
            fit_coefficient: List[float]
                Value of the coefficient
            lat_min: List[float]
                Minimum latitude that will be evaluated
                Not to be confused with 'lowlat'
            lat_shift: int
                Generic shift in latitude from map file
                default: 0
            lon_shift: int
                Generic shift in longitude from map file
                default: 0
            fit_order: int
                order of the fit
                default: 6
            lowlat: int
                Lowest latitude on plot
                default: 60
            hemisphere: Enum
                Describes the hemisphere, North or South
                default: Hemisphere.North

        '''
        # Lowest latitude to calculate potential to
        theta_max = np.radians(90-np.abs(lat_min)) * hemisphere.value

        # Make a grid of the space the potential is evaluated on
        # in magnetic coordinates
        lat_step = 1
        lon_step = 2
        num_lats = int((90.0 - lowlat) / lat_step) + 1
        num_lons = int(360.0 / lon_step) + 1
        lat_arr = np.array(range(num_lats)) * lat_step + lowlat
        lon_arr = np.array(range(num_lons)) * lon_step

        # Set up Grid
        grid_arr = np.zeros((2, num_lats * num_lons))
        count1 = 0
        for lons in lon_arr:
            for lats in lat_arr:
                grid_arr[0, count1] = lats
                grid_arr[1, count1] = lons
                count1 += 1

        # Convert grid vals to spherical coords
        theta = np.radians(90.0 - np.abs(grid_arr[0, :]))
        phi = np.radians(grid_arr[1, :])

        # Adjusted/Normalised values (runs 0 - pi)
        alpha = np.pi / theta_max
        x = np.cos(alpha*theta)
        # Legendre Polys
        for j, xj in enumerate(x):
            plm_tmp = special.lpmn(fit_order, fit_order, xj)
            if j == 0:
                plm_fit = np.append([plm_tmp[0]], [plm_tmp[0]], axis=0)
            else:
                plm_fit = np.append(plm_fit, [plm_tmp[0]], axis=0)
        # Remove first element as it is duplicated to start off the array
        plm_fit = np.delete(plm_fit, 0, 0)

        # Eval the potential
        lmax = plm_fit.shape
        lmax = lmax[1]
        v = np.zeros(phi.shape)

        coeff_fit_flat = fit_coefficient.flatten()
        for m in range(lmax):
            for l in range(m, lmax):
                k = cls.index_legendre(l, m)
                if m == 0:
                    v = v + coeff_fit_flat[k] * plm_fit[:, 0, l]
                else:
                    v = v + coeff_fit_flat[k] * np.cos(m * phi) \
                          * plm_fit[:, m, l] + coeff_fit_flat[k+1] \
                          * np.sin(m * phi) * plm_fit[:, m, l]

        pot_arr = np.zeros((num_lons, num_lats))
        pot_arr = np.reshape(v, pot_arr.shape) / 1000.0

        # TODO: Account for lon_shift
        # TODO: Code for lat shift! (both rarely non-0 though)
        # grid_arr[1,:] = (grid_arr[1,:] + lon_shift)

        mlat_center = grid_arr[0, :].reshape((num_lons, num_lats))
        # Set everything below the latmin as 0
        ind = np.where(abs(mlat_center) < abs(lat_min))
        pot_arr[ind] = 0

        mlon_center = grid_arr[1, :].reshape((num_lons, num_lats))
        # Invert for Southern maps
        mlat_center = mlat_center * hemisphere.value

        return mlat_center, mlon_center, pot_arr


    @classmethod
    def plot_potential_contours(cls, fit_coefficient: list, lat_min: list,
                                date: object, ax: object, lat_shift: int = 0,
                                lon_shift: int = 0, fit_order: int = 6,
                                hemisphere: Enum = Hemisphere.North,
                                contour_levels: list = [],
                                contour_color: str = 'dimgrey',
                                contour_linewidths: float = 0.8,
                                contour_fill: bool = False,
                                contour_colorbar: bool = True,
                                contour_fill_cmap: str = 'RdBu',
                                contour_colorbar_label: str = 'Potential (kV)',
                                pot_minmax_color: str = 'k', **kwargs):
        # TODO: No evaluation of coordinate system made! May need if in
        # plotting to plot in radians/geo ect.
        '''
        Takes the grid of potentials, plots a contour plot and min and max
        potential positions

        Parameters
        ----------
            fit_coefficient: List[float]
                Value of the coefficient
            lat_min: List[float]
                Minimum latitude that will be evaluated
                Not to be confused with 'lowlat'
            date: datetime object
                Date from record
            ax: object
                matplotlib axis object
            lat_shift: int
                Generic shift in latitude from map file
                default: 0
            lon_shift: int
                Generic shift in longitude from map file
                default: 0
            fit_order: int
                order of the fit
                default: 6
            contour_levels: np.arr
                Array of values at which the contours
                are plotted
                Default: []
                Default list is defined in function due
                to length of the list, values higher or
                lower than the minimum and maximum values
                given are colored in as min and max color
                values if contour_fill=True
            contour_color: str
                Colour of the contour lines plotted
                Default: dimgrey
            contour_label: bool - NOT CURRENTLY IMPLEMENTED
                If contour_fill is True, contour labels will
                be plotted on the contour lines
                Default: True
            contour_linewidths: float
                Thickness of contour lines
                Default: 0.8
            contour_fill: bool
                Option to use filled contours rather than
                an outline. If True, contour_color and
                contour_linewidths are ignored
                If False
                Default: False
            contour_colorbar: bool
                Option to show the colorbar for the contours
                if contour_fill = True
                Default: True
            contour_fill_cmap: matplotlib.cm
                Colormap used to fill the contours if
                contour_fill is True
                Default: 'RdBu'
            contour_colorbar_label: str
                Label for the colorbar describing the
                contours if contour_fill is True
                Default: empty string ''
            pot_minmax_color: str
                Colour of the cross and plus symbols for
                minimum and maximum potentials
                Default: 'k' - black
            **kwargs
                including lowlat and hemisphere for calculating
                potentials
        '''
        mlat, mlon_u, pot_arr = cls.calculate_potentials(
                             fit_coefficient, lat_min,
                             lat_shift=lat_shift, lon_shift=lon_shift,
                             fit_order=fit_order, hemisphere=hemisphere,
                             **kwargs)

        # Shift mlon to MLT
        shifted_mlts = mlon_u[0, 0] - \
            (aacgmv2.convert_mlt(mlon_u[0, 0], date) * 15)
        shifted_lons = mlon_u - shifted_mlts
        mlon = shifted_lons

        # Contained in function as too long to go into the function call
        if contour_levels == []:
            contour_levels = [-100, -95, -90, -85, -80, -75, -70, -65, -60,
                              -55, -50, -45, -40, -35, -30, -25, -20, -15,
                              -10, -5, -1, 1, 5, 10, 15, 20, 25, 30, 35, 40,
                              45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]

        if contour_fill:
            # Filled contours
            plt.contourf(np.radians(mlon), mlat, pot_arr, 2,
                         vmax=abs(pot_arr).max(),
                         vmin=-abs(pot_arr).max(),
                         locator=ticker.FixedLocator(contour_levels),
                         cmap=contour_fill_cmap, alpha=0.5,
                         extend='both', zorder=3.0)
            if contour_colorbar is True:
                norm = colors.Normalize
                norm = norm(-abs(pot_arr).max(), abs(pot_arr).max())
                mappable = cm.ScalarMappable(norm=norm, cmap=contour_fill_cmap)
                locator = ticker.MaxNLocator(symmetric=True, min_n_ticks=3,
                                             integer=True, nbins='auto')
                ticks = locator.tick_values(vmin=-abs(pot_arr).max(),
                                            vmax=abs(pot_arr).max())
                cb = plt.colorbar(mappable, ax=ax, extend='both', ticks=ticks)
                if contour_colorbar_label != '':
                    cb.set_label(contour_colorbar_label)
        else:
            # Contour lines only
            cs = plt.contour(np.radians(mlon), mlat, pot_arr, 2,
                             vmax=abs(pot_arr).max(),
                             vmin=-abs(pot_arr).max(),
                             locator=ticker.FixedLocator(contour_levels),
                             colors=contour_color, alpha=0.8,
                             linewidths=contour_linewidths, zorder=3.0)
            # TODO: Add in contour labels
            # if contour_label:
            #    plt.clabel(cs, cs.levels, inline=True, fmt='%d', fontsize=5)

        # Get max value of potential
        ind_max = np.where(pot_arr == pot_arr.max())
        ind_min = np.where(pot_arr == pot_arr.min())
        max_mlon = mlon[ind_max]
        max_mlat = mlat[ind_max]
        min_mlon = mlon[ind_min]
        min_mlat = mlat[ind_min]

        plt.scatter(np.radians(max_mlon), max_mlat, marker='+', s=70,
                    color=pot_minmax_color, zorder=5.0)
        plt.scatter(np.radians(min_mlon), min_mlat, marker='_', s=70,
                    color=pot_minmax_color, zorder=5.0)
