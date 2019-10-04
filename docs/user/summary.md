# Summary plots 

Summary plots in SuperDARN are a collection of set parameter plots from a FitACF file. The parameters typically in the plots are:
- Time-series plots:
  - Sky Noise and Search Noise (`noise.sky` and `noise.search`)
  - Transmission Frequency and Number of averages (`tfreq` and `nav`)
  - Control Program ID (`cp`)
- Range-time plots:
  - Signal to Noise (`p_l`)
  - Velocity (`v`)
  - Spectral Width (`w_l`)

!!! Note
    Elevation (`elv`) is optional to plot and is set to be plotted, however, not all radars have elevation data. 
    If the radar doesn't have elevation data then it is not plotted.

See API of this function to see all possible options [`RTP.plot_summary`](/code/plot_summary.md)

## Standard plot 

```python
import pydarn
import matplotlib.pyplot as plt
  
```
