# Copyright (C) 2022 SuperDARN Canada, University of Saskatchewan
# Author: Shibaji Chakraborty
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

import bz2
import datetime as dt
import matplotlib.pyplot as plt
import warnings

import pydarn

with bz2.open('test/data/boxcar.sas.fitacf.bz2') as fp:
    fitacf_stream = fp.read()
beam_sounds = pydarn.SuperDARNRead(fitacf_stream, True).read_fitacf()

import sys
sys.path.append("pydarn/utils/")
from boxcar_filter import Boxcar

bx = Boxcar(
    thresh=0.7,
    w=None
)
bx.run_filter(beam_sounds)