from distutils.core import setup
from setuptools import setup, find_packages

#rstmodule = Extension('dmap',
#                      sources= ['dmap.c'])

setup(
    name="pydarn",
    version="0.1dev",
    license="GNU",
    packages=find_packages(exclude=['docs', 'test']),
    author="SuperDARN",
    #ext_modules = [rstmodule]
)

