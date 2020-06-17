# Fan plots
---

Fan plots are a way to visualise data from the entire scan of SuperDARN radar. It is when the data in all beams and ranges for a given parameter (such as line-of-sight velocity, backscatter power, etc) and a particular scan is projected onto a magnetic local time/magnetic latitude plot in [AACGMv2 coordinates](http://superdarn.thayer.dartmouth.edu/aacgm.html).

Currently, fan plots in pyDARN get the geographic positions of a radars range gates automatically by reading in pre-generated files (found in the `/pydarn/radar_fov_files` folder), and then [converts](https://pypi.org/project/aacgmv2/) them to AACGMv2 coordinates. This will change in the future, such that pyDARN will work out the positions itself. That will bring suport for not standard range/beam layouts.

### Basic usage
pyDARN and pyplot need to be imported, as well as any FITACF file needs to be [read in](https://pydarn.readthedocs.io/en/master/user/SDarnRead/):

```python
import matplotlib.pyplot as plt
import pydarn

#Read in fitACF file using SDarn_read
file = "path/to/fitacf/file"
SDarn_read = pydarn.SDarnRead(file)
fitacf_data = SDarn_read.read_fitacf()

```
With the FITACF data loaded as a list of dictionaries (`fitacf_data` variable in above example), you may now call the `plot_radar_fov` method. Make sure you tell it which scan (numbered from first recorded scan in file) you want using `scan_index`:
```python
a = pydarn.fan.plot_radar_fov(fitacf_data, scan_index=27)
plt.show()

```
Here I plotted the 27th scan in the file, and because I didn't tell it which parameter to use, it has defaulted to line-of-sight velocity:
![](../imgs/fan_1.png)

Default plots also do not show groundscatter as grey. Set it to true to colour groundscatter this way:
```python
a = pydarn.fan.plot_radar_fov(fitacf_data, scan_index=27, groundscatter=1)
plt.show()

```
![](../imgs/fan_2.png)

### Additional parameters

In addition to line-of-sight velocity, you can choose one of three other data products to plot by setting `parameter=String name`:

| Data product                          | String name |
|---------------------------------------|-------------|
| Line of sight velocity (m/s) [Default]| 'v'         |
| Spectral width (m/s)                  | 'w_l'       |
| Elevation angle (degrees)             | 'elv'       |
| Power (dB)                            | 'p_l'       |

### Additional options

Here is a list of all the current options than can be used with `plot_radar_fov`

| Option                  | Action                                                                                              |
|-------------------------|-----------------------------------------------------------------------------------------------------|
| scan_index=(int)        | Scan number, from start of records in file                                                          |
| lowlat=(int)            | Control the lower latitude boundary of the plot (default 50/-50 AACGM lat)                          |
| groundscatter=(bool)    | True or false to showing ground scatter as grey                                                     |
| all_gates=(bool)        | True of false to show all the range gates for the radar (default false, cuts out at 75 range gates) |
| cmap=matplotlib.cm      | A matplotlib color map object. Will override the pyDARN defaults for chosen parameter               |
| zmin=(int)              | Minimum data value for colouring                                                                    |
| zmax=(int)              | Maximum data value for colouring                                                                    |
| colorbar_label=(string) | Label for the colour bar                                                                            |

As an example, the following code produces the following fan plot (using data from one of the mid-latitude radars:
```python
a = pydarn.fan.plot_radar_fov(fitacf_data, scan_index=140, parameter='p_l', colorbar_label='Power [dB]', all_gates=True, lowlat=40)

```
![](../imgs/fan_3.png)

