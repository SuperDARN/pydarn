<!--Copyright (C) SuperDARN Canada, University of Saskatchewan 
Author(s): Marina Schmidt 
Modifications:

Disclaimer:
pyDARN is under the LGPL v3 license found in the root directory LICENSE.md 
Everyone is permitted to copy and distribute verbatim copies of this license 
document, but changing it is not allowed.

This version of the GNU Lesser General Public License incorporates the terms
and conditions of version 3 of the GNU General Public License, supplemented by
the additional permissions listed below.
-->

### Auto-Correlation Function Plots

`plot_acfs` simply plots the Auto-Correlation Function (ACF) of the imaginary and real parts in the selected RAWACF file. 

Basic code to plot ACFs from a RAWACF file would look like:
```python
import matplotlib.pyplot as plt
import pydarn


file = "20180101.0000.01.rkn.rawacf"
sdarn_read = pydarn.SuperDARNRead(file)
rawacf_data = sdarn_read.read_rawacf()
 
pydarn.ACF.plot_acfs(rawacf_data)
plt.show()
```  

![](../imgs/acf_plot1.png)

You also have access to numerous plotting options:


| Parameter              | Action                                                                          |
| ---------------------- | ------------------------------------------------------------------------------- |
| beam_num=0             | beam number to plot                                                             |
| gate_num=0             | gate number to plot                                                             |
| parameter='acfd'       | parameter to pick between acfd or xcfd plotting                                 |
| scan_num=0             | the scan number to plot                                                         |
| start_time=None        | plot the closest beam scan to the given start time (overrides the scan number if set) |
| ax                     | matplotlib axes object                                                          |
| normalized=True        | normalizes the parameter data with the associated power 0 value                 |
| real_color='red'       | Real part of the parameter line color                                           |
| imaginary_color='blue' | Imaginary part of the parameter line color                                      |
| plot_blank=False       | Determine if blanked lags should be plotted                                     |
| blank_marker='o'       | Choice of marker to indicate blanked lags are a dot (general python markers accepted)             |
| legend=True            | plot a legend                                                                   |
| kwargs                 | arguments passed in matplotlib line_plot for real and imaginary plots           |


If blank lags are present in the data, it will look similar to the following: 

```python
import pydarn
import matplotlib.pyplot as plt 
from datetime import datetime

rawacf_file = '20140105.1200.03.cly.rawacf'
rawacf_data = pydarn.SuperDARNRead(rawacf_file).read_rawacf()
pydarn.ACF.plot_acfs(rawacf_data, beam_num=15, gate_num=16, start_time=datetime(2014, 1, 5, 13, 30))
plt.show()
```    

![](../imgs/plot_acf_2.png)
