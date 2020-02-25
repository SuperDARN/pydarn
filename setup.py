"""
Copyright 2018 SuperDARN

setup.py
2018-11-05
To setup pyDARN as a third party library. Include installing need libraries for
running the files.

author:
Marina Schmidt
"""

from distutils.core import setup
from setuptools import setup, find_packages
from os import path
import sys
from subprocess import check_call
from setuptools.command.install import install

# TODO: currently not implemented due to some challenges
# with C API and memory leaks.
#rstmodule = Extension('dmap',
#                      sources= ['dmap.c'])

class initialize_submodules(install):
    def run(self):
        if path.exists('.git'):
            check_call(['git', 'submodule', 'update', '--init', '--recursive'])
        if self.old_and_unmanageable or self.single_version_externally_managed:
            return install.run(self)
        #install.run(self)
        caller = sys._getframe(2)
        caller_module = caller.f_globals.get('__name__','')
        caller_name = caller.f_code.co_name
        if caller_module != 'distutils.dist' or caller_name!='run_commands':
            # We weren't called from the command line or setup(), so we
            # should run in backward-compatibility mode to support bdist_*
            # commands.
            install.run(self)
        else:
            self.do_egg_install()

# Setup information
setup(
    cmdclass = {'install': initialize_submodules},
    name="pydarn",
    version="0.1.dev",
    description="Data visualization library for SuperDARN data",
    url='https://github.com/SuperDARN/pydarn.git',
    classifiers=[
        'Development status :: 3 - Alpha',
        'LICENSE :: GNU license',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'],
    python_requires='>=3.6',
    packages=find_packages(exclude=['docs', 'test']),
    author="SuperDARN",
    # used to import the logging config file into pydarn.
    include_package_data=True,
    setup_requires=['pyyaml','numpy','matplotlib',
                      'h5py', 'deepdish', 'pathlib2'],
    # pyyaml library install
    install_requires=['pyyaml','numpy','matplotlib',
                      'h5py', 'deepdish', 'pathlib2']
    # commented out due to not implemented yet.
    #ext_modules = [rstmodule]
)
