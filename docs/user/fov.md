# Field Of View Plots
---

Field Of View (FOV) plots show the radars scanning region for a given radar station id. 

```python
import pydarn
from datetime import datetime
import matplotlib.pyplot as plt 

pydarn.Fan.plot_fov(66, datetime(2015, 3, 8, 15, 0), radar_label=True)
plt.show()
```

![](../imgs/fov_1.png)

A `datetime` object of the date is required to convert to AACGM MLT coordinates (see [coordinates](coordinates.md)). 

!!! Note
    This will not be required for other coordinates once implemented. 

### Additional options

Here is a list of all the current options than can be used with `plot_fov`

| Option                  | Action                                                                                                  |
| ----------------------- | ------------------------------------------------------------------------------------------------------- |
| stid=(int)              | Station id of the radar. Can be found using [SuperDARNRadars](hardware.md)                              |
| date=(datetime)         | `datetime` object to determine the position the radar fov is in MLT
| ranges=(list)           | Two element list giving the lower and upper ranges to plot, grabs ranges from hardware file (default [] |
| colorbar_label=(string) | Label for the colour bar (requires colorbar to be true)                                                 |
| boundary=(bool)         | Set false to not show the outline of the radar FOV (default: True)                                      |
| fov_color=(string)      | Sets the fill in color for the fov plot (default: transparency)                                         |
| line_color=(string)     | Sets the boundary line and radar location dot color (default: black)                                    |
| alpha=(int)             | Sets the transparency of the fill color (default: 0.5)                                                  |
| radar_location=(bool)   | Places a dot in the plot representing the radar location (default: True)                                |
| radar_label=(bool)      | Places the radar 3-letter abbreviation next to the radar location                                       |
| kwargs **               | Axis Polar settings. See [polar axis](axis.md)                                                          |

To plot based on hemisphere or selection of radars, here is an example plotting North hemisphere radars with selected SuperDARN Canada radars colored as green:

```python
for stid in pydarn.SuperDARNRadars.radars.keys():
    if pydarn.SuperDARNRadars.radars[stid].hemisphere == pydarn.Hemisphere.North:
        if stid != 2:
            if stid in [66, 65, 6, 65, 5]: 
                pydarn.Fan.plot_fov(stid, datetime(2021, 2, 5, 12, 5), 
                                    radar_label=True, fov_color='green',
                                    line_color='green', alpha=0.8)

            pydarn.Fan.plot_fov(stid, datetime(2021, 2, 5, 12, 5), 
                                radar_label=True, fov_color='blue',
                                line_color='blue', alpha=0.2, lowlat=10)

plt.show()
```

![](../imgs/fov_2.png)

This example will plots the South Hemisphere radars FOV in red:

```python
for stid in pydarn.SuperDARNRadars.radars.keys():
    if pydarn.SuperDARNRadars.radars[stid].hemisphere == pydarn.Hemisphere.South:
        if stid != 2:
            pydarn.Fan.plot_fov(stid, datetime(2021, 2, 5, 12, 5),
                                radar_label=True, fov_color='red',
                                line_color='red', alpha=0.2)
plt.show()
```

![](../imgs/fov_3.png)

`plot_fov` use two other plotting methods `plot_radar_posistion` and `plot_radar_label`, these methods have the following parameters: 

| Option                  | Action                                                                                                  |
| ----------------------- | ------------------------------------------------------------------------------------------------------- |
| stid=(int)              | Station id of the radar. Can be found using [SuperDARNRadars](hardware.md)                              |
| date=(datetime)         | `datetime` object to determine the position the radar fov is in MLT
| line_color=(string)     | Sets the boundary line and radar location dot color (default: black)                                    |

!!! Note
    These methods do not plot on a polar axis so it is strongly encouraged to use `plot_fov` to use them. 

To obtain only dots and labels 

```python
pydarn.Fan.plot_fov(66, datetime(2021, 2, 5, 12, 5), boundary=False,
                    radar_label=True)
```

![](../imgs/fov_4.png)
