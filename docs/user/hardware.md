<!--Copyright (C) SuperDARN Canada, University of Saskatchewan 
Author(s): Marina Schmidt, Daniel Billett
Modifications:
2020-12-01 Carley Martin added git_hdw_file
2020-01-05 Marin Schmidt switched VT hardware repo to SuperDARN hardware repo

Disclaimer:
pyDARN is under the LGPL v3 license found in the root directory LICENSE.md 
Everyone is permitted to copy and distribute verbatim copies of this license 
document, but changing it is not allowed.

This version of the GNU Lesser General Public License incorporates the terms
and conditions of version 3 of the GNU General Public License, supplemented by
the additional permissions listed below.
-->
# Accessing Hardware File Information 

SuperDARN Radar hardware information is stored in hardware files located [here](https://github.com/SuperDARN/hdw). 
pyDARN pulls down the hardware files from the `main` branch on the [repository](https://github.com/SuperDARN/hdw) to obtain geographical and hardware information for plotting functionality. 

Users can also read and access these hardware files information by using the function `read_hdw_file`.
``` python 
import pydarn

# Read Saskatoon's hardware file
hdw_data = pydarn.read_hdw_file('sas')
print(hdw_data.geographic)
```
expected output: 
``` python 
_Coord(lat=52.16, lon=-106.53, alt=494.0)
```

A user also has the ability to pull down hardware information for a specific date:
``` python
import pydarn
from datetime import datetime

# Read Goose Bay radars hardware file for 2003 03 20
hdw_data = pydarn.read_hdw_file('gbr', datetime(2003 3, 20))
print(hdw_data.gates)
```

Expected output: 
``` python
75
```

Other information a user can access from the `_HdwInfo` object is:

| Field name              | Description                                                                                                                                                                     |
| :---:                   | :---                                                                                                                                                                            |
| `stid`                  | Station Id of the radar                                                                                                                                                         |
| `abbrev`                | 3 letter radar abbreviation                                                                                                                                                     |
| `date`                  | Date the hardware specifications were changed                                                                                                                                   | 
| `geographic`            | Geographic coordinates of the radar and altitude in meters (lat, long, alt)                                                                                                     |
| `boresight`             | Boresight of the centre beam (physical, electronic)                                                                                                                             |
| `beam_separation`       | Angular separation between radar beams in degrees                                                                                                                               |
| `velocity_sign`         | To help identify backscatter velocities which the signs can be reversed based on receiver design                                                                                |
| `rx_attenuator`         | Analog Rx attenuator step in dB                                                                                                                                                 |
| `tdiff`                 | propagation time from interferometer array antenna to phasing matrix input minus propagation time from main array antenna through transmitter in phasing matrix in microseconds (channel_a, channel_b)|
| `phase_sign`            | Account for cable error in analyzing data                                                                                                                                       |
| `interferometer_offset` | Cartesian coordinates (x,y,z) from midpoint interferometer array to midpoint main array in meters                                                                               |
| `rx_rise_time`          | Analog Rx rise time measured in microseconds                                                                                                                                    |
| `attenuation_stages`    | Analog Attenuation stages are used for gain control of an analog receiver or front-end                                                                                          |
| `gates`                 | Maximum range gates the radar has                                                                                                                                               |
| `beams`                 | Maximum beams the radar has                                                                                                                                                     |

!!! Note
    For more detailed information on all the fields in a hardware file, please read the [hardware repo README.md](https://github.com/SuperDARN/hdw).

!!! Warning
    Prior to version 3.0, pyDARN was built to use the old format of hardware files. However, versions 2.2.1 or lower of pyDARN will try to pull hardware files from the `master` branch of the hardware repository and this may cause some errors in use.
    Version 3.0 uses the new format of hardware files, and pulls hardware files from the `main` hardware branch. Updating to pyDARN version 3.0 or higher will fix any hardware errors. 

# Accessing Radar and Hardware Information

Another way to access the hardware information, the radar's full name, the institution's name and the  hemisphere that the radar is located in is by using the `SuperDARNRadars` class with the station id number (`stid` field in most files). 
This class contains a dictionary of all currently accepted SuperDARN radars (including decommissioned):
``` python
import pydarn

# Access Prince Georges Radar information
radar_info = pydarn.SuperDARNRadars.radars[6]
print(radar_info)
```

Expected output:
```python
_Radar(name='Prince George', institution='University of Saskatchewan', hemisphere=<Hemisphere.North: 1>, hardware_info=_HdwInfo(stid=6, status=<Status.online: 1>, abbrev='pgr', date=datetime.datetime(2000, 3, 3, 0, 0), geographic=_Coord(lat=53.98, lon=-122.59, alt=670.0), boresight=_Boresight(physical=-5.0, electronic=0.0), beam_separation=3.24, velocity_sign=1.0, rx_attenuator=10.0, tdiff=_Tdiff(channel_a=0.0, channel_b=0.0), phase_sign=1.0, interferometer_offset=_InterferometerOffset(x=0.0, y=-100.0, z=0.0), rx_rise_time=0.0, attenuation_stages=0, gates=225, beams=16))
```

!!! Warning
    The hardware information obtained via this class contains most recent updates to the hardware file as it does not take a specific date as an input. To get specific hardware information, please use `read_hdw_file`.
    
# Obtaining coordinates for radar fields-of-view

The `radar_fov` function in pyDARN is an easy way to grab the coordinates of a specific radars field-of-view. All you need is the station id (key: `stid`) of the radar of interest.

Example code:
```python
import pydarn

# Geographic coordinates for Clyde River (STID: 66) FOV
geo_lats, geo_lons=pydarn.Coords.GEOGRAPHIC(66)
```

You also have the option to set the `coords` keyword to `aacgm`. In this case, [Altitude adjusted corrected geomagnetic](http://superdarn.thayer.dartmouth.edu/aacgm.html) latitude and longitude are returned instead of geographic. Because AACGM requires a date to convert coordinates accurately, a python datetime object is also required to be passed in to `radar_fov` under this circumstance:
```python
import pydarn
import datetime as dt

# AACGMv2 coordinates for Dome C (STID: 96), valid for November 26th, 2005
aacgm_lats, aacgm_lons=pydarn.Coords.AACGM(96, date=dt.datetime(2005, 11, 26))
```
The `Coords` keyword points to the function to convert the radar's Field-of-View to the designed coordinate system. The outputs are two numpy arrays of latitude and longitude coordinates with dimensions (number_of_beams+1 x number_of_gates+1). They correspond to the corners of each range gate.

# Updating Radar and Hardware Information

pyDARN does not release new versions based on hardware file changes. Because hardware files change infrequently you can update the hardware files in pyDARN by using the following command:
``` python
import pydarn
pydarn.get_hdw_files()
```
This should also replace any missing files.

# Troubleshooting

If you get an error on importing pyDARN regarding hardware files or the `get_hdw_files()` is not getting the required files to run pyDARN please create an [issue](https://github.com/SuperDARN/pydarn/issues) detailing your computer specifications, commands used to get the error, and output of the error. 
