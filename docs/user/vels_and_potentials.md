# Getting convection map velocities and potentials
---

This tutorial is for getting the derived SuperDARN fitted velocities and electric potentials from a convection map file (`.map` extension) at any location. Note that these are **fitted** parameters, based on accessing the Map Potential spherical harmonic solution to the line-of-sight velocities located in `.fitacf` format files. To look at data from fitacf files, see the [Range-Time Parameter Plots](range_time.md) and [Fan plots](fan.md) tutorials.

We start by reading in the map file the standard way:
```python
import pydarn

# Read in a map file into the `map_data` list of dictionaries
mapfile = '/Users/danielbillett/Data/20220201.n.map'  # Change to where you keep your maps
SDarn_read = pydarn.SuperDARNRead(mapfile)
map_data = SDarn_read.read_map()
```

Before grabbing velocities and/or potentials, we need to know which record(s) of the file to access. If you have a specific time range in mind, you can find the associated records:
```python
import datetime as dt
import numpy as np

start_time = dt.datetime(2022, 2, 1, 3, 30)
end_time = dt.datetime(2022, 2, 1, 4, 30)

# Get all the record times in the file
record_times = np.array([dt.datetime(rec_map['start.year'],
                                     rec_map['start.month'],
                                     rec_map['start.day'],
                                     rec_map['start.hour'],
                                     rec_map['start.minute'])
                for rec_map in map_data])

# Gets the records between and including start_time and end_time
rec_indexes = np.where((record_times >= start_time) & (record_times <= end_time))[0].tolist() 
```

Now we need some paramaters of the convection map fit itself in order to derive the associated velocity and electric potential. This includes the spherical harmonic coefficients, fit order, latitude and longitude shift, minimum latitude, and hemisphere. For more detail on these parameters, see [the RST documentation](https://radar-software-toolkit-rst.readthedocs.io/en/develop/references/general/map/):

```python
# Get lists of all the parameters needed from the map potential fits
# If you only want a single record, just replace "rec" with the relevant index and remove the list comprehension
fit_coefficient = [map_data[rec]['N+2'] for rec in rec_indexes]
fit_order = [map_data[rec]['fit.order'] for rec in rec_indexes]
lat_shift = [map_data[rec]['lat.shft'] for rec in rec_indexes]
lon_shift = [map_data[rec]['lon.shft'] for rec in rec_indexes]
lat_min = [map_data[rec]['latmin'] for rec in rec_indexes]
hemisphere = [pydarn.Hemisphere(map_data[rec]['hemisphere']) for rec in rec_indexes]
```

Finally, choose the magnetic latitude(s) and longitude(s) you want to get values for:
```python
mlats = [75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85]
mlons = np.radians([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]) # Make sure you use radians! It doesn't matter in this case as I'm using zero longitude.
```

### Convection map velocities

To get the velocities, we'll use the inbuilt pyDARN function `calculated_fitted_velocities()`, using list comprehension to loop through the fitting parameters required for input:

```python
velocity, azm = zip(*[pydarn.Maps.calculated_fitted_velocities(mlats,
                                                               mlons,
                                                               map_data[rec]['N+2'],
                                                               pydarn.Hemisphere(map_data[rec]['hemisphere']),
                                                               map_data[rec]['fit.order'],
                                                               map_data[rec]['lat.shft'])
                  for rec in rec_indexes])
velocity, azm = np.array(velocity), np.array(azm)

```
Note that the `velocity` and `azm` variables produced here are 31x11 arrays, because we've gotten velocities for 31 records at 11 different positions. Your array sizes will vary based on your needs, or will just be single values or lists if you have one coordinate of interest.

If you want the velocity in terms of east-west (zonal) and north-south (meridional) components, you can simply resolve the vectors:
```python
v_n = velocity * np.cos(azm) # Northward velocity
v_e = velocity * np.sin(azm) # Eastward velocity
```

