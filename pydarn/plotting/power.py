#  Copyright (C) 2020 SuperDARN Canada, University of Saskatchewan
#  Author: Cooper Ross Robertson, Summer Student 2020, Marina Schmidt
import copy
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
                            min_frequency: float = None,
                            max_frequency: float = None,
                            split_frequency: float = None,
                            statistical_method: object = np.mean):

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

        Future Work
        -----------
        Allow for multi-beam comparison to get a directional
        sense of the interference


        Parameters
        ----------
        records: List[dict]
        beam_num: int
            The beam number with the desired data to plot
        min_frequency: float
            set a minimum frequency boundary to plot
            default: None
        max_frequency: float
            set a maximum frequency boundary to plot
            default: None
        split_frequency: float
            frequency to specifically look for or split between depending
            on the setting of compare.
            default: None
        statistical_method: numpy object
            numpy statistical calculation or generic min or max functions
            e.g. numpy.std, numpy.median, numpy.min, numpy.max
            default: numpy.mean

        Raise
        -----
        NoDataFound
        """
        if split_frequency is None:
            if min_frequency is None and max_frequency is None:
                # Plot all frequencies
                records_of_interest = cls.__apply_stat2pwr0(records,
                                                            statistical_method,
                                                            beam_num)
                cls.__plot_pwr0(records_of_interest, beam_num,
                                statistical_method)
            else:
                # plot all frequencies lower than max_frequency
                if min_frequency is None:
                    records_of_interest = cls.\
                            __apply_stat2pwr0(records, statistical_method,
                                              beam_num, '<=', max_frequency)
                    cls.__plot_pwr0(records_of_interest, beam_num,
                                    statistical_method)

                elif max_frequency is None:
                    # plot all frequencies higher than min_frequency
                    records_of_interest = cls.\
                            __apply_stat2pwr0(records, statistical_method,
                                              beam_num, '>=', min_frequency)
                    cls.__plot_pwr0(records_of_interest, beam_num,
                                    statistical_method)

                else:
                    # plot all frequencies between min and max frequency
                    # same as single frequency plotting if min=max
                    records_of_interest = cls.\
                        __apply_stat2pwr0(records, statistical_method,
                                          beam_num, '>=', min_frequency)
                    records_of_interest = cls.\
                        __apply_stat2pwr0(records_of_interest,
                                          statistical_method,
                                          beam_num, '<=', max_frequency)

                    cls.__plot_pwr0(records_of_interest, beam_num,
                                    statistical_method)
        else:
            if min_frequency is None and max_frequency is None:
                # Plot high and low frequencies
                low_frequency_records = cls.\
                    __apply_stat2pwr0(records, statistical_method,
                                      beam_num, '<', split_frequency)
                # arbitrary pick for the inclusion of split_frequency
                high_frequency_records = cls.\
                    __apply_stat2pwr0(records, statistical_method,
                                      beam_num=beam_num, operand='>=',
                                      frequency=split_frequency)
                plt.subplot(2, 1, 1)
                cls.__plot_pwr0(low_frequency_records, beam_num,
                                statistical_method)
                plt.xticks([])
                plt.subplot(2, 1, 2)
                cls.__plot_pwr0(high_frequency_records, beam_num,
                                statistical_method, False)

            else:
                # plot all frequencies lower than
                # split_frequency and plot all frequencies between
                # split_frequency and max_frequency
                if min_frequency is None:
                    records_of_interest = cls.\
                        __apply_stat2pwr0(records, statistical_method,
                                          beam_num, '<=', max_frequency)
                    low_frequency_records = cls.\
                        __apply_stat2pwr0(records_of_interest,
                                          statistical_method,
                                          beam_num, '<', split_frequency)
                    high_frequency_records = cls.\
                        __apply_stat2pwr0(records_of_interest,
                                          statistical_method,
                                          beam_num, '>=', split_frequency)
                    plt.subplot(2, 1, 1)
                    cls.__plot_pwr0(low_frequency_records, beam_num,
                                    statistical_method)
                    plt.xticks([])
                    plt.subplot(2, 1, 2)
                    cls.__plot_pwr0(high_frequency_records, beam_num,
                                    statistical_method, False)

                elif max_frequency is None:
                    # plot all frequencies between min_frequency and
                    # split_frequency and plot all frequencies higher than
                    # split_frequency
                    records_of_interest = cls.\
                        __apply_stat2pwr0(records, statistical_method,
                                          beam_num, '>=', min_frequency)
                    low_frequency_records = cls.\
                        __apply_stat2pwr0(records_of_interest,
                                          statistical_method,
                                          beam_num, '<', split_frequency)
                    high_frequency_records = cls.\
                        __apply_stat2pwr0(records_of_interest,
                                          statistical_method,
                                          beam_num, '>=', split_frequency)
                    plt.subplot(2, 1, 1)
                    cls.__plot_pwr0(low_frequency_records, beam_num,
                                    statistical_method)
                    plt.xticks([])
                    plt.subplot(2, 1, 2)
                    cls.__plot_pwr0(high_frequency_records, beam_num,
                                    statistical_method, False)

                # if min=max=split frequency this is the same as
                # split and compare = False
                elif max_frequency != min_frequency:
                    # plot all low and high frequencies between
                    # min and max frequency
                    records_of_interest = cls.\
                        __apply_stat2pwr0(records, statistical_method,
                                          beam_num, '>=', min_frequency)
                    records_of_interest = cls.\
                        __apply_stat2pwr0(records_of_interest,
                                          statistical_method,
                                          beam_num, '<=', max_frequency)

                    low_frequency_records = cls.\
                        __apply_stat2pwr0(records_of_interest,
                                          statistical_method,
                                          beam_num, '<', split_frequency)
                    high_frequency_records = cls.\
                        __apply_stat2pwr0(records_of_interest,
                                          statistical_method,
                                          beam_num, '>=', split_frequency)
                    plt.subplot(2, 1, 1)
                    cls.__plot_pwr0(low_frequency_records, beam_num,
                                    statistical_method)
                    plt.xticks([])
                    plt.subplot(2, 1, 2)
                    cls.__plot_pwr0(high_frequency_records, beam_num,
                                    statistical_method, False)
                else:
                    records_of_interest = cls.\
                        __apply_stat2pwr0(records, statistical_method,
                                          beam_num, '==', split_frequency)
                    cls.__plot_pwr0(records_of_interest, beam_num,
                                    statistical_method)

    @staticmethod
    def __plot_pwr0(records: list, beam_num: int, statistical_method: object,
                    title: bool = True):
        """
        This is a method that handles all the plotting calls for pwr0

        Parameters
        ----------
            records: List[dict]
                data records of SuperDARN data
            beam_num: int
                beam number needed for error message if no
                data is found for the frequency
            statistical_method: object
                statistical method to apply to pwr0 array
            title: bool
                to include the title or not
                default: True
        """
        # get station ID and radar abbreviation for the title
        stid = records[0]['stid']
        radar_abbrev = SuperDARNRadars.radars[stid].hardware_info.abbrev
        # plot a time series using RTP class of pwr0
        RTP.plot_time_series(records, parameter='pwr0', beam_num=beam_num)
        plt.ylabel("[{}] A/D power\n [arbitrary units]"
                   "".format(statistical_method.__name__.capitalize()))
        # Find the range of frequencies for the legend
        min_freq = records[0]['tfreq']
        max_freq = records[0]['tfreq']
        for record in records:
            if record['tfreq'] < min_freq:
                min_freq = record['tfreq']
            if record['tfreq'] > max_freq:
                max_freq = record['tfreq']
        if min_freq == max_freq:
            plt.legend(["{} kHz".format(min_freq)])
        else:
            plt.legend(["{}-{} kHz".format(min_freq, max_freq)])

        if title:
            plt.title(' Lag 0 Power for {} Beam: {} '.format(radar_abbrev,
                                                             beam_num))

    @staticmethod
    def __apply_stat2pwr0(records: List[dict], stat_method: object,
                          beam_num: int, operand: str = '',
                          frequency: float = None):
        """
        Finds the records of interest based on the logic expression and
        frequency passed in. The record then is updated with a
        statistical method applying pwr0 to it

        Parameters
        ----------
            records: List[dict]
                data records of SuperDARN data
            stat_method: object
                statistical method to apply to pwr0 array
            beam_num: int
                beam number needed for error message if no
                data is found for the frequency
            operand: str
                str containing a logical operation to
                compare tfreq value in the records to
                the given frequency
            frequency: float
                a number to indicate the frequency threshold
                to compare to the tfreq. If none all
                frequencies are used
                default: None

        Returns
        -------
            records_of_interest: list[dict]
                contains all the records that met the operational
                condition when compared to frequency

        Raises
        ------
            NoDataFound: when no data is found within the comparison
        """

        # deep copy so we don't modify the original records
        records_of_interest = copy.deepcopy(records)

        # tfreq greater than frequency
        if operand == '>':
            records_of_interest = [record for record in records_of_interest
                                   if record['tfreq'] > frequency]
        # tfreq less than frequency
        elif operand == '<':
            records_of_interest = [record for record in records_of_interest
                                   if record['tfreq'] < frequency]
        # tfreq greater than equal to frequency
        elif operand == '>=':
            records_of_interest = [record for record in records_of_interest
                                   if record['tfreq'] >= frequency]
        # tfreq less than equal to frequency
        elif operand == '<=':
            records_of_interest = [record for record in records_of_interest
                                   if record['tfreq'] <= frequency]
        # tfreq equal to frequency
        elif operand == '==':
            records_of_interest = [record for record in records_of_interest
                                   if record['tfreq'] == frequency]

        # if no data is found so raise an error!
        if len(records_of_interest) == 0:
            raise exceptions.plot_exceptions.\
                  NoDataFoundError('tfreq', beam_num,
                                   opt_beam_num=records[0]['bmnum'],
                                   opt_parameter_value=records[0]['tfreq'])

        # loop through the applied records of interest and apply the
        # statistic method provided
        for record in records_of_interest:
            stat_pwr = stat_method(record['pwr0'])
            record.update({'pwr0': stat_pwr})
        return records_of_interest
