# Copyright (C) 2019  SuperBorealis
# Author: Marci Detwiller
"""
This test suite is to test the implementation for the following classes:
    BorealisRead
    BorealisUtilities
    BorealisWrite
Support for the following Borealis file types:
    rawrf
    output_ptrs_iq
    bfiq
    rawacf
And supports conversion to the following SuperBorealis types:
    bfiq -> iqdat
    rawacf -> rawacf
"""

import unittest
import numpy as np
import logging
import collections
import bz2
import os
import copy

import pydarn
import borealis_rawacf_data_sets
import borealis_bfiq_data_sets

pydarn_logger = logging.getLogger('pydarn')

# Test files

borealis_bfiq_file = "../test_files/20190523.0200.00.sas.0.bfiq.hdf5"
borealis_rawacf_file = "../test_files/20190523.0200.00.sas.0.rawacf.hdf5"
#borealis_output_ptrs_iq_file = 
#borealis_rawrf_file =

# Problem files


class TestBorealisRead(unittest.TestCase):
    """
    Testing class for BorealisRead
    """

    def setUp(self):
        pass

    def test_incorrect_path(self):
        """
        Testing BorealisRead constructor with an nonexistent folder.

        Expected behaviour: raise FileNotFoundError
        """
        self.assertRaises(FileNotFoundError, pydarn.BorealisRead,
                          './dog/somefile.rawacf')

    def test_incorrect_file(self):
        """
        Tests if BorealisRead constructor with an non-existent file

        Expected behaviour: raises FileNotFoundError
        """
        self.assertRaises(FileNotFoundError, pydarn.BorealisRead,
                          '../testfiles/somefile.rawacf')

    def test_empty_file(self):
        """
        Tests if BorealisRead constructor with an empty file

        Expected behaviour: raise EmptyFileError
        """
        self.assertRaises(pydarn.dmap_exceptions.EmptyFileError,
                          pydarn.BorealisRead, '../testfiles/empty.rawacf')

    def test_open_rawacf(self):
        """
        Tests BorealisRead constructor on opening a rawacf.
        It should be able to open the file, read it and convert to dictionary

        Checks:
            - group names is a list, greater than length 0
        """
        file_path = borealis_rawacf_file
        reader = pydarn.BorealisRead(file_path)
        self.assertIsInstance(reader.group_names, list)
        self.assertGreater(len(reader.group_names), 0)

    def test_open_bfiq(self):
        """
        Tests BorealisRead constructor on opening a iqdat.
        It should be able to open the file, read it and convert to dictionary

        Checks:
            - group names is a list, greater than length 0
        """
        file_path = borealis_bfiq_file
        reader = pydarn.BorealisRead(file_path)
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
        file_path = borealis_bfiq_file
        dm = pydarn.BorealisRead(file_path)
        records = dm.read_bfiq()
        first_record = records[dm.group_names[0]]
        self.assertIsInstance(records, collections.OrderedDict)
        self.assertIsInstance(first_record, dict)
        self.assertIsInstance(first_record['num_slices'], int)

    def test_read_rawacf(self):
        """
        Test reading records from rawacf.

        Checks:
            - returns correct data structures
            - returns expected values
        """
        file_path = borealis_rawacf_file
        dm = pydarn.BorealisRead(file_path)
        records = dm.read_rawacf()
        first_record = records[dm.group_names[0]]
        self.assertIsInstance(dm_records, collections.OrderedDict)
        self.assertIsInstance(first_record, dict)
        self.assertIsInstance(first_record['num_slices'], int)


class TestBorealisWrite(unittest.TestCase):
    """
    Tests BorealisWrite class
    """
    def setUp(self):
        pass

    def test_borealis_write_constructor(self):
        """
        Tests BorealisWrite constructor

        Expected behaviour
        ------------------
        Contains file name of the data if given to it.
        """
        rawacf_data = copy.deepcopy(borealis_rawacf_data_sets.borealis_rawacf_data)
        writer = pydarn.BorealisWrite(rawacf_data, "test_rawacf.rawacf.hdf5")
        self.assertEqual(writer.filename, "test_rawacf.rawacf.hdf5")

    def test_writing_rawacf(self):
        """
        Tests write_rawacf method - writes a rawacf file

        Expected behaviour
        ------------------
        Rawacf file is produced
        """
        rawacf_data = copy.deepcopy(borealis_rawacf_data_sets.borealis_rawacf_data)

        writer = pydarn.BorealisWrite(rawacf_data, "test_rawacf.rawacf.hdf5")
        writer.write_rawacf()
        # only testing the file is created since it should only be created
        # at the last step after all checks have passed
        # Testing the integrity of the insides of the file will be part of
        # integration testing since we need BorealisRead for that.
        self.assertTrue(os.path.isfile("test_rawacf.rawacf.hdf5"))
        os.remove("test_rawacf.rawacf.hdf5")

    def test_incorrect_filename_input_using_write_methods(self):
        """
        Tests if a file name is not provided to any of the write methods

        Expected behaviour
        ------------------
        All should raise a FilenameRequiredError - if no file name is given
        what do we write to ¯\_(ツ)_/¯
        """
        rawacf_data = copy.deepcopy(borealis_rawacf_data_sets.borealis_rawacf_data)
        writer = pydarn.BorealisWrite(rawacf_data)
        with self.assertRaises(pydarn.dmap_exceptions.FilenameRequiredError):
            writer.write_rawacf()
            writer.write_bfiq()

    def test_BorealisWrite_missing_field_rawacf(self):
        """
        Tests write_rawacf method - writes a rawacf structure file for the
        given data

        Expected behaviour
        ------------------
        Raises BorealisFieldMissingError - because the rawacf data is
        missing field num_sequences
        """
        rawacf_missing_field = copy.deepcopy(borealis_rawacf_data_sets.borealis_rawacf_data)
        keys = sorted(list(rawacf_missing_field.keys()))
        del rawacf_missing_field[keys[0]]['num_sequences']

        writer = pydarn.BorealisWrite(rawacf_missing_field, "test_rawacf.rawacf.hdf5")

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
        rawacf_extra_field = copy.deepcopy(borealis_rawacf_data_sets.borealis_rawacf_data)
        keys = sorted(list(rawacf_extra_field.keys()))
        rawacf_extra_field[keys[0]]['dummy'] = 'dummy'

        writer = pydarn.BorealisWrite(rawacf_extra_field, "test_rawacf.rawacf.hdf5")

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
        rawacf_incorrect_fmt = copy.deepcopy(borealis_rawacf_data_sets.borealis_rawacf_data)
        keys = sorted(list(rawacf_incorrect_fmt.keys()))
        rawacf_incorrect_fmt[keys[0]]['scan_start_marker'] = 1

        writer = pydarn.BorealisWrite(rawacf_incorrect_fmt, "test_rawacf.rawacf.hdf5")

        try:
            writer.write_rawacf()
        except pydarn.borealis_exceptions.BorealisDataFormatTypeError as err:
            self.assertEqual(err.incorrect_params['scan_start_marker'], 'bool')
            self.assertEqual(err.record_name, keys[0])

    def test_writing_bfiq(self):
        """
        Tests write_bfiq method - writes a bfiq file

        Expected behaviour
        ------------------
        bfiq file is produced
        """
        bfiq_data = copy.deepcopy(borealis_bfiq_data_sets.borealis_bfiq_data)

        writer = pydarn.BorealisWrite(bfiq_data, "test_bfiq.bfiq.hdf5")
        writer.write_bfiq()
        # only testing the file is created since it should only be created
        # at the last step after all checks have passed
        # Testing the integrity of the insides of the file will be part of
        # integration testing since we need BorealisRead for that.
        self.assertTrue(os.path.isfile("test_bfiq.bfiq.hdf5"))
        os.remove("test_bfiq.bfiq.hdf5")

    def test_missing_bfiq_field(self):
        """
        Tests write_bfiq method - writes a bfiq structure file for the
        given data

        Expected behaviour
        ------------------
        Raises BorealisFieldMissingError - because the bfiq data is
        missing field antenna_arrays_order
        """
        bfiq_missing_field = copy.deepcopy(borealis_bfiq_data_sets.borealis_bfiq_data)
        keys = sorted(list(bfiq_missing_field.keys()))
        del bfiq_missing_field[keys[0]]['antenna_arrays_order']
        writer = pydarn.BorealisWrite(bfiq_missing_field, "test_bfiq.bfiq.hdf5")

        try:
            writer.write_bfiq()
        except pydarn.borealis_exceptions.BorealisFieldMissingError as err:
            self.assertEqual(err.fields, {'antenna_arrays_order'})
            self.assertEqual(err.record_name, keys[0])

    def test_extra_bfiq_field(self):
        """
        Tests write_bfiq method - writes a bfiq structure file for the
        given data

        Expected behaviour
        ------------------
        Raises BorealisExtraFieldError because the bfiq data
        has an extra field dummy
        """
        bfiq_extra_field = copy.deepcopy(borealis_bfiq_data_sets.borealis_bfiq_data)
        keys = sorted(list(bfiq_extra_field.keys()))
        bfiq_extra_field[keys[0]]['dummy'] = 'dummy'
        writer = pydarn.BorealisWrite(bfiq_extra_field, "test_bfiq.bfiq.hdf5")

        try:
            writer.write_bfiq()
        except pydarn.borealis_exceptions.BorealisExtraFieldError as err:
            self.assertEqual(err.fields, {'dummy'})
            self.assertEqual(err.record_name, keys[0])

    def test_incorrect_bfiq_data_type(self):
        """
        Tests write_bfiq method - writes a bfiq structure file for the
        given data

        Expected Behaviour
        -------------------
        Raises BorealisDataFormatTypeError because the bfiq data has the
        wrong type for the first_range_rtt field
        """
        bfiq_incorrect_fmt = copy.deepcopy(borealis_bfiq_data_sets.borealis_bfiq_data)
        keys = sorted(list(bfiq_incorrect_fmt.keys()))
        bfiq_incorrect_fmt[keys[0]]['first_range_rtt'] = 5
        writer = pydarn.BorealisWrite(bfiq_incorrect_fmt, "test_bfiq.bfiq.hdf5")

        try:
            writer.write_bfiq()
        except pydarn.borealis_exceptions.BorealisDataFormatTypeError as err:
            self.assertEqual(err.incorrect_params['first_range_rtt'], 'np.float32')
            self.assertEqual(err.record_name, keys[0])


class TestBorealisConvert(unittest.TestCase):
    """
    Tests BorealisWrite class
    """
    def setUp(self):
        pass

    def test_borealis_convert_constructor(self):
        """
        Tests BorealisConvert constructor

        Expected behaviour
        ------------------
        Contains file name of the data if given to it.
        """
        file_path = borealis_rawacf_file
        converter = pydarn.BorealisConvert(file_path)
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
        file_path = borealis_rawacf_file
        converter = pydarn.BorealisConvert(file_path)
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
        file_path = borealis_bfiq_file
        converter = pydarn.BorealisConvert(file_path)
        converter.write_to_dmap("iqdat", "test_iqdat.iqdat.dmap")

        # only testing the file is created since it should only be created
        # at the last step after all checks have passed
        # Testing the integrity of the insides of the file will be part of
        # integration testing since we need BorealisRead for that.
        self.assertTrue(os.path.isfile("test_iqdat.iqdat.dmap"))
        os.remove("test_iqdat.iqdat.dmap")
