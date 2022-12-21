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


class TestRTP_defaults:

    def test_range_time_defaults(self):
        """ """
        with warnings.catch_warnings(record=True):
            pydarn.RTP.plot_range_time(data)

    def test_normal_time_series(self):
        """ """
        with warnings.catch_warnings(record=True):
            pydarn.RTP.plot_time_series(data)

    def test_normal_summary_plot(self):
        """ """
        with warnings.catch_warnings(record=True):
            pydarn.RTP.plot_summary(data)


@pytest.mark.parametrize('background', ['w'])
@pytest.mark.parametrize('zmin', [0, -200])
@pytest.mark.parametrize('zmax', [200, 1000])
@pytest.mark.parametrize('groundscatter_params', [True, 'grey'])
@pytest.mark.parametrize('colorbar_label', ['test'])
@pytest.mark.parametrize('yspacing', [150, 250])
@pytest.mark.parametrize('range_estimation',
                         [pydarn.RangeEstimation.RANGE_GATE,
                          pydarn.RangeEstimation.GSMR,
                          pydarn.RangeEstimation.HALF_SLANT])
@pytest.mark.parametrize('ymin', [10])
@pytest.mark.parametrize('ymax', [70])
@pytest.mark.parametrize('parameters', ['v', 'p_l', 'w_l'])
@pytest.mark.parametrize('cmap', [plt.get_cmap('rainbow')])
@pytest.mark.parametrize('start_time', [dt.datetime(2018, 4, 4, 6, 2)])
@pytest.mark.parametrize('end_time', [dt.datetime(2018, 4, 4, 6, 4)])
@pytest.mark.parametrize('date_fmt', ['%H:%M'])
@pytest.mark.parametrize('round_start', [False])
class TestRangTime:

    def test_parameters_range_time(self, groundscatter_params,
                                   parameters, background, zmin, zmax,
                                   start_time, end_time, ymin, ymax,
                                   colorbar_label, yspacing, round_start,
                                   range_estimation, cmap, date_fmt):
        """ this test will give bare minimum input needed for """
        with warnings.catch_warnings(record=True):
            pydarn.RTP.plot_range_time(data, beam_num=15,
                                       parameter=parameters, channel=1,
                                       groundscatter=groundscatter_params,
                                       background=background, zmin=zmin,
                                       zmax=zmax, start_time=start_time,
                                       end_time=end_time, ymin=ymin, ymax=ymax,
                                       colorbar_label=colorbar_label,
                                       yspacing=yspacing,
                                       round_start=round_start,
                                       range_estimation=range_estimation,
                                       cmap=cmap, date_fmt=date_fmt)
        plt.close('all')

    def test_parameters_channel_2_range_time(self, groundscatter_params,
                                             parameters, background, zmin,
                                             zmax, start_time, end_time,
                                             ymin, ymax, colorbar_label,
                                             yspacing, round_start,
                                             range_estimation,
                                             cmap, date_fmt):
        """ this test will give bare minimum input needed for """
        with warnings.catch_warnings(record=True):
            pydarn.RTP.plot_range_time(data, beam_num=9,
                                       parameter=parameters, channel=2,
                                       groundscatter=groundscatter_params,
                                       background=background, zmin=zmin,
                                       zmax=zmax, start_time=start_time,
                                       end_time=end_time, ymin=ymin, ymax=ymax,
                                       colorbar_label=colorbar_label,
                                       yspacing=yspacing,
                                       round_start=round_start,
                                       range_estimation=range_estimation,
                                       cmap=cmap, date_fmt=date_fmt)
        plt.close('all')


@pytest.mark.parametrize('parameters_scalar', ['tfreq', 'cp', 'nave',
                                               'p_l', 'w_l', 'v'])
@pytest.mark.parametrize('gate', [38, 48])
@pytest.mark.parametrize('scale', ['linear', 'log'])
@pytest.mark.parametrize('cp_name', [True, False])
@pytest.mark.parametrize('color', ['green'])
@pytest.mark.parametrize('linestyle', ['--'])
@pytest.mark.parametrize('linewidth', [0.5, 2])
@pytest.mark.parametrize('start_time', [dt.datetime(2018, 4, 4, 6, 2)])
@pytest.mark.parametrize('end_time', [dt.datetime(2018, 4, 4, 6, 4)])
@pytest.mark.parametrize('date_fmt', ['%H:%M'])
@pytest.mark.parametrize('round_start', [False])
class TestTimeSeries:

    def test_parameters_time_series_channel2(self, parameters_scalar, gate,
                                             scale, cp_name, color, linestyle,
                                             linewidth, date_fmt, end_time,
                                             start_time, round_start):
        """

        """
        with warnings.catch_warnings(record=True):
            pydarn.RTP.plot_time_series(data, parameter=parameters_scalar,
                                        beam_num=9, gate=gate,
                                        start_time=start_time,
                                        end_time=end_time, date_fmt=date_fmt,
                                        channel=2, scale=scale,
                                        cp_name=cp_name, color=color,
                                        linestyle=linestyle,
                                        linewidth=linewidth,
                                        round_start=round_start,)

    def test_parameters_time_series_channel1(self, parameters_scalar, gate,
                                             scale, cp_name, color, linestyle,
                                             linewidth, date_fmt, end_time,
                                             start_time, round_start):
        """

        """
        with warnings.catch_warnings(record=True):
            pydarn.RTP.plot_time_series(data, parameter=parameters_scalar,
                                        beam_num=15, gate=gate,
                                        start_time=start_time,
                                        end_time=end_time, date_fmt=date_fmt,
                                        channel=1, scale=scale,
                                        cp_name=cp_name, color=color,
                                        linestyle=linestyle,
                                        linewidth=linewidth,
                                        round_start=round_start,)


@pytest.mark.parametrize('fig_size', [(11, 10), (10, 11)])
@pytest.mark.parametrize('watermark', [False, True])
@pytest.mark.parametrize('boundary', [{'w_l': (0, 100),
                                       'nave': (0, 30),
                                       'elv': (0, 20),
                                       'tfreq': (0, 15)}])
@pytest.mark.parametrize('cmaps', [{'elv': plt.get_cmap('rainbow'),
                                    'p_l': plt.get_cmap('rainbow'),
                                    'vel': plt.get_cmap('rainbow')}])
@pytest.mark.parametrize('lines', [{'nave': '--', 'tfreq': '-'}])
@pytest.mark.parametrize('plot_elv', [False])
@pytest.mark.parametrize('title', ['test test'])
@pytest.mark.parametrize('background', ['grey'])
@pytest.mark.parametrize('groundscatter', [False, 'grey'])
@pytest.mark.parametrize('range_estimation',
                         [pydarn.RangeEstimation.RANGE_GATE,
                          pydarn.RangeEstimation.GSMR,
                          pydarn.RangeEstimation.HALF_SLANT])
class TestSummaryPlots:

    def test_params_summary_plots(self, fig_size, watermark, boundary, cmaps,
                                  lines, plot_elv, title, background,
                                  groundscatter, range_estimation):
        with warnings.catch_warnings(record=True):
            pydarn.RTP.plot_summary(data, beam_num=15, channel=1,
                                    figsize=fig_size, watermark=watermark,
                                    boundary=boundary, cmaps=cmaps,
                                    lines=lines, plot_elv=plot_elv,
                                    title=title, background=background,
                                    groundscatter=groundscatter,
                                    range_estimation=range_estimation)
        plt.close('all')

    def test_beam9_channel2_summary_plots(self, fig_size, watermark, boundary,
                                          cmaps, lines, plot_elv, title,
                                          background, groundscatter,
                                          range_estimation):
        with warnings.catch_warnings(record=True):
            pydarn.RTP.plot_summary(data, beam_num=9, channel=2,
                                    figsize=fig_size, watermark=watermark,
                                    boundary=boundary, cmaps=cmaps,
                                    lines=lines, plot_elv=plot_elv,
                                    title=title, background=background,
                                    groundscatter=groundscatter,
                                    range_estimation=range_estimation)
        plt.close('all')
