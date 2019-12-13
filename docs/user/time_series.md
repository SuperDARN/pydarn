### Time Series Plots

`plot_time_series` simply plots out a time series of any scalar beam parameter in the loaded in FITACF or RAWACF file. These include things like.... Currently there is no functionalilty to plot parameters from MAP files. To do that, you would need to manually extract the information from those loaded dictionaries. See [`SDarnRead`](code/SDarnRead.md) for more info.

Basic code to plot a time series from a FITACF file would look like:
```python
import pydarn
import matplotlib.pyplot as plt

file = "path/to/data"
sdarn_read = pydarn.SDarnRead(file)
fitacf_data = sdarn_read.read_fitacf()
 
pydarn.RTP.plot_time_series(fitacf_data)
plt.show()
```    
If no scalar parameter is specified (using `parameter=string`), or beam (using `beam_num=int`), then the default is a `tfreq` time series from beam 0. 

In a similar way to RTP plots, you also have access to numerous plotting options:

| Parameter                    | Action                                                      |
|------------------------------|-------------------------------------------------------------|
| start_time=(datetime object) | Control the start time of the plot                          |
| end_time=(datetime object)   | Control the end time of the plot                            |
| date_fmt=(string)            | How the x-tick labels look. Default is ('%y/%m/%d\n %H:%M') |
| channel=(int or string)      | Choose which channel to plot. Default is 'all'.             |
| cp_name=(bool)               | Print the name of the cp ID when plotting cp ID timeseries' |

For example, checking out the cp ID's for a 24hour Clyde FITACF file:
```python
file = "20180101.C0.cly.fitacf"
SDarn_read = pydarn.SDarnRead(file)
fitacf_data = SDarn_read.read_fitacf()

plt.title("20180101, Beam 7, CLY")
pydarn.RTP.plot_time_series(fitacf_data, parameter='cp', date_fmt=('%H:%M'), beam_no=7)
plt.show()
```    
![](../imgs/cpid_eg.png)

