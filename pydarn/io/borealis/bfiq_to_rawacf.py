# Copyright 2019 SuperDARN Canada, University of Saskatchewan
# Authors: Liam Graham, Marci Detwiller
"""
This file contains a function for processing beam-formed IQ data into rawacf
data product matching the real-time product produced by datawrite module in
Borealis.

Classes
-------
BorealisBfiqToRawacfPostProcessor
    reads a bfiq file, processes the data within
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
BorealisRestructureUtilities

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
from typing import Union, List

from multiprocessing import Manager, Process

from pydarn import borealis_exceptions, BorealisRead, BorealisWrite
from .restructure_borealis import BorealisRestructureUtilities


class BorealisBfiqToRawacfPostProcessor():
    """
    Class for converting bfiq data into rawacf data.

    See Also
    --------
    BorealisRead
    BorealisSiteRead
    BorealisArrayRead
    BorealisWrite
    BorealisSiteWrite
    BorealisArrayWrite
    BorealisRawacf
    BorealisBfiq

    Attributes
    ----------
    bfiq_filename: str
        The filename of the Borealis HDF5 bfiq file being read.
    rawacf_filename: str
        The filename of the Borealis HDF5 rawacf file being written.
    num_processes: int
        The number of processes to use to convert the records in the dictionary.
        Default 4.
    read_file_structure: Union[str, None]
        How to read the bfiq data. If 'site', will read as record stored data
        (site files). If 'array', will read as array stored. None lets
        BorealisRead determine, which tries array first and then site.
    write_file_structure: str
        How to write the rawacf data. If 'site', will write in record by record
        site format. If 'array', will write in array format. Default 'array'.
    bfiq_reader: BorealisRead
        BorealisRead instance containing read information.
    bfiq_records: OrderedDict{dict}
        Bfiq records read from the bfiq_filename
    rawacf_records: OrderedDict{dict}
        Rawacf records read from the rawacf_filename
    rawacf_writer: BorealisWrite
        BorealisWrite instance containing write information.
    compression: str
        The type of compression to write the file as.
    """

    def __init__(self, bfiq_filename: str, rawacf_filename: str,
                 read_file_structure: Union[str, None] = None,
                 write_file_structure: str = 'array', num_processes: int = 4,
                 **kwargs):
        """
        Processes the data from a bfiq.hdf5 file and creates auto and cross-
        correlations from the samples.

        This data is formatted and written as Borealis rawacf hdf5 files the
        same as if they had been produced on site.

        Parameters
        ----------
        bfiq_filename: str
            The file where the bfiq hdf5 data is located. Can be record or array
            stored.
        rawacf_filename: str
            The filename of where you want to place the rawacf hdf5 data. Rawacf
            data will be stored as per the write_file_structure.
        read_file_structure: Union[str, None]
            How to read the bfiq data. If 'site', will read as record stored data
            (site files). If 'array', will read as array stored. None lets
            BorealisRead determine, which tries array first and then site.
        write_file_structure: str
            How to write the rawacf data. If 'site', will write in record by record
            site format. If 'array', will write in array format. Default 'array'.
        num_processes: int
            The number of processes to use to convert the records in the dictionary.
            Default 4.
        kwargs
            args to pass into the write. Only possible argument is hdf5_compression.

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

        self.bfiq_filename = bfiq_filename
        self.rawacf_filename = rawacf_filename

        self.write_file_structure = write_file_structure

        self.__num_processes = num_processes

        if 'hdf5_compression' in kwargs.keys():
            self.compression = kwargs['hdf5_compression']

        if self.bfiq_filename == self.rawacf_filename:
            raise borealis_exceptions.ConvertFileOverWriteError(
                    self.bfiq_filename)

        # Suppress NaturalNameWarning when using timestamps as keys for records
        warnings.simplefilter('ignore', tables.NaturalNameWarning)

        # get the records from the bfiq file
        self.bfiq_reader = BorealisRead(self.bfiq_filename, 'bfiq',
                                   borealis_file_structure=read_file_structure)

        self.read_file_structure = self.bfiq_reader.borealis_file_structure
        self.bfiq_records = self.bfiq_reader.records

        self.rawacf_records = \
            self.__convert_bfiq_records_to_rawacf_records()

        if self.write_file_structure == 'site':
            rawacf_data = self.rawacf_records
        elif self.write_file_structure == 'array':
            rawacf_data = BorealisRestructureUtilities.borealis_site_to_array_dict(
                                                        self.rawacf_filename,
                                                        self.rawacf_records,
                                                        'rawacf')
        else: # unknown structure
            raise BorealisStructureError('Unknown write structure type: {}'\
                ''.format(self.write_file_structure))

        self.rawacf_writer = BorealisWrite(self.rawacf_filename, rawacf_data,
                            'rawacf',
                            borealis_file_structure=self.write_file_structure,
                            **kwargs)

    @property
    def num_processes(self):
        return self.__num_processes

    @staticmethod
    def __correlate_samples(time_stamped_dict: dict) -> (np.ndarray,
            np.ndarray, np.ndarray):
        """
        Builds the autocorrelation and cross-correlation matrices for the
        beamformed data contained in one timestamped dictionary

        Parameters
        ----------
        time_stamped_dict
            A timestamped record dictionary from a Borealis bfiq file

        Returns
        -------
        main_acfs
            Main array autocorrelations
        interferometer_acfs
            Interferometer array autocorrelations
        xcfs
            Cross-correlations between arrays

        """
        data_buff = time_stamped_dict["data"]
        num_slices = time_stamped_dict["num_slices"]
        num_ant_arrays = time_stamped_dict["data_dimensions"][0]
        num_sequences = time_stamped_dict["data_dimensions"][1]
        num_beams = time_stamped_dict["data_dimensions"][2]
        num_samples = time_stamped_dict["data_dimensions"][3]
        dims = time_stamped_dict["data_dimensions"]

        lags = time_stamped_dict["lags"]
        num_lags = np.shape(time_stamped_dict["lags"])[0]
        num_ranges = time_stamped_dict["num_ranges"]
        num_slices = time_stamped_dict["num_slices"]

        data_mat = data_buff.reshape(dims)

        # Get data from each antenna array (main and interferometer)
        main_data = data_mat[0][:][:][:]
        interferometer_data = data_mat[1][:][:][:]

        # Preallocate arrays for correlation results
        main_corrs = np.zeros((num_sequences, num_beams, num_samples,
                              num_samples), dtype=np.complex64)
        interferometer_corrs = np.zeros((num_sequences, num_beams, num_samples,
                              num_samples), dtype=np.complex64)
        cross_corrs = np.zeros((num_sequences, num_beams, num_samples,
                               num_samples), dtype=np.complex64)

        # Preallocate arrays for results of range-lag selection
        main_acfs = np.zeros((num_sequences, num_beams, num_ranges, num_lags),
                            dtype=np.complex64)
        interferometer_acfs = np.zeros((num_sequences, num_beams, num_ranges,
                            num_lags), dtype=np.complex64)
        xcfs = np.zeros((num_sequences, num_beams, num_ranges, num_lags),
                             dtype=np.complex64)

        # Perform autocorrelations of each array, and cross-correlation
        # between arrays
        for seq in range(num_sequences):
            for beam in range(num_beams):
                main_samples = main_data[seq, beam]
                interferometer_samples = interferometer_data[seq, beam]

                main_corrs[seq, beam] = np.outer(main_samples.conjugate(),
                                                 main_samples)
                interferometer_corrs[seq, beam] = np.outer(
                    interferometer_samples.conjugate(),
                    interferometer_samples)
                cross_corrs[seq, beam] = np.outer(main_samples.conjugate(),
                                                  interferometer_samples)

                beam_offset = num_beams * num_ranges * num_lags
                first_range_offset = int(time_stamped_dict["first_range"] /
                                         time_stamped_dict["range_sep"])

                # Select out the lags for each range gate
                main_small = np.zeros((num_ranges, num_lags,),
                                      dtype=np.complex64)
                interferometer_small = np.zeros((num_ranges, num_lags,),
                                      dtype=np.complex64)
                cross_small = np.zeros((num_ranges, num_lags,),
                                       dtype=np.complex64)

                # Retrieve the correlation info needed according to
                # range and lag information given. The whole array
                # will not be kept.
                for rng in range(num_ranges):
                    for lag in range(num_lags):
                        # tau spacing in us, sample rate in hz
                        tau_in_samples = np.ceil(
                                          time_stamped_dict["tau_spacing"] *
                                          1e-6 *
                                          time_stamped_dict["rx_sample_rate"])
                        # pulse 1 and pulse 2 offsets
                        p1_offset = lags[lag, 0] * tau_in_samples
                        p2_offset = lags[lag, 1] * tau_in_samples

                        row_offset = int(rng + first_range_offset + p1_offset)
                        col_offset = int(rng + first_range_offset + p2_offset)

                        # small array is for this sequence and beam only.
                        main_small[rng, lag] = \
                            main_corrs[seq, beam, row_offset, col_offset]
                        interferometer_small[rng, lag] = \
                            interferometer_corrs[seq, beam, row_offset,
                                                 col_offset]
                        cross_small[rng, lag] = \
                            cross_corrs[seq, beam, row_offset, col_offset]

                # replace full correlation matrix with resized range-lag matrix
                main_acfs[seq, beam] = main_small
                interferometer_acfs[seq, beam] = interferometer_small
                xcfs[seq, beam] = cross_small

        # average each correlation matrix over sequences dimension
        main_acfs = np.mean(main_acfs, axis=0)
        interferometer_acfs = np.mean(interferometer_acfs, axis=0)
        xcfs = np.mean(xcfs, axis=0)

        # END def correlate_samples(time_stamped_dict)
        return main_acfs, interferometer_acfs, xcfs

    def __convert_record(self, record_key, rawacf):
        """
        Convert a bfiq_record record.

        Parameters
        ----------
        record_key
            The key of the bfiq record being converted.
        rawacf
            The rawacf record dictionary to assign to. This is
            assigning the full record to the larger dictionary
            of all records.
        """
        # write common dictionary fields first

        bfiq_rawacf_shared_fields = ['beam_azms', 'beam_nums',
            'blanked_samples', 'lags', 'noise_at_freq', 'pulses',
            'sqn_timestamps', 'borealis_git_hash', 'data_normalization_factor',
            'experiment_comment', 'experiment_id', 'experiment_name',
            'first_range', 'first_range_rtt', 'freq', 'int_time',
            'intf_antenna_count', 'main_antenna_count', 'num_sequences',
            'num_slices', 'range_sep', 'rx_sample_rate', 'samples_data_type',
            'scan_start_marker', 'slice_comment', 'station', 'tau_spacing',
            'tx_pulse_len']

        rawacf_record = {}

        for f in bfiq_rawacf_shared_fields:
            rawacf_record[f] = self.bfiq_records[record_key][f]

        # Perform correlations and write to dictionary
        # Main array autocorrelations, interferometer autocorrelations,
        # and cross-correlations between arrays.
        main_acfs, interferometer_acfs, xcfs = self.__correlate_samples(
                                        self.bfiq_records[record_key])

        rawacf_record["correlation_dimensions"] = \
            np.array(main_acfs.shape, dtype=np.uint32)
        rawacf_record["correlation_descriptors"] = \
            np.array(['num_beams', 'num_ranges', 'num_lags'])

        rawacf_record["main_acfs"] = main_acfs.flatten()
        rawacf_record["intf_acfs"] = interferometer_acfs.flatten()
        rawacf_record["xcfs"] = xcfs.flatten()

        # Log information about how this file was generated
        now = dt.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M")
        rawacf_record["experiment_comment"] += "File generated on " + \
            date_str + " at " + time_str + " from " + self.bfiq_filename + \
            " via pydarn BorealisBfiqToRawacfPostProcessor"

        # reassign to this managed dict to notify the proxy
        rawacf[record_key] = rawacf_record

    def __convert_bfiq_records_to_rawacf_records(self) -> \
            OrderedDict:
        """
        Take a data dictionary of bfiq records and return a data
        dictionary of rawacf records. Uses parallelization.

        Parameters
        ----------
        bfiq
            Data OrderedDict of bfiq records.

        Returns
        -------
        rawacf
            OrderedDict of rawacf records generated by bfiq records.
        """
        # parallelization
        manager = Manager()
        rawacf_dict = manager.dict()
        jobs = []

        record_names = sorted(list(self.bfiq_records.keys()))

        for record_key in record_names:
            rawacf_dict[record_key] = dict()

        records_left = True
        record_index = 0
        while records_left:
            for procnum in range(self.num_processes):
                try:
                    record_key = record_names[record_index]
                except IndexError:
                    records_left = False
                    break
                p = Process(target=self.__convert_record, args=(record_key, rawacf_dict))
                jobs.append(p)
                p.start()

            for proc in jobs:
                proc.join()

            record_index += self.num_processes

        rawacf_records = OrderedDict(sorted(rawacf_dict.items()))

        return rawacf_records
