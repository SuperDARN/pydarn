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
Grid plots, mapped to AACGM coordinates in a polar format
"""

import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
from scipy import special
import warnings
from matplotlib import ticker, cm, colors
# from typing import List

# Third party libraries
import aacgmv2


from pydarn import (PyDARNColormaps, Grid, plot_exceptions, citing_warning,
                    standard_warning_format, Re, Fan)

warnings.formatwarning = standard_warning_format


class Maps():
    """
    Maps plots for SuperDARN data

    Methods
    -------
    plot_maps
    """

    def __str__(self):
        return "This class is static class that provides"\
                " the following methods: \n"\
                "   - plot_maps()\n"

    @classmethod
    def plot_map(cls, dmap_data, ax=None, parameter="vector.vel.median",
                 record=0, start_time=None, time_delta: int = 1,  alpha=1.0,
                 len_factor=150, cmap=None, zmin=None, zmax=None, **kwargs):
        """
        """
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
            record = 0
            date = dt.datetime(dmap_data[record]['start.year'],
                               dmap_data[record]['start.month'],
                               dmap_data[record]['start.day'],
                               dmap_data[record]['start.hour'],
                               dmap_data[record]['start.minute'])

        if cmap is None:
            cmap = {'fitted': 'plasma',
                    'vector.vel.median': 'plasma_r',
                    'vector.wdt.median': PyDARNColormaps.PYDARN_VIRIDIS}
            cmap = plt.cm.get_cmap(cmap[parameter])
        # Setting zmin and zmax
        defaultzminmax = {'fitted': [0, 50],
                          'vector.vel.median': [0, 1000],
                          'vector.wdt.median': [0, 250]}
        if zmin is None:
            zmin = defaultzminmax[parameter][0]
        if zmax is None:
            zmax = defaultzminmax[parameter][1]

        norm = colors.Normalize
        norm = norm(zmin, zmax)

        for stid in dmap_data[record]['stid']:
            _, aacgm_lons, _, _, ax =\
                    Fan.plot_fov(stid, date,
                                 ax=ax, **kwargs)
            data_lons = dmap_data[record]['vector.mlon']
            data_lats = dmap_data[record]['vector.mlat']

            # Hold the beam positions
            shifted_mlts = aacgm_lons[0, 0] - \
                (aacgmv2.convert_mlt(aacgm_lons[0, 0], date) * 15)
            shifted_lons = data_lons - shifted_mlts
            mlons = np.radians(shifted_lons)
            mlats = data_lats

        # If the parameter is velocity then plot the LOS vectors
        if parameter == "fitted":
            # Get the velocity data and magnetic coordinates
            azm_v = dmap_data[record]['vector.kvect']
            # velocities = dmap_data[record]['vector.vel.median']
            hemisphere = dmap_data[record]['hemisphere']
            fit_coefficient = dmap_data[record]['N+2']
            fit_order = dmap_data[record]['fit.order']
            # lat_shift = np.deg2rad(dmap_data[record]['lat.shft'])
            # lon_shift = np.deg2rad(dmap_data[record]['lon.shft'])
            lat_min = dmap_data[record]['latmin']

            theta = np.radians(90 - abs(mlats))
            theta_max = np.radians(90 - abs(lat_min))

            # Angle to "rotate" each vector by to get into same
            # reference frame Controlled by longitude, or "mltitude"
            alpha = np.pi / theta_max
            theta_prime = alpha * theta
            x = np.cos(theta_prime)

            for j, xj in enumerate(x):
                temp_poly = special.lpmn(fit_order, fit_order, xj)
                if j == 0:
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
            def index_legendre(m, l):
                if m == 0:
                    return l**2
                elif l != 0 and m != 0: # this seem redundant?
                    return l**2 + 2 * m - 1
                else:
                    return 0

            k_max = index_legendre(fit_order, fit_order)

            # set up arrays and small stuff for the eFld coeffs calculation
            theta_ecoeffs = np.zeros((k_max + 2, len(theta)))
            phi_ecoeffs = np.zeros((k_max + 2, len(theta)))

            q_prime = np.array(np.where(theta_prime != 0.0))
            q_prime = q_prime[0]
            q = np.array(np.where(theta != 0.0))
            q = q[0]

            # finally get to converting coefficients for the potential into
            # coefficients for elec. Field
            fit_coefficient_flat = fit_coefficient.flatten()
            for m in range(fit_order + 1):
                for l in range(m, fit_order + 1):
                    k3 = index_legendre(l, m)
                    k4 = index_legendre(l, m)

                    if k3 >= 0:
                        theta_ecoeffs[k4, q_prime] =\
                                theta_ecoeffs[k4, q_prime] -\
                                fit_coefficient_flat[k3] * alpha * l *\
                                np.cos(theta_prime[q_prime]) \
                                / np.sin(theta_prime[q_prime]) / Re
                        phi_ecoeffs[k4, q] = phi_ecoeffs[k4, q] - \
                            fit_coefficient_flat[k3 + 1] * m /\
                            np.sin(theta[q]) / Re
                        phi_ecoeffs[k4 + 1, q] = phi_ecoeffs[k4 + 1, q] + \
                            fit_coefficient_flat[k3] * m /\
                            np.sin(theta[q]) / Re

                    if l < fit_order:
                        k1 = index_legendre(l+1, m)
                    else:
                        k1 = -1

                    k2 = index_legendre(l, m)

                    if k1 >= 0:
                        theta_ecoeffs[k2, q_prime] =\
                            theta_ecoeffs[k2, q_prime] + \
                            fit_coefficient_flat[k1] * alpha * (l + 1 + m) / \
                            np.sin(theta_prime[q_prime]) / Re

                    if m > 0:
                        if k3 >= 0:
                            k3 = k3 + 1
                        k4 = k4 + 1

                        if k1 >= 0:
                            k1 = k1 + 1
                        k2 = k2 + 1

                        if k3 >= 0:
                            theta_ecoeffs[k4, q_prime] =\
                                    theta_ecoeffs[k4, q_prime] \
                                    - fit_coefficient_flat[k3] * alpha * l * \
                                    np.cos(theta_prime[q_prime]) / \
                                    np.sin(theta_prime[q_prime]) / Re

                        if k1 >= 0:
                            theta_ecoeffs[k2, q_prime] = \
                                theta_ecoeffs[k2, q_prime] \
                                + fit_coefficient_flat[k1] * alpha *\
                                (l + 1 + m) / np.sin(theta_prime[q_prime]) / Re

            # Calculate the Elec. fld positions where
            theta_ecomp = np.zeros(theta.shape)
            phi_ecomp = np.zeros(theta.shape)

            for m in range(fit_order + 1):
                for l in range(m, fit_order + 1):
                    k = index_legendre(l, m)
                    # Now in the IDL code we use
                    # legendre_poly[:,l,m] instead of
                    # legendre_poly[:,m,l] like here, this is
                    # because we have a different
                    # organization of legendre_poly due to the
                    # way scipy.special.lpmn
                    # stores values in arrays...
                    if m == 0:
                        theta_ecomp = theta_ecomp + theta_ecoeffs[k, :] * \
                                legendre_poly[:, m, l]
                        phi_ecomp = phi_ecomp + phi_ecoeffs[k, :] * \
                            legendre_poly[:, m, l]
                    else:
                        theta_ecomp = theta_ecomp + theta_ecoeffs[k, :] * \
                            legendre_poly[:, m, l] * np.cos(m * phi) + \
                            theta_ecoeffs[k+1, :] * legendre_poly[:, m, l] * \
                            np.sin(m * phi)
                        phi_ecomp = phi_ecomp + phi_ecoeffs[k, :] * \
                            legendre_poly[:, m, l] * np.cos(m * phi) + \
                            phi_ecoeffs[k+1, :] * legendre_poly[:, m, l] * \
                            np.sin(m * phi)

            # Store the two components of EFld into a single array
            efield_fit = np.append([theta_ecomp], [phi_ecomp], axis=0)

            # We'll calculate Bfld magnitude now, need to initialize some more
            # stuff
            alti = 300.0 * 1000.0
            b_fld_polar = -0.62e-4
            b_fld_mag = b_fld_polar * (1.0 - 3.0 * alti / Re) \
                * np.sqrt(3.0 * np.square(np.cos(theta)) + 1.0) / 2

            # get the velocity components from E-field
            vel_fit_vecs = np.zeros(efield_fit.shape)
            vel_fit_vecs[0, :] = efield_fit[1, :] / b_fld_mag
            vel_fit_vecs[1, :] = -efield_fit[0, :] / b_fld_mag

            vel_mag = np.sqrt(np.square(vel_fit_vecs[0, :]) +
                              np.square(vel_fit_vecs[1, :]))
            vel_chk_zero_inds = np.where(vel_mag != 0.0)
            vel_chk_zero_inds = vel_chk_zero_inds[0]

            azm_v = np.zeros(vel_mag.shape)

            if len(vel_chk_zero_inds) == 0:
                vel_mag = np.array([0.0])
                azm_v = np.array([0.0])
            else:
                if hemisphere == -1:
                    azm_v[vel_chk_zero_inds] =\
                            np.rad2deg(np.arctan2(vel_fit_vecs[1, vel_chk_zero_inds],
                                                  vel_fit_vecs[0, vel_chk_zero_inds]))
                else:
                    azm_v[vel_chk_zero_inds] =\
                            np.rad2deg(np.arctan2(vel_fit_vecs[1, vel_chk_zero_inds],
                                                  -vel_fit_vecs[0, vel_chk_zero_inds]))



        for nn, nn_mlats in enumerate(mlats):
            vec_len = vel_mag[nn] * len_factor / Re / 1000.0
            end_lat = np.arcsin(np.sin(nn_mlats) * np.cos(vec_len) +
                                np.cos(nn_mlats) * np.sin(vec_len) *
                                np.cos(azm_v[nn]))
            end_lat = np.degrees(end_lat)

            del_lon = np.arctan2(np.sin(azm_v[nn]) *
                                 np.sin(vec_len) * np.cos(nn_mlats),
                                 np.cos(vec_len) - np.sin(nn_mlats)
                                 * np.sin(np.deg2rad(end_lat)))

            end_lon = mlons[nn] + del_lon

            x_vec_strt = mlons[nn]
            y_vec_strt = nn_mlats
            x_vec_end = end_lon
            y_vec_end = end_lat
            plt.scatter(x_vec_strt, y_vec_strt, c=vel_mag[nn], s=2.0,
                        vmin=zmin, vmax=zmax,  cmap=cmap, zorder=5.0)

            #plt.plot([x_vec_strt, x_vec_end], [y_vec_strt, y_vec_end],
            #         c=cmap(norm(vel_mag[nn])))
           # ax.scatter(theta, rs, c=vel_mag),
           #            s=2.0, vmin=zmin, vmax=zmax, zorder=5, cmap=cmap)
