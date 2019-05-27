# Copyright 2018 SuperDARN
# Authors: Marina Schmidt
"""
This file contains several class with the fields that pertain to
SuperDARN Borealis HDF5 files.

Classes:
--------
BorealisRawacf
BorealisFitacf
BorealisBfiq
BorealisOutputPtrsIq
BorealisRawrf

Notes:
------
Borealis stage iq data will not be included here (intermediate writes
can be done between rawrf and output_ptrs_iq processing)

"""

import numpy as np


class BorealisRawacf():
    """
    Class containing Borealis Rawacf fields
    """
    single_element_types = {
        "borealis_git_hash" : np.unicode_, # Identifies the version of Borealis that made this data.
        "timestamp_of_write" : np.float64, # Timestamp of when the record was written. Seconds since epoch.
        "experiment_id" : np.int64, # Number used to identify experiment.
        "experiment_name" : np.unicode_, # Name of the experiment file.
        "experiment_comment" : np.unicode_,  # Comment about the whole experiment
        "slice_comment" : np.unicode_, # Additional text comment that describes the slice.
        "num_slices" : np.int64, # Number of slices in the experiment at this integration time.
        "station" : np.unicode_, # Three letter radar identifier.
        "num_sequences": np.int64, # Number of sampling periods in the integration time.
        "range_sep": np.float32, # range gate separation (equivalent distance between samples)
        "first_range_rtt" : np.float32, # Round trip time of flight to first range in microseconds.
        "first_range" : np.float32, # Distance to first range in km.
        "rx_sample_rate" : np.float64, # Sampling rate of the samples being written to file in Hz.
        "scan_start_marker" : np.bool_, # Designates if the record is the first in a scan.
        "int_time" : np.float32, # Integration time in seconds.
        "tx_pulse_len" : np.uint32, # Length of the pulse in microseconds.
        "tau_spacing" : np.uint32, # The minimum spacing between pulses, spacing between pulses is always a
                          # multiple of this in microseconds.
        "main_antenna_count" : np.uint32, # Number of main array antennas.
        "intf_antenna_count" : np.uint32, # Number of interferometer array antennas.
        "freq" : np.uint32, # The frequency used for this experiment slice in kHz.
        "samples_data_type" : np.unicode_, # C data type of the samples such as complex float.
        "data_normalization_factor" : np.float64 # data normalization factor determined by the filter scaling in the decimation scheme.
    }

    array_dtypes = {
        "pulses" : np.uint32, # The pulse sequence in units of the tau_spacing.
        "lags" : np.uint32, # The lags created from combined pulses.
        "blanked_samples" : np.uint32, # Samples that have been blanked during TR switching.
        "sqn_timestamps" : np.float64, # A list of GPS timestamps of the beginning of transmission for each
                             # sampling period in the integration time. Seconds since epoch.
        "beam_nums" : np.uint32, # A list of beam numbers used in this slice.
        "beam_azms" : np.float64, # A list of the beams azimuths for each beam in degrees.
        "noise_at_freq" : np.float64, # Noise at the receive frequency, should be an array (one value per sequence) (TODO units??) (TODO document FFT resolution bandwidth for this value, should be = output_sample rate?)
        "correlation_descriptors" : np.unicode_, # Denotes what each acf/xcf dimension represents.
        "correlation_dimensions" : np.uint32, # The dimensions in which to reshape the acf/xcf data.
        "main_acfs" : np.complex64, # Main array autocorrelations
        "intf_acfs" : np.complex64, # Interferometer array autocorrelations
        "xcfs" : np.complex64 # Crosscorrelations between main and interferometer arrays
    }


class BorealisBfiq():
    """
    Class contain Borealis Bfiq fields
    """

    single_element_types = {
        "borealis_git_hash" : np.unicode_, # Identifies the version of Borealis that made this data.
        "timestamp_of_write" : np.float64, # Timestamp of when the record was written. Seconds since epoch.
        "experiment_id" : np.int64, # Number used to identify experiment.
        "experiment_name" : np.unicode_, # Name of the experiment file.
        "experiment_comment" : np.unicode_,  # Comment about the whole experiment
        "slice_comment" : np.unicode_, # Additional text comment that describes the slice.
        "num_slices" : np.int64, # Number of slices in the experiment at this integration time.
        "station" : np.unicode_, # Three letter radar identifier.
        "num_sequences": np.int64, # Number of sampling periods in the integration time.
        "rx_sample_rate" : np.float64, # Sampling rate of the samples being written to file in Hz.
        "scan_start_marker" : np.bool_, # Designates if the record is the first in a scan.
        "int_time" : np.float32, # Integration time in seconds.
        "tx_pulse_len" : np.uint32, # Length of the pulse in microseconds.
        "tau_spacing" : np.uint32, # The minimum spacing between pulses, spacing between pulses is always a
                          # multiple of this in microseconds.
        "main_antenna_count" : np.uint32, # Number of main array antennas.
        "intf_antenna_count" : np.uint32, # Number of interferometer array antennas.
        "freq" : np.uint32, # The frequency used for this experiment slice in kHz.
        "samples_data_type" : np.unicode_, # C data type of the samples such as complex float.
        "num_samps" : np.uint32, # Number of samples in the sampling period.
        "range_sep": np.float32, # range gate separation (equivalent distance between samples)
        "first_range_rtt" : np.float32, # Round trip time of flight to first range in microseconds.
        "first_range" : np.float32, # Distance to first range in km.
        "num_ranges" : np.uint32, # Number of ranges to calculate correlations for.
        "data_normalization_factor" : np.float64 # data normalization factor determined by the filter scaling in the decimation scheme.
    }

    array_dtypes = {
        "pulses" : np.uint32, # The pulse sequence in units of the tau_spacing.
        "lags" : np.uint32, # The lags created from combined pulses.
        "blanked_samples" : np.uint32, # Samples that have been blanked during TR switching.
        "pulse_phase_offset" : np.float32, # For pulse encoding phase, in desgrees offset. Contains one phase offset per pulse in pulses.
        "sqn_timestamps" : np.float64, # A list of GPS timestamps of the beginning of transmission for each
                             # sampling period in the integration time. Seconds since epoch.
        "beam_nums" : np.uint32, # A list of beam numbers used in this slice.
        "beam_azms" : np.float64, # A list of the beams azimuths for each beam in degrees.
        "noise_at_freq" : np.float64, # Noise at the receive frequency, should be an array (one value per sequence) (TODO units??) (TODO document FFT resolution bandwidth for this value, should be = output_sample rate?)
        "antenna_arrays_order" : np.unicode_, # States what order the data is in. Describes the data layout.
        "data_descriptors" : np.unicode_, # Denotes what each data dimension represents.
        "data_dimensions" : np.uint32, # The dimensions in which to reshape the data.
        "data" : np.complex64 # A contiguous set of samples (complex float) at given sample rate
    }


class BorealisOutputPtrsIq():
    """
    Class contain Borealis Bfiq fields
    """

    single_element_types = {
        "borealis_git_hash" : np.unicode_, # Identifies the version of Borealis that made this data.
        "timestamp_of_write" : np.float64, # Timestamp of when the record was written. Seconds since epoch.
        "experiment_id" : np.int64, # Number used to identify experiment.
        "experiment_name" : np.unicode_, # Name of the experiment file.
        "experiment_comment" : np.unicode_,  # Comment about the whole experiment
        "slice_comment" : np.unicode_, # Additional text comment that describes the slice.
        "num_slices" : np.int64, # Number of slices in the experiment at this integration time.
        "station" : np.unicode_, # Three letter radar identifier.
        "num_sequences": np.int64, # Number of sampling periods in the integration time.
        "rx_sample_rate" : np.float64, # Sampling rate of the samples being written to file in Hz.
        "scan_start_marker" : np.bool_, # Designates if the record is the first in a scan.
        "int_time" : np.float32, # Integration time in seconds.
        "tx_pulse_len" : np.uint32, # Length of the pulse in microseconds.
        "tau_spacing" : np.uint32, # The minimum spacing between pulses, spacing between pulses is always a
                          # multiple of this in microseconds.
        "main_antenna_count" : np.uint32, # Number of main array antennas.
        "intf_antenna_count" : np.uint32, # Number of interferometer array antennas.
        "freq" : np.uint32, # The frequency used for this experiment slice in kHz.
        "samples_data_type" : np.unicode_, # C data type of the samples such as complex float.
        "num_samps" : np.uint32, # Number of samples in the sampling period.
        "data_normalization_factor" : np.float64 # data normalization factor determined by the filter scaling in the decimation scheme.
    }

    array_dtypes = {
        "pulses" : np.uint32, # The pulse sequence in units of the tau_spacing.
        "pulse_phase_offset" : np.float32, # For pulse encoding phase, in desgrees offset. Contains one phase offset per pulse in pulses.
        "sqn_timestamps" : np.float64, # A list of GPS timestamps of the beginning of transmission for each
                             # sampling period in the integration time. Seconds since epoch.
        "beam_nums" : np.uint32, # A list of beam numbers used in this slice.
        "beam_azms" : np.float64, # A list of the beams azimuths for each beam in degrees.
        "noise_at_freq" : np.float64, # Noise at the receive frequency, should be an array (one value per sequence) (TODO units??) (TODO document FFT resolution bandwidth for this value, should be = output_sample rate?)
        "antenna_arrays_order" : np.unicode_, # States what order the data is in. Describes the data layout.
        "data_descriptors" : np.unicode_, # Denotes what each data dimension represents.
        "data_dimensions" : np.uint32, # The dimensions in which to reshape the data.
        "data" : np.complex64 # A contiguous set of samples (complex float) at given sample rate
    }


class BorealisRawrf():
    """
    Class contain Borealis Rawrf fields
    """

    single_element_types = {
        "borealis_git_hash" : np.unicode_, # Identifies the version of Borealis that made this data.
        "timestamp_of_write" : np.float64, # Timestamp of when the record was written. Seconds since epoch.
        "experiment_id" : np.int64, # Number used to identify experiment.
        "experiment_name" : np.unicode_, # Name of the experiment file.
        "experiment_comment" : np.unicode_,  # Comment about the whole experiment
        "num_slices" : np.int64, # Number of slices in the experiment at this integration time.
        "station" : np.unicode_, # Three letter radar identifier.
        "num_sequences": np.int64, # Number of sampling periods in the integration time.
        "rx_sample_rate" : np.float64, # Sampling rate of the samples being written to file in Hz.
        "scan_start_marker" : np.bool_, # Designates if the record is the first in a scan.
        "int_time" : np.float32, # Integration time in seconds.
        "main_antenna_count" : np.uint32, # Number of main array antennas.
        "intf_antenna_count" : np.uint32, # Number of interferometer array antennas.
        "samples_data_type" : np.unicode_, # C data type of the samples such as complex float.
        "rx_center_freq" : np.float64, # The center frequency of this data in kHz
        "num_samps" : np.uint32 # Number of samples in the sampling period.
    }

    array_dtypes = {
        "sqn_timestamps" : np.float64, # A list of GPS timestamps of the beginning of transmission for each
                             # sampling period in the integration time. Seconds since epoch.
        "data_descriptors" : np.unicode_, # Denotes what each data dimension represents.
        "data_dimensions" : np.uint32, # The dimensions in which to reshape the data.
        "data" : np.complex64 # A contiguous set of samples (complex float) at given sample rate
    }


class BorealisFitacf():
    """
    Class containing Borealis Fitacf fields
    Not yet implemented
    """
    # Standard fields
    types = {}
    # Fields added if the data is good and can be fitted
    fitted_fields = {}

