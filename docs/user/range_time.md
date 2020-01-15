# Range-Time Parameter Plots 
---

Range-time parameter plots (also known as range-time intensity (RTI) plots) plot a radar measured parameter along range gates versus time. They are the most common way to look at data from a single radar. 

!!! Note
    Slant ranges are future enhancement we are currently working on. Sorry for inconvenience.

### Basic RTP
The general syntax for plot_range_time is:
'plot_range_time(fitacf_data, options)'
where 'fitacf_data' is the read in data, and the options are several python parameters used to control how the plot looks.

First, make sure Pydarn and matplotlib are imported, then read in the .fitacf file with the data you wish to plot:
```python
import pydarn
import matplotlib.pyplot as plt

fitacf_file = "path/to/fitacf/file"
sdarn_read = pydarn.SDarnRead(fitacf_file)
fitacf_data = sdarn_read.read_fitacf()

```

You can choose one of four data products to plot:

| Data product                | String name |
|-----------------------------|-------------|
| Line of sight velocity (m/s)| 'v'         |
| Spectral width (m/s)        | 'w_l'       |
| Elevation angle (degrees)   | 'elv'       |
| Power (dB)                  | 'p_l'       |

which is chosen by adding: 
'parameter=String name' 
as an option. The default if left blank is 'v'.

To specify which beam to look at, add the option:
'beam=beam_number"

As an example, taking a look at some 'v' data from the first record of Clyde River radar FIRACF file:
```python
fitacf_file = "20190831.C0.cly.fitacf"
sdarn_read = pydarn.SDarnRead(fitacf_file)
fitacf_data = sdarn_read.read_fitacf()

pydarn.RTP.plot_range_time(fitacf_data, beam_num=fitacf_data[0]['bmnum'])
plt.title("Radar {:d}, Beam {:d}".format(fitacf_data[0]['stid'], fitacf_data[0]['bmnum']))  

plt.show()
```
which produces:

![](../imgs/rtp_cly1.png)

`fitacf_data[0]['bmnum']` is used to extract the beam number of the first (0th) record from the data dictionary, whilst `fitacf_data[0]['stid']` gives the station id (which is 66 for Clyde River).

Notice that the velocity scale on the right is a bit larger than we need, and also ground scatter isn't shown by default. Showing the dates on the x axis is also a bit redundant, because it's data from a single day. Below, there are some additional parameters you can set to address these and more.

### Additional options
To see all the customisation options, check out all the parameters listed in 'rtp.py'. A few useful ones:

| Parameter                    | Action                                                      |
|------------------------------|-------------------------------------------------------------|
| start_time=(datetime object) | Control the start time of the plot                          |
| end_time=(datetime object)   | Control the end time of the plot                            |
| groundscatter=(bool)         | True or false to showing ground scatter as grey             |
| date_fmt=(string)            | How the x-tick labels look. Default is ('%y/%m/%d\n %H:%M') |
| zmin=(int)                   | Minimum data value to be plotted                            |
| zmax=(int)                   | Maximum data value to be plotted                            |

For instance, code for a velocity RTP showing the same beam of Clyde river radar as above, but with ground scatter, date format as 'hh:mm', custom min and max values and a colour bar label could look something like:
```python
pydarn.RTP.plot_range_time(fitacf_data, beam_num=fitacf_data[0]['bmnum'], groundscatter=1, zmax=500, zmin=-500, date_fmt='%H:%M', colorbar_label='Line-of-Sight Velocity (m s$^{-1}$)')
```
which outputs:

![](../imgs/rtp_cly2.png) 

and looks much more useful!

#### Plotting with a custom color map
Because the default parameter plotted is line-of-sight velocity, there is also a special red-blue colour map set as default (as seen above) which is only meant for velocity RTP's. 

To change the color map, use the 'cmap' parameter with the string name of a matplot lib color map ([found here](https://matplotlib.org/tutorials/colors/colormaps.html)). For example, plotting the power along the beam above using the colormap 'viridis':
```python
pydarn.RTP.plot_range_time(fitacf_data, beam_num=7, parameter='p_l', zmax=50, zmin=0, date_fmt='%H%M', colorbar_label='Power (dB)', cmap='viridis')
```
produces:

![](../imgs/rtp_cly3.png)

Feel free to choose a color map which is palatable for your needs.










