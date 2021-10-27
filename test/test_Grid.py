# Copyright (C) 2020 SuperDARN Canada, University of Saskatchewan
# Author: Marina Schmidt
#
# Modifications:
#
# Disclaimer:
# pyDARN is under the LGPL v3 license found in the root directory LICENSE.md
# Everyone is permitted to copy and distribute verbatim copies of this license
# document, but changing it is not allowed.
#
# This version of the GNU Lesser General Public License incorporates the terms
# and conditions of version 3 of the GNU General Public License,
# supplemented by the additional permissions listed below.

import bz2
import datetime as dt
import matplotlib.pyplot as plt
import pytest
import warnings

import pydarn


data = pydarn.SuperDARNRead('test/data/test.grd').read_grid()


class TestGrid_defaults:

    def test_grid_defaults(self):
        """ """
        with warnings.catch_warnings(record=True):
            pydarn.Grid.plot_grid(data)

@pytest.mark.parametrize('colorbar', [False])
@pytest.mark.parametrize('colorbar_label', 'green')
@pytest.mark.parametrize('title', [False])
@pytest.mark.parametrize('cmap', [plt.get_cmap('rainbow')])
@pytest.mark.parametrize('record', [2])
@pytest.mark.parametrize('ranges', [(5,70)])
@pytest.mark.parametrize('time_delta', [2])
@pytest.mark.parametrize('parameter', ['wdt', 'pwr'])
@pytest.mark.parametrize('radar_location', [False])
@pytest.mark.parametrize('radar_label', [True])
@pytest.mark.parametrize('start_time', [dt.datetime(2021, 2, 5, 12, 5)])
@pytest.mark.parametrize('zmin', [0])
@pytest.mark.parametrize('zmax', [100])
@pytest.mark.parametrize('len_factor', [150.0, 100.0])
class TestGrid:

    def test_plot_grid(self, record, colorbar, colorbar_label,
                       title, cmap, ranges, time_delta,
                       parameter, radar_location, radar_label,
                       start_time, zmin, zmax, len_factor):
        """ this test will give bare minimum input needed for """
        with warnings.catch_warnings(record=True):
            pydarn.Grid.plot_grid(data, ranges=ranges,
                                  record=record, time_delta=time_delta,
                                  parameter=parameter,
                                  radar_location=radar_location,
                                  radar_label=radar_label,
                                  start_time=start_time, zmin=zmin,
                                  zmax=zmax, len_factor=len_factor)
        plt.close('all')
