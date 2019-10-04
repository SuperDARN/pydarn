# Copyright (C) 2019 SuperDARN
# Author: Marina Schmidt

import matplotlib.pyplot as plt
import unittest

from datetime import datetime

import pydarn

class TestRTP(unittest.TestCase):
    """
    Testing class RTP, due to the plotting nature all plots will be saved
    since there is return testing
    """
    @classmethod
    def setUpClass(cls):
        """
        Runs once before all tests are ran. Loads and reads in the
        fitacf file that will be used in all the unit tests.
        """
        fitacf_file = "../testfiles/20180220.C0.rkn.fitacf"
        darn_read = pydarn.DarnRead(fitacf_file)
        cls.fitacf_data = darn_read.read_fitacf()

    def test_summary_like_plot(self):
        """
        plots four parameter range-time plots similar to a summary plots
        """

        plt.subplot(7, 1, 1)
        plt.title("Summary style plot")
        pydarn.RTP.plot_time_series(self.fitacf_data, parameter='nave',
                                    beam_num=7)
        pydarn.RTP.plot_time_series(self.fitacf_data, parameter='tfreq',
                                    beam_num=7)
        plt.ylabel('$MHz$')

        plt.subplot(7, 1, 2)
        pydarn.RTP.plot_time_series(self.fitacf_data, parameter='cp',
                                    beam_num=7)

        plt.subplot(7, 1, 3)
        pydarn.RTP.plot_time_series(self.fitacf_data, parameter='noise.sky',
                                    beam_num=7, scale='log')
        pydarn.RTP.plot_time_series(self.fitacf_data, parameter='noise.search',
                                    beam_num=7, scale='log')

        plt.subplot(7, 1, 4)
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='elevation',
                                   beam_num=7)
        plt.subplot(7, 1, 5)
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='power',
                                   beam_num=7)

        plt.subplot(7, 1, 6)
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='velocity',
                                   beam_num=7, color_map='jet_r')

        plt.subplot(7, 1, 7)
        pydarn.RTP.plot_range_time(self.fitacf_data,
                                   parameter='spectral width',
                                   beam_num=7)

        plt.show()

if __name__ == '__main__':
    unittest.main()
