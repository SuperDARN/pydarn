#  (C) Copyright 2021 SuperDARN Canada, University of Saskatachewan
#  Author(s): Marina Schmidt
#
# This file is part of the pyDARN Library.
#
# pyDARN is under the LGPL v3 license found in the root directory LICENSE.md
# Everyone is permitted to copy and distribute verbatim copies of this license
# document, but changing it is not allowed.
#
# This version of the GNU Lesser General Public License incorporates the terms
# and conditions of version 3 of the GNU Lesser General Public License,
# supplemented by the additional permissions listed below.
#
# Modifications:
#  2021-09-15 Francis Tholley moved the chisham and standard virtual heigh models to separate file for better encapsulation/modularity
""" virtual_heights.py comprises of different types of virtual heights"""

def chisham(slant_range: float):
    """
    Mapping ionospheric backscatter measured by the SuperDARN HF
    radars – Part 1: A new empirical virtual height model by
    G. Chisham 2008 (https://doi.org/10.5194/angeo-26-823-2008)
    """
    # Model constants
    A_const = (108.974, 384.416, 1098.28)
    B_const = (0.0191271, -0.178640, -0.354557)
    C_const = (6.68283e-5, 1.81405e-4, 9.39961e-5)

    # determine which region of ionosphere the gate
    if slant_range < 115:
        return (slant_range / 115.0) * 112.0
    elif slant_range < 787.5:
        return A_const[0] + B_const[0] * slant_range + C_const[0] *\
                 slant_range**2
    elif slant_range <= 2137.5:
        return A_const[1] + B_const[1] * slant_range + C_const[1] *\
                 slant_range**2
    else:
        return A_const[2] + B_const[2] * slant_range + C_const[2] *\
                 slant_range**2
                 
                 
def standard_virtual_height(slant_range: float, cell_height: float):
    """
    cell_height, slant_range and x_height are in km
    Default values set in virtual height model described
    Mapping ionospheric backscatter measured by the SuperDARN HF
    radars – Part 1: A new empirical virtual height model by
    G. Chisham 2008
    Equation (1) in the paper
    < 150 km climbing into the E region
    150 - 600 km E region scatter
    (Note in the paper 400 km is the edge of the E region)
    600 - 800 km is F region
    """
    # TODO: why 115?
    # map everything into the E region
    if cell_height <= 150 and slant_range > 150:
        return cell_height
    # virtual height equation (1) from the above paper
    elif slant_range < 150:
        return (slant_range / 150.0) * 115
    elif slant_range >= 150 and slant_range <= 600:
        return 115
    elif slant_range > 600 and slant_range < 800:
        return (slant_range - 600) / 200 * (cell_height - 115) + 115
    # higher than 800 km
    else:
        return cell_height       
                  
