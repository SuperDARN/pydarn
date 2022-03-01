# Copyright (C) 2021 SuperDARN Canada, University of Saskatchewan
# Author: Marina Schmidt
# Copyright (C) 2012  VT SuperDARN Lab
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
Grid plots, mapped to AACGM coordinates in a polar format
"""

import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import warnings

from enum import Enum
from matplotlib import ticker, cm, colors
from scipy import special
from typing import List

# Third party libraries
import aacgmv2

from pydarn import (PyDARNColormaps, plot_exceptions, citing_warning,
                    standard_warning_format, Re, Hemisphere,
                    time2datetime, find_record, Fan, MapParams, Projections)

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
                     len_factor: float = 150, cmap: str = None,
                     colorbar: bool = True, colorbar_label: str = '',
                     title: str = '', zmin: float = None, zmax: float = None,
                     hmb: bool = True, **kwargs):
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

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # TODO: Make FOV outlines optional or invisible
            for stid in dmap_data[record]['stid']:
                _, aacgm_lons, ax, _ =\
                        Fan.plot_fov(stid, date, ax=ax, **kwargs)
        if parameter == MapParams.MODEL_VELOCITY:
            data_lons = dmap_data[record]['model.mlon']
            data_lats = dmap_data[record]['model.mlat']
        else:
            data_lons = dmap_data[record]['vector.mlon']
            data_lats = dmap_data[record]['vector.mlat']

            # Hold the beam positions
            shifted_mlts = aacgm_lons[0, 0] - \
                (aacgmv2.convert_mlt(aacgm_lons[0, 0], date) * 15)
            shifted_lons = data_lons - shifted_mlts
            mlons = np.radians(shifted_lons)
            mlats = data_lats

        # If the parameter is velocity then plot the LOS vectors
        if parameter == MapParams.FITTED_VELOCITY:
            v_mag, azm_v =\
                    cls.calculated_fitted_velocities(mlats=mlats, mlons=np.radians(data_lons),
                                                     hemisphere=hemisphere,
                                                     fit_coefficient=dmap_data[record]['N+2'],
                                                     fit_order=dmap_data[record]['fit.order'],
                                                     lat_min=dmap_data[record]['latmin'],
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
            # Angle to "rotate" each vector by to get into same
            # reference frame Controlled by longitude, or "mltitude"
            alpha = mlons

            # Convert initial positions to Cartesian
            start_pos_x = (90 - mlats) * np.cos(mlons)
            start_pos_y = (90 - mlats) * np.sin(mlons)

            # Resolve LOS vector in x and y directions,
            # with respect to mag pole
            # Gives zonal and meridional components of LOS vector
            x = -v_mag * np.cos(-azm_v)
            y = -v_mag * np.sin(-azm_v)

            # Rotate each vector into same reference frame
            # following vector rotation matrix
            # https://en.wikipedia.org/wiki/Rotation_matrix
            vec_x = (x * np.cos(alpha)) - (y * np.sin(alpha))
            vec_y = (x * np.sin(alpha)) + (y * np.cos(alpha))

            # New vector end points, in Cartesian
            end_pos_x = start_pos_x + (vec_x / len_factor)
            end_pos_y = start_pos_y + (vec_y / len_factor)

            # Convert back to polar for plotting
            end_mlats = 90.0 - (np.sqrt(end_pos_x**2 + end_pos_y**2))
            end_mlons = np.arctan2(end_pos_y, end_pos_x)

            # Plot the vectomlats
            for i in range(len(v_mag)):
                plt.plot([mlons[i], end_mlons[i]],
                         [mlats[i], end_mlats[i]], c=cmap(norm(v_mag[i])),
                         linewidth=0.5)
        plt.scatter(mlons, mlats, c=v_mag, s=2.0,
                    vmin=zmin, vmax=zmax,  cmap=cmap, zorder=5.0)

        
        # Plot potential contours
        fit_coefficient = dmap_data[record]['N+2']
        fit_order = dmap_data[record]['fit.order']
        lat_shift = dmap_data[record]['lat.shft']
        lon_shift = dmap_data[record]['lon.shft']
        lat_min = dmap_data[record]['latmin']

        cls.plot_potential_contours(fit_coefficient, lat_min,
                             lat_shift=lat_shift, lon_shift=lon_shift, 
                             fit_order=fit_order, **kwargs)
        if hmb is True:
            # Plot the HMB
            mlats_hmb = dmap_data[record]['boundary.mlat']
            mlons_hmb = dmap_data[record]['boundary.mlon']
            cls.plot_heppner_maynard_boundary(mlats_hmb, np.radians(mlons_hmb))
        
        if colorbar is True:
            mappable = cm.ScalarMappable(norm=norm, cmap=cmap)
            locator = ticker.MaxNLocator(symmetric=True, min_n_ticks=3,
                                         integer=True, nbins='auto')
            ticks = locator.tick_values(vmin=zmin, vmax=zmax)

            cb = ax.figure.colorbar(mappable, ax=ax,
                                    extend='both', ticks=ticks)

            if colorbar_label != '':
                cb.set_label(colorbar_label)

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
        return (m == 0 and l**2) or \
                    ((l != 0) and (m != 0) and l**2 + 2 * m - 1) or 0


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
                        np.arctan2(velocity_fit_vectors[1,
                                                        velocity_chk_zero_inds],
                                   velocity_fit_vectors[0,
                                                        velocity_chk_zero_inds])
            else:
                azm_v[velocity_chk_zero_inds] =\
                        np.arctan2(velocity_fit_vectors[1,
                                                        velocity_chk_zero_inds],
                                   -velocity_fit_vectors[0,
                                                         velocity_chk_zero_inds])
        return velocity, azm_v


    @classmethod
    def plot_heppner_maynard_boundary(cls, mlats: list, 
                                      mlons: list, line_color: str='black'):
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

        """
        plt.plot(mlons,mlats, c=line_color, linewidth=1)


    @classmethod
    def calculate_potentials(cls, fit_coefficient: list, lat_min: list,
                             lat_shift: int=0, lon_shift: int=0, 
                             fit_order: int=6, lowlat: int=30, 
                             hemisphere: Enum = Hemisphere.North):
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
                default: 30
            hemisphere: Enum
                Describes the hemisphere, North or South
                default: Hemisphere.North
 
        '''
        # TODO: Do same updates Dan in doing for the fitted vels here
        # Lowest latitude to calculate potential to
        theta_max = np.radians(90-np.abs(lat_min))

        if hemisphere == Hemisphere.North:
            hemi = 1
        else:
            hemi = -1

        # Make a grid of the space the potential is evaluated on
        # in magnetic coordinates
        lat_step = 1
        lon_step = 2
        num_lats = int((90.0 - lowlat) / lat_step)
        num_lons = int(360.0 / lon_step) + 1
        lat_arr = np.array(range(num_lats)) * lat_step + lowlat
        lat_arr = lat_arr * hemi
        lon_arr = np.array(range(num_lons)) * lon_step

        # Set up Grid
        grid_arr = np.zeros((2,num_lats * num_lons))
        count1 = 0
        for lons in lon_arr:
            for lats in lat_arr:
                grid_arr[0, count1] = lats
                grid_arr[1, count1] = lons
                count1 += 1

        # Convert grid vals to spherical coords
        theta = np.radians(90.0 - np.abs(grid_arr[0,:]))
        phi = np.radians(grid_arr[1,:])

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
                    v = v + coeff_fit_flat[k] * plm_fit[:,0,l]
                else:
                    v = v + coeff_fit_flat[k] * np.cos(m * phi) * plm_fit[:,m,l] \
                          + coeff_fit_flat[k+1] * np.sin(m * phi) * plm_fit[:,m,l]

        pot_arr = np.zeros((num_lons, num_lats))
        pot_arr = np.reshape(v,pot_arr.shape) / 1000.0

        # TODO: Account for lon_shift
        # TODO: Code for lat shift! (both rarely non-0 though)
        # grid_arr[1,:] = (grid_arr[1,:] + lon_shift)

        mlat_center = grid_arr[0,:].reshape((num_lons,num_lats))
        # Set everything below the latmin as 0
        ind = np.where(mlat_center < lat_min)
        pot_arr[ind] = 0

        mlon_center = grid_arr[1,:].reshape((num_lons,num_lats))

        return mlat_center, mlon_center, pot_arr


    @classmethod
    def plot_potential_contours(cls, fit_coefficient: list, lat_min: list,
                             lat_shift: int=0, lon_shift: int=0, 
                             fit_order: int=6, **kwargs):
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
            lat_shift: int
                Generic shift in latitude from map file
                default: 0
            lon_shift: int
                Generic shift in longitude from map file
                default: 0
            fit_order: int
                order of the fit
                default: 6
            **kwargs
                including lowlat and hemisphere for calculating
                potentials
        '''
        mlat, mlon, pot_arr = cls.calculate_potentials(
                             fit_coefficient, lat_min,
                             lat_shift=lat_shift, lon_shift=lon_shift, 
                             fit_order=fit_order, **kwargs)

        # TODO: Other method to make ticker: this one is used to get the -1 1 
        # level but it's a hack. 
        # TODO: Assess colormaps
        # TODO: Edge color is annoying me, don't know how to remove it theres
        # currently a long issue on matplotlib github for this
        plt.contourf(np.radians(mlon), mlat, pot_arr, 2, vmax=abs(pot_arr).max(),
                            vmin=-abs(pot_arr).max(),
                            locator=ticker.FixedLocator(
                            [-100,-95,-90,-85,-80,-75,-70,-65,-60,-55,-50,-45,
                             -40,-35,-30,-25,-20,-15,-10,-5,-1,1,5,10,15,20,
                             25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100]),
                            cmap='PiYG', alpha=0.6)

        # Get max value of potential
        ind_max = np.where(pot_arr == pot_arr.max())
        ind_min = np.where(pot_arr == pot_arr.min())
        max_mlon = mlon[ind_max]
        max_mlat = mlat[ind_max]
        min_mlon = mlon[ind_min]
        min_mlat = mlat[ind_min]

        plt.scatter(np.radians(max_mlon),max_mlat,marker='+',s=70, color='k')
        plt.scatter(np.radians(min_mlon),min_mlat,marker='x',s=70, color='k')