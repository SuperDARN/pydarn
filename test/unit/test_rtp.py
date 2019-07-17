# Copyright 2019 SuperDARN
# Authors: Marina Schmidt

import matplotlib.pyplot as plt
import unittest

from datetime import datetime

import pydarn

# TODO: discuss show vs. save image? Also how does this fit in python test?
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
        #fitacf_file = "../testfiles/20190203.0001.00.fhw.fitacf3"
        fitacf_file = "../testfiles/20180220.C0.rkn.fitacf"
        darn_read = pydarn.DarnRead(fitacf_file)
        cls.fitacf_data = darn_read.read_fitacf()

    def test_simple_time_series_plot(self):
        """
        plots a simple elevation time-series plot for beam 7
        """
        pydarn.RTP.plot_time_series(self.fitacf_data, parameter='tfreq',
                                    beam_num=7)
        plt.ylabel('$MHz$')
        plt.title("Simple tfreq plot for beam 7")
        plt.show()

    def test_unknown_parameter_time_series_plot(self):
        """
        Trying to plot a time-series plot using an unknown parameter called
        dummy
        Expected behaviour is a raised exception for unknown parameter dummy
        """
        with self.assertRaises(pydarn.rtp_exceptions.RTPUnknownParameter):
            pydarn.RTP.plot_time_series(self.fitacf_data,
                                        parameter='dummy',
                                        beam_num=7)

    def test_incorrect_plot_method_array_type_time_series_plot(self):
        """
        Trying to plot a rang-time plot using the time-series plot method
        Expected behaviour is a raised exception for Incorrect plotting method
        """
        with self.assertRaises(pydarn.rtp_exceptions.RTPIncorrectPlotMethodError):
            pydarn.RTP.plot_time_series(self.fitacf_data,
                                        parameter='v_e',
                                        beam_num=7)

    def test_incorrect_plot_method_range_time_parameter_time_series_plot(self):
        """
        Trying to plot a rang-time plot using the time-series plot method
        Expected behaviour is a raised exception for Incorrect plotting method
        """
        with self.assertRaises(pydarn.rtp_exceptions.RTPIncorrectPlotMethodError):
            pydarn.RTP.plot_time_series(self.fitacf_data,
                                        parameter='elv',
                                        beam_num=7)

    def test_multiplots_time_series_plots(self):
        """
        plots multiple time-series plots using subplots
        """
        plt.subplot(2, 1, 1)
        plt.title("Multi subplot time-series plot for "
                  "sky noise and search noise")
        pydarn.RTP.plot_time_series(self.fitacf_data, parameter='noise.sky',
                                   beam_num=7, linestyle='--')
        plt.ylabel("Sky Noise")
        plt.subplot(2, 1, 2)
        pydarn.RTP.plot_time_series(self.fitacf_data, parameter='noise.search',
                                   beam_num=7, color='red')
        plt.ylabel("search Noise")
        plt.show()

    def test_axes_object_time_series_plot(self):
        """
        plots elevation time-series plot using axes object
        """
        fig, ax = plt.subplots()
        pydarn.RTP.plot_time_series(self.fitacf_data, parameter='nave',
                                   beam_num=7, ax=ax)
        ax.set_xlabel("Date (UTC)")
        fig.suptitle("Time sereies nace plot using axes object")
        plt.show()

    def test_multiplots_axes_object_time_series(self):
        """
        plots multi tranmission frequency plots using axes object
        to plot differnt channels for twofsound mode
        Note there is some missing data for when it switches
        to themisscan which uses channel 0
        """
        fig, (ax1, ax2) = plt.subplots(2, 1)
        pydarn.RTP.plot_time_series(self.fitacf_data, parameter='tfreq',
                                    beam_num=7, channel=1, ax=ax1)

        pydarn.RTP.plot_time_series(self.fitacf_data, parameter='tfreq',
                                    beam_num=7, channel=2, ax=ax2)
        ax2.set_xlabel("Date (UTC)")

        fig.suptitle("Multiple axes plots of twofsounds "
                     "transmission frequencies")
        plt.show()

    def test_overlapping_time_series_plot(self):
        """
        Plots two overlapping time-series plots: noise sky and noise search
        Includes then legend and using various parameters
        """
        pydarn.RTP.plot_time_series(self.fitacf_data, parameter='noise.sky',
                                    beam_num=7, scale='log', label='noise sky')
        pydarn.RTP.plot_time_series(self.fitacf_data, parameter='noise.search',
                                    beam_num=7, scale='log',
                                    linestyle='--', color='red',
                                    label='`noise search')
        plt.legend()
        plt.title("Overlapping sky noise and search noise")
        plt.show()

    def test_noise_mean_date_fmt_time_series_plot(self):
        """
        plots a simple elevation time-series plot for beam 7
        """
        pydarn.RTP.plot_time_series(self.fitacf_data, parameter='noise.mean',
                                    beam_num=7, date_fmt="%H:%M")
        plt.title("Simple noise mean plot for beam 7")
        plt.show()

    def test_cp_time_series_plot(self):
        """
        plots a cp ID time-series plot for beam 7
        """
        pydarn.RTP.plot_time_series(self.fitacf_data, parameter='cp',
                                    beam_num=7)
        plt.title("Simple cp ID plot for beam 7 with names")
        plt.show()


    def test_cp_no_names_time_series_plot(self):
        """
        plots a simple elevation time-series plot for beam 7
        """
        pydarn.RTP.plot_time_series(self.fitacf_data, parameter='cp',
                                    beam_num=7, cp_name=False)
        plt.title("Simple cp ID plot for beam 7 with no names")
        plt.show()

    def test_no_data_cp_time_series_plot(self):
        """
        raise an error of no data found because the time zone
        are out of the time range specified.
        """
        with self.assertRaises(pydarn.rtp_exceptions.RTPNoDataFoundError):
            pydarn.RTP.plot_time_series(self.fitacf_data, parameter='cp',
                                       beam_num=7,
                                       time_span=(datetime(2018, 12, 8, 0, 0),
                                                  datetime(2018, 12, 8, 8, 0)))
    def test_no_data_time_series_plot(self):
        """
        raise an error of no data found because the time zone
        are out of the time range specified.
        """
        with self.assertRaises(pydarn.rtp_exceptions.RTPNoDataFoundError):
            pydarn.RTP.plot_time_series(self.fitacf_data, parameter='tfreq',
                                       beam_num=7,
                                       time_span=(datetime(2018, 12, 8, 0, 0),
                                                  datetime(2018, 12, 8, 8, 0)))

    def test_no_data_time_series_plot(self):
        """
        raise an error of no data found because the time zone
        are out of the time range specified.
        """
        with self.assertRaises(IndexError):
            pydarn.RTP.plot_time_series(self.fitacf_data, parameter='tfreq',
                                       beam_num=7,
                                       time_span=(datetime(2018, 12, 8, 0, 0),
                                                  datetime(2018, 12, 8, 8, 0),
                                                  datetime(2018, 12, 8, 8, 0)))

    def test_simple_range_time_plot(self):
        """
        plots a simple elevation range-time plot for beam 7
        """
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='elv',
                                   beam_num=7,
                                   boundary=(0, 57))
        plt.title("Simple Elevation no ground scatter, beam 7 Saskatoon plot")
        plt.show()

    def test_groundscatter_range_time_plot(self):
        """
        plots a simple elevation rang-time plot with ground scatter
        """
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='elv',
                                   beam_num=7, groundscatter=True)
        plt.title("Elevation with Ground Scatter with beam 7")
        plt.show()

    def test_velocity_range_time_plot(self):
        """
        plots a velocity range-time plot for
        beam 5 with the reversed jet colour mapping
        """
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='v',
                                   beam_num=5, color_map='jet_r')
        plt.title("Velocity with reversed jet color map")
        plt.show()

    def test_velocity_error_range_time_plot(self):
        """
        plots velocity error range time plot which is not a pre-set
        parameter also added extra settings for the color bar.
        """
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='v_e',
                                   beam_num=5, color_map='jet_r',
                                   color_bar_label="velocity error $m/s$",
                                   boundary=(-200, 200))
        plt.title("Non-standard parameter: Velocity error\n"
                  " with reversed jet color map")
        plt.show()

    def test_power_range_time_plot(self):
        """
        plots power range-time with ground scatter
        """
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='p_l',
                                   beam_num=7, groundscatter=True)
        plt.title("Elevation with Ground Scatter")
        plt.show()

    def test_multiplots_range_time_plt(self):
        """
        plots multiple range-time plots using subplots
        """
        plt.subplot(2, 1, 1)
        plt.title("Subplots using plt method")
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='elv',
                                   beam_num=7)
        plt.subplot(2, 1, 2)
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='elv',
                                   beam_num=15)
        plt.show()

    def test_axes_object_range_time_plot(self):
        """
        plots elevation range-time plot using axes object
        """
        fig, ax = plt.subplots()
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='elv',
                                   beam_num=7, ax=ax)
        ax.set_xlabel("Date (UTC)")
        ax.set_ylabel("Elevation $degrees$")
        fig.suptitle("RTP plot using Axes object")
        plt.show()

    def test_multiplots_axes_object_range_time_plot(self):
        """
        plots multi elevation plots using axes object
        """
        fig, (ax1, ax2) = plt.subplots(2, 1)
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='elv',
                                   beam_num=7, ax=ax1)
        ax1.set_ylabel("Elevation $degrees$")

        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='elv',
                                   beam_num=15, ax=ax2)
        ax2.set_xlabel("Date (UTC)")
        ax2.set_ylabel("Elevation $degrees$")

        fig.suptitle("RTP subplots using Axes Object")
        plt.show()

    def test_multichannel_axes_object_range_time_plot(self):
        """
        plots multi elevation plots using axes object
        """
        fig, (ax1, ax2) = plt.subplots(2, 1)
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='elv',
                                   beam_num=7, ax=ax1, channel=1)
        ax1.set_ylabel("ch. 1")

        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='elv',
                                   beam_num=7, ax=ax2,
                                   channel=2)
        ax2.set_xlabel("Date (UTC)")
        ax2.set_ylabel("ch. 2")

        fig.suptitle("RTP subplots using Axes Object")
        plt.show()

    def test_zero_data_to_plot(self):
        """
        raise an error of no data found because the time zone
        are out of the time range specified.
        """
        with self.assertRaises(pydarn.rtp_exceptions.RTPNoDataFoundError):
            pydarn.RTP.plot_range_time(self.fitacf_data, parameter='elv',
                                       beam_num=7,
                                       time_span=(datetime(2018, 12, 8, 0, 0),
                                                  datetime(2018, 12, 8, 8, 0)),
                                       groundscatter=True)

    def test_gapped_data_range_time_plt(self):
        """
        tests if gapped data would be plotted correctly.
        Loops over the fitacf data and excludes some of
        the records to make it a gapped set of data
        """
        gapped_data = []
        for i in range(0, 500):
            gapped_data.append(self.fitacf_data[i])
        for i in range(5000, 10000):
            gapped_data.append(self.fitacf_data[i])

        pydarn.RTP.plot_range_time(gapped_data, parameter='elv',
                                   beam_num=7, groundscatter=True,
                                   boundary=(0, 57))
        plt.title("Gapped Elevation Data")
        plt.show()

    def test_time_span_range_time_plot(self):
        """
        plots an elevation range-time plot for a given time range
        """
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='elv',
                                   beam_num=7,
                                   time_span=(datetime(2018, 2, 20, 0, 0),
                                              datetime(2018, 2, 20, 8, 0)),
                                   groundscatter=True)
        plt.title("Time range between 00:00 - 08:00")
        plt.show()

    def test_range_time_plot_for_all_beams(self):
        """
        plots an elevation range-time plot for all beams
        """
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='elv',
                                   beam_num="all")
        plt.title("Elevation plot of all beams")
        plt.show()

    def test_summary_range_time_plot(self):
        """
        plots four parameter range-time plots similar to a summary plots
        """
        plt.subplot(4, 1, 1)
        plt.title("Summary style plot")
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='elv',
                                   beam_num=7)
        plt.subplot(4, 1, 2)
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='p_l',
                                   beam_num=7)

        plt.subplot(4, 1, 3)
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='v',
                                   beam_num=7, color_map='jet_r')

        plt.subplot(4, 1, 4)
        pydarn.RTP.plot_range_time(self.fitacf_data,
                                   parameter='w_l',
                                   beam_num=7)

        plt.show()

    def test_range_time_data_format_plot(self):
        """
        plot a default rang-time plot with a different date
        time format
        """
        pydarn.RTP.plot_range_time(self.fitacf_data, date_fmt="%H:%M")
        plt.xlabel("Date format HH:MM")
        plt.title("Change in date format")
        plt.show()

    def test_range_time_plot_with_no_color_bar(self):
        """
        plots a range-time plot with no color bar
        """
        pydarn.RTP.plot_range_time(self.fitacf_data, parameter='p_l',
                                   color_bar=False)
        plt.title("Elevation, No Color Bar")
        plt.show()

    def test_calling_scalar_parameter_for_range_time_plot(self):
        """
        Raises an incorrect plot error because a scalar parameter is selected
        for a range-time plot
        """
        with self.assertRaises(pydarn.rtp_exceptions.RTPIncorrectPlotMethodError):
            pydarn.RTP.plot_range_time(self.fitacf_data, parameter='stid',
                                       beam_num="all")

    def test_calling_non_existant_parameter(self):
        """
        Raises an unknown parameter error because a dummy parameter is passed
        that does not exist in the fitacf data
        """
        with self.assertRaises(pydarn.rtp_exceptions.RTPUnknownParameter):
            pydarn.RTP.plot_range_time(self.fitacf_data, parameter='dummy',
                                       beam_num="all")

    def test_simple_time_series_plot(self):
        """
        plots a simple time series plot
        """
        pydarn.RTP.plot_time_series(self.fitacf_data, parameter='tfreq',
                                    beam_num=7)
        plt.ylim(8, 18)
        plt.title("Simple Frequency plot for Beam 7")
        plt.show()

    def test_simple_summary_plot(self):
        """
        plot default summary options
        """
        pydarn.RTP.plot_summary(self.fitacf_data, beam_num=8)
        plt.show()

    def test_grounscatter_with_summary_plot(self):
        """
        plot groundscatter with summary plot
        Should only show ground scatter on velocity
        """
        pydarn.RTP.plot_summary(self.fitacf_data, beam_num=8,
                                groundscatter=True)
        plt.show()

    def test_figsize_summary_plot(self):
        """
        plot a summary plot with a different figure size
        """
        pydarn.RTP.plot_summary(self.fitacf_data, beam_num=8,
                                figsize=(14,8))
        plt.show()

    def test_boundary_wtih_summary_plot(self):
        """
        plot a summary plot with a different boundary range for velocity
        and nave
        """

        boundary = {'v': (-100,100),
                    'nave': (0, 100)}
        pydarn.RTP.plot_summary(self.fitacf_data, beam_num=7,
                                boundary=boundary)
        plt.show()

    def test_color_map_with_summary_plot(self):
        """
        plot a normal summary plot with a different color map: jet
        """
        pydarn.RTP.plot_summary(self.fitacf_data, beam_num=7,
                                color_map='jet')
        plt.show()

    def test_no_plotting_elevation_summary_plot(self):
        """
        plot a summary plot with elevation
        """
        pydarn.RTP.plot_summary(self.fitacf_data, beam_num=8,
                                plot_elv=False)

        plt.show()

    def test_summary_plot_with_custom_title(self):
        """
        plot summary plot with a custom title
        """
        pydarn.RTP.plot_summary(self.fitacf_data, beam_num=8,
                                title="Summary plot of Rankin Inlet on Feb 22nd, 2018 for beam 8")
        plt.show()


if __name__ == '__main__':
    unittest.main()
