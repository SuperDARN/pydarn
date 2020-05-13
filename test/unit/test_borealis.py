# Copyright 2019 SuperDARN Canada, University of Saskatchewan
# Author: Marci Detwiller
"""
This test suite is to test the implementation for the following classes:
    BorealisRead
    BorealisWrite
    BorealisConvert
Support for the following Borealis file types:
    rawrf
    antennas_iq
    bfiq
    rawacf
And supports conversion of the following Borealis -> SDARN DMap types:
    bfiq -> iqdat
    rawacf -> rawacf
"""
import collections
import copy
import logging
import numpy as np
import os
import pytest
import random
import tables
import unittest

import pydarn

from collections import OrderedDict

from borealis_rawacf_data_sets import (borealis_array_rawacf_data,
                                       borealis_site_rawacf_data)
from borealis_bfiq_data_sets import (borealis_array_bfiq_data,
                                     borealis_site_bfiq_data)

pydarn_logger = logging.getLogger('pydarn')

# Site Test files v0.5
borealis_site_bfiq_file_v05 = \
    "/home/marci/data/borealis-v05/20200303.2143.00.sas.0.bfiq.hdf5.site"
borealis_site_rawacf_file_v05 = \
    "/home/marci/data/borealis-v05/20200303.2143.00.sas.0.rawacf.hdf5.site"
borealis_site_antennas_iq_file_v05 = \
    "/home/marci/data/borealis-v05/20200303.2143.00.sas.0.antennas_iq.hdf5."\
    "site"
borealis_site_rawrf_file_v05 = ""

# Array Test files v0.5
borealis_array_bfiq_file_v05 = \
    "/home/marci/data/borealis-v05/20200303.2143.00.sas.0.bfiq.hdf5"
borealis_array_rawacf_file_v05 = \
    "/home/marci/data/borealis-v05/20200303.2143.00.sas.0.rawacf.hdf5"
borealis_array_antennas_iq_file_v05 = \
    "/home/marci/data/borealis-v05/20200303.2143.00.sas.0.antennas_iq.hdf5"

# Site Test files v0.4
borealis_site_bfiq_file_v04 = \
    "/home/marci/data/borealis-v04/20200311.1734.00.sas.0.bfiq.hdf5.site"
borealis_site_rawacf_file_v04 = \
    "/home/marci/data/borealis-v04/20200311.1734.00.sas.0.rawacf.hdf5.site"
borealis_site_antennas_iq_file_v04 = \
    "/home/marci/data/borealis-v04/20200311.1734.00.sas.0.antennas_iq.hdf5."\
    "site"
borealis_site_rawrf_file_v04 = ""

# Array Test files v0.4
borealis_array_bfiq_file_v04 = \
    "/home/marci/data/borealis-v04/20200311.1734.00.sas.0.bfiq.hdf5"
borealis_array_rawacf_file_v04 = \
    "/home/marci/data/borealis-v04/20200311.1734.00.sas.0.rawacf.hdf5"
borealis_array_antennas_iq_file_v04 = \
    "/home/marci/data/borealis-v04/20200311.1734.00.sas.0.antennas_iq.hdf5"

# Problem files TODO
borealis_site_extra_field_file = ""
borealis_site_missing_field_file = ""
borealis_site_incorrect_data_format_file = ""

borealis_array_extra_field_file = ""
borealis_array_missing_field_file = ""
borealis_array_incorrect_data_format_file = ""
borealis_array_num_records_error_file = ""
borealis_empty_file = "../test_files/empty.rawacf"


@pytest.mark.skip
class TestBorealisRead_v04(unittest.TestCase):
    """
    Testing class for BorealisSiteRead
    """

    def setUp(self):
        self.rawacf_site_file_path = borealis_site_rawacf_file_v04
        self.bfiq_site_file_path = borealis_site_bfiq_file_v04
        self.antennas_site_file_path = borealis_site_antennas_iq_file_v04
        self.rawrf_site_file_path = borealis_site_rawrf_file_v04
        self.nonexistent_dir_path = './dog/somefile.rawacf'
        self.nonexistent_file_path = '../test_files/somefile.rawacf'
        self.empty_file_path = borealis_empty_file
        self.rawacf_array_file_path = borealis_array_rawacf_file_v04
        self.bfiq_array_file_path = borealis_array_bfiq_file_v04
        self.antennas_array_file_path = borealis_array_antennas_iq_file_v04

    def test_read_site_bfiq(self):
        """
        Test reading records from bfiq.

        Checks:
            - returns correct data structures, both records and arrays
                (restructuring happens internally)
            - returns expected values
        """
        dm = pydarn.BorealisRead(self.bfiq_site_file_path, 'bfiq', 'site')
        records = dm.records
        first_record = records[dm.record_names[0]]
        self.assertIsInstance(records, collections.OrderedDict)
        self.assertIsInstance(first_record, dict)
        self.assertIsInstance(first_record['num_slices'], np.int64)

        arrays = dm.arrays
        self.assertIsInstance(arrays, dict)
        self.assertIsInstance(arrays['num_slices'], np.ndarray)
        self.assertIsInstance(arrays['num_slices'][0], np.int64)
        del dm, records, arrays

    def test_read_site_rawacf(self):
        """
        Test reading records from rawacf.

        Checks:
            - returns correct data structures, both records and arrays
                (restructuring happens internally)
            - returns expected values
        """
        dm = pydarn.BorealisRead(self.rawacf_site_file_path, 'rawacf',
                                 'site')
        records = dm.records
        first_record = records[dm.record_names[0]]
        self.assertIsInstance(records, collections.OrderedDict)
        self.assertIsInstance(first_record, dict)
        self.assertIsInstance(first_record['num_slices'], np.int64)

        arrays = dm.arrays
        self.assertIsInstance(arrays, dict)
        self.assertIsInstance(arrays['num_slices'], np.ndarray)
        self.assertIsInstance(arrays['num_slices'][0], np.int64)
        del dm, records, arrays

    def test_read_site_antennas_iq(self):
        """
        Test reading records from antennas_iq.

        Checks:
            - returns correct data structures, both records and arrays
                (restructuring happens internally)
            - returns expected values
        """
        dm = pydarn.BorealisRead(self.antennas_site_file_path,
                                 'antennas_iq', 'site')
        records = dm.records
        first_record = records[dm.record_names[0]]
        self.assertIsInstance(records, collections.OrderedDict)
        self.assertIsInstance(first_record, dict)
        self.assertIsInstance(first_record['num_slices'], np.int64)

        arrays = dm.arrays
        self.assertIsInstance(arrays, dict)
        self.assertIsInstance(arrays['num_slices'], np.ndarray)
        self.assertIsInstance(arrays['num_slices'][0], np.int64)
        del dm, records, arrays

    # TODO add rawrf file for test
    # def test_read_site_rawrf(self):
    #     """
    #     Test reading records from antennas_iq.

    #     Checks:
    #         - returns correct data structures
    #         - returns expected values
    #     """
    #     dm = pydarn.BorealisSiteRead(self.rawrf_site_file_path, 'rawrf',
    #                                  'site')
    #     records = dm.records
    #     first_record = records[dm.record_names[0]]
    #     self.assertIsInstance(records, collections.OrderedDict)
    #     self.assertIsInstance(first_record, dict)
    #     self.assertIsInstance(first_record['num_slices'], np.int64)

    def test_read_array_bfiq(self):
        """
        Test reading records from bfiq.

        Checks:
            - returns correct data structures, both records and arrays
                (restructuring happens internally)
            - returns expected values
        """
        dm = pydarn.BorealisRead(self.bfiq_array_file_path, 'bfiq', 'array')
        arrays = dm.arrays
        self.assertIsInstance(arrays, dict)
        self.assertIsInstance(arrays['num_slices'], np.ndarray)
        self.assertIsInstance(arrays['num_slices'][0], np.int64)

        records = dm.records
        first_record = records[dm.record_names[0]]
        self.assertIsInstance(records, collections.OrderedDict)
        self.assertIsInstance(first_record, dict)
        self.assertIsInstance(first_record['num_slices'], np.int64)
        del dm, records, arrays

    def test_read_array_rawacf(self):
        """
        Test reading records from rawacf.

        Checks:
            - returns correct data structures, both records and arrays
                (restructuring happens internally)
            - returns expected values
        """
        dm = pydarn.BorealisRead(self.rawacf_array_file_path, 'rawacf',
                                 'array')
        arrays = dm.arrays
        self.assertIsInstance(arrays, dict)
        self.assertIsInstance(arrays['num_slices'], np.ndarray)
        self.assertIsInstance(arrays['num_slices'][0], np.int64)

        records = dm.records
        first_record = records[dm.record_names[0]]
        self.assertIsInstance(records, collections.OrderedDict)
        self.assertIsInstance(first_record, dict)
        self.assertIsInstance(first_record['num_slices'], np.int64)
        del dm, records, arrays

    def test_read_array_antennas_iq(self):
        """
        Test reading records from bfiq.

        Checks:
            - returns correct data structures, both records and arrays
                (restructuring happens internally)
            - returns expected values
        """
        dm = pydarn.BorealisRead(self.antennas_array_file_path,
                                 'antennas_iq', 'array')
        arrays = dm.arrays
        self.assertIsInstance(arrays, dict)
        self.assertIsInstance(arrays['num_slices'], np.ndarray)
        self.assertIsInstance(arrays['num_slices'][0], np.int64)

        records = dm.records
        first_record = records[dm.record_names[0]]
        self.assertIsInstance(records, collections.OrderedDict)
        self.assertIsInstance(first_record, dict)
        self.assertIsInstance(first_record['num_slices'], np.int64)
        del dm, records, arrays

    def test_return_reader(self):
        """
        Test the internal BorealisRead return_reader function which should
        be able to determine which structure of file to use
        if none is provided.
        """
        site_reader = pydarn.BorealisRead(self.bfiq_site_file_path, 'bfiq')
        record_data = site_reader.records
        random_key = random.choice(list(record_data.keys()))
        self.assertIsInstance(record_data[random_key]['num_slices'], np.int64)

        array_reader = pydarn.BorealisRead(self.bfiq_array_file_path, 'bfiq')
        array_data = array_reader.arrays
        self.assertIsInstance(array_data['num_slices'], np.ndarray)

    # READ FAILURE TESTS

    def test_incorrect_path(self):
        """
        Testing BorealisSiteRead and BorealisArrayRead constructor with
        a non-existent folder.

        Expected behaviour: raise OSError
        """
        self.assertRaises(OSError, pydarn.BorealisRead,
                          self.nonexistent_dir_path, 'rawacf', 'site')
        self.assertRaises(OSError, pydarn.BorealisRead,
                          self.nonexistent_dir_path, 'rawacf', 'array')

    def test_incorrect_file(self):
        """
        Tests if BorealisSiteRead and BorealisArrayRead constructor with
        a non-existent file

        Expected behaviour: raises OSError
        """
        self.assertRaises(OSError, pydarn.BorealisRead,
                          self.nonexistent_file_path, 'rawacf', 'site')
        self.assertRaises(OSError, pydarn.BorealisRead,
                          self.nonexistent_file_path, 'rawacf', 'array')

    def test_empty_file(self):
        """
        Tests if BorealisSiteRead and BorealisArrayRead constructor with
        an empty file

        Expected behaviour: raise OSError, unable to open
            (file signature not found)
            or raises HDF5ExtError (not an HDF5 file)
        """
        self.assertRaises(OSError,
                          pydarn.BorealisRead, self.empty_file_path, 'rawacf',
                          'site')
        HDF5ExtError = tables.exceptions.HDF5ExtError
        self.assertRaises((OSError, HDF5ExtError),
                          pydarn.BorealisRead, self.empty_file_path, 'rawacf',
                          'array')

    def test_wrong_borealis_filetype(self):
        """
        Provide the wrong filetype.
        """
        wrong_filetype_exceptions = \
            (pydarn.borealis_exceptions.BorealisExtraFieldError,
             pydarn.borealis_exceptions.BorealisFieldMissingError,
             pydarn.borealis_exceptions.BorealisDataFormatTypeError)
        self.assertRaises(wrong_filetype_exceptions, pydarn.BorealisRead,
                          self.bfiq_site_file_path, 'antennas_iq', 'site')

    def test_wrong_borealis_file_structure(self):
        """
        Provide the wrong file structure.
        """
        wrong_file_structure_exceptions = \
            (pydarn.borealis_exceptions.BorealisStructureError)
        self.assertRaises(wrong_file_structure_exceptions, pydarn.BorealisRead,
                          self.bfiq_site_file_path, 'bfiq', 'array')
        self.assertRaises(wrong_file_structure_exceptions, pydarn.BorealisRead,
                          self.bfiq_array_file_path, 'bfiq', 'site')


@pytest.mark.skip
class TestBorealisRead_v05(TestBorealisRead_v04):
    """
    Testing class for BorealisSiteRead
    """

    def setUp(self):
        self.rawacf_site_file_path = borealis_site_rawacf_file_v05
        self.bfiq_site_file_path = borealis_site_bfiq_file_v05
        self.antennas_site_file_path = borealis_site_antennas_iq_file_v05
        self.rawrf_site_file_path = borealis_site_rawrf_file_v05
        self.nonexistent_dir_path = './dog/somefile.rawacf'
        self.nonexistent_file_path = '../test_files/somefile.rawacf'
        self.empty_file_path = borealis_empty_file
        self.rawacf_array_file_path = borealis_array_rawacf_file_v05
        self.bfiq_array_file_path = borealis_array_bfiq_file_v05
        self.antennas_array_file_path = borealis_array_antennas_iq_file_v05


@pytest.mark.skip
class TestBorealisWrite(unittest.TestCase):
    """
    Tests BorealisWrite class
    """

    def setUp(self):
        self.rawacf_site_data = copy.deepcopy(
            borealis_site_rawacf_data)
        self.rawacf_site_missing_field = copy.deepcopy(
            borealis_site_rawacf_data)
        self.rawacf_site_extra_field = copy.deepcopy(
            borealis_site_rawacf_data)
        self.rawacf_site_incorrect_fmt = copy.deepcopy(
            borealis_site_rawacf_data)
        self.bfiq_site_data = copy.deepcopy(
            borealis_site_bfiq_data)
        self.bfiq_site_missing_field = copy.deepcopy(
            borealis_site_bfiq_data)
        self.bfiq_site_extra_field = copy.deepcopy(
            borealis_site_bfiq_data)
        self.bfiq_site_incorrect_fmt = copy.deepcopy(
            borealis_site_bfiq_data)

        self.rawacf_array_data = copy.deepcopy(
            borealis_array_rawacf_data)
        self.rawacf_array_missing_field = copy.deepcopy(
            borealis_array_rawacf_data)
        self.rawacf_array_extra_field = copy.deepcopy(
            borealis_array_rawacf_data)
        self.rawacf_array_incorrect_fmt = copy.deepcopy(
            borealis_array_rawacf_data)
        self.bfiq_array_data = copy.deepcopy(
            borealis_array_bfiq_data)
        self.bfiq_array_missing_field = copy.deepcopy(
            borealis_array_bfiq_data)
        self.bfiq_array_extra_field = copy.deepcopy(
            borealis_array_bfiq_data)
        self.bfiq_array_incorrect_fmt = copy.deepcopy(
            borealis_array_bfiq_data)

    # Read/write tests to check input vs output
    def check_dictionaries_are_same(self, dict1, dict2):

        self.assertEqual(sorted(list(dict1.keys())),
                         sorted(list(dict2.keys())))
        for key1, value1 in dict1.items():
            if isinstance(value1, dict) or isinstance(value1, OrderedDict):
                self.check_dictionaries_are_same(value1, dict2[key1])
            elif isinstance(value1, np.ndarray):
                self.assertTrue((value1 == dict2[key1]).all())
            else:
                self.assertEqual(value1, dict2[key1])

        return True

    def test_writing_site_rawacf(self):
        """
        Tests write_rawacf method - writes a rawacf file

        Expected behaviour
        ------------------
        Rawacf file is produced
        """
        test_file = "./test_rawacf.rawacf.hdf5"
        pydarn.BorealisWrite(test_file, self.rawacf_site_data,
                             'rawacf', 'site')
        # only testing the file is created since it should only be created
        # at the last step after all checks have passed
        # Testing the integrity of the insides of the file will be part of
        # integration testing since we need BorealisSiteRead for that.
        self.assertTrue(os.path.isfile(test_file))
        reader = pydarn.BorealisRead(test_file, 'rawacf', 'site')
        records = reader.records
        dictionaries_are_same =\
            self.check_dictionaries_are_same(records, self.rawacf_site_data)
        self.assertTrue(dictionaries_are_same)
        os.remove(test_file)

    def test_missing_field_site_rawacf(self):
        """
        Tests write_rawacf method - writes a rawacf structure file for the
        given data

        Expected behaviour
        ------------------
        Raises BorealisFieldMissingError - because the rawacf data is
        missing field num_sequences
        """

        keys = sorted(list(self.rawacf_site_missing_field.keys()))
        del self.rawacf_site_missing_field[keys[0]]['num_sequences']

        try:
            pydarn.BorealisWrite("test_rawacf.rawacf.hdf5",
                                 self.rawacf_site_missing_field,
                                 'rawacf', 'site')
        except pydarn.borealis_exceptions.BorealisFieldMissingError as err:
            self.assertEqual(err.fields, {'num_sequences'})
            self.assertEqual(err.record_name, keys[0])

    def test_extra_field_site_rawacf(self):
        """
        Tests write_rawacf method - writes a rawacf structure file for the
        given data

        Expected behaviour
        ------------------
        Raises BorealisExtraFieldError because the rawacf data
        has an extra field dummy
        """
        keys = sorted(list(self.rawacf_site_extra_field.keys()))
        self.rawacf_site_extra_field[keys[0]]['dummy'] = 'dummy'
        try:
            pydarn.BorealisWrite("test_rawacf.rawacf.hdf5",
                                 self.rawacf_site_extra_field,
                                 'rawacf', 'site')
        except pydarn.borealis_exceptions.BorealisExtraFieldError as err:
            self.assertEqual(err.fields, {'dummy'})
            self.assertEqual(err.record_name, keys[0])

    def test_incorrect_data_format_site_rawacf(self):
        """
        Tests write_rawacf method - writes a rawacf structure file for the
        given data

        Expected Behaviour
        -------------------
        Raises BorealisDataFormatTypeError because the rawacf data has the
        wrong type for the scan_start_marker field
        """
        keys = sorted(list(self.rawacf_site_incorrect_fmt.keys()))
        self.rawacf_site_incorrect_fmt[keys[0]]['scan_start_marker'] = 1

        try:
            pydarn.BorealisWrite("test_rawacf.rawacf.hdf5",
                                 self.rawacf_site_incorrect_fmt,
                                 'rawacf', 'site')
        except pydarn.borealis_exceptions.BorealisDataFormatTypeError as err:
            self.assertEqual(
                err.incorrect_types['scan_start_marker'],
                "<class 'numpy.bool_'>")
            self.assertEqual(err.record_name, keys[0])

    def test_writing_site_bfiq(self):
        """
        Tests write_bfiq method - writes a bfiq file

        Expected behaviour
        ------------------
        bfiq file is produced
        """
        test_file = "./test_bfiq.bfiq.hdf5"
        pydarn.BorealisWrite(test_file, self.bfiq_site_data, 'bfiq', 'site')
        # only testing the file is created since it should only be created
        # at the last step after all checks have passed
        # Testing the integrity of the insides of the file will be part of
        # integration testing since we need BorealisSiteRead for that.
        self.assertTrue(os.path.isfile(test_file))
        reader = pydarn.BorealisRead(test_file, 'bfiq', 'site')
        records = reader.records
        dictionaries_are_same = \
            self.check_dictionaries_are_same(records, self.bfiq_site_data)
        self.assertTrue(dictionaries_are_same)
        os.remove(test_file)

    def test_missing_field_site_bfiq(self):
        """
        Tests write_bfiq method - writes a bfiq structure file for the
        given data

        Expected behaviour
        ------------------
        Raises BorealisFieldMissingError - because the bfiq data is
        missing field antenna_arrays_order
        """
        keys = sorted(list(self.bfiq_site_missing_field.keys()))
        del self.bfiq_site_missing_field[keys[0]]['antenna_arrays_order']

        try:
            _ = pydarn.BorealisWrite("test_bfiq.bfiq.hdf5",
                                     self.bfiq_site_missing_field,
                                     'bfiq', 'site')
        except pydarn.borealis_exceptions.BorealisFieldMissingError as err:
            self.assertEqual(err.fields, {'antenna_arrays_order'})
            self.assertEqual(err.record_name, keys[0])

    def test_extra_field_site_bfiq(self):
        """
        Tests write_bfiq method - writes a bfiq structure file for the
        given data

        Expected behaviour
        ------------------
        Raises BorealisExtraFieldError because the bfiq data
        has an extra field dummy
        """
        keys = sorted(list(self.bfiq_site_extra_field.keys()))
        self.bfiq_site_extra_field[keys[0]]['dummy'] = 'dummy'

        try:
            _ = pydarn.BorealisWrite("test_bfiq.bfiq.hdf5",
                                     self.bfiq_site_extra_field,
                                     'bfiq', 'site')
        except pydarn.borealis_exceptions.BorealisExtraFieldError as err:
            self.assertEqual(err.fields, {'dummy'})
            self.assertEqual(err.record_name, keys[0])

    def test_incorrect_data_format_site_bfiq(self):
        """
        Tests write_bfiq method - writes a bfiq structure file for the
        given data

        Expected Behaviour
        -------------------
        Raises BorealisDataFormatTypeError because the bfiq data has the
        wrong type for the first_range_rtt field
        """
        keys = sorted(list(self.bfiq_site_incorrect_fmt.keys()))
        self.bfiq_site_incorrect_fmt[keys[0]]['first_range_rtt'] = 5

        try:
            _ = pydarn.BorealisWrite("test_bfiq.bfiq.hdf5",
                                     self.bfiq_site_incorrect_fmt,
                                     'bfiq', 'site')
        except pydarn.borealis_exceptions.BorealisDataFormatTypeError as err:
            self.assertEqual(
                err.incorrect_types['first_range_rtt'],
                "<class 'numpy.float32'>")
            self.assertEqual(err.record_name, keys[0])

    def test_writing_array_rawacf(self):
        """
        Tests write_rawacf method - writes a rawacf file

        Expected behaviour
        ------------------
        Rawacf file is produced
        """
        test_file = "test_rawacf.rawacf.hdf5"
        _ = pydarn.BorealisWrite(test_file,
                                 self.rawacf_array_data, 'rawacf',
                                 'array')
        self.assertTrue(os.path.isfile(test_file))
        reader = pydarn.BorealisRead(test_file, 'rawacf', 'array')
        data = reader.arrays
        dictionaries_are_same =\
            self.check_dictionaries_are_same(data, self.rawacf_array_data)
        self.assertTrue(dictionaries_are_same)
        os.remove(test_file)

    def test_missing_field_array_rawacf(self):
        """
        Tests write_rawacf method - writes a rawacf structure file for the
        given data

        Expected behaviour
        ------------------
        Raises BorealisFieldMissingError - because the rawacf data is
        missing field num_sequences
        """

        del self.rawacf_array_missing_field['num_sequences']

        try:
            _ = pydarn.BorealisWrite("test_rawacf.rawacf.hdf5",
                                     self.rawacf_array_missing_field,
                                     'rawacf', 'array')
        except pydarn.borealis_exceptions.BorealisFieldMissingError as err:
            self.assertEqual(err.fields, {'num_sequences'})

    def test_extra_field_array_rawacf(self):
        """
        Tests write_rawacf method - writes a rawacf structure file for the
        given data

        Expected behaviour
        ------------------
        Raises BorealisExtraFieldError because the rawacf data
        has an extra field dummy
        """
        self.rawacf_array_extra_field['dummy'] = 'dummy'
        try:
            _ = pydarn.BorealisWrite("test_rawacf.rawacf.hdf5",
                                     self.rawacf_array_extra_field,
                                     'rawacf', 'array')
        except pydarn.borealis_exceptions.BorealisExtraFieldError as err:
            self.assertEqual(err.fields, {'dummy'})

    def test_incorrect_data_format_array_rawacf(self):
        """
        Tests write_rawacf method - writes a rawacf structure file for the
        given data

        Expected Behaviour
        -------------------
        Raises BorealisDataFormatTypeError because the rawacf data has the
        wrong type for the scan_start_marker field
        """
        num_records =\
            self.rawacf_array_incorrect_fmt['scan_start_marker'].shape[0]
        self.rawacf_array_incorrect_fmt['scan_start_marker'] = \
            np.array([1] * num_records)

        try:
            _ = pydarn.BorealisWrite("test_rawacf.rawacf.hdf5",
                                     self.rawacf_array_incorrect_fmt,
                                     'rawacf', 'array')
        except pydarn.borealis_exceptions.BorealisDataFormatTypeError as err:
            self.assertEqual(err.incorrect_types['scan_start_marker'],
                             "np.ndarray of <class 'numpy.bool_'>")

    def test_writing_array_bfiq(self):
        """
        Tests write_bfiq method - writes a bfiq file

        Expected behaviour
        ------------------
        bfiq file is produced
        """
        test_file = "test_bfiq.bfiq.hdf5"
        _ = pydarn.BorealisWrite(test_file, self.bfiq_array_data,
                                 'bfiq', 'array')
        self.assertTrue(os.path.isfile(test_file))
        reader = pydarn.BorealisRead(test_file, 'bfiq', 'array')
        data = reader.arrays
        dictionaries_are_same = \
            self.check_dictionaries_are_same(data,
                                             self.bfiq_array_data)
        self.assertTrue(dictionaries_are_same)
        os.remove(test_file)

    def test_missing_field_array_bfiq(self):
        """
        Tests write_bfiq method - writes a bfiq structure file for the
        given data

        Expected behaviour
        ------------------
        Raises BorealisFieldMissingError - because the bfiq data is
        missing field antenna_arrays_order
        """
        del self.bfiq_array_missing_field['antenna_arrays_order']

        try:
            _ = pydarn.BorealisWrite("test_bfiq.bfiq.hdf5",
                                     self.bfiq_array_missing_field,
                                     'bfiq', 'array')
        except pydarn.borealis_exceptions.BorealisFieldMissingError as err:
            self.assertEqual(err.fields, {'antenna_arrays_order'})

    def test_extra_field_array_bfiq(self):
        """
        Tests write_bfiq method - writes a bfiq structure file for the
        given data

        Expected behaviour
        ------------------
        Raises BorealisExtraFieldError because the bfiq data
        has an extra field dummy
        """
        self.bfiq_array_extra_field['dummy'] = 'dummy'

        try:
            _ = pydarn.BorealisWrite("test_bfiq.bfiq.hdf5",
                                     self.bfiq_array_extra_field,
                                     'bfiq', 'array')
        except pydarn.borealis_exceptions.BorealisExtraFieldError as err:
            self.assertEqual(err.fields, {'dummy'})

    def test_incorrect_data_format_array_bfiq(self):
        """
        Tests write_bfiq method - writes a bfiq structure file for the
        given data

        Expected Behaviour
        -------------------
        Raises BorealisDataFormatTypeError because the bfiq data has the
        wrong type for the first_range_rtt field
        """
        self.bfiq_array_incorrect_fmt['first_range_rtt'] = 5

        try:
            _ = pydarn.BorealisWrite("test_bfiq.bfiq.hdf5",
                                     self.bfiq_array_incorrect_fmt,
                                     'bfiq', 'array')
        except pydarn.borealis_exceptions.BorealisDataFormatTypeError as err:
            self.assertEqual(
                err.incorrect_types['first_range_rtt'],
                "<class 'numpy.float32'>")

    # # WRITE FAILURE TESTS

    def test_wrong_borealis_filetype(self):
        """
        Provide the wrong filetype.
        """
        wrong_filetype_exceptions = \
            (pydarn.borealis_exceptions.BorealisExtraFieldError,
             pydarn.borealis_exceptions.BorealisFieldMissingError,
             pydarn.borealis_exceptions.BorealisDataFormatTypeError)
        self.assertRaises(wrong_filetype_exceptions, pydarn.BorealisWrite,
                          'test_write_borealis_file.bfiq.hdf5',
                          self.bfiq_site_data, 'antennas_iq', 'site')

    def test_wrong_borealis_file_structure(self):
        """
        Provide the wrong file structure.
        """
        self.assertRaises(pydarn.borealis_exceptions.BorealisStructureError,
                          pydarn.BorealisWrite,
                          'test_write_borealis_file.bfiq.hdf5',
                          self.bfiq_site_data,  'rawacf', 'array')
        self.assertRaises(pydarn.borealis_exceptions.BorealisStructureError,
                          pydarn.BorealisWrite,
                          'test_write_borealis_file.bfiq.hdf5',
                          self.bfiq_array_data, 'rawacf', 'site')


@pytest.mark.skip
class TestBorealisConvert(unittest.TestCase):
    """
    Tests BorealisConvert class
    """

    def setUp(self):
        self.rawacf_array_data = copy.deepcopy(borealis_array_rawacf_data)
        self.bfiq_array_data = copy.deepcopy(borealis_array_bfiq_data)

        # write some v0.4 data
        self.bfiq_test_file = "test_bfiq.bfiq.hdf5"
        _ = pydarn.BorealisWrite(self.bfiq_test_file,
                                 self.bfiq_array_data, 'bfiq', 'array')
        self.rawacf_test_file = "test_rawacf.rawacf.hdf5"
        _ = pydarn.BorealisWrite(self.rawacf_test_file,
                                 self.rawacf_array_data,
                                 'rawacf', 'array')

        # get v0.5 data from file
        self.bfiqv05_test_file = borealis_site_bfiq_file_v05
        self.rawacfv05_test_file = borealis_site_rawacf_file_v05

    def test_borealis_convert_to_rawacfv04(self):
        """
        Tests BorealisConvert to rawacf

        Expected behaviour
        ------------------
        write a SDARN DMap rawacf
        """
        _ = pydarn.BorealisConvert(self.rawacf_test_file, "rawacf",
                                   "test_rawacf.rawacf.dmap",
                                   borealis_slice_id=0,
                                   borealis_file_structure='array')
        self.assertTrue(os.path.isfile("test_rawacf.rawacf.dmap"))
        os.remove("test_rawacf.rawacf.dmap")

    def test_borealis_convert_to_iqdatv04(self):
        """
        Tests BorealisConvert to iqdat

        Expected behaviour
        ------------------
        write a SDARN DMap iqdat
        """

        _ = pydarn.BorealisConvert(self.bfiq_test_file, "bfiq",
                                   "test_bfiq.bfiq.dmap",
                                   borealis_slice_id=0,
                                   borealis_file_structure='array')
        self.assertTrue(os.path.isfile("test_bfiq.bfiq.dmap"))
        os.remove("test_bfiq.bfiq.dmap")

    def test_borealis_convert_to_rawacfv05(self):
        _ = pydarn.BorealisConvert(self.rawacfv05_test_file, "rawacf",
                                   "test_rawacf.rawacf.dmap",
                                   borealis_file_structure='site')
        self.assertTrue(os.path.isfile("test_rawacf.rawacf.dmap"))
        os.remove("test_rawacf.rawacf.dmap")

    def test_borealis_convert_to_iqdatv05(self):
        """
        Tests BorealisConvert to iqdat

        Expected behaviour
        ------------------
        write a SDARN DMap iqdat
        """
        _ = pydarn.BorealisConvert(self.bfiqv05_test_file, "bfiq",
                                   "test_bfiq.bfiq.dmap",
                                   borealis_file_structure='site')
        self.assertTrue(os.path.isfile("test_bfiq.bfiq.dmap"))
        os.remove("test_bfiq.bfiq.dmap")


if __name__ == '__main__':
    """
    Runs the above class in a unittest system.
    """
    pydarn_logger.info("Starting Borealis unit testing on v0.5 files")

    unittest.main()
