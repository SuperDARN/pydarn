import pydarn
import unittest
import matplotlib.pyplot as plt
from datetime import datetime


class TestRTP(unittest.TestCase):
    """
    Testing class RTP, due to the plotting nature all plots will be saved
    since there is return testing
    """
    @classmethod
    def setUpClass(cls):
        fitacf_file = "../testfiles/20181209.C0.sas.fitacf"
        darn_read = pydarn.DarnRead(fitacf_file)
        cls.fitacf_data = darn_read.read_fitacf()

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

    def test_velocity_range_time_plot(self):
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='elevation',
                                   beamnum=5, color_map='jet_r',
                                   norm_range=(0,57))
        plt.title("Velocity with reversed jet color map")
        plt.show()

    def test_power_range_time_plot(self):
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='elevation',
                                   beamnum=7, ground_scatter=True,
                                   norm_range=(0,57))
        plt.title("Elevation with Ground Scatter")
        plt.show()

    def test_multiplots_range_time_plt(self):
        plt.Subplot(1,1)
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='elevation',
                                   beamnum=7)
        plt.title("Elevation for Beam 7")
        plt.Subplot(2,1)
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='elevation',
                                   beamnum=5)
        plt.title("Elevation for Beam 5")
        plt.show()

    def test_axes_object_range_time_plot(self):
        fig, ax = plt.Subplot()
        fig.subplots_adjust(hspace)
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='elevation',
                                   beamnum=7, ax=ax)
        ax.set_title("Using Axes Object")
        ax.set_xlabel("Date (UTC)")
        ax.set_ylabel("Elevation $degrees$")
        fig.suptitle("RTP subplots title")
        plt.show()

    def test_multiplots_axes_object_range_time_plot(self):
        fig, (ax1, ax2) = plt.Subplot(2,1)
        fig.subplots_adjust(hspace)
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='elevation',
                                   beamnum=7, ax=ax1)
        ax1.set_title("Using Axes Object")
        ax1.set_xlabel("Date (UTC)")
        ax1.set_ylabel("Elevation $degrees$")

        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='elevation',
                                   beamnum=5, ax=ax2)
        ax2.set_title("Using Axes Object")
        ax2.set_xlabel("Date (UTC)")
        ax2.set_ylabel("Elevation $degrees$")

        fig.suptitle("RTP subplots title")
        plt.show()

    def test_zero_data_to_plot(self):
        with self.assertRaises(pydarn.rtp_exceptions.RTPNoDataFoundError):
            pydarn.RTP.plot_range_time(self.fitacf_data, parameter='elevation',
                                       beamnum=7,
                                       time_range=(datetime(2018, 12, 8, 0, 0),
                                                   datetime(2018, 12, 8, 8, 0)),
                                       ground_scatter=True)
        plt.title("Time range between 00:00 - 08:00")
        plt.show()


    def test_gapped_data_range_time_plt(self):
        gapped_data = []
        for i in range(0, 500):
            gapped_data.append(self.fitacf_data[i])
        for i in range(5000, 10000):
            gapped_data.append(self.fitacf_data[i])

        pydarn.RTP.plot_range_time(gapped_data, parameter='elevation',
                                   beamnum=7, ground_scatter=True,
                                   norm_range=(0,57))
        plt.title("Gapped Elevation Data")
        plt.show()

    def test_time_range_range_time_plot(self):
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='elevation',
                                   beamnum=7,
                                   time_range=(datetime(2018, 12, 9, 0, 0),
                                               datetime(2018, 12, 9, 8, 0)),
                                   ground_scatter=True)
        plt.title("Time range between 00:00 - 08:00")
        plt.show()


if __name__ == '__main__':
    unittest.main()
