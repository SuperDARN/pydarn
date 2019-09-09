# Copyright 2019 SuperDARN Canada, University of Saskatchewan
# Authors: Liam Graham, Marci Detwiller
"""
This file contains a function for processing beam-formed IQ data into rawacf
data product matching the real-time product produced by datawrite module in 
Borealis.

Functions
---------
bfiq_to_rawacf_postprocessing: reads a bfiq file, processes the data within 
    to a rawacf format, and writes a rawacf file. The data is the same as if
    the write had happened on site. Read/write can be done as arrays or 
    as records. 

Exceptions
----------
BorealisFileTypeError
BorealisFieldMissingError
BorealisExtraFieldError
BorealisDataFormatTypeError
BorealisNumberOfRecordsError
BorealisConversionTypesError
BorealisConvert2IqdatError
BorealisConvert2RawacfError
BorealisRestructureError
ConvertFileOverWriteError

See Also
--------
read_borealis_file
write_borealis_file
borealis_site_to_array_dict
"""

import deepdish as dd
import numpy as np
import os
import subprocess as sp
import sys
import tables
import warnings

from collections import OrderedDict
from datetime import datetime as dt
from pathlib2 import Path

from pydarn import borealis_exceptions, read_borealis_file, \
                   write_borealis_file, borealis_site_to_array_dict

def bfiq_to_rawacf_postprocessing(bfiq_filepath: str, rawacf_filepath: str, 
                                  site: bool, write_site: bool = False):
    """
    Processes the data from a bfiq.hdf5 file and creates auto and cross 
    correlations from the samples.
    
    This data is formatted and written as Borealis rawacf hdf5 files the 
    same as if they had been produced on site. 

    Parameters 
    ----------
    bfiq_filepath: str
        The file where the bfiq hdf5 data is located. Can be record or array 
        stored as per site flag.
    rawacf_filepath: str
        The path to where you want to place the rawacf hdf5 data. Rawacf 
        data will be stored as per the write_site flag. 
    site: bool
        How to read the bfiq data. If True, will read as record stored data 
        (site files). If False, will read as array stored. 
    write_site: bool
        How to write the rawacf data. If True, will write in record by record
        site format. If False, will write in array format. Default False.

    Raises
    ------
    BorealisFileTypeError
    BorealisFieldMissingError
    BorealisExtraFieldError
    BorealisDataFormatTypeError
    BorealisNumberOfRecordsError
    BorealisConversionTypesError
    BorealisConvert2IqdatError
    BorealisConvert2RawacfError
    BorealisRestructureError
    ConvertFileOverWriteError
    """

    if bfiq_filepath == rawacf_filepath:
        raise borealis_exceptions.ConvertFileOverWriteError(bfiq_filepath)

    def correlate_samples(ts_dict: dict) -> np.ndarray:
        """
        Builds the autocorrelation and cross-correlation matrices for the 
        beamformed data contained in one timestamped dictionary
        
        Parameters
        ----------
        ts_dict
            A timestamped record dictionary from a Borealis bfiq file

        Returns
        -------
        out_main
            Main array correlations
        out_intf
            Interferometer array correlations
        out_cross
            Cross correlations between arrays

        """
        data_buff = ts_dict["data"]
        num_slices = ts_dict["num_slices"]
        num_ant_arrays = ts_dict["data_dimensions"][0]
        num_sequences = ts_dict["data_dimensions"][1]
        num_beams = ts_dict["data_dimensions"][2]
        num_samples = ts_dict["data_dimensions"][3]
        dims = ts_dict["data_dimensions"]

        lags = ts_dict["lags"]
        num_lags = np.shape(ts_dict["lags"])[0]
        num_ranges = ts_dict["num_ranges"]
        num_slices = ts_dict["num_slices"]
        
        data_mat = data_buff.reshape(dims)

        # Get data from each antenna array
        main_data = data_mat[0][:][:][:]
        intf_data = data_mat[1][:][:][:]

        # Preallocate arrays for correlation results
        main_corrs = np.zeros((num_sequences, num_beams, num_samples, 
                              num_samples), dtype=np.complex64)
        intf_corrs = np.zeros((num_sequences, num_beams, num_samples, 
                              num_samples), dtype=np.complex64)
        cross_corrs = np.zeros((num_sequences, num_beams, num_samples, 
                               num_samples), dtype=np.complex64)

        # Preallocate arrays for results of range-lag selection
        out_main = np.zeros((num_sequences, num_beams, num_ranges, num_lags), 
                            dtype=np.complex64)
        out_intf = np.zeros((num_sequences, num_beams, num_ranges, num_lags), 
                            dtype=np.complex64)
        out_cross = np.zeros((num_sequences, num_beams, num_ranges, num_lags),
                             dtype=np.complex64)

        # Perform autocorrelations of each array, and cross correlation 
        # between arrays
        for seq in range(num_sequences):
            for beam in range(num_beams):
                main_samps = main_data[seq, beam]
                intf_samps = intf_data[seq, beam]

                main_corrs[seq, beam] = np.outer(main_samps.conjugate(), 
                                                 main_samps)
                intf_corrs[seq, beam] = np.outer(intf_samps.conjugate(), 
                                                 intf_samps)
                cross_corrs[seq, beam] = np.outer(main_samps.conjugate(), 
                                                  intf_samps)

                beam_offset = num_beams * num_ranges * num_lags
                first_range_offset = int(ts_dict["first_range"] / 
                                         ts_dict["range_sep"])

                # Select out the lags for each range gate
                main_small = np.zeros((num_ranges, num_lags,), 
                                      dtype=np.complex64)
                intf_small = np.zeros((num_ranges, num_lags,), 
                                      dtype=np.complex64)
                cross_small = np.zeros((num_ranges, num_lags,), 
                                       dtype=np.complex64)

                for rng in range(num_ranges):
                    for lag in range(num_lags):
                        # tau spacing in us, sample rate in hz
                        tau_in_samples = np.ceil(ts_dict["tau_spacing"] * 1e-6
                                                 * ts_dict["rx_sample_rate"])
                        p1_offset = lags[lag, 0] * tau_in_samples
                        p2_offset = lags[lag, 1] * tau_in_samples
                        
                        row_offset = int(rng + first_range_offset + p1_offset)
                        col_offset = int(rng + first_range_offset + p2_offset)

                        main_small[rng, lag] = \
                            main_corrs[seq, beam, row_offset, col_offset]
                        intf_small[rng, lag] = \
                            intf_corrs[seq, beam, row_offset, col_offset]
                        cross_small[rng, lag] = \
                            cross_corrs[seq, beam, row_offset, col_offset]

                # replace full correlation matrix with resized range-lag matrix
                out_main[seq, beam] = main_small
                out_intf[seq, beam] = intf_small
                out_cross[seq, beam] = cross_small

        # average each correlation matrix over sequences dimension
        out_main = np.mean(out_main, axis=0)
        out_intf = np.mean(out_intf, axis=0)
        out_cross = np.mean(out_cross, axis=0)

        # END def correlate_samples(ts_dict)
        return out_main, out_intf, out_cross

    
    def convert_bfiq_records_to_rawacf_records(bfiq: OrderedDict) -> \
            OrderedDict:
        """
        Take a data dictionary of bfiq records and return a data 
        dictionary of rawacf records.

        Parameters
        ----------
        bfiq
            Data OrderedDict of bfiq records.

        Returns
        -------
        correlations
            Data OrderedDict of rawacf records generated by bfiq.

        """
        correlations = OrderedDict()

        bfiq_rawacf_shared_fields = ['beam_azms', 'beam_nums', 
            'blanked_samples', 'lags', 'noise_at_freq', 'pulses', 
            'sqn_timestamps', 'borealis_git_hash', 'data_normalization_factor',
            'experiment_comment', 'experiment_id', 'experiment_name', 
            'first_range', 'first_range_rtt', 'freq', 'int_time', 
            'intf_antenna_count', 'main_antenna_count', 'num_sequences', 
            'num_slices', 'range_sep', 'rx_sample_rate', 'samples_data_type', 
            'scan_start_marker', 'slice_comment', 'station', 'tau_spacing', 
            'tx_pulse_len']

        for k in bfiq:
            correlations[k] = dict()
            # write common dictionary fields first
            for f in bfiq_rawacf_shared_fields:
                correlations[k][f] = bfiq[k][f]

            # Perform correlations and write to dictionary
            main_acfs, intf_acfs, xcfs = correlate_samples(bfiq[k])

            correlations[k]["correlation_dimensions"] = \
                np.array(main_acfs.shape, dtype=np.uint32)
            correlations[k]["correlation_descriptors"] = \
                np.array(['num_beams', 'num_ranges', 'num_lags'])

            correlations[k]["main_acfs"] = main_acfs.flatten()
            correlations[k]["intf_acfs"] = intf_acfs.flatten()
            correlations[k]["xcfs"] = xcfs.flatten()
            
            # Log information about how this file was generated
            now = dt.now()
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H:%M")
            correlations[k]["experiment_comment"] += "File generated on " + \
                date_str + " at " + time_str + " from " + bfiq_filepath + \
                " via pydarn bfiq_to_rawacf_postprocessing"

        return correlations

    # Suppress NaturalNameWarning when using timestamps as keys for records
    warnings.simplefilter('ignore', tables.NaturalNameWarning)

    # get the records from the bfiq file
    bfiq = read_borealis_file(bfiq_filepath, 'bfiq', site=site, records=True)

    rawacf = convert_bfiq_records_to_rawacf_records(bfiq)

    if write_site == True:
        write_borealis_file(rawacf, rawacf_filepath, 'rawacf', records=True)
    else:
        rawacf_arrays = borealis_site_to_array_dict(rawacf, 'rawacf')
        write_borealis_file(rawacf_arrays, rawacf_filepath, 'rawacf', 
                            records=False)
