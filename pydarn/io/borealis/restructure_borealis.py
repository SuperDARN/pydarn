# Copyright 2019 SuperDARN Canada, University of Saskatchewan
# Author: Liam Graham

#
# restructure_borealis.py
# 2019-08-08

import deepdish as dd
import numpy as np
import sys
import os
import subprocess as sp
import datetime
import warnings
import tempfile
from pathlib2 import Path


########################## RESTRUCTURING CODE #################################
# Functions for restructuring Borealis files
# for bfiq, antennas iq, and raw acf data into a smaller,
# faster, and more usable format

shared_antiq = ['antenna_arrays_order', 'beam_azms', 'beam_nums', 'borealis_git_hash', 'data_descriptors',
				'data_normalization_factor', 'experiment_comment', 'experiment_id', 'experiment_name',
				'freq', 'intf_antenna_count', 'main_antenna_count', 'num_samps', 'num_slices',
				'pulse_phase_offset', 'pulses', 'rx_sample_rate', 'samples_data_type', 'scan_start_marker',
				'slice_comment', 'station', 'tau_spacing', 'tx_pulse_len']

shared_bfiq =  ['antenna_arrays_order', 'beam_azms', 'beam_nums', 'blanked_samples', 'borealis_git_hash', 
				'data_descriptors', 'data_normalization_factor', 'experiment_comment', 'experiment_id',
				'experiment_name', 'first_range', 'first_range_rtt', 'freq', 'intf_antenna_count', 'lags',
				'main_antenna_count', 'num_ranges', 'num_samps', 'num_slices', 'pulse_phase_offset', 'pulses',
				'range_sep', 'rx_sample_rate', 'samples_data_type', 'scan_start_marker', 'slice_comment',
				'station', 'tau_spacing', 'tx_pulse_len']

shared_rawacf = ['beam_azms', 'beam_nums', 'blanked_samples', 'borealis_git_hash', 'correlation_descriptors',
				 'data_normalization_factor', 'experiment_comment', 'experiment_id', 'experiment_name',
				 'first_range', 'first_range_rtt', 'freq', 'intf_antenna_count', 'lags', 'main_antenna_count',
				 'num_slices', 'pulses', 'range_sep', 'rx_sample_rate', 'samples_data_type', 'scan_start_marker',
				 'slice_comment', 'station', 'tau_spacing', 'tx_pulse_len', 'correlation_dimensions']

def find_max_sequences(data):
	"""
	Finds the maximum number of sequences between records in a Borealis data file
	Args
		data:		Site formatted data from a Borealis file, 
					organized as one record for each slice
	Returns:
		max_seqs:	The largest number of sequences found 
					in one record from the file
	"""
	max_seqs = 0
	for k in data:
		if max_seqs < data[k]["num_sequences"]:
			max_seqs = data[k]["num_sequences"]
	return max_seqs


def iq_site_to_array(data_record):
	"""
	Restructuring method for pre bfiq data
	args:
		data_record		a timestamped record loaded from an hdf5
						Borealis antenna iq or bfiq data file
		 Returns:
		 	data_dict:	A dictionary containing the data from data_record
		 				reformatted to be stored entirely as arrays, or as
		 				one entry if the field does not change between records
	"""
	data_dict = dict()
	num_records = len(data_record)

	# write shared fields to dictionary
	first_key = list(data_record.keys())[0]


	# find maximum number of sequences
	max_seqs = find_max_sequences(data_record)
	dims = data_record[first_key]["data_dimensions"]

	first_dim = data_record[first_key]["data_descriptors"][0]
	if first_dim == 'num_antennas':  # antenna iq file
		for field in shared_antiq:
			data_dict[field] = data_record[first_key][field]

		num_antennas = dims[0]
		num_samps = dims[2]

		data_buffer_offset = num_antennas * num_samps * max_seqs
		data_buffer = np.zeros(num_records * data_buffer_offset, dtype=np.complex64)
		data_shape = (num_records, num_antennas, max_seqs, num_samps)

	elif first_dim == 'num_antenna_arrays':  # bfiq file
		for field in shared_bfiq:
			data_dict[field] = data_record[first_key][field]
		num_arrays = dims[0]
		num_beams = dims[2]
		num_samps = dims[3]

		data_buffer_offset = num_arrays * num_beams * num_samps * max_seqs
		data_buffer = np.zeros(num_records * data_buffer_offset, dtype=np.complex64)
		data_shape = (num_records, num_arrays, max_seqs, num_beams, num_samps)

	else:  # Unrecognized
		raise Exception("Unrecognized filetype based on descriptor check")

	sqn_buffer_offset = max_seqs
	sqn_ts_buffer = np.zeros(num_records * max_seqs)
	sqn_shape = (num_records, max_seqs)

	noise_buffer_offset = max_seqs
	noise_buffer = np.zeros(num_records * max_seqs)
	noise_shape = (num_records, max_seqs)

	sqn_num_array = np.empty(num_records)
	int_time_array = np.empty(num_records)

	data_dims_array = np.empty((num_records, len(data_record[first_key]["data_descriptors"])))

	rec_idx = 0
	for k in data_record:
		# handle unshared fields
		int_time_array[rec_idx] = data_record[k]["int_time"]
		sqn_num_array[rec_idx] = data_record[k]["num_sequences"]
		data_dims_array[rec_idx] = data_record[k]["data_dimensions"]

		# insert data into buffer
		record_buffer = data_record[k]["data"]
		data_pos = rec_idx * data_buffer_offset
		data_end = data_pos + len(record_buffer)
		data_buffer[data_pos:data_end] = record_buffer

		# insert sequence timestamps into buffer
		rec_sqn_ts = data_record[k]["sqn_timestamps"]
		sqn_pos = rec_idx * sqn_buffer_offset
		sqn_end = sqn_pos + data_record[k]["num_sequences"]
		sqn_ts_buffer[sqn_pos:sqn_end] = rec_sqn_ts

		rec_noise = data_record[k]["noise_at_freq"]
		noise_pos = rec_idx * noise_buffer_offset
		noise_end = noise_pos + data_record[k]["num_sequences"]
		noise_buffer[noise_pos:noise_end] = rec_noise

		rec_idx += 1

	# write leftover metadata and data
	data_dict["int_time"] = int_time_array
	data_dict["num_sequences"] = sqn_num_array

	data_dict["data"] = data_buffer.reshape(data_shape)
	data_dict["sqn_timestamps"] = sqn_ts_buffer.reshape(sqn_shape)
	data_dict["noise_at_freq"] = noise_buffer.reshape(noise_shape)

	data_dict["data_descriptors"] = np.insert(data_dict["data_descriptors"], 0, "num_records")
	data_dict["data_dimensions"] = data_dims_array

	return data_dict


def rawacf_site_to_array(data_record):
	"""
	Restructuring method for rawacf data
	Args:
		data_record		a timestamped record loaded from an
		 				hdf5 Borealis rawacf data file
	Returns:
		 	data_dict:	A dictionary containing the data from data_record
		 				reformatted to be stored entirely as arrays, or as
		 				one entry if the field does not change between records
	"""
	data_dict = dict()
	num_records = len(data_record)
	max_seqs = find_max_sequences(data_record)

	# write shared fields to dictionary
	first_key = list(data_record.keys())[0]
	for field in shared_rawacf:
		data_dict[field] = data_record[first_key][field]

	# handle unshared data fields
	dims = data_dict["correlation_dimensions"]
	num_beams = dims[0]
	num_ranges = dims[1]
	num_lags = dims[2]
	data_shape = (num_records, num_beams, num_ranges, num_lags)

	noise_buffer_offset = max_seqs
	noise_buffer = np.zeros(num_records * max_seqs)
	noise_shape = (num_records, max_seqs)

	sqn_ts_array = np.empty((num_records, max_seqs))
	sqn_num_array = np.empty(num_records)
	main_array = np.empty(data_shape, dtype=np.complex64)
	intf_array = np.empty(data_shape, dtype=np.complex64)
	xcfs_array = np.empty(data_shape, dtype=np.complex64)

	int_time_array = np.empty(num_records)
	

	rec_idx = 0
	for k in data_record:
		sqn_num_array[rec_idx] = data_record[k]["num_sequences"]
		int_time_array[rec_idx] = data_record[k]["int_time"]

		# some records have fewer than the specified number of sequences
		# get around this by zero padding to the recorded number
		sqn_timestamps = data_record[k]["sqn_timestamps"]
		while len(sqn_timestamps) < max_seqs:
			sqn_timestamps = np.append(sqn_timestamps, 0)
		sqn_ts_array[rec_idx] = sqn_timestamps

		rec_noise = data_record[k]["noise_at_freq"]
		noise_pos = rec_idx * noise_buffer_offset
		noise_end = noise_pos + data_record[k]["num_sequences"]
		noise_buffer[noise_pos:noise_end] = rec_noise

		data_dict["noise_at_freq"] = noise_buffer.reshape(noise_shape)

		main_array[rec_idx] = data_record[k]["main_acfs"].reshape(dims)
		intf_array[rec_idx] = data_record[k]["intf_acfs"].reshape(dims)
		xcfs_array[rec_idx] = data_record[k]["xcfs"].reshape(dims)

		rec_idx += 1

	# write leftover metadata and data
	data_dict["int_time"] = int_time_array
	data_dict["sqn_timestamps"] = sqn_ts_array
	data_dict["num_sequences"] = sqn_num_array
	data_dict["noise_at_freq"] = noise_buffer.reshape(noise_shape)
	data_dict["correlation_descriptors"] = np.insert(data_dict["correlation_descriptors"], 0, "num_records")

	data_dict["main_acfs"] = main_array
	data_dict["intf_acfs"] = intf_array
	data_dict["xcfs"] = xcfs_array

	return data_dict


def write_array_format_data(data_dict, data_path):
	"""
	Writes a record of restructured borealis data to file.
	Args:
		data_dict:		A timestamped dictionary containing site
						formatted Borealis data
		data_path:		The path to the data file storing data_dict
	"""
	print("Compressing...")
	# Quick check of path format
	filename = data_path.split('/')[-1]
	if not len(filename.split('.')) == 7:
		raise Exception("filename does not match standard format")
	dd.io.save(data_path[:-5], data_dict, compression='zlib')


def site_to_array_format(data_path):
	"""
	Restructure the data contained in an hdf5 file to eliminate the record format.
	Rather, data will be contained in a large array according to data dimensions.
	Examples: for rawacfs, this array will be of shape (num_records, num_arrays, num_sequences, num_beams, num_ranges, num_lags)
	Fields from the original record that do not change between records will be stored as fields in one metadata record within
	the file. Other fields will contain the data arrays and other metadata that does change record to record.
	Args:
		data_path:	string containing the path to the data file for restructuring
	Returns:	If valid filetype, returns None and saves the data as a newly
				formatted hdf5 file.
	"""
	print("Restructuring", data_path, "...")

	data = dd.io.load(data_path)

	if ('output_ptrs_iq' in data_path) or ('antennas_iq' in data_path):
		print("Loaded an antenna iq file...")
		ant_iq = iq_site_to_array(data)
		write_array_format_data(ant_iq, data_path)
	elif 'bfiq' in data_path:
		print("Loaded a bfiq file...")
		bfiq = iq_site_to_array(data)
		write_array_format_data(bfiq, data_path)
	elif 'rawacf' in data_path:
		print("Loaded a raw acf file")
		raw_acf = rawacf_site_to_array(data)
		write_array_format_data(raw_acf, data_path)
	else:
		print(suffix, 'filetypes are not supported')
		return

	print("Success!")


########################## BACKCONVERSION CODE #####################################
# Functions for converting restructured and compressed
# Borealis files back to their original site format


def iq_array_to_site(data_record):
	"""
	Converts a restructured bfiq or antenna iq file back to its
	original site format
	Args:
		data_record:	An opened bfiq hdf5 file in array format
	Returns:
		ts_dict:		A timestamped dictionary containing the data
						from data_record formatted as the output from
						a site file.
	"""
	num_records = len(data_record["int_time"])
	ts_dict = dict()
	# get keys from first sequence timestamps
	for rec, seq_ts in enumerate(data_record["sqn_timestamps"]):
		# format dictionary key in the same way it is done
		# in datawrite on site
		sqn_dt_ts = datetime.datetime.utcfromtimestamp(seq_ts[0])
		epoch = datetime.datetime.utcfromtimestamp(0)
		key = str(int((sqn_dt_ts - epoch).total_seconds() * 1000))
		
		ts_dict[key] = dict()
		for field in data_record:
			if not type(data_record[field]) is np.ndarray:
				ts_dict[key][field] = data_record[field]
			else:
				if np.shape(data_record[field])[0] == num_records:
					# pass data fields that are written per record
					pass
				else:
					ts_dict[key][field] = data_record[field]
		# Handle per record fields
		num_sequences = data_record["num_sequences"][rec]
		ts_dict[key]["num_sequences"] = num_sequences
		ts_dict[key]["int_time"] = data_record["int_time"][rec]
		ts_dict[key]["sqn_timestamps"] = data_record["sqn_timestamps"][rec, 0:int(num_sequences)]
		ts_dict[key]["noise_at_freq"] = data_record["noise_at_freq"][rec, 0:int(num_sequences)]
		ts_dict[key]["data_descriptors"] = ts_dict[key]["data_descriptors"][1:]
		ts_dict[key]["data_dimensions"] = data_record["data_dimensions"][rec]

		ts_dict[key]["data"] = np.trim_zeros(data_record["data"][rec].flatten())
	
	return ts_dict

def rawacf_array_to_site(data_record):
	"""
	Converts a restructured raw acf file back to its
	original site format
	Args:
		data_record:	An opened rawacf hdf5 file in array format
	Returns:
		ts_dict:		A timestamped dictionary containing the data
						from data_record formatted as the output from
						a site file.
	"""
	num_records = len(data_record["int_time"])
	ts_dict = dict()
	# get keys from first sequence timestamps
	for rec, seq_ts in enumerate(data_record["sqn_timestamps"]):
		# format dictionary key in the same way it is done
		# in datawrite on site
		sqn_dt_ts = datetime.datetime.utcfromtimestamp(seq_ts[0])
		epoch = datetime.datetime.utcfromtimestamp(0)
		key = str(int((sqn_dt_ts - epoch).total_seconds() * 1000))
		
		ts_dict[key] = dict()
		for field in data_record:
			if not type(data_record[field]) is np.ndarray:
				ts_dict[key][field] = data_record[field]
			else:
				if np.shape(data_record[field])[0] == num_records:
					# pass data fields that are written per record
					pass
				else:
					ts_dict[key][field] = data_record[field]
		# Handle per record fields
		num_sequences = data_record["num_sequences"][rec]
		ts_dict[key]["num_sequences"] = num_sequences
		ts_dict[key]["int_time"] = data_record["int_time"][rec]
		ts_dict[key]["sqn_timestamps"] = data_record["sqn_timestamps"][rec, 0:int(num_sequences)]
		ts_dict[key]["noise_at_freq"] = data_record["noise_at_freq"][rec, 0:int(num_sequences)]
		ts_dict[key]["correlation_descriptors"] = ts_dict[key]["correlation_descriptors"][1:]

		ts_dict[key]["main_acfs"] = data_record["main_acfs"][rec].flatten()
		ts_dict[key]["intf_acfs"] = data_record["intf_acfs"][rec].flatten()
		ts_dict[key]["xcfs"] = data_record["xcfs"][rec].flatten()
		
	return ts_dict


def write_site_format_data(ts_dict, data_path):
	"""
	Writes a set of back-converted borealis data to file in the original site
	file format
	Args:
		ts_dict:	The timestamped dictionary to be written to file
		data_path:	Path to the restructured file from which the data
					in ts_dict was converted
	"""
	temp_file = tempfile.NamedTemporaryFile().name
	site_format_file = data_path + '.site'
	Path(site_format_file).touch()
	for key in ts_dict:
		time_stamped_dd = {}
		time_stamped_dd[key] = ts_dict[key]

		dd.io.save(temp_file, time_stamped_dd, compression=None)
		cmd = 'h5copy -i {newfile} -o {fullfile} -s {dtstr} -d {dtstr}'
		cmd = cmd.format(newfile=temp_file, fullfile=site_format_file, dtstr=key)

		sp.call(cmd.split())
		os.remove(temp_file)
		print("Done", key)



def array_to_site_format(data_path):
	"""
	Converts a restructured and compressed hdf5 borealis datafile
	back to its original, record based format.
	Args:
		data_path (str): Path to the data file to be back converted
	"""

	print("Restructuring", data_path, "...")

	data = dd.io.load(data_path)

	warnings.simplefilter('ignore')


	if ('output_ptrs_iq' in data_path) or ('antennas_iq' in data_path):
		print("Loaded an antenna iq file...")
		ant_iq = iq_array_to_site(data)
		write_site_format_data(ant_iq, data_path)
	elif 'bfiq' in data_path:
		print("Loaded a bfiq file...")
		bfiq = iq_array_to_site(data)
		write_site_format_data(bfiq, data_path)
	elif 'rawacf' in data_path:
		print("Loaded a raw acf file")
		raw_acf = rawacf_array_to_site(data)
		write_site_format_data(raw_acf, data_path)
	else:
		print(suffix, 'filetypes are not supported')
		return

	print("Success!")
