"""
Copyright 2018 SuperDARN

setup.py
2018-11-05
To setup pydarn as a third party library. Include installing need libraries for
running the files.

author:
Marina Schmidt
"""

from distutils.core import setup
from setuptools import setup, find_packages

# TODO: currently not implemented due to some challenges
# with C API and memory leaks.
#rstmodule = Extension('dmap',
#                      sources= ['dmap.c'])

# Setup information
setup(
    name="pydarn",
    version="0.1dev",
    license="GNU",
    packages=find_packages(exclude=['docs', 'test']),
    author="SuperDARN",
    # used to import the logging config file into pydarn.
    data_files=[('pydarn',['pydarn/logging_config.yaml'])],
    # pyyaml library install
    install_requires=['pyyaml']
    # commented out due to not implemented yet.
    #ext_modules = [rstmodule]
)

