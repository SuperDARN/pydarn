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

def chisham(target_range: float, **kwargs):
    """
    Mapping ionospheric backscatter measured by the SuperDARN HF
    radars – Part 1: A new empirical virtual height model by
    G. Chisham 2008 (https://doi.org/10.5194/angeo-26-823-2008)

    Parameters
    ----------
    target_range: float
        is the range from radar to the target (echos)
        sometimes known as slant range [km]
    kwargs: is only needed to avoid key item errors

    Returns
    -------
    altered target_range (slant range) [km]
    """
    # Model constants
    A_const = (108.974, 384.416, 1098.28)
    B_const = (0.0191271, -0.178640, -0.354557)
    C_const = (6.68283e-5, 1.81405e-4, 9.39961e-5)

    # determine which region of ionosphere the gate
    if target_range < 115:
        return (target_range / 115.0) * 112.0
    elif target_range < 787.5:
        return A_const[0] + B_const[0] * target_range + C_const[0] *\
                 target_range**2
    elif target_range <= 2137.5:
        return A_const[1] + B_const[1] * target_range + C_const[1] *\
                 target_range**2
    else:
        return A_const[2] + B_const[2] * target_range + C_const[2] *\
                 target_range**2


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
    target_range: float
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
    # map everything into the E region
    if cell_height <= 150 and target_range > 150:
        return cell_height
    # virtual height equation (1) from the above paper
    elif target_range < 150:
        return (target_range / 150.0) * 115
    elif target_range >= 150 and target_range <= 600:
        return 115
    elif target_range > 600 and target_range < 800:
        return (target_range - 600) / 200 * (cell_height - 115) + 115
    # higher than 800 km
    else:
        return cell_height


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
