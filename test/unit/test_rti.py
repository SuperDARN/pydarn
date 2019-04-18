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
                                   beam_num=7, ground_scatter=False,
                                   norm_range=(0,57))
        plt.title("Simple Elevation no ground scatter, beam 7 Saskatoon plot")
        plt.show()

    def test_ground_scatter_range_time_plot(self):
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='elevation',
                                   beam_num=7, ground_scatter=True)
        plt.title("Elevation with Ground Scatter with beam 7")
        plt.show()

    def test_velocity_range_time_plot(self):
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='velocity',
                                   beam_num=5, color_map='jet_r')
        plt.title("Velocity with reversed jet color map")
        plt.show()

    def test_velocity_error_range_time_plot(self):
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='v_e',
                                   beam_num=5, color_map='jet_r',
                                   color_bar_label="velocity error $m/s$",
                                   value_boundaries=(-200, 200))
        plt.title("Non-standard parameter: Velocity error\n"\
                  " with reversed jet color map")
        plt.show()


    def test_power_range_time_plot(self):
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='power',
                                   beam_num=7, ground_scatter=True)
        plt.title("Elevation with Ground Scatter")
        plt.show()

    def test_multiplots_range_time_plt(self):
        plt.subplots(121)
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='elevation',
                                   beam_num=7)
        plt.subplots(122)
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='elevation',
                                   beam_num=15)
        plt.title("Subplots using plt method")
        plt.show()

    def test_axes_object_range_time_plot(self):
        fig, ax = plt.subplots()
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='elevation',
                                   beam_num=7, ax=ax)
        ax.set_xlabel("Date (UTC)")
        ax.set_ylabel("Elevation $degrees$")
        fig.suptitle("RTP plot using Axes object")
        plt.show()

    def test_multiplots_axes_object_range_time_plot(self):
        fig, (ax1, ax2) = plt.subplots(2,1)
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='elevation',
                                   beam_num=7, ax=ax1)
        ax1.set_ylabel("Elevation $degrees$")

        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='elevation',
                                   beam_num=15, ax=ax2)
        ax2.set_xlabel("Date (UTC)")
        ax2.set_ylabel("Elevation $degrees$")

        fig.suptitle("RTP subplots using Axes Object")
        plt.show()

    def test_zero_data_to_plot(self):
        with self.assertRaises(pydarn.rtp_exceptions.RTPNoDataFoundError):
            pydarn.RTP.plot_range_time(self.fitacf_data, parameter='elevation',
                                       beam_num=7,
                                       time_span=(datetime(2018, 12, 8, 0, 0),
                                                   datetime(2018, 12, 8, 8, 0)),
                                       ground_scatter=True)


    def test_gapped_data_range_time_plt(self):
        gapped_data = []
        for i in range(0, 500):
            gapped_data.append(self.fitacf_data[i])
        for i in range(5000, 10000):
            gapped_data.append(self.fitacf_data[i])

        pydarn.RTP.plot_range_time(gapped_data, parameter='elevation',
                                   beam_num=7, ground_scatter=True,
                                   norm_range=(0,57))
        plt.title("Gapped Elevation Data")
        plt.show()

    def test_time_span_range_time_plot(self):
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='elevation',
                                   beam_num=7,
                                   time_span=(datetime(2018, 12, 9, 0, 0),
                                               datetime(2018, 12, 9, 8, 0)),
                                   ground_scatter=True)
        plt.title("Time range between 00:00 - 08:00")
        plt.show()

    def test_range_time_plot_for_all_beams(self):
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='elevation',
                                   beam_num="all")
        plt.title("Elevation plot of all beams")
        plt.show()

    def test_summary_range_time_plot(self):
        plt.subplots(141)
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='elevation',
                                   beam_num=7)
        plt.subplots(142)
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='power',
                                   beam_num=7)

        plt.subplots(143)
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='velocity',
                                   beam_num=7, color_map='jet_r')

        plt.subplots(144)
        pydarn.RTP.plot_range_time(self.fitacf_data,
                                   parameter='spectral width',
                                   beam_num=7)

        plt.title("Summary style plot")
        plt.show()

    def test_range_time_data_format_plot(self):
        pydarn.RTP.plot_range_time(self.fitacf_data, date_fmt="%H:%M")
        plt.xlabel("Date format HH:MM")
        plt.title("Change in date format")
        plt.show()

    def test_range_time_plot_with_no_color_bar(self):
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='elevation',
                                   color_bar=False)
        plt.title("Elevation, No Color Bar")
        plt.show()

    def test_range_time_plot_for_all_beams(self):
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='elevation',
                                   beam_num="all")
        plt.title("Elevation plot of all beams")
        plt.show()

    def test_calling_time_series_parameter_for_range_time_plot(self):
        with self.assertRaises(pydarn.rtp_exceptions.RTPIncorrectPlotMethodError):
            pydarn.RTP.plot_range_time(self.fitacf_data, parameter='sky noise',
                                       beam_num="all")

    def test_calling_scalar_parameter_for_range_time_plot(self):
        with self.assertRaises(pydarn.rtp_exceptions.RTPIncorrectPlotMethodError):
            pydarn.RTP.plot_range_time(self.fitacf_data, parameter='stid',
                                       beam_num="all")
    def test_calling_non_existant_parameter(self):
        with self.assertRaises(pydarn.rtp_exceptions.RTPUnkownParameter):
            pydarn.RTP.plot_range_time(self.fitacf_data, parameter='dummy',
                                       beam_num="all")


if __name__ == '__main__':
    unittest.main()
