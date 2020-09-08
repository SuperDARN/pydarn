# Copyright (C) 2020 SuperDARN Canada, University of Saskatchewan
# Author: Cooper Ross Robertson, Summer Student 2020
import matplotlib.pyplot as plt
import numpy as np

from typing import List

import pydarn


class Power():
    """
    Power class to plot SuperDARN RAWACF data power related.


    Methods
    -------
    plot_interference
    """
    def _str_(self):

        return "This class provides the following methods: \n"\
                " - plot_interference()"

    def plot_interference(cls, records: List[dict], beam_num: int,
                          frequency: float, parameter: str,
                          compare: bool = False):

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


        Parameters
        __________
        records: List[dict]
        beam_num: int
            The beam number with the desired data to plot
        frequency: int
            if compare = False then data with a tfreq value of
            frequency will be plotted
            if compare = True then the records will be separate by
            this value as a cutoff
        parameter: str
            key name indicating which statistical parameter of
            lag 0 power to plot
        compare: boolean
            if True then the records will be separated to allow for a
            comparison of interference power at two frequencies
            if false then the records will only display interference power
            for a single specified frequency

        """

        # consider the case when we do not want to compare frequencies but
        # rather just look at interference with a single frequency
        if compare is False:
            records_of_interest = []
            for record in records:
                if record['tfreq'] == frequency:
                    # then separate the record with the desired frequency
                    records_of_interest.append(record)

            if len(records_of_interest) == 0:
                print('There is no data for that beam and/or frequency.'
                      'You must select a different combination of beam number'
                      'and frequency. \n'
                      'For example, you can find data with beam: ' +
                      str(records[0]['bmnum']) + ' and Freq: ' + str(
                          records[0]['tfreq']) + ' kHz')
            # gather important info regarding the records of interest
            date = records_of_interest[0]['origin.time']
            stid = records_of_interest[0]['stid']
            radar_abbrev = pydarn.SuperDARNRadars.radars[stid].\
                hardware_info.abbrev

            for record in records_of_interest:

                # check which statistical parameter is to be plotted and
                # then compute that parameter and update the record to
                # include an additional field called 'noise'
                if parameter == 'mean':
                    mean_pwr0 = np.mean(record['pwr0'])
                    record.update({'noise': mean_pwr0})
                if parameter == 'median':
                    median_pwr0 = np.median(record['pwr0'])
                    record.update({'noise': median_pwr0})
                if parameter == 'std':
                    std = np.std(record['pwr0'])
                    record.update({'noise': std})
                if parameter == 'max':
                    mx = max(record['pwr0'])
                    record.update({'noise': mx})
                if parameter == 'min':
                    mn = min(record['pwr0'])
                    record.update({'noise': mn})

            plt.figure()
            # use the time series RTP function
            pydarn.RTP.plot_time_series(records_of_interest, parameter='noise',
                                        beam_num=beam_num)
            plt.ylabel(str(parameter).capitalize() + ' Power \n [raw units]')
            plt.title(parameter.capitalize() + ' Lag 0 Power at ' +
                      str(radar_abbrev) + ' on ' + str(
                date) + '\n Beam: ' + str(
                beam_num) + '  Frequency: ' + str(frequency) + ' kHz')
            plt.show()

        if compare is True:
            # now compare frequencies separated by a frequency cutoff
            # predefine the lists of separated records
            low_freq_records = []
            high_freq_records = []

            # separate the records by frequency
            for record in records:
                if record['tfreq'] > frequency:
                    high_freq_records.append(record)
                if record['tfreq'] < frequency:
                    low_freq_records.append(record)

            # gather important info regarding the records of interest
            # get the date information from the first record
            date = low_freq_records[0]['origin.time']
            # get the site location
            stid = high_freq_records[0]['stid']
            # site location in terms of abbreviation
            radar_abbrev = pydarn.SuperDARNRadars.radars[
                stid].hardware_info.abbrev

            # check the length of the low and high frequency records to
            # ensure there is actually data to plot
            if len(low_freq_records) == 0 and len(high_freq_records) == 0:
                print(
                    'There is no data for both frequencies above and below the'
                    'frequency cutoff that you have provided')
                exit()
            # now compute the statistical parameter of lag 0 power to be
            # plotted in the high frequency records
            for record in high_freq_records:
                # check which statistical parameter is to be plotted
                if parameter == 'mean':
                    mean_pwr0 = np.mean(record['pwr0'])
                    record.update({'noise': mean_pwr0})
                if parameter == 'median':
                    median_pwr0 = np.median(record['pwr0'])
                    record.update({'noise': median_pwr0})
                if parameter == 'std':
                    std = np.std(record['pwr0'])
                    record.update({'noise': std})
                if parameter == 'max':
                    mx = max(record['pwr0'])
                    record.update({'noise': mx})
                if parameter == 'min':
                    mn = min(record['pwr0'])
                    record.update({'noise': mn})

            # repeat for the low frequency data
            for record in low_freq_records:
                if parameter == 'mean':
                    mean_pwr0 = np.mean(record['pwr0'])
                    record.update({'noise': mean_pwr0})
                if parameter == 'median':
                    median_pwr0 = np.median(record['pwr0'])
                    record.update({'noise': median_pwr0})
                if parameter == 'std':
                    std = np.std(record['pwr0'])
                    record.update({'noise': std})
                if parameter == 'max':
                    mx = max(record['pwr0'])
                    record.update({'noise': mx})
                if parameter == 'min':
                    mn = min(record['pwr0'])
                    record.update({'noise': mn})

            plt.subplot(2, 1, 1)
            pydarn.RTP.plot_time_series(high_freq_records, parameter='noise',
                                        beam_num=beam_num)
            plt.title(parameter.capitalize() + ' Lag 0 Power at ' +
                      str(radar_abbrev) + ' on ' + str(
                date) + '\n Beam: ' + str(beam_num))
            plt.ylabel(str(parameter).capitalize() + ' Power \n [raw units]')
            plt.legend([str(high_freq_records[0]['tfreq']) + ' kHz'])

            plt.subplot(2, 1, 2)
            pydarn.RTP.plot_time_series(low_freq_records, parameter='noise',
                                        beam_num=beam_num)
            plt.ylabel(str(parameter).capitalize() + ' Power \n [raw units]')
            plt.legend([str(low_freq_records[0]['tfreq']) + ' kHz'])
