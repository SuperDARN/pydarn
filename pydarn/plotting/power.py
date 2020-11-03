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
    plot_pwr0_statistic()
    """
    def _str_(self):

        return "This class provides the following methods: \n"\
                " - plot_interference()"

    @classmethod
    def plot_pwr0_statistic(cls, records: List[dict], beam_num: int = 0,
                            compare: bool = True, frequency: float = 11000,
                            statistical_calc: object = np.mean):

        """
        This function will calculate and plot a statistic of the lag-0
        power of each record as a function of time.

        This function applies the statistical function (ex. numpy.mean)
        to the pwr0 vector (lag-0 power for each range) for each record
        before plotting the results from all records chronologically.

        Notes
        -----
        This code can be used to study background interference in rawacf data
        when the radar has been operating in a receive-only mode such as 
        "politescan" (cpid -3380), or during periods without any obvious 
        coherent scatter returns from any range.

        If you wish to compare the background interference associated with two
        different frequencies then let compare=true. The frequencies will be
        organized by the 'frequency' input. For example, if politescan ran
        with 10.3 and 12.2 MHz then you could let 'frequency' equal 11000.
        All records with tfreq below 11000 will be separated from those records
        with tfreq above 11000. If compare = False then frequency is simply
        the frequency that politescan ran with i.e 12.2 MHz exclusively.

        Future Work
        -----------
        Allow for multi-beam comparison to get a directional
        sense of the interference


        Parameters
        ----------
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
            e.g. numpy.std, numpy.median, numpy.min, numpy.max
            default: numpy.mean

        Raise
        -----
        NoDataFound
        """

        if compare:
            # now compare frequencies separated by a frequency cutoff
            # predefine the lists of separated records
            low_freq_records = [record for record in records
                                if record['tfreq'] < frequency]
            high_freq_records = [record for record in records
                                 if record['tfreq'] > frequency]

            if len(low_freq_records) == 0 and high_freq_records == 0:
                raise(exceptions.plot_exceptions.\
                      NoDataFoundError('lag0', beam_num,
                                       opt_beam_num=records[0]['bmnum']))
            # gather important info regarding the records of interest
            # get the date information from the first record
            date = low_freq_records[0]['origin.time']
            # get the site location
            stid = high_freq_records[0]['stid']
            # site location in terms of abbreviation
            radar_abbrev = SuperDARNRadars.radars[stid].hardware_info.abbrev
            # now compute the statistical statistical_calc of lag 0 power to be
            # plotted in the high frequency records
            for record in high_freq_records:
                stat_pwr = statistical_calc(record['pwr0'])
                record.update({'pwr0': stat_pwr})
            for record in low_freq_records:
                stat_pwr = statistical_calc(record['pwr0'])
                record.update({'pwr0': stat_pwr})

            plt.subplot(2, 1, 1)
            RTP.plot_time_series(high_freq_records, parameter='pwr0',
                                 beam_num=beam_num)
            plt.title(' Lag 0 Power for {} Beam: {} '.format(radar_abbrev,
                                                             beam_num))
            plt.ylabel("{} Power\n [raw units]".format(statistical_calc))
            plt.legend(["{} kHz".format(low_freq_records[0]['tfreq'])])
            plt.xticks([])
            plt.subplot(2, 1, 2)
            RTP.plot_time_series(low_freq_records, parameter='pwr0',
                                 beam_num=beam_num)
            plt.ylabel("{} Power\n [raw units]".format(statistical_calc))
            plt.legend(["{} kHz".format(low_freq_records[0]['tfreq'])])
        else:
            # get records of interest that have a specific frequency
            records_of_interest = [record for record in records
                                   if record['tfreq'] == frequency]

            if len(records_of_interest) == 0:
                raise(exceptions.plot_exceptions.\
                      NoDataFoundError('lag0', beam_num,
                                       opt_beam_num=records[0]['bmnum']))

            # gather important info regarding the records of interest
            date = records_of_interest[0]['origin.time']
            stid = records_of_interest[0]['stid']
            radar_abbrev = SuperDARNRadars.radars[stid].hardware_info.abbrev

            for record in records_of_interest:
                stat_pwr = statistical_calc(record['pwr0'])
                record.update({'pwr0': stat_pwr})

            plt.figure()
            # use the time series RTP function
            RTP.plot_time_series(records_of_interest, parameter='pwr0',
                                 beam_num=beam_num)
            plt.ylabel("{} Power\n [raw units]".format(statistical_calc))
            plt.legend(["{} kHz".format(low_freq_records[0]['tfreq'])])
            plt.title(' Lag 0 Power for {} Beam: {} '.format(radar_abbrev,
                                                             beam_num))
