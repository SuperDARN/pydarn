# (C) Copyright 2021 University of Scranton
# Author(s): Francis Tholley
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
#

"""
virtual_heights_types.py is a group of methods that focus on the type of virtual heights
"""
import enum

class VH_types(enum.Enum):
    """
    This virtual height types class is to list the current virtual height systems
    a user can pick from

    enumerators:
        STANDARD_VIRTUAL_HEIGHT: Standard_Virtual_height (km)
        CHISHAM: chisham (km)
    """

    STANDARD_VIRTUAL_HEIGHT = enum.auto()
    CHISHAM = enum.auto()
   
