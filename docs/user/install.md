<!--Copyright (C) SuperDARN Canada, University of Saskatchewan 
Author(s): Marina Schmidt 
Modifications:
2020-12-01 Carley Martin updated documentation

Disclaimer:
pyDARN is under the LGPL v3 license found in the root directory LICENSE.md 
Everyone is permitted to copy and distribute verbatim copies of this license 
document, but changing it is not allowed.

This version of the GNU Lesser General Public License incorporates the terms
and conditions of version 3 of the GNU General Public License, supplemented by
the additional permissions listed below.
-->

# Installing pyDARN 
---

[![License: LGPL v3](https://img.shields.io/badge/License-LGPLv3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0) 
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/) 
![GitHub release (latest by date)](https://img.shields.io/github/v/release/superdarn/pydarn)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3727269.svg)](https://doi.org/10.5281/zenodo.3727269)


!!! Important 
    It is recommended to install pyDARN via `pip`; however, please cite via the [DOI for the release](https://doi.org/10.5281/zenodo.3727269) 


## Prerequisites

pyDARN requires **python 3.6** or later and **matplotlib 3.3.4** or later.

Depending on your operating system or distribution, the following package installers, development environments or data parsers are required: 
 
| Ubuntu      | OpenSuse       | Fedora        | OSX           | Windows       |
| ----------- | -------------- | ------------- | ------------- | ------------- |
| libyaml-dev | python3-PyYAML | libyaml-devel | Xcode/pip     | pip           |

You can check your python version using

`$ python --version` or 
`$ python3 --version`

!!! Note
    If you have already installed `pydarn` you can use `pip3 install --upgrade pydarn`

## Dependencies

pyDARN's setup will download the following dependencies: 

- [Git](https://git-scm.com/) (For developers)
- [pip3](https://help.dreamhost.com/hc/en-us/articles/115000699011-Using-pip3-to-install-Python3-modules)
- [NumPy](https://numpy.org/)
- [matplotlib 3.3.4+](https://matplotlib.org/) 
- [PyYAML](https://pyyaml.org/wiki/PyYAMLDocumentation)
- [pyDARNio](https://pydarnio.readthedocs.io/en/latest/user/install/)
- [AACGMv2](https://pypi.org/project/aacgmv2/) 

!!! Note
    If you wish to plot coastlines you will need to install cartopy separately

### Cartopy 
[Cartopy](https://scitools.org.uk/cartopy/docs/latest/) is a Python package designed for geospatial data processing in order to produce maps and other geospatial data analyses. This library is used when invoking a projection system needing overlapped coastline maps in Fan, Grid and Map plots. 

For installing cartopy please follow the packages [installation](https://scitools.org.uk/cartopy/docs/latest/installing.html) instructions. 

!!! Note
    cartopy is a challenging package to install so please provide any information on troubleshoot or solutions to common issue on [pyDARN github](https://github.com/SuperDARN/pydarn) page. 

## Virtual Environments
It is recommended to install pyDARN in one of the suggested virtual environments if you have multiple python/pip 3 version on your computer, or do not want to affect the main system's python libraries. 

The following virtual environments have been tested by pyDARN developers:"

### pip Virtual Environment
Instructions can be found here [virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

Option 1:
1. `$ python3 -m pip install --user virtualenv` (Install virtual environment package)
2. `$ python3 -m virtualenv <environment name>`  (Make your virtual environment)
3. `$ source <environment name>/bin/activate`  (Activate the virtual environment)
4. `$ pip install pydarn`    (Install pyDARN)

!!! Note
    If you have multiple versions of python 3 on your machine, you can access a specific version by: `python<version number>`. 
    For example, if you want to install python 3.6 virtual environment: `python3.6 -m pip install --user virtualenv`.

### Anaconda Virtual Environment
Instructions can be found here [conda environment](https://uoa-eresearch.github.io/eresearch-cookbook/recipe/2014/11/20/conda/) and installing [anaconda](https://docs.anaconda.com/anaconda/install/)

1. `$ conda create -n yourenvname python=3.7 anaconda`
2. `$ conda activate yourenvname`
* `$ pip install pydarn`

#### Adding the environment to PyCharm

To set the project interpreter to the anaconda environment:

1. File -> Settings -> Project Folder -> Project Interpreter
2. Click the project Interpreter drop down list and click on show all.
* If you don't see the environment you wish to use click the plus sign on the right side bar named "Add"
* Select "Conda Environment" on the left side menu.
* Click "Existing Environment" and give the interpreter field the path to your environment's python.exe and apply.

## Local Install
**pip3 install**

`pip3 install --user pydarn`

## System Install 
`sudo pip3 install pydarn`

## Installing for Development

pyDARN's default github branch is `develop` for quicker and easer development. 

It is encouraged to use [SSH keys in GitHub](https://docs.github.com/en/github/authenticating-to-github/connecting-to-github-with-ssh) 

`git clone git@github.com:SuperDARN/pydarn.git`

To install: 

`$ pip3 install . --user`

!!! Note
    If `pip --version` is pointing to python 3.6+ then you can use `pip install . --user` instead. 

!!! Note
    Sometimes `python setup.py install` is needed to grab all hardware files (known issue).

Please read pyDARN [Workflow documentation](../dev/team.md) to further understand how to develop in pyDARN.
    
## Troubleshooting

### Pip3 installation with Ubuntu 20.4/python 3.8.4

Issue: `pip3 install --user git+https://github.com/superdarn/pydarn@develop` not working

Solution:
1. check git is installed `apt install git` (for ubuntu)
2. Check pip version `pip --version` - with newer distros of Linux/Virtual machines `pip` may point to pyhon3 and you will not need pip3. 
3. Alternative virtual environment steps for getting python 3.8 working

```bash 
$ sudo apt-get update
$ sudo apt-get install python3-virtualenv python3-pip
$ cd ~/
$ mkdir venvs
$ virtualenv -p python3.8 ~/venvs/py38
$ echo "source $HOME/venvs/py38/bin/activate" >> ~/.bashrc
```
Then open a new terminal and you should see `(pyy38)` in the prompt. 

Credit to this solution is Ashton Reimer, more details on the [issue #37](https://github.com/SuperDARN/pydarn/issues/37)

### aacgmv2 won't install 

Issue: `unable to execute 'gcc': No such file or directory
    error: command 'gcc' failed with exit status 1`

Solution: 
  1. Ensure `gcc` is installed if not install it
  2. Ensure you install `python3-dev` (Ubuntu) or `python3-devel` for RPM OS Linux operating systems. 

Credit to this solution is Marina Schmidt brought up by Remington Rohel from SuperDARN Canada


> If you find any problems/solutions, please make a [github issue](https://github.com/superdarn/pydarn/issues/new) so the community can help you or add it to the documentation

### Summary plots get a ValueError 

Issue: `ValueError: Cannot convert 0 to a date.  This often happens if non-datetime values are passed to an axis that expects datetime objects.` when using `plot_summary`

Solution:
1. check matplotlib version, if lower than 3.3.4 then upgrade matplotlib equal or higher version.  
2. `pip install -U matplotlib`
