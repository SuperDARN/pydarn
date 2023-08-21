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

# Ranges, Coords and Projs
---

pyDARN uses several different measurement and plotting systems to easily allow the user to customise their plots, this page aims to describe their uses: 
- Range Estimation: the estimate of how far the target (echo) is from the radar
- Coordinate systems: determines the unique position using a set of points - primarily we use geographic and magnetic coordinate systems for Earth
- Projections: used primarily on spatial plots (FOV, Fan, Grid...) projection choices allow the user to choose what type of projection the plot appears in

## RangeEstimation

**Range Gates**: `RangeEstimation.RANGE_GATE` a rectangle section determined by beam width and set distance for each range (nominally 45 km). RAWACF and FITACF data give their parameter values with respect to range gates. Range gates are a unit-less measure of estimating distance.

**Slant Range**: `RangeEstimation.SLANT_RANGE` is a conversion from range gates to km units.  Slant range estimates the distance of ionospheric echos from the radar, using the time it takes for the radio wave to travel to the ionosphere and return, assuming the radio wave is travelling at the speed of light. Measured in km.

**Half Slant**: `RangeEstimation.HALF_SLANT` is slant range divided by two, measured in km.

**Ground Scatter Mapped Range**: `RangeEstimation.GSMR` uses echos from ground scatter to adjust slant range coordinates to be more accurate based on [Dr. Bill Bristow's paper](https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1029/93JA01470). Implemented by Dr. Nathaniel Frissell and Francis Tholley from University of Scranton. Measured in km.

!!! Note
    Slant range is calculated from the value of `frang`, the distance to the first range gate. In pyDARN, we assume 
    that this value is the distance to the *inner edge* of the first range gate. We are aware that not all radars use this 
    exact definition, this is *outside the remit of pyDARN and should be addressed at a higher level*.
    The value `rxrise` is also used in the definition of slant range. This is the receiver rise time of the radar, however, 
    due to discussion *outside of pyDARN's remit* the value of `rxrise` is adjusted in FITACF files and may not match 
    the value given in hardware files. Currently, pyDARN has decided to use the values for `rxrise` given in the 
    hardware files. We will amend or reconsider this approach as and when a solution to the differing values is found.
    In some plots, the user can change the `frang` value to fit their needs.

## Coords

Used to determine the position of data in spatial plots: fan, grid and convection map plots
Range time plots now allow for `Coords` use. The y-axis can be converted to latitude, longitude or MLT using a the `coords` keyword.
E.G. using `coords=Coords.Geographic` and `lat_or_lon='lon'` in the method call will convert the chosen range estimate (see above) into Geographic Longitudes.

**Geographic**: `Coords.GEOGRAPHIC` is the standard geographical coordinate system for latitude and longitude (degrees)

**AACGM**: `Coords.AACGM` is [Altitude Adjusted Corrected Geogmagnetic Coordinates developed by Dr. Simon Shepherd](http://superdarn.thayer.dartmouth.edu/aacgm.html) are an extension of corrected geomagnetic (CGM) coordinates that more accurately represent the actual magnetic field. In AACGM coordinates points along a given magnetic field line are given the same coordinates and thus are a better reflection of magnetic conjugacy. pyDARN uses AACGM-V2 from the [aacgmv2 python library](https://pypi.org/project/aacgmv2/).

**AACGM_MLT**: `Coords.AACGM_MLT` is `Coords.AACGM` with the geomagnetic longitude converted to magnetic local time.

`RangeEstimation` methods can be used with a `Coords` calculation. For example, using `Coords.GEOGRAPHIC` and `RangeEstimation.GSMR` together, will give a plot of ionospheric echoes at a distance from the radar calculated in ground scatter mapped range, in geographic coordinates. 

## Projs

Spatial plots have two options for projections. 

**Polar**: `Projs.POLAR` sets up the axis of the spatial plot in polar coordinates common in studies that show data over the poles.

**Geographic**: `Projs.GEO` sets up the axes of the spatial plots in geographic coordinates using Cartopy.

!!! Note
    The 'look-direction' of the two projections are different for the Southern hemisphere. 
    Polar projections show a view of the south pole as if looking down through the planet from above the north pole, 
    geographic projections show a view of the south pole as if looking from above the south pole.

!!! Note
    Some combinations of Projs/Coords/RangeEstimates are not designed to work. 
    For example, you cannot plot a fan plot using range gates, spatial plots require a value in kilometers. 
    At the moment, AACGM Coordinates do not plot on Geographic projections as it has not been developed yet. 
    Convection maps only support polar projections due to lack of interest in requiring geographic projections.

# Including a Terminator

Spatial plots have the option to include a terminator called `nightshade` at a given height in the ionosphere. This functions uses the *Cartopy* `nightshade` function.
Nightshade is only available using the geographic projection and can be implemented by adding `nightshade=250` to the spacial plot call where 250 is the desired height in the
ionosphere to be in the Earth's shadow. If you would like to plot your own terminator on any plot, the `terminator` function will return the anti-sub-solar position and the 
great circle distance to the terminator in geographic coordinates:
```python
antisolarpsn, arc_length, angle_of_terminator = terminator(date, nightshade)
```
The `antisolarpsn` is given in degrees lon, lat. The `arc_length` is in kilometers and the `angle_of_terminator` is the angle from the subsolar point to the terminator (i.e. is 90 degrees at ground level).
The terminator position can be calculated using `(lat, lon) = new_coordinate(lat, lon, arc_length, bearing, R=Re)` for any bearing from the antisolar position. This can be converted to magnetic coordinates using the
AACGMv2 library. Unfortunately, matplotlib is unable to plot the terminator using `fill` consistently, hence we leave this option up to the user.
An example of this is shown below:
```python
import pydarn
import aacgmv2
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np

# North Winter
_,_,ax1,ccrs1=pydarn.Fan.plot_fov(66, dt.datetime(2023, 12, 21, 0, 0),
    lowlat= 5, boundary=True, line_color='red', coastline=True, nightshade=250)

# Test to plot terminator if ever required - plot line not fill!
# Get antisolar point in geographic coords and radius of terminator
# at given height
date = dt.datetime(2023, 12, 21, 0, 0)
antisolarpsn, arc, ang = pydarn.terminator(date, 250)
# Convert position to magnetic coordinates
mlat, lon_mag, _ =  aacgmv2.convert_latlon(antisolarpsn[1],
                                           antisolarpsn[0],
                                           250, date, method_code='G2A')
# Shift to MLT
shifted_mlts = lon_mag - (aacgmv2.convert_mlt(lon_mag, date) * 15)
shifted_lons = lon_mag - shifted_mlts
mlon = np.radians(shifted_lons)
# Get positions at a distance from new position to plot terminator
lats = []
lons = []
for b in range(-180,180,1):
    (lat, lon) = pydarn.new_coordinate(mlat, shifted_lons, arc, b, R=pydarn.Re)
    nlon =np.radians(lon)
    lats.append(lat)
    lons.append(nlon)
lats2 = np.zeros(len(lats))
plt.plot(np.squeeze(lons), np.squeeze(lats), color='b', zorder=2.0,
         linewidth=3.0, linestyle='dashed')

plt.show()
```