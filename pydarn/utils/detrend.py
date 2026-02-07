import copy
import pydarn
import datetime as dt
import numpy as np
from scipy.signal import savgol_filter
from typing import List


class Detrend:
    """
    Methods
    -------
    detrend_running_mean
    detrend_fitacf
    """

    def __str__(self):
        return "This class is static class that provides"\
                " the following methods: \n"\
                "   - detrend_running_mean()\n"\
                "   - dentrend()\n"\


    @classmethod
    def detrend_savgol(cls,
                       timeseries: List[float],
                       half_k: int,
                       **kwargs
                       ):
        """
        Detrend a given timeseries with a Savitsky-Golay filter.

        Parameters
        -----------
        timeseries: List[float]
            List timeseries data to detrend
        half_k: int
            Half the window size for the running mean window
        **kwargs:
            Optional inputs for detrending using scipy's `savgol_filter()`
            E.g., polyorder, mode
            Defaults are polyorder = 2, mode = 'interp' (edge truncation)
        Returns
        -------
        detrended: List[float]
            Detrended timeseries data
        """

        # Convert to numpy array for processing
        y = np.array(timeseries, dtype=float)

        # Map out where the Nones are
        mask = np.isnan(y)
        # If everything is None, return as is
        if np.all(mask):
            return [None] * len(timeseries)
        indices = np.arange(len(y))

        # Linearly interpolate over "None"s so the filter can work
        # Will result in anomalous velocities/SNR's if data is sparse
        y_interp = np.copy(y)
        y_interp[mask] = np.interp(indices[mask], indices[~mask], y[~mask])

        # Generate filter series
        window_len = (half_k * 2) + 1
        if 'polyorder' not in kwargs:
            polyorder = 2
        background = savgol_filter(y_interp, window_length=window_len, polyorder=polyorder, **kwargs)

        # Detrend
        detrended_tmp = y_interp - background

        # Restore the original None positions
        # Convert back to list and replace masked values
        detrended = detrended_tmp.tolist()
        for i in range(len(detrended)):
            if mask[i]:
                detrended[i] = None

        return detrended


    @classmethod
    def detrend_running_mean(cls,
                             timeseries: List[float],
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


    @classmethod
    def detrend_fitacf(cls,
                       fitacf_data: List[dict],
                       parameter: str = 'all',
                       window_length: int = 600,
                       detrend_type: str='mean',
                       **kwargs
                       ):
        """
        Detrend a series of input fitacf records using a low-pass filter.
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
        detrend_type: str
            Type of detrending to be used
            Default: 'mean' - subtract a running mean of window_length
            Option: 'savgol' - subtract a Savitsky-Golay filter instead
        **kwargs:
            Optional inputs for detrending using scipy's `savgol_filter()`
            E.g., polyorder, mode
            Defaults are polyorder = 2, mode = 'interp' (edge truncation)

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
            if k % 2 == 0:
                k += 1
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

                    # Running mean detrend
                    if detrend_type == 'mean':
                        detrended = Detrend.detrend_running_mean(timeseries, half_k, n_times)
                    elif detrend_type == 'savgol':
                        detrended = Detrend.detrend_savgol(timeseries, half_k, **kwargs)
                    else:
                        raise NameError('No valid detrending type specified')

                    # Collect detrended timeseries for all parameters
                    detrended_timeseries.append(detrended)

                # Collect detrended timeseries for all beams List[List]
                all_range_detrends.append(detrended_timeseries)

            # Insert values into copied dmap List[dict]
            for beam_order, fitacf_index in enumerate(this_beam_indexes):
                for param_no, param in enumerate(params):
                    this_beam_detrended = [sublist[param_no][beam_order] for sublist in all_range_detrends]
                    fitacf_data_detrended[fitacf_index][param] = np.array([x for x in this_beam_detrended if x is not None])

        return fitacf_data_detrended
