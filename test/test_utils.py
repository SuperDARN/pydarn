# Copyright (C) 2023 SuperDARN Canada, University of Saskatchewan
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

import bz2
import datetime as dt
import pytest
import warnings

import pydarn


with bz2.open('test/data/test.fitacf.bz2') as fp:
    fitacf_stream = fp.read()
data = pydarn.SuperDARNRead(fitacf_stream, True).read_fitacf()


class TestUtils_citations:
    def test_citations(self):
        with warnings.catch_warnings(record=True):
            pydarn.Citations.print_citations()
    def test_acks(self):
        with warnings.catch_warnings(record=True):
            pydarn.Citations.print_acknowledgements()


class TestUtils_filters:
    def test_boxcar(self):
        with warnings.catch_warnings(record=True):
            bx = pydarn.Boxcar(thresh=0.7, w=None)
            bx.run_filter(data)


class TestUtils_general:
    def test_greatcircle(self):
        with warnings.catch_warnings(record=True):
            pydarn.GeneralUtils.great_circle(100, 50, 110, 60)
    def test_newcoord(self):
        with warnings.catch_warnings(record=True):
            pydarn.GeneralUtils.new_coordinate(100, 50, 100, 30)


@pytest.mark.parametrize('tdiff', [0.003, -0.003])
@pytest.mark.parametrize('overwrite', [True, False])
@pytest.mark.parametrize('interferometer_offset', [[0.0, 100.0, 0.0],
                                                  [1.0, -10.0, 2.0]])
class TestUtils_tdiff:
    def test_recalcelv(self, tdiff, overwrite, interferometer_offset):
        with warnings.catch_warnings(record=True):
            pydarn.recalculate_elevation(data, tdiff=tdiff,
                                         overwrite=overwrite,
                                         interferometer_offset=
                                         interferometer_offset)


class TestUtils_terminator:
    def test_terminator(self):
        with warnings.catch_warnings(record=True):
            pydarn.terminator(dt.datetime(2023,10,10,1,30), 300)


class TestUtils_calcazi:
    def test_calculateazimuth(self):
        with warnings.catch_warnings(record=True):
            pydarn.calculate_azimuth(100, 50, 100, 110, 60, 100)