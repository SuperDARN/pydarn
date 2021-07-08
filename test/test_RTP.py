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
import pytest

import pydarn

@pytest.fixture
def fitacf_data():
    """ read in fitacf data needed for the test functions """
    with bz2.open('data/test.fitacf.bz2') as fp:
        fitacf_stream = fp.read()
    return pydarn.SuperDARNRead(fitacf_stream, True).read_fitacf()


def test_normal_range_time(fitacf_data):
    """ this test will give bare minimum input needed for """
    pydarn.RTP.plot_range_time(fitacf_data)


def test_range_time_ground_scatter():
    """ """
    pass

def test_range_time_ground_scatter():
    """ """
    pass

def test_range_time_channel():
    """ """
    pass

def test_range_time_axis_object():
    """ """
    pass

def test_range_time_rawacf():
    """ """
    pass

def test_time_series():
    """ """
    pass

def test_time_series():
    """ """
    pass

def test_time_series_axis():
    """ """
    pass

def test_time_series_channel():
    """ """
    pass

def test_time_series_cpid():
    """ """
    pass

def test_summary():
    """ """
    pass

def test_summary_channel():
    """ """
    pass

def test_summary_groundscatter_str():
    """ """
    pass

def test_summary_range_gates():
    """ """
    pass

def test_summary_ground_scatter():
    """ """
    pass

def test_summary_kwargs():
    """ """
    pass

