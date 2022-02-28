# (C) Copyright 2021 SuperDARN Canada, University of Saskatchewan
# Author(s): Marina Schmidt
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

import enum
from pydarn import gate2slant, gate2groundscatter

class Range_Estimation(enum.Enum):
    """
    Range_Estimation class is to list the current range gate estimations
    a user can pick from

    enumerators:
        RANGE_GATE: range gates
        SLANT_RANGE: slant range (km)
        GSMR: ground scatter mapped range (km)
    """

    RANGE_GATE = enum.auto()
    SLANT_RANGE = gate2slant
    GSMR = gate2groundscatter
