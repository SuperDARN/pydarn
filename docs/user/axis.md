# Axes Setup 

For some spatial plots (FOV, Fan, Grid), pyDARN allows users to choose between Polar and
Geographic axes using the `projs` keyword and `Projs` module.
Convection maps do not allow for geographic projections due to lack of interest.

## Projs.POLAR 

| Option                       | Action                                                            |
| ---------------------------- | ----------------------------------------------------------------- |
| lowlat=(int)                 | Lower Latitude boundary for the polar plot (degree) (default: 30) |
| hemisphere=(pydarn.Hemisphere) | Hemisphere of the radar (default: Hemisphere.North)             |
| coastline=(bool)             | Uses Cartopy to add outlines fo the coastlines below data         |


This choice will return an `ax` object and a value of None for `ccrs`.

## Projs.GEO

**REQUIRES CARTOPY INSTALLATION**

| Option                       | Action                                                            |
| ---------------------------- | ----------------------------------------------------------------- |
| lowlat=(int)                 | Lower Latitude boundary for the polar plot (degree) (default: 30) |
| hemisphere=(pydarn.Hemisphere) | Hemisphere of the radar (default: Hemisphere.North)             |
| coastline=(bool)             | Uses Cartopy to add outlines fo the coastlines below data         |
| grid_lines=(bool)            | Uses Cartopy to plot grid lines                                   |

This choice will return an `ax` object and a Cartopy `ccrs` object.

## Custom Axes
pyDARN does not currently support use of custom axes to read in and plot on. This means
that use of subplots is not supported. There are ways to get around this if a custom axis
that has the same setup as either axes above is read into the subplot. For example, a polar
and a geographic plots can be positioned using subplots as follows:

```python
import pydarn
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt 
import cartopy.crs as ccrs

# Polar plot
date=dt.datetime(2022, 1, 8, 14, 5)
fig = plt.figure(figsize=(6, 6)) 
ax1 = fig.add_subplot(121, projection='polar')
ax1.set_ylim(90, 30)
ax1.set_yticks(np.arange(30, 90, 10))
ax1.set_xticks([0, np.radians(45), np.radians(90), np.radians(135),
                       np.radians(180), np.radians(225), np.radians(270),
                       np.radians(315)])
ax1.set_xticklabels(['00', '', '06', '', '12', '', '18', ''])
ax1.set_theta_zero_location("S")
pydarn.Fan.plot_fov(stid=65, date=date, ax=ax1)

# Geo plot
deg_from_midnight = (date.hour + date.minute / 60) / 24 * 360
pole_lat = 90
noon = -deg_from_midnight
ylocations = -5
proj = ccrs.Orthographic(noon, pole_lat)
ax2 = fig.add_subplot(122, projection=proj, aspect='auto')
ax2.gridlines(draw_labels=True)
extent = min(45e5,(abs(proj.transform_point(noon, 30, ccrs.PlateCarree())[1])))
ax2.set_extent(extents=(-extent, extent, -extent, extent), crs=proj)
pydarn.Fan.plot_fov(stid=65, date=date, ax=ax2, ccrs=ccrs, coords=pydarn.Coords.GEOGRAPHIC, projs=pydarn.Projs.GEO)
plt.tight_layout()
plt.show()
```

![](../imgs/subplots.png)
