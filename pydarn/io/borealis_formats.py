# Copyright 2018 SuperDARN
# Authors: Marina Schmidt
"""
This file contains several class with the fields that pertain to
SuperDARN Borealis HDF5 files. For more information on Borealis 
data files, see https://borealis.readthedocs.io/en/latest/ 

Classes:
--------
BorealisRawacf
BorealisBfiq
BorealisOutputPtrsIq
BorealisRawrf

Notes:
------
Debug data files such as Borealis stage iq data (an intermediate
product that can be generated during filtering and decimating, showing
progression from rawrf to output ptrs iq files) will not be included here 

"""

import numpy as np


class BorealisRawacf():
    """
    Class containing Borealis Rawacf fields
    """
    single_element_types = {
        # Identifies the version of Borealis that made this data.
        "borealis_git_hash": np.unicode_,
        # Timestamp of when the record was written. Seconds since epoch.
        "timestamp_of_write": np.float64,
        # Number used to identify experiment.
        "experiment_id": np.int64,  
        # Name of the experiment file.
        "experiment_name": np.unicode_,
        # Comment about the whole experiment  
        "experiment_comment": np.unicode_,  
        # Additional text comment that describes the slice.
        "slice_comment": np.unicode_,
        # Number of slices in the experiment at this integration time.
        "num_slices": np.int64,
        # Three letter radar identifier.
        "station": np.unicode_,  
        # Number of sampling periods in the integration time.
        "num_sequences": np.int64,
        # range gate separation (equivalent distance between samples), km.
        "range_sep": np.float32,
        # Round trip time of flight to first range in microseconds.
        "first_range_rtt": np.float32,
        # Distance to first range in km.
        "first_range": np.float32,  
        # Sampling rate of the samples being written to file in Hz.
        "rx_sample_rate": np.float64,
        # Designates if the record is the first in a scan.
        "scan_start_marker": np.bool_,
        # Integration time in seconds.
        "int_time": np.float32,  
        # Length of the pulse in microseconds.
        "tx_pulse_len": np.uint32,  
        # The minimum spacing between pulses, spacing between pulses is always a
        # multiple of this in microseconds.
        "tau_spacing": np.uint32,
        # Number of main array antennas.
        "main_antenna_count": np.uint32,  
        # Number of interferometer array antennas.
        "intf_antenna_count": np.uint32,
        # The frequency used for this experiment slice in kHz.
        "freq": np.uint32,
        # str denoting C data type of the samples included in the data array, such 
        # as 'complex float'.
        "samples_data_type": np.unicode_,
        # data normalization factor determined by the filter scaling in the decimation scheme.
        "data_normalization_factor": np.float64
    }

    array_dtypes = {
        # The pulse sequence in units of the tau_spacing.
        "pulses": np.uint32, 
        # The lags created from combined pulses.
        "lags": np.uint32,  
        # Samples that have been blanked during TR switching.
        "blanked_samples": np.uint32,
        # A list of GPS timestamps of the beginning of transmission for each
        # sampling period in the integration time. Seconds since epoch.
        "sqn_timestamps": np.float64,
        # A list of beam numbers used in this slice.
        "beam_nums": np.uint32,  
        # A list of the beams azimuths for each beam in degrees.
        "beam_azms": np.float64,
        # Noise at the receive frequency, should be an array 
        # (one value per sequence) (TODO units??) (TODO document 
        # FFT resolution bandwidth for this value, should be = output_sample rate?)
        "noise_at_freq": np.float64,
        # Denotes what each acf/xcf dimension represents.
        "correlation_descriptors": np.unicode_,
        # The dimensions in which to reshape the acf/xcf data.
        "correlation_dimensions": np.uint32,
        # Main array autocorrelations
        "main_acfs": np.complex64,  
        # Interferometer array autocorrelations
        "intf_acfs": np.complex64,  
        # Crosscorrelations between main and interferometer arrays
        "xcfs": np.complex64 
    }


class BorealisBfiq():
    """
    Class contain Borealis Bfiq fields
    """

    single_element_types = {
        # Identifies the version of Borealis that made this data.
        "borealis_git_hash": np.unicode_,
        # Timestamp of when the record was written. Seconds since epoch.
        "timestamp_of_write": np.float64,
        # Number used to identify experiment.
        "experiment_id": np.int64,  
        # Name of the experiment file.
        "experiment_name": np.unicode_,  
        # Comment about the whole experiment
        "experiment_comment": np.unicode_,  
        # Additional text comment that describes the slice.
        "slice_comment": np.unicode_,
        # Number of slices in the experiment at this integration time.
        "num_slices": np.int64,
        # Three letter radar identifier.
        "station": np.unicode_,  
        # Number of sampling periods in the integration time.
        "num_sequences": np.int64,
        # Sampling rate of the samples being written to file in Hz.
        "rx_sample_rate": np.float64,
        # Designates if the record is the first in a scan.
        "scan_start_marker": np.bool_,
        # Integration time in seconds.
        "int_time": np.float32,  
        # Length of the pulse in microseconds.
        "tx_pulse_len": np.uint32,  
        # The minimum spacing between pulses, spacing between pulses is always a
        # multiple of this. In microseconds.
        "tau_spacing": np.uint32,
        # Number of main array antennas.
        "main_antenna_count": np.uint32,  
        # Number of interferometer array antennas.
        "intf_antenna_count": np.uint32,
        # The frequency used for this experiment slice in kHz.
        "freq": np.uint32,
        # str denoting C data type of the samples included in the data array, such 
        # as 'complex float'.
        "samples_data_type": np.unicode_,
        # Number of samples in the sampling period.
        "num_samps": np.uint32,  
        # range gate separation (equivalent distance between samples), km
        "range_sep": np.float32,
        # Round trip time of flight to first range in microseconds.
        "first_range_rtt": np.float32,
        # Distance to first range in km.
        "first_range": np.float32,  
        # Number of ranges to calculate correlations for.
        "num_ranges": np.uint32,
        # data normalization factor determined by the filter scaling in the decimation scheme.
        "data_normalization_factor": np.float64
    }

    array_dtypes = {
        # The pulse sequence in units of the tau_spacing.
        "pulses": np.uint32,  
        # The lags created from combined pulses.
        "lags": np.uint32,  
        # Samples that have been blanked during TR switching.
        "blanked_samples": np.uint32,
        # For pulse encoding phase, in degrees offset. Contains one phase offset 
        # per pulse in pulses.
        "pulse_phase_offset": np.float32,
        # A list of GPS timestamps of the beginning of transmission for each
        # sampling period in the integration time. Seconds since epoch.
        "sqn_timestamps": np.float64,
        # A list of beam numbers used in this slice.
        "beam_nums": np.uint32,  
        # A list of the beams azimuths for each beam in degrees.
        "beam_azms": np.float64,
        # Noise at the receive frequency, should be an array (one value per 
        # sequence) (TODO units??) (TODO document FFT resolution bandwidth for 
        # this value, should be = output_sample rate?)
        "noise_at_freq": np.float64,
        # States what order the data is in. Describes the data layout.
        "antenna_arrays_order": np.unicode_,
        # Denotes what each data dimension represents.
        "data_descriptors": np.unicode_,
        # The dimensions in which to reshape the data.
        "data_dimensions": np.uint32,
        # A contiguous set of samples (complex float) at given sample rate
        "data": np.complex64
    }


class BorealisOutputPtrsIq():
    """
    Class contain Borealis Bfiq fields
    """

    single_element_types = {
        # Identifies the version of Borealis that made this data.
        "borealis_git_hash": np.unicode_,
        # Timestamp of when the record was written. Seconds since epoch.
        "timestamp_of_write": np.float64,
        # Number used to identify experiment.
        "experiment_id": np.int64,  
        # Name of the experiment file.
        "experiment_name": np.unicode_,  
        # Comment about the whole experiment
        "experiment_comment": np.unicode_,  
        # Additional text comment that describes the slice.
        "slice_comment": np.unicode_,
        # Number of slices in the experiment at this integration time.
        "num_slices": np.int64,
        # Three letter radar identifier.
        "station": np.unicode_, 
        # Number of sampling periods in the integration time.
        "num_sequences": np.int64,
        # Sampling rate of the samples being written to file in Hz.
        "rx_sample_rate": np.float64,
        # Designates if the record is the first in a scan.
        "scan_start_marker": np.bool_,
        # Integration time in seconds.
        "int_time": np.float32,  
        # Length of the pulse in microseconds.
        "tx_pulse_len": np.uint32,  
        # The minimum spacing between pulses, spacing between pulses is always a
        # multiple of this in microseconds.
        "tau_spacing": np.uint32,
        # Number of main array antennas.
        "main_antenna_count": np.uint32, 
        # Number of interferometer array antennas.
        "intf_antenna_count": np.uint32,
        # The frequency used for this experiment slice in kHz.
        "freq": np.uint32,
        # str denoting C data type of the samples included in the data array, such 
        # as 'complex float'.
        "samples_data_type": np.unicode_,
        # Number of samples in the sampling period.
        "num_samps": np.uint32,  
        # data normalization factor determined by the filter scaling in the decimation scheme.
        "data_normalization_factor": np.float64
    }

    array_dtypes = {
        # The pulse sequence in units of the tau_spacing.
        "pulses": np.uint32,  
        # For pulse encoding phase, in desgrees offset. Contains one phase 
        # offset per pulse in pulses.
        "pulse_phase_offset": np.float32,
        # A list of GPS timestamps of the beginning of transmission for each
        # sampling period in the integration time. Seconds since epoch.
        "sqn_timestamps": np.float64,
        # A list of beam numbers used in this slice.
        "beam_nums": np.uint32,  
        # A list of the beams azimuths for each beam in degrees.
        "beam_azms": np.float64,
        # Noise at the receive frequency, should be an array (one value 
        # per sequence) (TODO units??) (TODO document FFT resolution bandwidth 
        # for this value, should be = output_sample rate?)
        "noise_at_freq": np.float64,
        # States what order the data is in. Describes the data layout.
        "antenna_arrays_order": np.unicode_,
        # Denotes what each data dimension represents.
        "data_descriptors": np.unicode_,
        # The dimensions in which to reshape the data.
        "data_dimensions": np.uint32,
        # A contiguous set of samples (complex float) at given sample rate
        "data": np.complex64
    }


class BorealisRawrf():
    """
    Class contain Borealis Rawrf fields
    """

    single_element_types = {
        # Identifies the version of Borealis that made this data.
        "borealis_git_hash": np.unicode_,
        # Timestamp of when the record was written. Seconds since epoch.
        "timestamp_of_write": np.float64,
        # Number used to identify experiment.
        "experiment_id": np.int64,  
        # Name of the experiment file.
        "experiment_name": np.unicode_,  
        # Comment about the whole experiment
        "experiment_comment": np.unicode_,  
        # Number of slices in the experiment at this integration time.
        "num_slices": np.int64,
        # Three letter radar identifier.
        "station": np.unicode_,  
        # Number of sampling periods in the integration time.
        "num_sequences": np.int64,
        # Sampling rate of the samples being written to file in Hz.
        "rx_sample_rate": np.float64,
        # Designates if the record is the first in a scan.
        "scan_start_marker": np.bool_,
        # Integration time in seconds.
        "int_time": np.float32,  
        # Number of main array antennas.
        "main_antenna_count": np.uint32,  
        # Number of interferometer array antennas.
        "intf_antenna_count": np.uint32,
        # str denoting C data type of the samples included in the data array, such 
        # as 'complex float'.
        "samples_data_type": np.unicode_,
        # The center frequency of this data in kHz
        "rx_center_freq": np.float64,  
        # Number of samples in the sampling period.
        "num_samps": np.uint32  
    }

    array_dtypes = {
        # A list of GPS timestamps of the beginning of transmission for each
        # sampling period in the integration time. Seconds since epoch.
        "sqn_timestamps": np.float64,
        # Denotes what each data dimension represents.
        "data_descriptors": np.unicode_,
        # The dimensions in which to reshape the data.
        "data_dimensions": np.uint32,
        # A contiguous set of samples (complex float) at given sample rate
        "data": np.complex64
    }
