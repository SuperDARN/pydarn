# Range-Time Plots 

Range-time plots extends the *matplotlib* `pcolormesh` methods 
to produce SuperDARN based range-time paramter plots. This method
utilizes the time fields:


| field | format | description |
|-------|--------|-------------|
| *time.yr* | **short** | Year  |
| *time.mo* | **short** | month |
| *time.dy* | **short** | day   |
| *time.hr* | **short** | hour  |
| *time.mt* | **short** | minute |
| *time.sc* | **short** | seconds |
| *time.us* | **int**   | micro seconds|

to convert to a `datetime` object. This achieves plotting the date along 
the *x-axis* of the plot. The *y-axis* is determined by the number of 
range gates for the given radar date. This determined by the *nrng* field 
in the data structure. Then the parameter field passed in is normalized to 
color map to be plotted as the *z-data*. Any data flagged as ground scatter 
by the *gflg* (`gflg=1`) is not included in the *z-data* if the ground scatter
flag is not enabled. If enabled then the ground scatter data will appear on 
the plot as **grey**.

<blockquote class="is-info">  <b>Class Method:</b>
<i>RTP.plot_range_time(dmap_data, parameter='p_l', beam_num=0, channel='all', 
ax=None, color_norm=None, **kwargs)</i> </blockquote>

### Parameters:
<blockquote class="is-parameter"><p>        
<b>dmap_data</b>: <i>List[dict]</i><br/>
                Dmap Data dictionary or structure to be plotted. 
<b>parameter</b>: <i>str</i><br/>
                string name of the field to plot.
<b>beam_num</b>: <i>int</i><br/>
                Beam number to plot
<b>time_span</b>: <i>(datetime, datetime)</i><br/>
        List containing the start time and end time as `datetime` objects,
<b>channel</b>: <i>int</i>
        The channel 0, 1, 2, 'all'
<b>ground_scatter : boolean
<b>    Flag to indicate if ground scatter should be plotted.
<b>    default : False
<b>date_fmt : str
<b>    format of x-axis date ticks, follow datetime format
<b>    default: '%y/%m/%d \n %H:%M'
<b>color_bar: boolean
<b>    boolean to indicate if a color bar should be included
<b>    default: True
<b>color_bar_label: str
<b>    the label that appears next to the color bar
<b>    default: ''
<b>    Certain standard parameters have pre-set labels:
<b>    elevation: 'elevation $degrees$'
<b>    power: 'signal to noise $dB$'
<b>    spectral width: 'spectral width $m/s$'
<b>    velocity: 'velocity $m/s$'
<b>color_map: str
<b>    [matplotlib colour map](https://matplotlib.org/tutorials/colors/colormaps.html)
<b>    default: jet
<b>    note: to reverse the color just add _r to the string name
<b>color_norm: matplotlib.colors.Normalization object
<b>    This object use dependency injection to use any normalization
<b>    method with the zmin and zmax.
<b>    defualt: colors.Normalization()
<b>ax: matplotlib.axes
<b>    axes object for another way of plotting
<b>    default: None
<b>boundary: (int, int)
<b>    min and max values to include in the plot and set for normalization
<b>    of the color map.
<b>    default: None
<b>        - the min and max values in the data are used instead
<b>max_array_filter : dict
<b>    dictionary that contains the key parameter names and the values to
<b>    compare against. Will filter out any data points
<b>    that is above this value.
<b>min_array_filter : dict
<b>    dictionary that contains the key parameter names and the value to
<b>    compare against. Will filter out any data points that is
<b>    below this value.
<b>max_scalar_filter : dict
<b>    dictionary that contains the key parameter names and the values to
<b>    compare against. Will filter out data sections that is
<b>    above this value.
<b>min_scalar_filter : dict
<b>    dictionary that contains the key parameter names and the value to
<b>    compare against. Will filter out data sections
<b>    that is below this value.
<b>equal_scalar_filter : dict
    dictionary that contains the key parameter names and the value to
    compare against. Will filter out data sections
    that is does not equal the value.
</p></blockquote>

### Returns:
        im: matplotlib.pyplot.pcolormesh
            matplotlib object from pcolormesh
        cb: matplotlib.colorbar
            matplotlib color bar
        cmap: matplotlib.cm
            matplotlib color map object

### Examples

Generating a simple Range-time plot

```python

```

Generating multiple Range-time plots
```python

```

Filtering out data in Range-time plot

```python

```


(See also pyDARN HowTOs [rang-time plots]())
