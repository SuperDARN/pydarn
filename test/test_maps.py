# Copyright (C) 2020 SuperDARN Canada, University of Saskatchewan
# Author: Carley Martin
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

import datetime as dt
import matplotlib.pyplot as plt
import pytest
import warnings

import pydarn


data = pydarn.SuperDARNRead('test/data/test.north.mp').read_map()


class TestMap_defaults:

    def test_map_defaults(self):
        """ """
        with warnings.catch_warnings(record=True):
            pydarn.Maps.plot_mapdata(data)

@pytest.mark.parametrize('colorbar', [False])
@pytest.mark.parametrize('colorbar_label', 'green')
@pytest.mark.parametrize('title', [False])
@pytest.mark.parametrize('cmap', [plt.get_cmap('rainbow')])
@pytest.mark.parametrize('time_delta', [2])
@pytest.mark.parametrize('radar_location', [True])
@pytest.mark.parametrize('zmin', [0])
@pytest.mark.parametrize('zmax', [100])
@pytest.mark.parametrize('len_factor', [150.0, 100.0])
@pytest.mark.parametrize('color_vectors', [False])
@pytest.mark.parametrize('hmb', [False])
@pytest.mark.parametrize('map_info', [False])
@pytest.mark.parametrize('imf_dial', [False])
@pytest.mark.parametrize('reference_vector', [1000])
class TestMap:

    def test_plot_map(self, colorbar, colorbar_label,
                      title, cmap, time_delta, radar_location,
                      zmin, zmax, len_factor, color_vectors, hmb, map_info,
                      imf_dial, reference_vector):
        """ this test will give bare minimum input needed for """
        with warnings.catch_warnings(record=True):
            pydarn.Maps.plot_mapdata(data, colorbar=colorbar, cmap=cmap,
                                  colorbar_label=colorbar_label, title=title,
                                  time_delta=time_delta,
                                  radar_location=radar_location, zmin=zmin,
                                  zmax=zmax, len_factor=len_factor,
                                  color_vectors=color_vectors, hmb=hmb,
                                  imf_dial=imf_dial,
                                  reference_vector=reference_vector)
        plt.close('all')
