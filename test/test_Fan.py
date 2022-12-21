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

with bz2.open('test/data/test.fitacf.bz2') as fp:
    fitacf_stream = fp.read()
data = pydarn.SuperDARNRead(fitacf_stream, True).read_fitacf()


class TestFan_defaults:

    def test_fan_defaults(self):
        """ """
        with warnings.catch_warnings(record=True):
            pydarn.Fan.plot_fan(data)

    def test_fov_series(self):
        """ """
        with warnings.catch_warnings(record=True):
            pydarn.Fan.plot_fov(6, dt.datetime(2020, 4, 4, 6, 2))


@pytest.mark.parametrize('stid', [5, 97])
@pytest.mark.parametrize('ranges', [(5,70)])
@pytest.mark.parametrize('boundary', [False])
@pytest.mark.parametrize('rsep', [15])
@pytest.mark.parametrize('frang', [90])
@pytest.mark.parametrize('fov_color', ['grey'])
@pytest.mark.parametrize('alpha', [0.8, 1])
@pytest.mark.parametrize('radar_location', [False])
@pytest.mark.parametrize('radar_label', [True])
@pytest.mark.parametrize('line_color', ['red'])
@pytest.mark.parametrize('line_alpha', [0.8, 1])
@pytest.mark.parametrize('date', [dt.datetime(2020, 4, 4, 6, 2)])
@pytest.mark.parametrize('grid', [True, False])
class TestFov:

    def test_fov_plot(self, stid, ranges, boundary, fov_color,
                                   alpha, radar_location, radar_label,
                                   line_color, date, grid, line_alpha, rsep,
                                   frang):
        """ this test will give bare minimum input needed for """
        with warnings.catch_warnings(record=True):
            pydarn.Fan.plot_fov(stid=stid, ranges=ranges,
                                boundary=boundary, fov_color=fov_color,
                                alpha=alpha, rsep=rsep, frang=frang,
                                radar_location=radar_location,
                                radar_label=radar_label, grid=grid,
                                line_color=line_color, date=date,
                                line_alpha=line_alpha)
        plt.close('all')


@pytest.mark.parametrize('parameter', ['p_l', 'w_l', 'v'])
@pytest.mark.parametrize('cmap', [plt.get_cmap('rainbow')])
@pytest.mark.parametrize('groundscatter', [True])
@pytest.mark.parametrize('colorbar', [False])
@pytest.mark.parametrize('colorbar_label', 'green')
@pytest.mark.parametrize('zmin', [0])
@pytest.mark.parametrize('zmax', [100])
@pytest.mark.parametrize('title', [False])
@pytest.mark.parametrize('channel', [1,2])
class TestFan:

    def test_fan_plot(self, parameter, cmap, groundscatter, colorbar,
                      colorbar_label, zmin, zmax, title, channel):
        """

        """
        with warnings.catch_warnings(record=True):
            pydarn.Fan.plot_fan(data, parameter=parameter, cmap=cmap,
                                groundscatter=groundscatter, colorbar=colorbar,
                                colorbar_label=colorbar_label, zmin=zmin,
                                zmax=zmax, title=title, channel=channel)
