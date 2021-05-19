<!--Copyright (C) SuperDARN Canada, University of Saskatchewan 
Author(s): Marina Schmidt 
Modifications:

Disclaimer:
pyDARN is under the LGPL v3 license found in the root directory LICENSE.md 
Everyone is permitted to copy and distribute verbatim copies of this license 
document, but changing it is not allowed.

This version of the GNU Lesser General Public License incorporates the terms
and conditions of version 3 of the GNU General Public License, supplemented by
the additional permissions listed below.
-->

# Coordinate Systems 
---

pyDARN offers several different coordinate systems and units for plotting: 

## Range-Time Plots 

**Range Gates**: `Coords.RANGE_GATE` a rectangle section determined by beam width and set distance for each range (nominally 45 km). RAWACF and FITACF data give their parameter values with respect to range gates. Range gates are a unit-less measure of estimating distance.

**Slant Range**: `Coords.SLANT_RANGE` is a conversion from range gates to km units.  Slant range estimates the distance of ionospheric echos from the radar, using the time it takes for the radio wave to travel to the ionosphere and return, assuming the radio wave is travelling at the speed of light.

!!! Note
    Slant range is calculated from the value of `frang`, the distance to the first range gate. In pyDARN, we assume 
    that this value is the distance to the *inner edge* of the first range gate. We are aware that not all radars use this 
    exact definition, this is *outside the remit of pyDARN and should be addressed at a higher level*.
    The value `rxrise` is also used in the definition of slant range. This is the receiver rise time of the radar, however, 
    due to discussion *outside of pyDARN's remit* the value of `rxrise` is adjusted in FITACF files and may not match 
    the value given in hardware files. Currently, pyDARN has decided to use the values for `rxrise` given in the 
    hardware files. We will amend or reconsider this approach as and when a solution to the differing values is found.

**Ground Scatter Mapped Range**: `Coords.GROUND_SCATTER_MAPPED_RANGE` uses echos from ground scatter to adjust slant-range coordinates to be more accurate based on [Dr. Bill Bristow's paper](https://doi.org/10.1029/93JA01470). Implemented by Dr. Nathaniel Frissell and Francis Tholley from University of Scranton. Measured in km.

**Geographic Latitude** (Coming Soon)

**AACGM Latitude** (Coming Soon)

## Geographic Plots

Geographic plots include: fan, grid and convection map (coming soon) plots

**Geographic**: `Coords.GEOGRAPHIC` is the standard geographical coordinate system for latitude and longitude (degree) (coming soon)

**AACGM**: `Coords.AACGM` is [Altitude Adjusted Corrected Geogmagnetic Coordinates developed by Dr. Simon Shepherd](http://superdarn.thayer.dartmouth.edu/aacgm.html) are an extension of corrected geomagnetic (CGM) coordinates that more accurately represent the actual magnetic field. In AACGM coordinates points along a given magnetic field line are given the same coordinates and thus are a better reflection of magnetic conjugacy. pyDARN uses AACGM-V2 from the [aacgmv2 python library](https://pypi.org/project/aacgmv2/). Implemented by Dr. Daniel Billett from University of Saskatchewan. 

**Ground Scatter Mapped Geographic** (Coming Soon)

**Ground Scatter Mapped Geographic** (Coming Soon)
