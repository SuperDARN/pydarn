#  Copyright (C) 2020 SuperDARN Canada, University of Saskatchewan
#  Author: Cooper Ross Robertson, Summer Student 2020
import matplotlib.pyplot as plt
import numpy as np

from typing import List

from pydarn import SuperDARNRadars, exceptions, RTP


class Power():
    """
    Power class to plot SuperDARN RAWACF data power related.


    Methods
    -------
    plot_lag0
    """
    def _str_(self):

        return "This class provides the following methods: \n"\
                " - plot_interference()"

    @classmethod
    def plot_lag0(cls, records: List[dict], beam_num: int = 0,
                  compare: bool = True, frequency: float = 11000,
                  statistical_calc: object = np.mean):

        """
        This function will plot lag 0 power as a function of time.


        Extra  Details
        --------------
        If the records that are input correspond to politescan data then this
        can be a useful method for determining background interference
        variations and patterns.

        If you wish to compare the background interference associated with two
        different frequencies then let compare=true. The frequencies will be
        organized by the 'frequency' input. For example, if politescan ran
        with 10.3 and 12.2 MHz then you could let 'frequency' equal 11000.
        All records with tfreq below 11000 will be separated from those records
        with tfreq above 11000. If compare = False then frequency is simply
        the frequency that politescan ran with i.e 12.2 MHz exclusively.

        Future Work
        ___________
        Allow for multi-beam comparison to get a directional
        sense of the interference


        statistical_calcs
        __________
        records: List[dict]
        beam_num: int
            The beam number with the desired data to plot
        compare: bool
            determines if a single frequency is use in plotting lag0
            (compare=False) or two frequencies between a frequency
            (compare=True)
            default: False
        frequency: int
            frequency to specifically look for or split between depending
            on the setting of compare.
            default: 1100 kHz
        statistical_calc: numpy object
            numpy statistical calculation or generic min or max functions
            default. numpy.mean

        Raise
        -----
        NoDataFound
        """

        # consider the case when we do not want to compare frequencies but
        # rather just look at interference with a single frequency
        if compare:
            # now compare frequencies separated by a frequency cutoff
            # predefine the lists of separated records
            low_freq_records = [record for record in records
                                if record['tfreq'] < frequency]
            high_freq_records = [record for record in records
                                 if record['tfreq'] > frequency]

            if len(low_freq_records) == 0 and high_freq_records == 0:
                exceptions.plot_exceptions.\
                      NoDataFoundError('lag0', beam_num,
                                       opt_beam_num=records[0]['bmnum'])
            # gather important info regarding the records of interest
            # get the date information from the first record
            date = low_freq_records[0]['origin.time']
            # get the site location
            stid = high_freq_records[0]['stid']
            # site location in terms of abbreviation
            radar_abbrev = SuperDARNRadars.radars[stid].hardware_info.abbrev
            # now compute the statistical statistical_calc of lag 0 power to be
            # plotted in the high frequency records
            high_freq_records = [statistical_calc(record['pwr0'])
                                 for record in high_freq_records]
            # then the low frequency records
            low_freq_records = [statistical_calc(record['pwr0'])
                                for record in low_freq_records]

            plt.subplot(2, 1, 1)
            RTP.plot_time_series(high_freq_records, statistical_calc='noise',
                                 beam_num=beam_num)
            plt.title(statistical_calc.capitalize() + ' Lag 0 Power at ' +
                      str(radar_abbrev) + ' on ' + str(
                date) + '\n Beam: ' + str(beam_num))
            plt.ylabel(str(statistical_calc) + ' Power \n [raw units]')
            plt.legend([str(high_freq_records[0]['tfreq']) + ' kHz'])

            plt.subplot(2, 1, 2)
            RTP.plot_time_series(low_freq_records, statistical_calc='noise',
                                 beam_num=beam_num)
            plt.ylabel(str(statistical_calc) + ' Power \n [raw units]')
            plt.legend([str(low_freq_records[0]['tfreq']) + ' kHz'])
        else:
            # get records of interest that have a specific frequency
            records_of_interest = [record for record in records
                                   if record['tfreq'] == frequency]

            if len(records_of_interest) == 0:
                exceptions.plot_exceptions.\
                      NoDataFoundError('lag0', beam_num,
                                       opt_beam_num=records[0]['bmnum'])

            # gather important info regarding the records of interest
            date = records_of_interest[0]['origin.time']
            stid = records_of_interest[0]['stid']
            radar_abbrev = SuperDARNRadars.radars[stid].hardware_info.abbrev

            records_of_interest = [statistical_calc(record['pwr0'])
                                   for record in records_of_interest]

            plt.figure()
            # use the time series RTP function
            RTP.plot_time_series(records_of_interest, statistical_calc='noise',
                                 beam_num=beam_num)
            plt.ylabel(str(statistical_calc) + ' Power \n [raw units]')
            plt.title(str(statistical_calc) + ' Lag 0 Power at ' +
                      str(radar_abbrev) + ' on ' + str(
                date) + '\n Beam: ' + str(
                beam_num) + '  Frequency: ' + str(frequency) + ' kHz')
