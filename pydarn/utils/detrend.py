import copy
import pydarn
import datetime as dt
import numpy as np
from typing import List

def detrend_running_mean(timeseries: List[float],
                         half_k: int,
                         n_times: int=None
                         ):
    """
    Detrend a given timeseries with a running mean low-pass filter.

    Parameters
    -----------
    timeseries: List[float]
        List timeseries data to detrend
    half_k: int
        Half the window size for the running mean window
    n_times: int
        Size of the timeseries list.
        Default: None, and the code will work it out
        Giving the size is faster for loops if you already have it.

    Returns
    -------
    detrended: List[float]
        Detrended timeseries data
    """

    if n_times is None:
        n_times = len(timeseries)

    detrended = []
    for i in range(n_times):
        # If the original value is None, keep it None and move on
        if timeseries[i] is None:
            detrended.append(None)
            continue

        # Define the window boundaries (clamped to edges - beware of edge effects)
        start = max(0, i - half_k)
        end = min(n_times, i + half_k + 1)

        # Extract window and filter out None values
        window_values = [v for v in timeseries[start:end] if v is not None]

        if window_values:
            # Calculate running mean and subtract
            running_mean = sum(window_values) / len(window_values)
            detrended.append(timeseries[i] - running_mean)
        else:
            # Fallback if the entire window is Nones
            detrended.append(0)

    return detrended


def detrend(fitacf_data: List[dict],
            parameter: str = 'all',
            window_length: int = 600,
            ):
    """
    Detrend a series of input fitacf records using a low-pass moving average filter.
    Useful for the study of period ULF waves or generally removing background flows.

    Parameters
    -----------
    fitacf_data: List[dict]
        List of dictionaries where each dictionary contains a fitacf record (from pydarn.read_fitacf())
    parameter: str
        The parameter to be detrended
        Default: 'both' (Velocity and SNR)
        Options: 'both', 'v', 'p_l'
    window_length: int
        Length of the detrending low-pass filter in seconds

    Returns
    -------
    fitacf_data_detrended: List[dict]
        Copy of input dmap data with detrended data substituted
    """

    # Make a copy of the fitacf for the detrended data to be substituted into
    fitacf_data_detrended = copy.deepcopy(fitacf_data)

    # Max beams and range gates for this data
    no_beams = pydarn.SuperDARNRadars.radars[pydarn.RadarID(fitacf_data[0]['stid'])].hardware_info.beams
    no_rang = fitacf_data[0]['nrang']

    # Grab slist and time lists for all records. "None" indicates no data for that record.
    slists = [rec.get('slist') for rec in fitacf_data]
    rec_times =  [dt.datetime(rec.get('time.yr'),
                              rec.get('time.mo'),
                              rec.get('time.dy'),
                              rec.get('time.hr'),
                              rec.get('time.mt'),
                              rec.get('time.sc'),
                              rec.get('time.us'))
                  for rec in fitacf_data]

    # Handle parameter choice(s)
    params = []
    if parameter == 'both' or parameter == 'v':
        params.append('v')
    if parameter == 'both' or parameter == 'p_l':
        params.append('p_l')

    # Grab the data to be detrended
    values = []
    for param in params:
        values.append([rec.get(param) for rec in fitacf_data])

    # Iterate over beams
    for bmnum in range(0, no_beams):

        # Get all the slists and times for each record on this beam
        this_beam_indexes = [i for i, d in enumerate(fitacf_data) if d.get("bmnum") == bmnum]
        this_beam_slists = [slists[i]for i in this_beam_indexes]
        this_beam_times = [rec_times[i]for i in this_beam_indexes]

        # Calculate the interval between samples in seconds
        time_delta = (this_beam_times[1] - this_beam_times[0]).total_seconds()

        # Convert window length from seconds to number of records (k)
        # We use an odd number for k to make centering cleaner
        k = int(window_length / time_delta)
        if k % 2 == 0: k += 1
        half_k = k // 2
        n_times = len(this_beam_times)

        # Get the velocities and/or the powers for this beam
        this_beam_values = []
        for value in values:
            this_beam_values.append([s for rec, s in zip(fitacf_data, value) if rec.get('bmnum') == bmnum])

        # Iterate over range gates
        all_range_detrends = []
        for rangnum in range(0, no_rang):
            indexes = [
                (np.where(sublist == rangnum)[0][0] if rangnum in sublist else None)
                if sublist is not None else None
                for sublist in this_beam_slists
            ]

            detrended_timeseries = []
            for this_beam_value in this_beam_values:
                timeseries = [
                    sublist[idx] if (sublist is not None and idx is not None) else None
                    for sublist, idx in zip(this_beam_value, indexes)
                ]

                # This bit is just a sinwave substitution to test that the detrending code is working
                # timeseries = [np.sin(x) for x in np.linspace(0, 6*np.pi, num=len(this_beam_times))]

                # Running mean detrend
                detrended = detrend_running_mean(timeseries, half_k, n_times)

                # Collect detrended timeseries for all parameters
                detrended_timeseries.append(detrended)

                # # Testing the detrend
                # fig, ax, = plt.subplots()
                # ax.plot(this_beam_times, detrended, 'b-')
                # ax.plot(this_beam_times, timeseries, 'r')
                # fig.autofmt_xdate()
                # plt.show()

            # Collect detrended timeseries for all beams List[List]
            all_range_detrends.append(detrended_timeseries)

        # Insert values into copied dmap List[dict]
        for beam_order, fitacf_index in enumerate(this_beam_indexes):
            for param_no, param in enumerate(params):
                this_beam_detrended = [sublist[param_no][beam_order] for sublist in all_range_detrends]
                fitacf_data_detrended[fitacf_index][param] = np.array([x for x in this_beam_detrended if x is not None])

    return fitacf_data_detrended
