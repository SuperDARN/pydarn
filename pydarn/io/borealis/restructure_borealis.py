# Copyright 2019 SuperDARN Canada, University of Saskatchewan
# Authors: Liam Graham, Marci Detwiller
"""
This file contains a utility class for restructuring Borealis files. 
The files can be restructured from record-by-record format (as written on
site in real-time) to an array-based format where the number of records 
is a dimension of the array. This makes the files much more human-readable
and also faster to read.

Classes
-------
BorealisRestructureUtilities

Functions
---------
borealis_site_to_array_dict: uses the BorealisRestructureUtilities
    methods to convert dictionary of records into a dictionary
    of arrays 
borealis_array_to_site_dict: uses the BorealisRestructureUtilities
    methods to convert dictionary of arrays into a dictionary
    of records

Exceptions
----------
BorealisRestructureError
"""
import datetime
import deepdish as dd
import numpy as np
import os
import subprocess as sp
import sys
import tempfile
import warnings

from collections import OrderedDict
from functools import reduce
from pathlib2 import Path

from pydarn import BorealisRawacf, BorealisBfiq, BorealisAntennasIq, \
                   BorealisRestructureError, BorealisUtilities, \
                   borealis_formats


class BorealisRestructureUtilities():
    """
    Utility class containing static methods for restructuring Borealis files.

    Restructured files result in faster reads and a more human-readable
    format. 

    The shared fields of the file are written as a single value in the file, 
    and unshared fields are written as arrays where number of records is the 
    first dimension.

    Static Methods
    --------------
    find_max_sequences(data)
        Find the max number of sequences between records in a site file, for 
        restructuring to arrays.
    bfiq_site_to_array(filename, data_dict)
        Convert bfiq site data to array style dictionary.
    antennas_iq_site_to_array(filename, data_dict)
        Convert antennas_iq site data to array style dictionary.
    rawacf_site_to_array(filename, data_dict)
        Convert rawacf site data to array style dictionary.
    bfiq_array_to_site(filename, data_dict)
        Convert bfiq array data to site record dictionary.
    antennas_iq_array_to_site(filename, data_dict)
        Convert antennas_iq array data to site record dictionary.
    rawacf_array_to_site(data_dict)
        Convert rawacf array data to site record dictionary. 
    """

    @staticmethod
    def find_max_sequences(data: OrderedDict) -> int:
        """
        Finds the maximum number of sequences between records in a Borealis
        site style data file.

        Parameters
        ----------
        data
            Site formatted data from a Borealis file, organized as one 
            record for each slice
        
        Returns
        -------
        max_seqs
            The largest number of sequences found in one record from the 
            file
        """
        max_seqs = 0
        for k in data:
            if max_seqs < data[k]["num_sequences"]:
                max_seqs = data[k]["num_sequences"]
        return max_seqs

    @staticmethod
    def find_max_beams(data: OrderedDict) -> int:
        """
        Finds the maximum number of beams between records in a Borealis
        site style data file.

        Parameters
        ----------
        data
            Site formatted data from a Borealis file, organized as one 
            record for each slice
        
        Returns
        -------
        max_beams
            The largest number of beams found in one record from the 
            file
        """
        max_beams = 0
        for k in data:

            if max_beams < len(data[k]["beam_nums"]):
                max_beams = len(data[k]["beam_nums"])
        return max_beams

    @staticmethod
    def _iq_site_to_array(data_dict: OrderedDict, iq_filetype: str) -> dict:
        """
        Base function for converting both bfiq and antennas_iq data to 
        restructured array format.

        Parameters
        ----------
        data_dict: OrderedDict
            a dict of timestamped records loaded from an hdf5 Borealis bfiq
            or antennas_iq data file
        iq_filetype: str
            'bfiq' or 'antennas_iq' for more information on how to process.
        
        Returns
        -------
        new_data_dict
            A dictionary containing the data from data_dict
            reformatted to be stored entirely as arrays, or as
            one entry if the field does not change between records
        """
        new_data_dict = dict()
        num_records = len(data_dict)

        # write shared fields to dictionary
        first_key = list(data_dict.keys())[0]

        # find maximum number of sequences
        max_seqs = self.find_max_sequences(data_dict)
        max_beams = self.find_max_beams(data_dict)
        dims = data_dict[first_key]["data_dimensions"]

        if iq_filetype == 'antennas_iq':  
            # dims are num_antennas, num_sequences, num_samps
            for field in BorealisAntennasIq.shared_fields:
                new_data_dict[field] = data_dict[first_key][field]

            num_antennas = dims[0]
            num_samps = dims[2]
            data_buffer_offset = num_antennas * num_samps * max_seqs
            data_buffer = np.zeros(num_records * data_buffer_offset, dtype=np.complex64)

            data_descriptors = np.ndarray(["num_records", "num_antennas", 
                "max_num_sequences", "num_samps"], dtype=np.unicode_)
            data_shape = (num_records, num_antennas, max_seqs, num_samps)

        elif iq_filetype == 'bfiq': 
            # dims are num_antenna_arrays, num_sequences, num_beams, num_samps
            for field in BorealisBfiq.shared_fields:
                new_data_dict[field] = data_dict[first_key][field]
            num_arrays = dims[0]
            num_samps = dims[3]

            data_buffer_offset = num_arrays * max_beams * num_samps * max_seqs
            data_buffer = np.zeros(num_records * data_buffer_offset, dtype=np.complex64)
            data_descriptors = np.ndarray(["num_records", "num_antenna_arrays", 
                "max_num_sequences", "max_num_beams", "num_samps"], dtype=np.unicode_)
            data_shape = (num_records, num_arrays, max_seqs, max_beams, num_samps)

        else:  # Unrecognized
            raise BorealisRestructureError("Unrecognized filetype in _iq_site_to_array")

        sqn_buffer_offset = max_seqs
        sqn_ts_buffer = np.zeros(num_records * max_seqs)
        sqn_shape = (num_records, max_seqs)

        noise_buffer_offset = max_seqs
        noise_buffer = np.zeros(num_records * max_seqs)
        noise_shape = (num_records, max_seqs)

        sqn_num_array = np.empty(num_records)
        int_time_array = np.empty(num_records)
        scan_start_array = np.empty((num_records), dtype=np.bool_)
        num_slices_array = np.empty((num_records), dtype=np.int64)

        beam_nums_array = np.zeros((num_records, max_beams), dtype=np.uint32)
        beam_azms_array = np.zeros((num_records, max_beams), dtype=np.float64)
        num_beams_array = np.empty((num_records), dtype=np.uint32)

        for rec_idx, k in enumerate(data_dict):
            # handle unshared fields
            sqn_num_array[rec_idx] = data_dict[k]["num_sequences"]
            int_time_array[rec_idx] = data_dict[k]["int_time"]
            scan_start_array[rec_idx] = data_dict[k]["scan_start_marker"]
            num_slices_array[rec_idx] = data_dict[k]["num_slices"]

            beam_nums_buffer = data_dict[k]["beam_nums"]
            beam_azms_buffer = data_dict[k]["beam_azms"]
            # the beam_nums, beam_azms at a record may have appended zeros, 
            # which is why a num_beams array is necessary.
            beam_nums_array[rec_idx][0:len(beam_nums_buffer)] = beam_nums_buffer 
            beam_azms_array[rec_idx][0:len(beam_azms_buffer)] = beam_azms_buffer
            num_beams_array[rec_idx] = len(beam_nums_buffer)

            # insert data into buffer
            record_buffer = data_dict[k]["data"]
            data_pos = rec_idx * data_buffer_offset
            data_end = data_pos + len(record_buffer)
            data_buffer[data_pos:data_end] = record_buffer

            # insert sequence timestamps into buffer
            rec_sqn_ts = data_dict[k]["sqn_timestamps"]
            sqn_pos = rec_idx * sqn_buffer_offset
            sqn_end = sqn_pos + data_dict[k]["num_sequences"]
            sqn_ts_buffer[sqn_pos:sqn_end] = rec_sqn_ts

            rec_noise = data_dict[k]["noise_at_freq"]
            noise_pos = rec_idx * noise_buffer_offset
            noise_end = noise_pos + data_dict[k]["num_sequences"]
            noise_buffer[noise_pos:noise_end] = rec_noise

        # write leftover metadata and data
        new_data_dict["num_sequences"] = sqn_num_array
        new_data_dict["int_time"] = int_time_array
        new_data_dict["scan_start_marker"] = scan_start_array
        new_data_dict["num_slices"] = num_slices_array
        new_data_dict["beam_nums"] = beam_nums_array 
        new_data_dict["beam_azms"] = beam_azms_array
        new_data_dict["num_beams"] = num_beams_array

        new_data_dict["data"] = data_buffer.reshape(data_shape)
        new_data_dict["sqn_timestamps"] = sqn_ts_buffer.reshape(sqn_shape)
        new_data_dict["noise_at_freq"] = noise_buffer.reshape(noise_shape)

        new_data_dict["data_descriptors"] = data_descriptors
        # new_data_dict["data_dimensions"] = data_dims_array

        return new_data_dict

    @staticmethod
    def bfiq_site_to_array(filename: str, data_dict: OrderedDict) -> dict:
        """
        Restructuring method for bfiq data.

        Parameters
        ----------
        filename
            String of where file originated from for better error messages.
        data_dict
            a dict of timestamped records loaded from an hdf5 Borealis bfiq
            data file
        
        Returns
        -------
        new_data_dict
            A dictionary containing the data from data_dict
            reformatted to be stored entirely as arrays, or as
            one entry if the field does not change between records
        """
        
        try:
            new_data_dict = self._iq_site_to_array(data_dict, 'bfiq')

            BorealisUtilities.check_arrays(filename, new_data_dict, 
                borealis_formats.BorealisBfiq.array_single_element_types,
                borealis_formats.BorealisBfiq.array_array_dtypes,
                borealis_formats.BorealisBfiq.unshared_fields)

        except Exception as e:
            raise BorealisRestructureError('Error restructuring bfiq '\
                                           'from site to array style:'\
                                           '{}'.format(e))

        return new_data_dict

    @staticmethod
    def antennas_iq_site_to_array(filename: str, data_dict: OrderedDict) -> dict:
        """
        Restructuring method for antennas_iq data.

        Parameters
        ----------
        filename
            String of where file originated from for better error messages.
        data_dict
            a dict of timestamped records loaded from an hdf5 Borealis 
            antennas_iq data file
        
        Returns
        -------
        new_data_dict
            A dictionary containing the data from data_dict
            reformatted to be stored entirely as arrays, or as
            one entry if the field does not change between records
        """
        
        try:
            new_data_dict = self._iq_site_to_array(data_dict, 'antennas_iq')

            BorealisUtilities.check_arrays(filename, new_data_dict, 
                borealis_formats.BorealisAntennasIq.array_single_element_types,
                borealis_formats.BorealisAntennasIq.array_array_dtypes,
                borealis_formats.BorealisAntennasIq.unshared_fields)

        except Exception as e:
            raise BorealisRestructureError('Error restructuring antennas_iq '\
                                           'from site to array style:'\
                                           '{}'.format(e))

        return new_data_dict

    @staticmethod
    def rawacf_site_to_array(filename: str, data_dict: OrderedDict) -> dict:
        """
        Restructuring method for rawacf data.

        Parameters
        ----------
        filename
            String of where file originated from for better error messages.
        data_dict
            a dict of timestamped records loaded from an hdf5 Borealis rawacf
            data file
        
        Returns
        -------
        new_data_dict
            A dictionary containing the data from data_dict
            reformatted to be stored entirely as arrays, or as
            one entry if the field does not change between records
        """
        try:
            new_data_dict = dict()
            num_records = len(data_dict)
            max_seqs = self.find_max_sequences(data_dict)
            max_beams = self.find_max_beams(data_dict)

            # write shared fields to dictionary
            first_key = list(data_dict.keys())[0]
            for field in BorealisRawacf.shared_fields:
                new_data_dict[field] = data_dict[first_key][field]

            # handle unshared data fields
            dims = data_dict["correlation_dimensions"]
            # dims are num_beams, num_ranges, num_lags
            num_ranges = dims[1]
            num_lags = dims[2]
            correlation_descriptors = np.ndarray(['num_records', 'max_num_beams', 
                'num_ranges', 'num_lags'], dtype=np.unicode_)
            data_shape = (num_records, max_beams, num_ranges, num_lags)

            noise_buffer_offset = max_seqs
            noise_buffer = np.zeros(num_records * max_seqs)
            noise_shape = (num_records, max_seqs)


            main_array = np.empty(data_shape, dtype=np.complex64)
            intf_array = np.empty(data_shape, dtype=np.complex64)
            xcfs_array = np.empty(data_shape, dtype=np.complex64)

            sqn_ts_array = np.empty((num_records, max_seqs), dtype=np.float64)
            sqn_num_array = np.empty((num_records), dtype=np.int64)
            int_time_array = np.empty((num_records), dtype=np.float32)
            scan_start_array = np.empty((num_records), dtype=np.bool_)
            num_slices_array = np.empty((num_records), dtype=np.int64)

            beam_nums_array = np.zeros((num_records, max_beams), dtype=np.uint32)
            beam_azms_array = np.zeros((num_records, max_beams), dtype=np.float64)
            num_beams_array = np.empty((num_records), dtype=np.uint32)

            for rec_idx, k in enumerate(data_dict):
                sqn_num_array[rec_idx] = data_dict[k]["num_sequences"]
                int_time_array[rec_idx] = data_dict[k]["int_time"]
                scan_start_array[rec_idx] = data_dict[k]["scan_start_marker"]

                scan_start_array[rec_idx] = data_dict[k]["scan_start_marker"]
                num_slices_array[rec_idx] = data_dict[k]["num_slices"]

                beam_nums_buffer = data_dict[k]["beam_nums"]
                beam_azms_buffer = data_dict[k]["beam_azms"]
                # the beam_nums, beam_azms at a record may have appended zeros, 
                # which is why a num_beams array is necessary.
                beam_nums_array[rec_idx][0:len(beam_nums_buffer)] = beam_nums_buffer 
                beam_azms_array[rec_idx][0:len(beam_azms_buffer)] = beam_azms_buffer
                num_beams_array[rec_idx] = len(beam_nums_buffer)

                # some records have fewer than the specified number of sequences
                # get around this by zero padding to the recorded number
                sqn_timestamps = data_dict[k]["sqn_timestamps"]
                while len(sqn_timestamps) < max_seqs:
                    sqn_timestamps = np.append(sqn_timestamps, 0)
                sqn_ts_array[rec_idx] = sqn_timestamps

                rec_noise = data_dict[k]["noise_at_freq"]
                noise_pos = rec_idx * noise_buffer_offset
                noise_end = noise_pos + data_dict[k]["num_sequences"]
                noise_buffer[noise_pos:noise_end] = rec_noise

                data_dict["noise_at_freq"] = noise_buffer.reshape(noise_shape)

                main_array[rec_idx] = data_dict[k]["main_acfs"].reshape(dims)
                intf_array[rec_idx] = data_dict[k]["intf_acfs"].reshape(dims)
                xcfs_array[rec_idx] = data_dict[k]["xcfs"].reshape(dims)

            # write leftover metadata and data
            new_data_dict["num_sequences"] = sqn_num_array
            new_data_dict["int_time"] = int_time_array
            new_data_dict["scan_start_marker"] = scan_start_array
            new_data_dict["num_slices"] = num_slices_array
            new_data_dict["beam_nums"] = beam_nums_array 
            new_data_dict["beam_azms"] = beam_azms_array
            new_data_dict["num_beams"] = num_beams_array
            new_data_dict["sqn_timestamps"] = sqn_ts_array
            new_data_dict["noise_at_freq"] = noise_buffer.reshape(noise_shape)

            new_data_dict["correlation_descriptors"] = correlation_descriptors
            new_data_dict["main_acfs"] = main_array
            new_data_dict["intf_acfs"] = intf_array
            new_data_dict["xcfs"] = xcfs_array

            BorealisUtilities.check_arrays(filename, new_data_dict, 
                borealis_formats.BorealisRawacf.array_single_element_types,
                borealis_formats.BorealisRawacf.array_array_dtypes,
                borealis_formats.BorealisRawacf.unshared_fields)

        except Exception as e:
            raise BorealisRestructureError('Error restructuring rawacf '\
                                           'from site to array style:'\
                                           '{}'.format(e))
        return new_data_dict

    @staticmethod
    def _iq_array_to_site(data_dict: dict, iq_filetype: str) -> OrderedDict:
        """
        Base function for converting both bfiq and antennas_iq back to 
        original site format. 

        Parameters
        ----------
        data_dict: dict
            An opened bfiq hdf5 file in array format
        iq_filetype: str
            'bfiq' or 'antennas_iq' for more information on how to process.

        Returns
        -------
        ts_dict
            A timestamped dictionary containing the data from data_dict
            formatted as the output from a site file (as records, where 
            keys are timestamp of first sequence in the record)
        """

        ts_dict = OrderedDict()

        if iq_filetype == 'bfiq':
            # dims are num_antenna_arrays, num_sequences, num_beams, num_samps
            shared_fields = borealis_formats.BorealisBfiq.shared_fields
            unshared_fields = borealis_formats.BorealisBfiq.unshared_fields
            num_records, num_antenna_arrays, max_num_sequences, \
                max_num_beams, num_samps = data_dict["data"].shape
            # new data descriptors
            data_descriptors = np.ndarray(["num_antenna_arrays", 
                "num_sequences", "num_beams", "num_samps"], dtype=np.unicode_)
        elif iq_filetype == 'antennas_iq':
            # dims are num_antennas, num_sequences, num_samps
            shared_fields = borealis_formats.BorealisAntennasIq.shared_fields
            unshared_fields = borealis_formats.BorealisAntennasIq.unshared_fields
            num_records, num_antennas, max_num_sequences, num_samps = \
                data_dict["data"].shape
            max_num_beams = max(data_dict["num_beams"]) # array only field
            # new data descriptors
            data_descriptors = np.ndarray(["num_antennas", "num_sequences", 
                "num_samps"], dtype=np.unicode_)
        else:
            raise BorealisRestructureError("Unrecognized filetype in \
                _iq_site_to_array")
        
        # get keys from first sequence timestamps
        for rec, seq_ts in enumerate(data_dict["sqn_timestamps"]):
            # format dictionary key in the same way it is done
            # in datawrite on site
            sqn_dt_ts = datetime.datetime.utcfromtimestamp(seq_ts[0])
            epoch = datetime.datetime.utcfromtimestamp(0)
            key = str(int((sqn_dt_ts - epoch).total_seconds() * 1000))
            
            ts_dict[key] = dict()
            # copy shared_fields
            for field in shared_fields:
                ts_dict[key][field] = data_dict[field]

            # data_descriptors needs to be overwritten
            ts_dict[key]["data_descriptors"] = data_descriptors

            # Handle per record fields
            for field in unshared_fields:
                ts_dict[key][field] = data_dict[field][rec]
            
            # Handle special cases - where dimensions may be larger than necessary.
            num_beams = data_dict["num_beams"][rec] # array only field
            if num_beams != max_num_beams:
                ts_dict[key]["beam_nums"] = ts_dict[key]["beam_nums"][rec,:num_beams]
                ts_dict[key]["beam_azms"] = ts_dict[key]["beam_azms"][rec,:num_beams]

            num_sequences = ts_dict[key]["num_sequences"]
            if num_sequences != max_num_sequences:
                ts_dict[key]["sqn_timestamps"] = data_dict["sqn_timestamps"][rec,:num_sequences]
                ts_dict[key]["noise_at_freq"] = data_dict["noise_at_freq"][rec,:num_sequences]

            # have to take correct dimensions to remove appended zeros if num_sequences or
            # num_beams are less than max. 
            if iq_filetype == 'bfiq':
                dims = np.ndarray([num_antenna_arrays, num_sequences, num_beams, num_samps],
                        dtype=np.uint32)
                new_data = data_dict["data"][rec,:dims[0],:dims[1],:dims[2],:dims[3]]
            elif iq_filetype == 'antennas_iq':
                dims = np.ndarray([num_antennas, num_sequences, num_samps], dtype=np.uint32)
                new_data = data_dict["data"][rec,:dims[0],:dims[1],:dims[2]]
            
            ts_dict[key]["data_dimensions"] = dims # site only field
            ts_dict[key]["data"] = new_data.flatten()

        return ts_dict

    @staticmethod
    def bfiq_array_to_site(filename: str, data_dict: dict) -> OrderedDict:
        """
        Converts a restructured array bfiq file back to the original site 
        format.

        Parameters
        ----------
        filename
            String of where file originated from for better error messages.
        data_dict
            An opened bfiq hdf5 file in array format
        
        Returns
        -------
        ts_dict
            A timestamped dictionary containing the data from data_dict
            formatted as the output from a site file (as records, where 
            keys are timestamp of first sequence in the record)
        """
        try:
            ts_dict = self._iq_array_to_site(data_dict)
            BorealisUtilities.check_records(filename, ts_dict, 
                borealis_formats.BorealisBfiq.single_element_types,
                borealis_formats.BorealisBfiq.array_dtypes)

        except Exception as e:
            raise BorealisRestructureError('Error restructuring bfiq '\
                                           'from array to site style:'\
                                           '{}'.format(e))
        return ts_dict

    @staticmethod
    def antennas_iq_array_to_site(filename: str, data_dict: dict) -> OrderedDict:
        """
        Converts a restructured array antennas_iq file back to the
        original site format.

        Parameters
        ----------
        filename
            String of where file originated from for better error messages.
        data_dict
            An opened antennas_iq hdf5 file in array format
        
        Returns
        -------
        ts_dict
            A timestamped dictionary containing the data from data_dict
            formatted as the output from a site file (as records, where 
            keys are timestamp of first sequence in the record)
        """
        try:
            ts_dict = self._iq_array_to_site(data_dict)
            BorealisUtilities.check_records(filename, ts_dict, 
                borealis_formats.BorealisAntennasIq.single_element_types,
                borealis_formats.BorealisAntennasIq.array_dtypes)

        except Exception as e:
            raise BorealisRestructureError('Error restructuring antennas_iq '\
                                           'from array to site style:'\
                                           '{}'.format(e))
        return ts_dict

    @staticmethod
    def rawacf_array_to_site(filename: str, data_dict: dict) -> OrderedDict:
        """
        Converts a restructured array rawacf file back to the
        original site format.

        Parameters
        ----------
        filename
            String of where file originated from for better error messages.
        data_dict
            An opened rawacf hdf5 file in array format
        
        Returns
        -------
        ts_dict
            A timestamped dictionary containing the data from data_dict
            formatted as the output from a site file (as records, where 
            keys are timestamp of first sequence in the record)
        """
        shared_fields = borealis_formats.BorealisRawacf.shared_fields
        unshared_fields = borealis_formats.BorealisRawacf.unshared_fields

        try:
            num_records, max_num_beams, num_ranges, num_lags = \
                data_dict["data"].shape
            # new correlation descriptors
            correlation_descriptors = np.ndarray(['num_beams', 'num_ranges',
                'num_lags'], dtype=np.unicode_)

            ts_dict = OrderedDict()
            # get keys from first sequence timestamps
            for rec, seq_ts in enumerate(data_dict["sqn_timestamps"]):
                # format dictionary key in the same way it is done
                # in datawrite on site
                sqn_dt_ts = datetime.datetime.utcfromtimestamp(seq_ts[0])
                epoch = datetime.datetime.utcfromtimestamp(0)
                key = str(int((sqn_dt_ts - epoch).total_seconds() * 1000))
                
                ts_dict[key] = dict()
                for field in shared_fields:
                    ts_dict[key][field] = data_dict[field]
                # overwrite the correlation descriptors
                ts_dict["correlation_descriptors"] = correlation_descriptors

                # Handle per record fields
                for field in unshared_fields:
                    ts_dict[key][field] = data_dict[field][rec]

                # Handle special cases - where dimensions may be larger than necessary.
                num_beams = data_dict["num_beams"][rec] # array only field
                if num_beams != max_num_beams:
                    ts_dict[key]["beam_nums"] = ts_dict[key]["beam_nums"][rec,:num_beams]
                    ts_dict[key]["beam_azms"] = ts_dict[key]["beam_azms"][rec,:num_beams]

                num_sequences = ts_dict[key]["num_sequences"]
                if num_sequences != max_num_sequences:
                    ts_dict[key]["sqn_timestamps"] = data_dict["sqn_timestamps"][rec,:num_sequences]
                    ts_dict[key]["noise_at_freq"] = data_dict["noise_at_freq"][rec,:num_sequences]

                dims = np.ndarray([num_beams, num_ranges, num_lags],
                        dtype=np.uint32)
                main_acfs = data_dict["main_acfs"][rec,:dims[0],:dims[1],:dims[2]]
                intf_acfs = data_dict["intf_acfs"][rec,:dims[0],:dims[1],:dims[2]]
                xcfs = data_dict["xcfs"][rec,:dims[0],:dims[1],:dims[2]]

                ts_dict[key]["main_acfs"] = main_acfs.flatten()
                ts_dict[key]["intf_acfs"] = intf_acfs.flatten()
                ts_dict[key]["xcfs"] = xcfs.flatten()

                ts_dict[key]["correlation_dimensions"] = dims # site only field

            BorealisUtilities.check_records(filename, ts_dict, 
                borealis_formats.BorealisRawrf.single_element_types,
                borealis_formats.BorealisRawrf.array_dtypes)
        
        except Exception as e:
            raise BorealisRestructureError('Error restructuring rawacf '\
                                           'from array to site style:'\
                                           '{}'.format(e))
        return ts_dict


def borealis_site_to_array_dict(data_dict: OrderedDict, 
                                conversion_type: str) -> dict:
    """
    Converts a file from site style to restructured array style. Determines
    which base function to call based on conversion_type. 

    Parameters
    ----------
    data_dict: OrderedDict
        An opened rawacf hdf5 file in site record-by-record format
    }
    conversion_type: str
        'bfiq', 'antennas_iq' or 'rawacf' to determine keys to convert
    
    Returns
    -------
    new_dict
        A dictionary containing the data from data_dict
        formatted to the array format
    """ 
    if conversion_type == 'bfiq':
        new_dict = BorealisRestructureUtilities.bfiq_site_to_array(data_dict)
    elif conversion_type == 'rawacf':
        new_dict = BorealisRestructureUtilities.rawacf_site_to_array(data_dict)
    elif conversion_type == 'antennas_iq':
        new_dict = BorealisRestructureUtilities.antennas_iq_site_to_array(data_dict)        
    else:
        raise BorealisRestructureError('File type {} not recognized '\
                                       'as restructureable from site to '\
                                       'array style'.format(conversion_type))
    return new_dict


def borealis_array_to_site_dict(data_dict: dict, 
                                conversion_type: str) -> OrderedDict:
    """
    Converts a file back to its original site format. Determines
    which base function to call based on conversion_type. 

    Parameters
    ---------_
    data_dict: dict
        An opened rawacf hdf5 file in array format
    conversion_type: str
        'bfiq', 'antennas_iq' or 'rawacf' to determine keys to convert
    
    Returns
    -------
    new_dict
        A timestamped dictionary containing the data from data_dict
        formatted as the output from a site file.
    """ 
    if conversion_type == 'bfiq':
        new_dict = BorealisRestructureUtilities.bfiq_array_to_site(data_dict)
    elif conversion_type == 'rawacf':
        new_dict = BorealisRestructureUtilities.rawacf_array_to_site(data_dict)
    elif conversion_type == 'antennas_iq':
        new_dict = BorealisRestructureUtilities.antennas_iq_array_to_site(data_dict)        
    else:
        raise BorealisRestructureError('File type {} not recognized '\
                                       'as restructureable from array to '\
                                       'site style'.format(conversion_type))
    return new_dict
