# Time-Series Plots 

Time-series plots extends the *matplotlib* `date_plot` method
to produce SuperDARN based time-series paramter plots. This method
utilizes the time fields:

| field | format | description |
--------------------------------
| *time.yr* | **short** | Year  |
---------------------------------
| *time.mo* | **short** | month |
---------------------------------
| *time.dy* | **short** | day   |
---------------------------------
| *time.hr* | **short** | hour  |
---------------------------------
| *time.mt* | **short** | minute |
----------------------------------
| *time.sc* | **short** | seconds |
-----------------------------------
| *time.us* | **int**   | micro seconds|
----------------------------------------

to convert to a `datetime` object. This achieves plotting the date along 
the *x-axis* of the plot. The parameter field passed in is plotted along the
*y-axis*. 

If the parameter field passed is **cp** then vertical lines are plotted when
the *cp* field changes in the data set. The *cp* ID is then printed next to the
vertical line. 

**NOTE**: Names of the control programs can be printed along the *cp* ID's;
however, the list may not include them all or print the correct formatted name 
to the flexibility of creating new control programs. 

> `plot_time_series(dmap_data: List[dict], *args, parameter: str = 'tfreq', beam_num: int = 0, ax=None, time_span=None, date_fmt: str='%y/%m/%d\n %H:%M', channel='all', scale: str = 'linear' cp_name: bool=True, \*\*kwargs)` *Class Method*

### Parameters
        dmap_data : List[dict]
            List of dictionaries representing SuperDARN data
        parameter : str
            Scalar parameter to plot
            default: frequency
        time_span : (datetime, datetime)
            tuple containing the start time and end time
        cp_name : bool
            If True, the cp ID name will be printed
            along side the number. Otherwise the cp ID will
            just be printed. This is only used for the parameter cp
            default: True
        scale: str
            The y-axis scaling. This is not used for plotting the cp ID
            Default: log
        beam_num : int
            beam number
            default: 0
        channel : int or str
            integer indicating which channel to plot or 'all' to
            plot all channels
            default: 'all'
        date_fmt : datetime format string
            Date format for the x-axis
            default: '%y/%m/%d \n %H:%M'
        ax : matplotlib axes object
            option to pass in axes object from matplotlib.pyplot
            default: None
            side note: this will default to using plt.gca()



### Returns 
        None if it is a cp ID plot; otherwise returns lines object returned
        from plot_date

### Examples

Simple time-series plot
```python
```

Simple **cp** time-series plot

```python
```

Combined time-series plots

```python
```
