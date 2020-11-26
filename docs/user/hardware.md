<!--Copyright (C) SuerDARN Canada, University of Saskatchewan 
Author(s): Marina Schmidt -->
# Accessing Hardware File Information 

SuperDARN Radar hardware information is stored in hardware files located [here](https://github.com/vtsuperdarn/hdw.dat). 
pyDARN pulls down the hardware files from the `master` branch on the [repository](https://github.com/vtsuperdarn/hdw.dat) to obtain geographical and hardware information for plotting functionality. 

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

expected output: 
``` python
75
```

Other information a user can access from the `_HdwInfo` object is:

| Field name              | Description                                                                                                                                                                     |
| :---:                   | :---                                                                                                                                                                            |
| `stid`                  | Station Id of the radar                                                                                                                                                         |
| `abbrev`                | 3 letter radar abbreviation                                                                                                                                                     |
| `geographic`            | Geographic coordinates of the radar and altitude in meters (lat, long, alt)                                                                                                     |
| `boresight`             | Boresight of the centre beam                                                                                                                                                    |
| `beam_speration`        | Angular seperation between radar beams in degrees                                                                                                                               |
| `velocity_sign`         | To help identify backscatter velocities which the signs can be reversed based on receiver design                                                                                |
| `rx_attenuator`         | Analog Rx attenuator step in dB                                                                                                                                                 |
| `tdiff`                 | propagation time from interferometer array antenna to phasing matrix input minus propagation time from main array antenna through transmitter in phasing matrix in microseconds |
| `phase_sign`            | Account for cable error in analyzing data                                                                                                                                       |
| `interferometer_offset` | Cartesian coordinates (x,y,z) from midpoint interferometer array to midpoint main array in meters                                                                               |
| `rx_rise`               | Analog Rx rise time measured in microseconds                                                                                                                                    |
| `attenuation_stages`    | Analog Attenuation stages are used for gain control of an analog receiver or front-end                                                                                          |
| `gates`                 | Maximum range gates the radar has                                                                                                                                               |
| `beams`                 | Maximum beams the radar has                                                                                                                                                     |

!!! Note
    For more detailed information on all the fields in a hardware file, please read the hardware file found on the [Virginia Tech SuperDARN repository](https://github.com/vtsuperdarn/hdw.dat).

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
_Radar(name='Prince George', institution='University of Saskatchewan', hemisphere=<Hemisphere.North: 1>, hardware_info=_HdwInfo(stid=6, abbrev='pgr', geographic=_Coord(lat=53.98, lon=-122.59, alt=670.0), boresight=-5.0, beam_seperation=3.24, velocity_sign=1.0, rx_attenuator=10.0, tdiff=0.0, phase_sign=1.0, interferometer_offset=_InterferometerOffset(x=0.0, y=-100.0, z=0.0), rx_rise_time=0.0, attenuation_stages=0.0, gates=225, beams=16))
```

!!! Warning
    The hardware information obtained via this class contains most recent updates to the hardware file as it does not take a specific date as an input. To get specific hardware information, please use `read_hdw_file`.

# Updating Radar and Hardware Information

Radar hardware is infrequently updated or changed. To update your hardware files without updating or reinstalling pyDARN use the following command:
``` python
import pydarn
pydarn.get_hdw_files()
```
This should also replace any missing files.
