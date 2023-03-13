![pydarn](https://raw.githubusercontent.com/SuperDARN/pydarn/master/docs/imgs/pydarn_logo.png)

[![License: LGPL v3](https://img.shields.io/badge/License-LGPLv3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0) 
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/) 
![GitHub release (latest by date)](https://img.shields.io/github/v/release/superdarn/pydarn)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3727269.svg)](https://doi.org/10.5281/zenodo.3727269)

Python data visualization library for the Super Dual Auroral Radar Network (SuperDARN).

## Changelog

## Version 3.1.1 - Patch Release!

This patch release includes:
- **Bug fix** `hdw` repository installation issues resolved
- Inclusion of ICE and ICW in `hdw` repository and superdarn_radars module

Most recent minor release (3.1.0) changes listed below:
- Full Cartopy coastline plotting options for all spatial plots
  - **NEW** `coastline` keyword in method calls
- Full Cartopy integration for plotting in geographic coordinates for grid and fan plots
- Completed polar coordinate convection maps including reference vector and many customization options
- Improved ACF plotting
- New `HALF_SLANT` range estimation for RTP
- **Bug fix** Multiple fan plots now available on one axis
- **Bug fix** `lowlat` keyword now available for geographic coordinate plots
- **Bug fix** Colorbars now extend/don't extend as required
along with many other minor improvements and bug fixes!


## Documentation

pyDARN's documentation can be found [here](https://pydarn.readthedocs.io/en/latest/index.html)

## Getting Started

`pip install pydarn`

Or read the [installation guide](https://pydarn.readthedocs.io/en/latest/user/install.html).

If wish to get access to SuperDARN data please read the [SuperDARN data access documentation](https://pydarn.readthedocs.io/en/latest/user/superdarn_data.html).
Please make sure to also read the documentation on [**citing superDARN and pydarn**](https://pydarn.readthedocs.io/en/latest/user/citing.html). 

As a quick tutorial on using pydarn to read a non-compressed file: 


```python
import matplotlib.pyplot as plt

import pydarn

# read a non-compressed file
fitacf_file = '20190831.C0.cly.fitacf'

# pyDARN functions to read a fitacf file
fitacf_data = pydarn.SuperDARNRead(fitacf_file).read_fitacf()

pydarn.RTP.plot_summary(fitacf_data, beam_num=2)
plt.show()
```

[summary plot](docs/imgs/summary_clyb2.png)

For more information and tutorials on pyDARN please see the [tutorial section](https://pydarn.readthedocs.io/en/latest/index.html)

## Getting involved

pyDARN is always looking for testers and developers keen on learning python, github, and/or SuperDARN data visualizations! 
Here are some ways to get started: 

  - **Testing Pull Request**: to determine which [pull requests](https://github.com/SuperDARN/pydarn/pulls) need to be tested right away, filter them by their milestones (v3.0 is currently highest priority).
  - **Getting involved in projects**: if you are looking to help in a specific area, look at pyDARN's [projects tab](https://github.com/SuperDARN/pydarn/projects). The project you are interested in will give you information on what is needed to reach completion. This includes things currently in progress, and those awaiting reviews. 
  - **Answer questions**: if you want to try your hand at answering some pyDARN questions, or adding to the discussion, look at pyDARN's [issues](https://github.com/SuperDARN/pydarn/issues) and filter by labels.
  - **Become a developer**: if you want to practice those coding skills and add to the library, look at pyDARN [issues](https://github.com/SuperDARN/pydarn/issues) and filter by milestone's to see what needs to get done right away. 

Please read [pyDARN team](https://pydarn.readthedocs.io/en/latest/dev/team) on how to join the pyDARN team. 
