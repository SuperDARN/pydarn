# Copyright 2019 SuperDARN Canada, University of Saskatchewan
# Author: Marci Detwiller
"""
This file contains several classes with the fields that pertain to
SuperDARN Borealis HDF5 files. 

Classes
-------
BorealisRawacf
BorealisBfiq
BorealisAntennasIq
BorealisRawrf

Notes
-----
Debug data files such as Borealis stage iq data (an intermediate
product that can be generated during filtering and decimating, showing
progression from rawrf to output ptrs iq files) will not be included here.
This is a debug format only and should not be used for higher level 
data products.

See Also
--------
For more information on Borealis data files, see:
https://borealis.readthedocs.io/en/latest/ 
"""

import numpy as np


class BorealisRawacf():
    """
    Class containing Borealis Rawacf data fields and their types.

    Rawacf data has been mixed, filtered, and decimated; beamformed and 
    combined into antenna arrays; then autocorrelated and correlated between
    antenna arrays to produce matrices of num_ranges x num_lags. 

    Attributes
    ----------
    single_element_types: dict
        Dictionary of data field name to type expected in that field for a 
        dictionary of Borealis data.
    array_dtypes: dict
        Dictionary of data field name to array of given numpy dtype expected  
        in the field for a dictionary of Borealis data.
    shared_fields: list
        List of the fields that are restructured to a single value per
        file in the Borealis array type files. 
    unshared_fields: list
        List of the fields that are restructured to be an array with first
        dimension equal to the number of records in the file. 

    Notes
    -----
    single_element_types.keys() + array_dtypes.keys() = all known fields
    as well as 
    shared_fields + unshared_fields = all known fields
    in the Borealis Rawacf files.
    """

    single_element_types = {
        # Identifies the version of Borealis that made this data.
        "borealis_git_hash": np.unicode_,
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
        # The minimum spacing between pulses, spacing between pulses is always
        # a multiple of this in microseconds.
        "tau_spacing": np.uint32,
        # Number of main array antennas.
        "main_antenna_count": np.uint32,  
        # Number of interferometer array antennas.
        "intf_antenna_count": np.uint32,
        # The frequency used for this experiment slice in kHz.
        "freq": np.uint32,
        # str denoting C data type of the samples included in the data array, 
        # such as 'complex float'.
        "samples_data_type": np.unicode_,
        # data normalization factor determined by the filter scaling in the 
        # decimation scheme.
        "data_normalization_factor": np.float64
    }

    array_dtypes = {
        # The pulse sequence in multiples of the tau_spacing.
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
        # FFT resolution bandwidth for this value, should be = output_sample 
        # rate?)
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

    shared_fields = ['beam_azms', 'beam_nums', 'blanked_samples', 
                     'borealis_git_hash', 'correlation_descriptors',
                     'data_normalization_factor', 'experiment_comment', 
                     'experiment_id', 'experiment_name', 'first_range', 
                     'first_range_rtt', 'freq', 'intf_antenna_count', 'lags', 
                     'main_antenna_count', 'num_slices', 'pulses', 'range_sep',
                     'rx_sample_rate', 'samples_data_type', 
                     'scan_start_marker', 'slice_comment', 'station', 
                     'tau_spacing', 'tx_pulse_len', 'correlation_dimensions']

    unshared_fields = ['num_sequences', 'int_time', 'sqn_timestamps',
                       'noise_at_freq', 'main_acfs', 'intf_acfs', 'xcfs']


class BorealisBfiq():
    """
    Class containing Borealis Bfiq data fields and their types.

    Bfiq data is beamformed i and q data. It has been mixed, filtered, 
    decimated to the final output receive rate, and it has been beamformed
    and all channels have been combined into their arrays. No correlation
    or averaging has occurred.

    Attributes
    ----------
    single_element_types: dict
        Dictionary of data field name to type expected in that field for a 
        dictionary of Borealis data.
    array_dtypes: dict
        Dictionary of data field name to array of given numpy dtype expected  
        in the field for a dictionary of Borealis data.
    shared_fields: list
        List of the fields that are restructured to a single value per
        file in the Borealis array type files. 
    unshared_fields: list
        List of the fields that are restructured to be an array with first
        dimension equal to the number of records in the file. 
    
    Notes
    -----
    single_element_types.keys() + array_dtypes.keys() = all known fields
    as well as 
    shared_fields + unshared_fields = all known fields
    in the Borealis Bfiq files.
    """

    single_element_types = {
        # Identifies the version of Borealis that made this data.
        "borealis_git_hash": np.unicode_,
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
        # The minimum spacing between pulses, spacing between pulses is always 
        # a multiple of this. In microseconds.
        "tau_spacing": np.uint32,
        # Number of main array antennas.
        "main_antenna_count": np.uint32,  
        # Number of interferometer array antennas.
        "intf_antenna_count": np.uint32,
        # The frequency used for this experiment slice in kHz.
        "freq": np.uint32,
        # str denoting C data type of the samples included in the data array, 
        # such as 'complex float'.
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
        # data normalization factor determined by the filter scaling in the 
        # decimation scheme.
        "data_normalization_factor": np.float64
    }

    array_dtypes = {
        # The pulse sequence in multiples of the tau_spacing.
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

    shared_fields =  ['antenna_arrays_order', 'beam_azms', 'beam_nums',
                      'blanked_samples', 'borealis_git_hash', 
                      'data_descriptors', 'data_normalization_factor', 
                      'experiment_comment', 'experiment_id', 'experiment_name',
                      'first_range', 'first_range_rtt', 'freq', 
                      'intf_antenna_count', 'lags', 'main_antenna_count', 
                      'num_ranges', 'num_samps', 'num_slices', 
                      'pulse_phase_offset', 'pulses', 'range_sep', 
                      'rx_sample_rate', 'samples_data_type', 
                      'scan_start_marker', 'slice_comment', 'station', 
                      'tau_spacing', 'tx_pulse_len']

    unshared_fields = ['num_sequences', 'int_time', 'sqn_timestamps',
                       'noise_at_freq', 'data_dimensions', 'data']


class BorealisAntennasIq():
    """
    Class containing Borealis Antennas iq data fields and their types.

    Antennas iq data is data with all channels separated. It has been mixed
    and filtered, but it has not been beamformed or combined into the 
    entire antenna array data product. 

    Attributes
    ----------
    single_element_types: dict
        Dictionary of data field name to type expected in that field for a 
        dictionary of Borealis data.
    array_dtypes: dict
        Dictionary of data field name to array of given numpy dtype expected  
        in the field for a dictionary of Borealis data.
    shared_fields: list
        List of the fields that are restructured to a single value per
        file in the Borealis array type files. 
    unshared_fields: list
        List of the fields that are restructured to be an array with first
        dimension equal to the number of records in the file. 
    
    Notes
    -----
    single_element_types.keys() + array_dtypes.keys() = all known fields
    as well as 
    shared_fields + unshared_fields = all known fields
    in the Borealis Antennas_iq files.
    """

    single_element_types = {
        # Identifies the version of Borealis that made this data.
        "borealis_git_hash": np.unicode_,
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
        # The minimum spacing between pulses, spacing between pulses is always 
        # a multiple of this in microseconds.
        "tau_spacing": np.uint32,
        # Number of main array antennas.
        "main_antenna_count": np.uint32, 
        # Number of interferometer array antennas.
        "intf_antenna_count": np.uint32,
        # The frequency used for this experiment slice in kHz.
        "freq": np.uint32,
        # str denoting C data type of the samples included in the data array, 
        # such as 'complex float'.
        "samples_data_type": np.unicode_,
        # Number of samples in the sampling period.
        "num_samps": np.uint32,  
        # data normalization factor determined by the filter scaling in the 
        # decimation scheme.
        "data_normalization_factor": np.float64
    }

    array_dtypes = {
        # The pulse sequence in multiples of the tau_spacing.
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

    shared_fields = ['antenna_arrays_order', 'beam_azms', 'beam_nums', 
                     'borealis_git_hash', 'data_descriptors',
                     'data_normalization_factor', 'experiment_comment', 
                     'experiment_id', 'experiment_name', 'freq', 
                     'intf_antenna_count', 'main_antenna_count', 'num_samps',
                     'num_slices', 'pulse_phase_offset', 'pulses', 
                     'rx_sample_rate', 'samples_data_type', 
                     'scan_start_marker', 'slice_comment', 'station', 
                     'tau_spacing', 'tx_pulse_len']

    unshared_fields = ['num_sequences', 'int_time', 'sqn_timestamps',
                       'noise_at_freq', 'data_dimensions', 'data']


class BorealisRawrf():
    """
    Class containing Borealis Rawrf data fields and their types.

    Rawrf data is data that has been produced at the original receive bandwidth
    and has not been mixed, filtered, or decimated. 

    Attributes
    ----------
    single_element_types: dict
        Dictionary of data field name to type expected in that field for a 
        dictionary of Borealis data.
    array_dtypes: dict
        Dictionary of data field name to array of given numpy dtype expected  
        in the field for a dictionary of Borealis data.
    """

    single_element_types = {
        # Identifies the version of Borealis that made this data.
        "borealis_git_hash": np.unicode_,
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
        # str denoting C data type of the samples included in the data array, 
        # such as 'complex float'.
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
