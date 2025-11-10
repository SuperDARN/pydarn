# Retrieving Data from Convection Map plots
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

Finally, choose the magnetic latitude(s) and longitude(s) you want to get values for:
```python
mlats = [75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85]
mlons = np.radians([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]) # Make sure you use radians! It doesn't matter in this case, as I'm using zero longitude
```

Note that for deriving the velocity and electric potential, we need some parameters of the convection map fit itself. This includes the spherical harmonic coefficients, fit order, latitude and longitude shift, minimum latitude, and hemisphere. For more details on these parameters, see [the RST documentation](https://radar-software-toolkit-rst.readthedocs.io/en/develop/references/general/map/).

### Convection map velocities

To get the velocity magnitude and azimuth (angle from north), we'll use the inbuilt pyDARN function `calculated_fitted_velocities()`, using list comprehension to loop through the fitting parameters required for input:

```python
velocity, azm = zip(*[pydarn.Maps.calculated_fitted_velocities(mlats, # We zip it like this to pull out the velocity and azimuth arrays separately
                                                               mlons,
                                                               map_data[rec]['N+2'],
                                                               pydarn.Hemisphere(map_data[rec]['hemisphere']),
                                                               map_data[rec]['fit.order'],
                                                               map_data[rec]['lat.shft'])
                  for rec in rec_indexes])
velocity, azm = np.array(velocity), np.array(azm)

```
Note that the `velocity` and `azm` variables produced here are 31x11 arrays, because we've gotten velocities for 31 records at 11 different positions. Your array sizes will vary based on your needs, or will be single values or lists if you have one coordinate of interest.

As a final step, it's important to set all velocities below the minimum of the map to zero (the spherical harmonic fit is cyclic with latitude, so we want to limit derived velocities to above the Heppner-Maynard boundary):
```python
for counter, rec in enumerate(rec_indexes): # Iterate over the records
    rec_vels = velocity[counter] # Grab the velocities for all coordinates for just this record
    rec_vels[np.where(mlats < map_data[rec]['latmin'])] = 0 # Set all velocities below the minimum latitude to zero
    velocity[counter] = rec_vels # Put back in the array
```

As an optional step, you can derive the velocity in terms of east-west (zonal) and north-south (meridional) components by simply resolving the vectors:
```python
v_n = velocity * np.cos(azm) # Northward velocity
v_e = velocity * np.sin(azm) # Eastward velocity
```

### Convection map potentials

Deriving the electric potentials at a specific coordinate is similar to deriving the velocity. We use the `calculate_potentials_pos()` function:
```python
potential = ([pydarn.Maps.calculate_potentials_pos(mlats, # No zipping required as the potential is a scalar
                                                   mlons,
                                                   map_data[rec]['N+2'],
                                                   map_data[rec]['latmin'],
                                                   map_data[rec]['lat.shft'],
                                                   map_data[rec]['lon.shft'],
                                                   map_data[rec]['fit.order'],
                                                   pydarn.Hemisphere(map_data[rec]['hemisphere']))[0]
                  for rec in rec_indexes])
```
Don't forget to set potentials below the minimum latitude to zero, like the velocities:
```python
for counter, rec in enumerate(rec_indexes):
    rec_pots = potential[counter]
    rec_pots[np.where(mlats < map_data[rec]['latmin'])] = 0
    potential[counter] = rec_pots
```


