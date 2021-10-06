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

# import datetime as dt
# import matplotlib.pyplot as plt
import numpy as np
from scipy import special
import warnings
import matplotlib.pyplot as plt
from matplotlib import ticker, cm, colors
# from typing import List

# Third party libraries
# import aacgmv2


from pydarn import (PyDARNColormaps, Grid, plot_exceptions, citing_warning,
                    standard_warning_format, Re)

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
    def plot_map(cls, dmap_data, parameter="vector.vel.median",
                 alpha=1.0, len_factor=500, **kwargs):
        """
        """

        # If the parameter is velocity then plot the LOS vectors
        if parameter == "fitted":
            record = 0
            # Get the velocity data and magnetic coordinates
            azm_v = dmap_data[record]['vector.kvect']
            mlat = np.deg2rad(dmap_data[record]['vector.mlat'])
            mlon = np.deg2rad(dmap_data[record]['vector.mlon'])
            # velocities = dmap_data[record]['vector.vel.median']
            hemisphere = dmap_data[record]['hemisphere']
            fit_coefficient = dmap_data[record]['N+2']
            fit_order = dmap_data[record]['fit.order']
            # lat_shift = np.deg2rad(dmap_data[record]['lat.shft'])
            # lon_shift = np.deg2rad(dmap_data[record]['lon.shft'])
            lat_min = np.deg2rad(dmap_data[record]['latmin'])

            theta = np.pi/2 - abs(mlat)
            theta_max = np.pi/2 - lat_min

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
            phi = mlon

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
                elif fit_order != 0 and fit_order != 0:
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
            # Plot the vectors
            for i in range(len(theta)):
                plt.plot([theta[i], azm_v[i]],
                         [vel_fit_vecs[i], vel_mag[i]])

