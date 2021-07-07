import pytest

import pydarn

fitacf_data = pydarn.SuperDARNRead().read_dmap('data/test.fitacf')

@pytest.fixture
def rawacf_data():
    """ read in fitacf data needed for the test functions """
    return pydarn.SuperDARNRead().read_dmap('data/test.rawacf')


def test_normal_range_time():
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

