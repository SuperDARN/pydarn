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
import 

# import rawacf_data_sets
# import fitacf_data_sets
# import iqdat_data_sets
# import map_data_sets
# import grid_data_sets

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
        rawacf_data = copy.deepcopy(rawacf_data_sets.rawacf_data)
        Borealis = pydarn.BorealisWrite(rawacf_data, "rawacf_test.rawacf")
        self.assertEqual(Borealis.filename, "rawacf_test.rawacf")

    def test_empty_record(self):
        """
        Tests if an empty record is given. This will later be changed for
        real-time implementation.

        Expected behaviour
        ------------------
        Raise DmapDataError if no data is provided to the constructor
        """
        with self.assertRaises(pydarn.dmap_exceptions.DmapDataError):
            pydarn.BorealisWrite([], 'dummy_file.acf')

    def test_incorrect_filename_input_using_write_methods(self):
        """
        Tests if a file name is not provided to any of the write methods

        Expected behaviour
        ------------------
        All should raise a FilenameRequiredError - if no file name is given
        what do we write to ¯\_(ツ)_/¯
        """
        rawacf_data = copy.deepcopy(rawacf_data_sets.rawacf_data)
        dmap_data = pydarn.BorealisWrite(rawacf_data)
        with self.assertRaises(pydarn.dmap_exceptions.FilenameRequiredError):
            dmap_data.write_rawacf()
            dmap_data.write_fitacf()
            dmap_data.write_iqdat()
            dmap_data.write_grid()
            dmap_data.write_map()
            dmap_data.write_dmap()

    def test_BorealisWrite_missing_field_rawacf(self):
        """
        Tests write_rawacf method - writes a rawacf structure file for the
        given data

        Expected behaviour
        ------------------
        Raises SuperBorealisFieldMissingError - because the rawacf data is
        missing field nave
        """
        rawacf_missing_field = copy.deepcopy(rawacf_data_sets.rawacf_data)
        del rawacf_missing_field[2]['nave']

        dmap = pydarn.BorealisWrite(rawacf_missing_field)

        try:
            dmap.write_rawacf("test_rawacf.rawacf")
        except pydarn.superBorealis_exceptions.SuperBorealisFieldMissingError as err:
            self.assertEqual(err.fields, {'nave'})
            self.assertEqual(err.record_number, 2)

    def test_extra_field_rawacf(self):
        """
        Tests write_rawacf method - writes a rawacf structure file for the
        given data

        Expected behaviour
        ------------------
        Raises SuperBorealisExtraFieldError because the rawacf data
        has an extra field dummy
        """
        rawacf_extra_field = copy.deepcopy(rawacf_data_sets.rawacf_data)
        rawacf_extra_field[1]['dummy'] = pydarn.DmapScalar('dummy', 'nothing',
                                                           chr(1), 's')
        dmap = pydarn.BorealisWrite(rawacf_extra_field)

        try:
            dmap.write_rawacf("test_rawacf.rawacf")
        except pydarn.superBorealis_exceptions.SuperBorealisExtraFieldError as err:
            self.assertEqual(err.fields, {'dummy'})
            self.assertEqual(err.record_number, 1)

    def test_incorrect_data_format_rawacf(self):
        """
        Tests write_rawacf method - writes a rawacf structure file for the
        given data

        Expected Behaviour
        -------------------
        Raises SuperBorealisDataFormatTypeError because the rawacf data has the
        wrong type for the scan field
        """
        rawacf_incorrect_fmt = copy.deepcopy(rawacf_data_sets.rawacf_data)
        rawacf_incorrect_fmt[2]['scan'] = \
            rawacf_incorrect_fmt[2]['scan']._replace(data_type_fmt='c')
        dmap = pydarn.BorealisWrite(rawacf_incorrect_fmt)

        try:
            dmap.write_rawacf("test_rawacf.rawacf")
        except pydarn.superBorealis_exceptions.SuperBorealisDataFormatTypeError as err:
            self.assertEqual(err.incorrect_params['scan'], 'h')
            self.assertEqual(err.record_number, 2)

    def test_writing_rawacf(self):
        """
        Tests write_rawacf method - writes a rawacf file

        Expected behaviour
        ------------------
        Rawacf file is produced
        """
        rawacf_data = copy.deepcopy(rawacf_data_sets.rawacf_data)

        dmap = pydarn.BorealisWrite(rawacf_data)

        dmap.write_rawacf("test_rawacf.rawacf")
        # only testing the file is created since it should only be created
        # at the last step after all checks have passed
        # Testing the integrity of the insides of the file will be part of
        # integration testing since we need BorealisRead for that.
        self.assertTrue(os.path.isfile("test_rawacf.rawacf"))
        os.remove("test_rawacf.rawacf")

    def test_writing_iqdat(self):
        """
        Tests write_iqdat method - writes a iqdat file

        Expected behaviour
        ------------------
        iqdat file is produced
        """
        iqdat_data = copy.deepcopy(iqdat_data_sets.iqdat_data)
        dmap = pydarn.BorealisWrite(iqdat_data)

        dmap.write_iqdat("test_iqdat.iqdat")
        self.assertTrue(os.path.isfile("test_iqdat.iqdat"))
        os.remove("test_iqdat.iqdat")

    def test_missing_iqdat_field(self):
        """
        Tests write_iqdat method - writes a iqdat structure file for the
        given data

        Expected behaviour
        ------------------
        Raises SuperBorealisFieldMissingError - because the iqdat data is
        missing field chnnum
        """

        iqdat_missing_field = copy.deepcopy(iqdat_data_sets.iqdat_data)
        del iqdat_missing_field[1]['chnnum']
        dmap = pydarn.BorealisWrite(iqdat_missing_field)

        try:
            dmap.write_iqdat("test_iqdat.iqdat")
        except pydarn.superBorealis_exceptions.SuperBorealisFieldMissingError as err:
            self.assertEqual(err.fields, {'chnnum'})
            self.assertEqual(err.record_number, 1)

    def test_extra_iqdat_field(self):
        """
        Tests write_iqdat method - writes a iqdat structure file for the
        given data

        Expected behaviour
        ------------------
        Raises SuperBorealisExtraFieldError because the iqdat data
        has an extra field dummy
        """
        iqdat_extra_field = copy.deepcopy(iqdat_data_sets.iqdat_data)
        iqdat_extra_field[2]['dummy'] = \
            pydarn.DmapArray('dummy', np.array([1, 2]), chr(1), 'c', 1, [2])
        dmap = pydarn.BorealisWrite(iqdat_extra_field)

        try:
            dmap.write_iqdat("test_iqdat.iqdat")
        except pydarn.superBorealis_exceptions.SuperBorealisExtraFieldError as err:
            self.assertEqual(err.fields, {'dummy'})
            self.assertEqual(err.record_number, 2)

    def test_incorrect_iqdat_data_type(self):
        """
        Tests write_iqdat method - writes a iqdat structure file for the
        given data

        Expected Behaviour
        -------------------
        Raises SuperBorealisDataFormatTypeError because the iqdat data has the
        wrong type for the lagfr field
        """
        iqdat_incorrect_fmt = copy.deepcopy(iqdat_data_sets.iqdat_data)
        iqdat_incorrect_fmt[2]['lagfr'] = \
            iqdat_incorrect_fmt[2]['lagfr']._replace(data_type_fmt='d')
        dmap = pydarn.BorealisWrite(iqdat_incorrect_fmt)

        try:
            dmap.write_iqdat("test_iqdat.iqdat")
        except pydarn.superBorealis_exceptions.SuperBorealisDataFormatTypeError as err:
            self.assertEqual(err.incorrect_params['lagfr'], 'h')
            self.assertEqual(err.record_number, 2)
