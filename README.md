![pydarn](docs/imgs/pydarn_logo.png)

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0) [![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/) [![GitHub version](https://badge.fury.io/gh/boennemann%2Fbadges.svg)](http://badge.fury.io/gh/boennemann%2Fbadges)

Python data visualization library for the Super Dual Auroral Radar Network (SuperDARN).

## Changelog

## Version 1.0 - Release!

pyDarn is released! Included are the following features:
- Reading and writing DMap format IQDAT, RAWACF, FITACF, GRID/GRD and MAP files
- Reading and writing HDF5 format files for Borealis radar data, as well as conversion to and from DMap format
- Range-time parameter style plots for RAWACF and FITACF files
- Summary plots for RAWACF and FITACF files
- Time series plots for RAWACF and FITACF files

## Documentation

pyDARN's documentation can found [here](https://pydarn.readthedocs.io/en/latest)

## Getting Started

To install and use pyDARN please read the [installation guide](https://pydarn.readthedocs.io/en/latest/user/install/).

If wish to get access to SuperDARN data please read [SuperDARN data access documentation](https://pydarn.readthedocs.io/en/latest/user/superdarn_data/).
Please make sure to also read the documentation on [**citing superDARN and pydarn**](https://pydarn.readthedocs.io/en/latest/user/citing/). 

As a quick tutorial on using pydarn to read a compressed file: 
``` python
import bz2
import pydarn 

# read in compressed file
fitacf_file = '20180220.C0.rkn.stream.fitacf.bz2'
with bz2.open(fitacf_file) as fp: 
      fitacf_stream = fp.read()

reader = pydarn.SDarnRead(fitacf_stream, True)
records = reader.read_fitacf()
```

For more information and tutorials on pyDARN please see the [tutorial section](https://pydarn.readthedocs.io/en/latest/)

## Getting involved

pyDARN is always looking for testers and developers keen on learning python, github, and/or SuperDARN data visualization. 
If you wish to help out in testing we have priority list based on **Milestone** releases that you can sort on [GitHub's Pull Request tab](https://github.com/SuperDARN/pydarn/pulls?q=is%3Aopen+is%3Apr+milestone%3A%22v1.0.0+%22)
If you want to get involved in a specific project on pyDARN look at what we have to offer in [projects tab](https://github.com/SuperDARN/pydarn/projects), you can also filter [Pull Requests](https://github.com/SuperDARN/pydarn/pulls) and [Issues](https://github.com/SuperDARN/pydarn/issues) via the project you are interested in. 
If you want to help out with developing some code or answer some issues and sort by milestones to get the [highest priority issues](https://github.com/SuperDARN/pydarn/issues?q=is%3Aopen+is%3Aissue+milestone%3A%22v1.1.0+%22). Filtering by labels may also help if you looking for a `question`, `enhancement`, `documentation`. 

Please contact the main developer or group if you would like to become a member of the team!
