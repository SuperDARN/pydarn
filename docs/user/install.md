# pydarn
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0) [![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/) [![GitHub version](https://badge.fury.io/gh/boennemann%2Fbadges.svg)](http://badge.fury.io/gh/boennemann%2Fbadges)

SuperDARN data visualization library. 

## Getting Started 

!!! Warning 
    Requires python 3.6. 
    To check if you are using the correct python version: `python --version`

### Virtual Environment

It is encouraged to install a virtual environment then install pyDARN. 
    1. **Recommended**: Installing a [virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtualenv/), this option allows the library to install needed version of libraries without affecting system libraries.  
        * First install the environment:  
      `$ python3 -m pip install --user virtualenv`  
      `$ python3 -m virtualenv <environment name>`  
		  `$ source <environment name>/bin/activate`

### pip3

To install with pip3:
`pip3 install pydarn`

### Installing via GitHub (Recommended for developers)

1. Clone git repository:   
   `git clone https://github.com/SuperDARN/pydarn`

2. Change directories to pydarn 
2. Install pydarn   
    1. Install in a virtual environment 
		  `$ python3 setup.py install`

    2. Install in the system (root privileges required):  
		   `$ sudo python3 setup.py install`


