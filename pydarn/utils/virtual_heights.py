# (C) Copyright 2021 SuperDARN Canada, University of Saskatachewan
# Author(s): Marina Schmidt
# (C) Copyright 2021 University of Scranton
# Author(s): Francis Tholley
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
#  2021-09-15 Francis Tholley moved the chisham and standard virtual
#  height models to separate file for better encapsulation/modularity
#  2022-03-04 Marina Schmidt add the VH_Types class to the bottom
""" virtual_heights.py comprises of different of virtual height models"""
import enum
import numpy as np

def chisham(target_range: float, **kwargs):
    """
    Mapping ionospheric backscatter measured by the SuperDARN HF
    radars – Part 1: A new empirical virtual height model by
    G. Chisham 2008 (https://doi.org/10.5194/angeo-26-823-2008)

    Parameters
    ----------
    target_range: float or np.array
        is the range from radar to the target (echos)
        sometimes known as slant range [km]
    kwargs: is only needed to avoid key item errors

    Returns
    -------
    altered target_range (slant range) [km]
    """

    # Check for single inputs - will convert back at the end so it doesn't break upstream code
    is_scalar = np.isscalar(target_range)
    x = np.asarray(target_range, dtype=float)
    result = np.empty_like(x)

    # Model constants
    A_const = (108.974, 384.416, 1098.28)
    B_const = (0.0191271, -0.178640, -0.354557)
    C_const = (6.68283e-5, 1.81405e-4, 9.39961e-5)

    # Determine which region of ionosphere the gate is from
    m1 = x < 115
    result[m1] = (x[m1] / 115.0) * 112.0

    m2 = (x >= 115) & (x < 787.5)
    result[m2] = A_const[0] + B_const[0] * x[m2] + C_const[0] * x[m2] ** 2

    m3 = (x >= 787.5) & (x <= 2137.5)
    result[m3] = A_const[1] + B_const[1] * x[m3] + C_const[1] * x[m3] ** 2

    m4 = x > 2137.5
    result[m4] = A_const[2] + B_const[2] * x[m4] + C_const[2] * x[m4] ** 2

    # If it was a single range, convert it back
    return result.item() if is_scalar else result


def standard_virtual_height(target_range: float, cell_height: int = 300,
                            **kwargs):
    """
    cell_height, target_range and x_height are in km
    Default values set in virtual height model described
    Mapping ionospheric backscatter measured by the SuperDARN HF
    radars – Part 1: A new empirical virtual height model by
    G. Chisham 2008
    Equation (1) in the paper
    < 150 km climbing into the E region
    150 - 600 km E region scatter
    (Note in the paper 400 km is the edge of the E region)
    600 - 800 km is F region

    Parameters
    ----------
    target_range: float or np.array
        is the range from radar to the target (echos)
        sometimes known as slant range [km]
    cell_height: int
        the default height of the echo if the target_range
        is within a certain range
    kwargs: is only needed to avoid key item errors

    Returns
    -------
    altered target_range (slant range) [km]
    """
    # TODO: why 115?

    # Check for single inputs - will convert back at the end so it doesn't break upstream code
    is_scalar = np.isscalar(target_range) and np.isscalar(cell_height)
    # broadcasting handles if ones a float and ones an array
    x, ch = np.broadcast_arrays(target_range, cell_height)
    x = x.astype(float)
    ch = ch.astype(float)
    result = np.empty_like(x)

    # map everything into the E region
    m1 = (ch <= 150) & (x > 150)
    result[m1] = ch[m1]

    # virtual height equation (1) from the above paper
    # (m1 requires x > 150, so m1 and m2 can never overlap. No need to exclude m1.)
    m2 = x < 150
    result[m2] = (x[m2] / 150.0) * 115

    # (x >= 150 CAN overlap with m1, so we explicitly exclude m1)
    m3 = (~m1) & (x >= 150) & (x <= 600)
    result[m3] = 115

    m4 = (~m1) & (x > 600) & (x < 800)
    result[m4] = (x[m4] - 600) / 200.0 * (ch[m4] - 115) + 115

    #  higher than 800 km, just what's left
    m5 = ~(m1 | m2 | m3 | m4)
    result[m5] = ch[m5]

    # If it was a single range, convert it back
    return result.item() if is_scalar else result



class VHModels(enum.Enum):
    """
    This virtual height models class is to list the current
    virtual height model user can pick from

    enumerators:
        STANDARD: Standard_Virtual_height (km)
        CHISHAM: chisham (km)
    """

    STANDARD = (standard_virtual_height, )
    CHISHAM = (chisham, )

    # Need this to make the functions callable
    def __call__(self, *args, **kwargs):
        return self.value[0](*args, **kwargs)
