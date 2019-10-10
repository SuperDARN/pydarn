"""
Test data sets for Borealis Bfiq.
"""

import numpy as np

from collections import OrderedDict


borealis_site_bfiq_data = OrderedDict([(str(1558583991060), {
    "borealis_git_hash": np.str_('v0.2-61-gc13ab34'), 
    "experiment_id": np.int64(100000000),
    "experiment_name": np.str_('TestScheme9ACFs'), 
    "experiment_comment": np.str_(''), 
    "num_slices": np.int64(1), 
    "slice_comment": np.str_(''), 
    "station": np.str_('sas'),
    "num_sequences": np.int64(29), 
    "pulse_phase_offset": np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]).astype(np.float32),
    "range_sep": np.float32(44.96887), 
    "first_range_rtt": np.float32(1200.8307), 
    "first_range": np.float32(180.0), 
    "rx_sample_rate": np.float64(3333.3333333333335),
    "scan_start_marker": np.bool_(True), 
    "int_time": np.float32(3.000395), 
    "tx_pulse_len": np.uint32(300), 
    "tau_spacing": np.uint32(2400), 
    "main_antenna_count": np.uint32(16), 
    "intf_antenna_count": np.uint32(4), 
    "freq": np.uint32(10500), 
    "samples_data_type": np.str_('complex float'), 
    "num_samps": np.uint32(297),
    "num_ranges": np.uint32(75),
    "pulses": np.array([0, 9, 12, 20, 22, 26, 27]).astype(np.uint32), 
    "lags": np.array([[ 0,  0],
                    [26, 27],
                    [20, 22],
                    [9, 12],
                    [22, 26],
                    [22, 27],
                    [20, 26],
                    [20, 27],
                    [12, 20],
                    [0, 9],
                    [12, 22],
                    [9, 20],
                    [0, 12],
                    [9, 22],
                    [12, 26],
                    [12, 27],
                    [9, 26],
                    [9, 27],
                    [0, 20],
                    [0, 22],
                    [0, 26],
                    [0, 27],
                    [27, 27]]).astype(np.uint32),
    "blanked_samples": np.array([0, 72, 96, 160, 176, 208, 216]).astype(np.uint32), 
    "sqn_timestamps": np.array([1.55858399e+09, 1.55858399e+09,
    1.55858399e+09, 1.55858399e+09, 1.55858399e+09, 1.55858399e+09, 
    1.55858399e+09, 1.55858399e+09, 1.55858399e+09, 1.55858399e+09, 
    1.55858399e+09, 1.55858399e+09, 1.55858399e+09, 1.55858399e+09, 
    1.55858399e+09, 1.55858399e+09, 1.55858399e+09, 1.55858399e+09, 
    1.55858399e+09, 1.55858399e+09, 1.55858399e+09, 1.55858399e+09, 
    1.55858399e+09, 1.55858399e+09, 1.55858399e+09, 1.55858399e+09, 
    1.55858399e+09, 1.55858399e+09, 1.55858399e+09]), 
    "beam_nums": np.array([0]).astype(np.uint32), 
    "beam_azms": np.array([0.0]), 
    "data_descriptors": np.array(['num_antenna_arrays', 'num_sequences', 
                                'num_beams', 'num_samps']), 
    "data_dimensions": np.array([2, 29, 1, 297]).astype(np.uint32), 
    "antenna_arrays_order": np.array(['main', 'intf']),
    "noise_at_freq": np.array([0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 
                             0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 
                             0., 0., 0., 0., 0., 0., 0.]), 
    "data_normalization_factor": np.float64(9999999.999999996),
    "data": np.zeros(17226).astype(np.complex64)
    }), 
    (str(1558583994062), {
    "borealis_git_hash": np.str_('v0.2-61-gc13ab34'), 
    "experiment_id": np.int64(100000000),
    "experiment_name": np.str_('TestScheme9ACFs'), 
    "experiment_comment": np.str_(''), 
    "num_slices": np.int64(1), 
    "slice_comment": np.str_(''), 
    "station": np.str_('sas'),
    "num_sequences": np.int64(29), 
    "pulse_phase_offset": np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]).astype(np.float32),
    "range_sep": np.float32(44.96887), 
    "first_range_rtt": np.float32(1200.8307), 
    "first_range": np.float32(180.0), 
    "rx_sample_rate": np.float64(3333.3333333333335),
    "scan_start_marker": np.bool_(True), 
    "int_time": np.float32(3.090798), 
    "tx_pulse_len": np.uint32(300), 
    "tau_spacing": np.uint32(2400), 
    "main_antenna_count": np.uint32(16), 
    "intf_antenna_count": np.uint32(4), 
    "freq": np.uint32(10500), 
    "samples_data_type": np.str_('complex float'), 
    "num_samps": np.uint32(297),
    "num_ranges": np.uint32(75),
    "pulses": np.array([0, 9, 12, 20, 22, 26, 27]).astype(np.uint32), 
    "lags": np.array([[ 0,  0],
                    [26, 27],
                    [20, 22],
                    [9, 12],
                    [22, 26],
                    [22, 27],
                    [20, 26],
                    [20, 27],
                    [12, 20],
                    [0, 9],
                    [12, 22],
                    [9, 20],
                    [0, 12],
                    [9, 22],
                    [12, 26],
                    [12, 27],
                    [9, 26],
                    [9, 27],
                    [0, 20],
                    [0, 22],
                    [0, 26],
                    [0, 27],
                    [27, 27]]).astype(np.uint32),
    "blanked_samples": np.array([0, 72, 96, 160, 176, 208, 216]).astype(np.uint32), 
    "sqn_timestamps": np.array([1.55858399e+09, 1.55858399e+09,
    1.55858399e+09, 1.55858399e+09, 1.55858399e+09, 1.55858399e+09, 
    1.55858399e+09, 1.55858399e+09, 1.55858399e+09, 1.55858399e+09, 
    1.55858399e+09, 1.55858399e+09, 1.55858399e+09, 1.55858399e+09, 
    1.55858399e+09, 1.55858399e+09, 1.55858399e+09, 1.55858399e+09, 
    1.55858399e+09, 1.55858399e+09, 1.55858399e+09, 1.55858399e+09, 
    1.55858399e+09, 1.55858399e+09, 1.55858399e+09, 1.55858399e+09, 
    1.55858399e+09, 1.55858399e+09, 1.55858399e+09]), 
    "beam_nums": np.array([0]).astype(np.uint32), 
    "beam_azms": np.array([0.0]), 
    "data_descriptors": np.array(['num_antenna_arrays', 'num_sequences', 
                                'num_beams', 'num_samps']), 
    "data_dimensions": np.array([2, 29, 1, 297]).astype(np.uint32), 
    "antenna_arrays_order": np.array(['main', 'intf']),
    "noise_at_freq": np.array([0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 
                             0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 
                             0., 0., 0., 0., 0., 0., 0.]), 
    "data_normalization_factor": np.float64(9999999.999999996),
    "data": np.zeros((17226)).astype(np.complex64)
    })])

num_records = 1500
borealis_array_bfiq_data = {
    "borealis_git_hash": np.str_('v0.2-61-gc13ab34'), 
    "experiment_id": np.int64(100000000),
    "experiment_name": np.str_('TestScheme9ACFs'), 
    "experiment_comment": np.str_(''), 
    "num_slices": np.array([1] * num_records, dtype=np.int64), 
    "slice_comment": np.str_(''), 
    "station": np.str_('sas'),
    "pulse_phase_offset": np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]).astype(np.float32),
    "range_sep": np.float32(44.96887), 
    "first_range_rtt": np.float32(1200.8307), 
    "first_range": np.float32(180.0), 
    "rx_sample_rate": np.float64(3333.3333333333335),
    "scan_start_marker": np.array([True] * num_records).astype(np.bool_), 
    "tx_pulse_len": np.uint32(300), 
    "tau_spacing": np.uint32(2400), 
    "main_antenna_count": np.uint32(16), 
    "intf_antenna_count": np.uint32(4), 
    "freq": np.uint32(10500), 
    "samples_data_type": np.str_('complex float'), 
    "num_samps": np.uint32(297),
    "num_ranges": np.uint32(75),
    "num_beams": np.array([1] * num_records).astype(np.uint32),
    "pulses": np.array([0, 9, 12, 20, 22, 26, 27]).astype(np.uint32), 
    "lags": np.array([[ 0,  0],
                    [26, 27],
                    [20, 22],
                    [9, 12],
                    [22, 26],
                    [22, 27],
                    [20, 26],
                    [20, 27],
                    [12, 20],
                    [0, 9],
                    [12, 22],
                    [9, 20],
                    [0, 12],
                    [9, 22],
                    [12, 26],
                    [12, 27],
                    [9, 26],
                    [9, 27],
                    [0, 20],
                    [0, 22],
                    [0, 26],
                    [0, 27],
                    [27, 27]]).astype(np.uint32),
    "blanked_samples": np.array([0, 72, 96, 160, 176, 208, 216]).astype(np.uint32), 
    "beam_nums": np.array([[0]] * num_records).astype(np.uint32), 
    "beam_azms": np.array([[0.0]] * num_records), 
    "data_descriptors": np.array(['num_records', 'num_antenna_arrays', 'num_sequences', 
                                'num_beams', 'num_samps']), 
    "data_normalization_factor": np.float64(9999999.999999996),
    "antenna_arrays_order": np.array(['main', 'intf']),
    "int_time": np.array([3.000395] * num_records).astype(np.float32), 
    "num_sequences": np.array([np.int64(29)] * num_records, dtype=np.int64), 
    "sqn_timestamps": np.array([[1.55858399e+09, 1.55858399e+09,
    1.55858399e+09, 1.55858399e+09, 1.55858399e+09, 1.55858399e+09, 
    1.55858399e+09, 1.55858399e+09, 1.55858399e+09, 1.55858399e+09, 
    1.55858399e+09, 1.55858399e+09, 1.55858399e+09, 1.55858399e+09, 
    1.55858399e+09, 1.55858399e+09, 1.55858399e+09, 1.55858399e+09, 
    1.55858399e+09, 1.55858399e+09, 1.55858399e+09, 1.55858399e+09, 
    1.55858399e+09, 1.55858399e+09, 1.55858399e+09, 1.55858399e+09, 
    1.55858399e+09, 1.55858399e+09, 1.55858399e+09]] * num_records), 
    "noise_at_freq": np.array([[0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 
                             0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 
                             0., 0., 0., 0., 0., 0., 0.]] * num_records), 
    "data": np.zeros((num_records, 2, 29, 1, 297)).astype(np.complex64)
    }
