import pydarn
import unittest
import matplotlib.pyplot as plt
from datetime import datetime


class TestRTP(unittest.TestCase):
    """
    Testing class RTP, due to the plotting nature all plots will be saved
    since there is return testing
    """
    def setUp(self):
        fitacf_file = "../testfiles/20181209.C0.sas.fitacf"
        darn_read = pydarn.DarnRead(fitacf_file)
        self.fitacf_data = darn_read.read_fitacf()

    def test_simple_range_time_plot(self):
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='elevation',
                                   beamnum=7, ground_scatter=False,
                                   norm_range=(0,57))
        plt.title("Elevation")
        plt.show()

    def test_ground_scatter_range_time_plot(self):
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='elevation',
                                   beamnum=7, ground_scatter=True,
                                   norm_range=(0,57))
        plt.title("Elevation with Ground Scatter")
        plt.show()


if __name__ == '__main__':
    unittest.main()
