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
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/) 
![GitHub release (latest by date)](https://img.shields.io/github/v/release/superdarn/pydarn)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3727269.svg)](https://doi.org/10.5281/zenodo.3727269)

For most users, pyDARN can be installed simply by:

```
pip3 install pydarn
```

If already installed, pyDARN can be upgraded by:

```
pip3 install --upgrade pydarn
```

Installing in virtual environments is recommended, see below for details.

## Prerequisites

pyDARN requires **python 3.7** or later and **matplotlib 3.3.4** or later.

!!! Note
    Python 3.6 is commonly the default version included on many operating systems, you may need to install a newer version and specify that version when running python programs and installing libraries.

Depending on your operating system or distribution, the following package installers, development environments or data parsers are required: 
 
| Ubuntu      | OpenSuse       | Fedora        | OSX           | Windows       |
| ----------- | -------------- | ------------- | ------------- | ------------- |
| libyaml-dev | python3-PyYAML | libyaml-devel | Xcode/pip     | pip           |

You can check your python version using

`$ python --version` or 
`$ python3 --version`


## Dependencies

On installation, pyDARN will download the following dependencies: 

- [NumPy](https://numpy.org/)
- [matplotlib 3.3.4+](https://matplotlib.org/) 
- [PyYAML](https://pyyaml.org/wiki/PyYAMLDocumentation)
- [pyDARNio](https://pydarnio.readthedocs.io/en/latest/user/install/)
- [AACGMv2](https://pypi.org/project/aacgmv2/) 
- [Cartopy 0.22.0+](https://scitools.org.uk/cartopy/docs/latest/)

and dependencies of the above.


### Cartopy
Updates to the Cartopy library mean that new versions can be installed as dependencies easily, unlike earlier versions which required an installation process.
If you have any issues with the installation, you can try to pre-install Cartopy before pyDARN:

To install cartopy please follow the [official installation](https://scitools.org.uk/cartopy/docs/latest/installing.html) instructions.


## Virtual Environments
It is recommended to install pyDARN in one of the suggested virtual environments if you have multiple python versions on your computer, or do not want to affect the main systems python libraries. 

### pip Virtual Environment
Instructions can be found here [virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

Option 1:

1. `$ python3 -m pip install --user virtualenv` (Install virtual environment package)
2. `$ python3 -m virtualenv <environment name>` (Make your virtual environment)
* `$ source <environment name>/bin/activate` (Activate the virtual environment)
* `$ pip3 install pydarn` (Install pyDARN)

!!! Note
    In newer python versions, `virtualenv` is now `venv`.

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


## Installing for Development or Testing

pyDARN's default github branch is `develop` for quicker and easer development. 

`git clone https://github.com/SuperDARN/pydarn.git`

To install a specific branch to develop or test: 

`cd pydarn`

`git checkout branch_name`

`pip3 install .`

You can alternatively install a specific branch using the following installation, this is most useful for testing new branches:

`pip3 install git+https://github.com/superdarn/pydarn@branch_name`

Please read pyDARN [Workflow documentation](../dev/team.md) to further understand how to develop in pyDARN.
    
## Troubleshooting

Some known issues with solutions are:

### pip3 installation with Ubuntu 20.4/python 3.8.4

Issue: `pip3 install --user git+https://github.com/superdarn/pydarn@develop` not working

Solution:

1. check git is installed `apt install git` (for ubuntu)
2. Check pip version `pip --version` - with newer distros of Linux/Virtual machines `pip` may point to pyhon3 and you will not need pip3.
* Alternative virtual environment steps for getting python 3.8 working

```bash 
$ sudo apt-get update
$ sudo apt-get install python3-virtualenv python3-pip
$ cd ~/
$ mkdir venvs
$ virtualenv -p python3.8 ~/venvs/py38
$ echo "source $HOME/venvs/py38/bin/activate" >> ~/.bashrc
```
Then open a new terminal and you should see `(pyy38)` in the prompt. 

More details on [issue #37](https://github.com/SuperDARN/pydarn/issues/37)

### aacgmv2 won't install 

Issue: `unable to execute 'gcc': No such file or directory error: command 'gcc' failed with exit status 1`

Solution:

  1. Ensure `gcc` is installed if not install it
  2. Ensure you install `python3-dev` (Ubuntu) or `python3-devel` for RPM OS Linux operating systems.

### General Plotting Errors

Solution:

1. check matplotlib version, if lower than 3.3.4 then upgrade matplotlib equal or higher version.
2. `pip install -U matplotlib`

!!! Note 
If you find any problems/solutions, please make a [github issue](https://github.com/superdarn/pydarn/issues/new) so the community can help you or add it to the documentation!
