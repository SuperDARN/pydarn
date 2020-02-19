# Installing pyDARN 
---

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0) [![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/) [![GitHub version](https://badge.fury.io/gh/boennemann%2Fbadges.svg)](http://badge.fury.io/gh/boennemann%2Fbadges)

## Prerequisites

**python 3.6+**

| Ubuntu      | OpenSuse       | Fedora        | OSX           |
| ----------- | -------------- | ------------- | ------------- |
| libyaml-dev | python3-PyYAML | libyaml-devel | Xcode/pip     |

You can check your python version with  

`$ python --version` or 
`$ python3 --version`

## Dependencies

pyDARN's setup will download the following dependencies: 

- [NumPy](https://numpy.org/)
- [matplotlib](https://matplotlib.org/)
- [deepdish](https://deepdish.readthedocs.io/en/latest/api_io.html)
- [pathlib2](https://docs.python.org/dev/library/pathlib.html)
- [PyYAML](https://pyyaml.org/wiki/PyYAMLDocumentation)
- [h5py](https://www.h5py.org/)

## Virtual Environments
It is recommended to install pyDARN in one of the suggested virtual environments if you have multiple python/pip 3 version on your computer, or do not want to affect the main system's python libraries. 

The following virtual environments have been tested by pyDARN developers:"

### pip Virtual Environment
Instructions can be found here [virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

1. `$ python3 -m pip install --user virtualenv`  
2. `$ python3 -m virtualenv <environment name>`  
* `$ source <environment name>/bin/activate`
* `$ pip install git+https://github.com/superdarn/pydarn@develop`

!!! Note
    If you have multiple versions of python 3 on your machine, you can access a specific version by: `python<version number>`. 
    For example, if you want to install python 3.6 virtual environment: `python3.6 -m pip install --user virtualenv`.

### Anaconda Virtual Environment
Instructions can be found here [conda environment](https://uoa-eresearch.github.io/eresearch-cookbook/recipe/2014/11/20/conda/) and installing [anaconda](https://docs.anaconda.com/anaconda/install/)

1. `$ conda create -n yourenvname python=3.7 anaconda`
2. `$ conda activate yourenvname`
* `$ pip install git+https://github.com/superdarn/pydarn@develop

#### Adding the environment to PyCharm

To set the project interpreter to the anaconda environment:

1. File -> Settings -> Project Folder -> Project Interpreter
2. Click the project Interpreter drop down list and click on show all.
* If you don't see the environment you wish to use click the plus sign on the right side bar named "Add"
* Select "Conda Environment" on the left side menu.
* Click "Existing Environment" and give the interpreter field the path to your environment's python.exe and apply.

## Local Install
**pip3 install**

`pip3 install --user git+https://github.com/superdarn/pydarn@develop`

## System Install 
`sudo pip3 install git+https://github.com/supdarn/pydarn@develop`

## Installing for Development 
`$ git clone https://github.com/superdarn/pydarn`

Change directories to pydarn 

`$ git checkout develop`

To install: 

`$ python setup.py --user install`

or 

`pip install --user .`

## Troubleshooting

> If you find any problems/solutions, please make a [github issue](https://github.com/superdarn/pydarn/issues/new) so the community can help you or add it to the documentation
