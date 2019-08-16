# Copyright 2019 SuperDARN Canada, University of Saskatchewan
# Author: Marci Detwiller
"""
This test suite is to test the implementation for the following classes:
    BorealisRead
    BorealisUtilities
    BorealisWrite
Support for the following Borealis file types:
    rawrf
    antennas_iq
    bfiq
    rawacf
And supports conversion to the following Borealis types:
    bfiq -> iqdat
    rawacf -> rawacf
"""
import bz2
import collections
import copy
import logging
import numpy as np
import os
import unittest

import borealis_rawacf_data_sets
import borealis_bfiq_data_sets
import pydarn

pydarn_logger = logging.getLogger('pydarn')

# Test files

borealis_bfiq_file = "../test_files/20190605.0000.02.sas.0.bfiq.hdf5"
borealis_rawacf_file = "../test_files/20190605.0000.02.sas.0.rawacf.hdf5"
# borealis_antennas_iq_file = 
# borealis_rawrf_file =

# Problem files


class TestBorealisRead(unittest.TestCase):
    """
    Testing class for BorealisRead
    """

    def setUp(self):
        rawacf_file_path = borealis_rawacf_file
        bfiq_file_path = borealis_bfiq_file
        nonexistent_dir_path = './dog/somefile.rawacf'
        nonexistent_file_path = '../test_files/somefile.rawacf'
        empty_file_path = '../test_files/empty.rawacf'

    def test_incorrect_path(self):
        """
        Testing BorealisRead constructor with an nonexistent folder.

        Expected behaviour: raise OSError
        """
        self.assertRaises(OSError, pydarn.BorealisRead,
                          nonexistent_dir_path)

    def test_incorrect_file(self):
        """
        Tests if BorealisRead constructor with an non-existent file

        Expected behaviour: raises OSError
        """
        self.assertRaises(OSError, pydarn.BorealisRead,
                          nonexistent_file_path)

    def test_empty_file(self):
        """
        Tests if BorealisRead constructor with an empty file

        Expected behaviour: raise OSError, unable to open (file signature not found)
        """
        self.assertRaises(OSError,
                          pydarn.BorealisRead, empty_file_path)

    def test_open_rawacf(self):
        """
        Tests BorealisRead constructor on opening a rawacf.
        It should be able to open the file, read it and convert to dictionary

        Checks:
            - group names is a list, greater than length 0
        """
        reader = pydarn.BorealisRead(rawacf_file_path)
        self.assertIsInstance(reader.group_names, list)
        self.assertGreater(len(reader.group_names), 0)

    def test_open_bfiq(self):
        """
        Tests BorealisRead constructor on opening a iqdat.
        It should be able to open the file, read it and convert to dictionary

        Checks:
            - group names is a list, greater than length 0
        """
        reader = pydarn.BorealisRead(bfiq_file_path)
        self.assertIsInstance(reader.records, dict)
        self.assertGreater(len(reader.group_names), 0)

    # TODO: potential issue if files change and the values are not the same :/
    def test_read_bfiq(self):
        """
        Test reading records from bfiq.

        Checks:
            - returns correct data structures
            - returns expected values
        """
        dm = pydarn.BorealisRead(bfiq_file_path)
        records = dm.read_bfiq()
        first_record = records[dm.group_names[0]]
        self.assertIsInstance(records, collections.OrderedDict)
        self.assertIsInstance(first_record, dict)
        self.assertIsInstance(first_record['num_slices'], np.int64)

    def test_read_rawacf(self):
        """
        Test reading records from rawacf.

        Checks:
            - returns correct data structures
            - returns expected values
        """
        dm = pydarn.BorealisRead(rawacf_file_path)
        records = dm.read_rawacf()
        first_record = records[dm.group_names[0]]
        self.assertIsInstance(records, collections.OrderedDict)
        self.assertIsInstance(first_record, dict)
        self.assertIsInstance(first_record['num_slices'], np.int64)


class TestBorealisWrite(unittest.TestCase):
    """
    Tests BorealisWrite class
    """

    def setUp(self):
        rawacf_data = copy.deepcopy(
            borealis_rawacf_data_sets.borealis_rawacf_data)
        rawacf_missing_field = copy.deepcopy(
            borealis_rawacf_data_sets.borealis_rawacf_data)
        rawacf_extra_field = copy.deepcopy(
            borealis_rawacf_data_sets.borealis_rawacf_data)
        rawacf_incorrect_fmt = copy.deepcopy(
            borealis_rawacf_data_sets.borealis_rawacf_data)
        bfiq_data = copy.deepcopy(borealis_bfiq_data_sets.borealis_bfiq_data)
        bfiq_missing_field = copy.deepcopy(
            borealis_bfiq_data_sets.borealis_bfiq_data)
        bfiq_extra_field = copy.deepcopy(
            borealis_bfiq_data_sets.borealis_bfiq_data)
        bfiq_incorrect_fmt = copy.deepcopy(
            borealis_bfiq_data_sets.borealis_bfiq_data)

    def test_borealis_write_constructor(self):
        """
        Tests BorealisWrite constructor

        Expected behaviour
        ------------------
        Contains file name of the data if given to it.
        """
        writer = pydarn.BorealisWrite("test_rawacf.rawacf.hdf5", rawacf_data)
        self.assertEqual(writer.filename, "test_rawacf.rawacf.hdf5")

    def test_writing_rawacf(self):
        """
        Tests write_rawacf method - writes a rawacf file

        Expected behaviour
        ------------------
        Rawacf file is produced
        """

        writer = pydarn.BorealisWrite("test_rawacf.rawacf.hdf5", rawacf_data)
        writer.write_rawacf()
        # only testing the file is created since it should only be created
        # at the last step after all checks have passed
        # Testing the integrity of the insides of the file will be part of
        # integration testing since we need BorealisRead for that.
        self.assertTrue(os.path.isfile("test_rawacf.rawacf.hdf5"))
        os.remove("test_rawacf.rawacf.hdf5")

    def test_missing_field_rawacf(self):
        """
        Tests write_rawacf method - writes a rawacf structure file for the
        given data

        Expected behaviour
        ------------------
        Raises BorealisFieldMissingError - because the rawacf data is
        missing field num_sequences
        """

        keys = sorted(list(rawacf_missing_field.keys()))
        del rawacf_missing_field[keys[0]]['num_sequences']

        writer = pydarn.BorealisWrite(
            "test_rawacf.rawacf.hdf5", rawacf_missing_field)

        try:
            writer.write_rawacf()
        except pydarn.borealis_exceptions.BorealisFieldMissingError as err:
            self.assertEqual(err.fields, {'num_sequences'})
            self.assertEqual(err.record_name, keys[0])

    def test_extra_field_rawacf(self):
        """
        Tests write_rawacf method - writes a rawacf structure file for the
        given data

        Expected behaviour
        ------------------
        Raises BorealisExtraFieldError because the rawacf data
        has an extra field dummy
        """
        keys = sorted(list(rawacf_extra_field.keys()))
        rawacf_extra_field[keys[0]]['dummy'] = 'dummy'

        writer = pydarn.BorealisWrite(
            "test_rawacf.rawacf.hdf5", rawacf_extra_field)

        try:
            writer.write_rawacf()
        except pydarn.borealis_exceptions.BorealisExtraFieldError as err:
            self.assertEqual(err.fields, {'dummy'})
            self.assertEqual(err.record_name, keys[0])

    def test_incorrect_data_format_rawacf(self):
        """
        Tests write_rawacf method - writes a rawacf structure file for the
        given data

        Expected Behaviour
        -------------------
        Raises BorealisDataFormatTypeError because the rawacf data has the
        wrong type for the scan_start_marker field
        """
        keys = sorted(list(rawacf_incorrect_fmt.keys()))
        rawacf_incorrect_fmt[keys[0]]['scan_start_marker'] = 1

        writer = pydarn.BorealisWrite(
            "test_rawacf.rawacf.hdf5", rawacf_incorrect_fmt)

        try:
            writer.write_rawacf()
        except pydarn.borealis_exceptions.BorealisDataFormatTypeError as err:
            self.assertEqual(
                err.incorrect_params['scan_start_marker'], "<class 'numpy.bool_'>")
            self.assertEqual(err.record_name, keys[0])

    def test_writing_bfiq(self):
        """
        Tests write_bfiq method - writes a bfiq file

        Expected behaviour
        ------------------
        bfiq file is produced
        """
        writer = pydarn.BorealisWrite("test_bfiq.bfiq.hdf5", bfiq_data)
        writer.write_bfiq()
        # only testing the file is created since it should only be created
        # at the last step after all checks have passed
        # Testing the integrity of the insides of the file will be part of
        # integration testing since we need BorealisRead for that.
        self.assertTrue(os.path.isfile("test_bfiq.bfiq.hdf5"))
        os.remove("test_bfiq.bfiq.hdf5")

    def test_missing_field_bfiq(self):
        """
        Tests write_bfiq method - writes a bfiq structure file for the
        given data

        Expected behaviour
        ------------------
        Raises BorealisFieldMissingError - because the bfiq data is
        missing field antenna_arrays_order
        """
        keys = sorted(list(bfiq_missing_field.keys()))
        del bfiq_missing_field[keys[0]]['antenna_arrays_order']
        writer = pydarn.BorealisWrite(
            "test_bfiq.bfiq.hdf5", bfiq_missing_field)

        try:
            writer.write_bfiq()
        except pydarn.borealis_exceptions.BorealisFieldMissingError as err:
            self.assertEqual(err.fields, {'antenna_arrays_order'})
            self.assertEqual(err.record_name, keys[0])

    def test_extra_field_bfiq(self):
        """
        Tests write_bfiq method - writes a bfiq structure file for the
        given data

        Expected behaviour
        ------------------
        Raises BorealisExtraFieldError because the bfiq data
        has an extra field dummy
        """
        keys = sorted(list(bfiq_extra_field.keys()))
        bfiq_extra_field[keys[0]]['dummy'] = 'dummy'
        writer = pydarn.BorealisWrite("test_bfiq.bfiq.hdf5", bfiq_extra_field)

        try:
            writer.write_bfiq()
        except pydarn.borealis_exceptions.BorealisExtraFieldError as err:
            self.assertEqual(err.fields, {'dummy'})
            self.assertEqual(err.record_name, keys[0])

    def test_incorrect_data_format_bfiq(self):
        """
        Tests write_bfiq method - writes a bfiq structure file for the
        given data

        Expected Behaviour
        -------------------
        Raises BorealisDataFormatTypeError because the bfiq data has the
        wrong type for the first_range_rtt field
        """
        keys = sorted(list(bfiq_incorrect_fmt.keys()))
        bfiq_incorrect_fmt[keys[0]]['first_range_rtt'] = 5
        writer = pydarn.BorealisWrite(
            "test_bfiq.bfiq.hdf5", bfiq_incorrect_fmt)

        try:
            writer.write_bfiq()
        except pydarn.borealis_exceptions.BorealisDataFormatTypeError as err:
            self.assertEqual(
                err.incorrect_params['first_range_rtt'], "<class 'numpy.float32'>")
            self.assertEqual(err.record_name, keys[0])


class TestBorealisConvert(unittest.TestCase):
    """
    Tests BorealisConvert class
    """

    def setUp(self):
        rawacf_file_path = borealis_rawacf_file
        bfiq_file_path = borealis_bfiq_file

    def test_borealis_convert_constructor(self):
        """
        Tests BorealisConvert constructor

        Expected behaviour
        ------------------
        Contains file name of the data if given to it.
        """
        converter = pydarn.BorealisConvert(rawacf_file_path)
        self.assertIsInstance(converter.group_names, list)
        self.assertGreater(len(converter.group_names), 0)
        self.assertEqual(converter.origin_filetype, 'rawacf')

    def test_borealis_convert_to_rawacf(self):
        """
        Tests BorealisConvert to rawacf

        Expected behaviour
        ------------------
        write a darn rawacf
        """
        converter = pydarn.BorealisConvert(rawacf_file_path)
        converter.write_to_dmap("rawacf", "test_rawacf.rawacf.dmap")

        # only testing the file is created since it should only be created
        # at the last step after all checks have passed
        # Testing the integrity of the insides of the file will be part of
        # integration testing since we need BorealisRead for that.
        self.assertTrue(os.path.isfile("test_rawacf.rawacf.dmap"))
        os.remove("test_rawacf.rawacf.dmap")

    def test_borealis_convert_to_iqdat(self):
        """
        Tests BorealisConvert to iqdat

        Expected behaviour
        ------------------
        write a darn iqdat
        """
        converter = pydarn.BorealisConvert(bfiq_file_path)
        converter.write_to_dmap("iqdat", "test_iqdat.iqdat.dmap")

        # only testing the file is created since it should only be created
        # at the last step after all checks have passed
        # Testing the integrity of the insides of the file will be part of
        # integration testing since we need BorealisRead for that.
        self.assertTrue(os.path.isfile("test_iqdat.iqdat.dmap"))
        os.remove("test_iqdat.iqdat.dmap")
