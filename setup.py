#Copyright 2018 SuperDARN Canada, University of Saskatchewan
# Author(s): Marina Schmidt
#
# Disclaimer:
# pyDARN is under the LGPL v3 license found in the root directory LICENSE.md
# Everyone is permitted to copy and distribute verbatim copies of this license
# document, but changing it is not allowed.
#
# This version of the GNU Lesser General Public License incorporates the terms
# and conditions of version 3 of the GNU General Public License,
# supplemented by the additional permissions listed below.
#
# Modifications
# 2022-03-10 MTS - removed radar_fov files
#setup.py
#2018-11-05
"""
To setup pyDARN as a third party library. Include installing need libraries for
running the files.
"""
import sys
import warnings

from os import path
from setuptools import setup, find_packages
from setuptools.command.install import install, orig
from setuptools.command.develop import develop
from glob import glob
from subprocess import check_call

class update_submodules(develop):
    def run(self):
        if path.exists('.git'):
            check_call(['git', 'submodule', 'update', '--init', '--recursive'])
            check_call(['git', 'submodule', 'update', '--recursive', '--remote'])
        develop.run(self)


# This class and function overrides the install python
# setup method to add an extra git command in to install
# the submodule
class initialize_submodules(install):
    def run(self):
        if path.exists('.git'):
            print("updating")
            check_call(['git', 'submodule', 'update', '--init', '--recursive'])
            check_call(['git', 'submodule', 'update', '--recursive', '--remote'])
        if self.old_and_unmanageable or self.single_version_externally_managed:
            return orig.install.run(self)
        caller = sys._getframe(2)
        caller_module = caller.f_globals.get('__name__', '')
        caller_name = caller.f_code.co_name
        if caller_module != 'distutils.dist' or caller_name != 'run_commands':
            # We weren't called from the command line or setup(), so we
            # should run in b`ackward-compatibility mode to support bdist_*
            # commands.
            orig.install.run(self)
        else:
            self.do_egg_install()

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

exec(open('pydarn/version.py').read())
warnings.warn("If you are going to use Fan, Grid, and/or Convection Map "
                 "plots, then make sure cartopy is installed on your machine. "
                 "If you do not need to use cartopy for your plotting, ignore "
                 "this message.")

# Setup information
setup(
    cmdclass={'install': initialize_submodules, 'develop': update_submodules},
    name="pydarn",
    version=__version__,
    long_description=long_description,
    long_description_content_type='text/markdown',
    description="Data visualization library for SuperDARN data",
    url='https://pydarn.readthedocs.io/en/latest/',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'],
    python_requires='>=3.6',
    packages=find_packages(exclude=['docs', 'test']),
    author="SuperDARN Data Visualization Working Group",
    # used to import the logging config file into pydarn.
    include_package_data=True,
    # setup_requires=['pyyaml', 'numpy', 'matplotlib', 'aacgmv2'],
    install_requires=['pyyaml', 'numpy', 'matplotlib>=3.3.4', 'aacgmv2',
                      'pydarnio>=1.1.0'],
)
