# Copyright (C) 2019 SuperDARN Canada, University of Saskatchewan
# Author: Marina Schmidt
"""
This test suite is to test the implementation for the following classes:
    SDarnRead
    DarnUtilities
    SDarnWrite
Support for the following SuperDARN file types:
    iqdat
    rawacf
    fitacf
    grid
    map
"""

import bz2
import copy
import collections
import logging
import numpy as np
import os
import pytest
import unittest

import pydarn

import map_data_sets
import grid_data_sets
import fitacf_data_sets
import iqdat_data_sets
import rawacf_data_sets

pydarn_logger = logging.getLogger('pydarn')

# Test files
rawacf_stream = "../testfiles/20170410.1801.00.sas.stream.rawacf.bz2"
rawacf_file = "../testfiles/20170410.1801.00.sas.rawacf"
fitacf_file = "../testfiles/20160331.2201.00.mcm.a.fitacf"
map_file = "../testfiles/20170114.map"
iqdat_file = "../testfiles/20160316.1945.01.rkn.iqdat"
grid_file = "../testfiles/20180220.C0.rkn.grid"
# Black listed files
corrupt_file1 = "../testfiles/20070117.1001.00.han.rawacf"
corrupt_file2 = "../testfiles/20090320.1601.00.pgr.rawacf"


@pytest.mark.skip
class TestSDarnRead(unittest.TestCase):
    """
    Testing class for SDarnRead class
    """
    def setUp(self):
        pass

    """
    Testing SDarnRead constructor
    """
    def test_incorrect_path(self):
        """
        Testing SDarnRead constructor with an nonexistent folder.

        Expected behaviour: raise FileNotFoundError
        """
        self.assertRaises(FileNotFoundError, pydarn.SDarnRead,
                          './dog/somefile.rawacf')

    def test_incorrect_file(self):
        """
        Tests if SDarnRead constructor with an non-existent file

        Expected behaviour: raises FileNotFoundError
        """
        self.assertRaises(FileNotFoundError, pydarn.SDarnRead,
                          '../testfiles/somefile.rawacf')

    def test_empty_file(self):
        """
        Tests if SDarnRead constructor with an empty file

        Expected behaviour: raise EmptyFileError
        """
        self.assertRaises(pydarn.dmap_exceptions.EmptyFileError,
                          pydarn.SDarnRead, '../testfiles/empty.rawacf')

    def test_open_rawacf(self):
        """
        Tests SDarnRead constructor on opening a rawacf.
        It should be able to open the file, read it and convert to bytearray.

        Checks:
            - bytearray instance is created from reading in the file
            - bytearray is not empty
        """
        file_path = rawacf_file
        dm = pydarn.SDarnRead(file_path)
        self.assertIsInstance(dm.dmap_bytearr, bytearray)
        self.assertGreater(dm.dmap_end_bytes, 0)

    def test_open_fitacf(self):
        """
        Tests SDarnRead constructor on opening a fitacf.
        It should be able to open the file, read it and convert to bytearray.

        Checks:
            - bytearray instance is created from reading in the file
            - bytearray is not empty
        """
        file_path = fitacf_file
        dm = pydarn.SDarnRead(file_path)
        self.assertIsInstance(dm.dmap_bytearr, bytearray)
        self.assertGreater(dm.dmap_end_bytes, 0)

    def test_open_map(self):
        """
        Tests SDarnRead constructor on opening a map.
        It should be able to open the file, read it and convert to bytearray.

        Checks:
            - bytearray instance is created from reading in the file
            - bytearray is not empty
        """
        file_path = map_file
        dm = pydarn.SDarnRead(file_path)
        self.assertIsInstance(dm.dmap_bytearr, bytearray)
        self.assertGreater(dm.dmap_end_bytes, 0)

    def test_open_grid(self):
        """
        Tests SDarnRead constructor on opening a grid.
        It should be able to open the file, read it and convert to bytearray.

        Checks:
            - bytearray instance is created from reading in the file
            - bytearray is not empty
        """
        file_path = grid_file
        dm = pydarn.SDarnRead(file_path)
        self.assertIsInstance(dm.dmap_bytearr, bytearray)
        self.assertGreater(dm.dmap_end_bytes, 0)

    def test_open_iqdat(self):
        """
        Tests SDarnRead constructor on opening a iqdat.
        It should be able to open the file, read it and convert to bytearray.

        Checks:
            - bytearray instance is created from reading in the file
            - bytearray is not empty
        """
        file_path = iqdat_file
        dm = pydarn.SDarnRead(file_path)
        self.assertIsInstance(dm.dmap_bytearr, bytearray)
        self.assertGreater(dm.dmap_end_bytes, 0)

    # TODO: potential issue if files change and the values are not the same :/
    def test_read_iqdat(self):
        """
        Test reading records from iqdat.

        Checks:
            - returns correct data structures
            - returns expected values
        """
        file_path = iqdat_file
        dm = pydarn.SDarnRead(file_path)
        _ = dm.read_iqdat()
        dm_records = dm.get_dmap_records
        self.assertIsInstance(dm_records, collections.deque)
        self.assertIsInstance(dm_records[0], collections.OrderedDict)
        self.assertIsInstance(dm_records[0]['rxrise'], pydarn.DmapScalar)
        self.assertIsInstance(dm_records[3]['tsc'], pydarn.DmapArray)
        self.assertIsInstance(dm_records[5]['mppul'].value, int)
        self.assertIsInstance(dm_records[6]['tnoise'].value, np.ndarray)
        self.assertEqual(dm_records[7]['channel'].value, 0)
        self.assertEqual(dm_records[10]['data'].dimension, 1)

    def test_read_rawacf(self):
        """
        Test reading records from rawacf.

        Checks:
            - returns correct data structures
            - returns expected values
        """
        file_path = rawacf_file
        dm = pydarn.SDarnRead(file_path)
        dm_records = dm.read_rawacf()
        dm_records = dm.get_dmap_records
        self.assertIsInstance(dm_records, collections.deque)
        self.assertIsInstance(dm_records[0], collections.OrderedDict)
        self.assertIsInstance(dm_records[4]['channel'], pydarn.DmapScalar)
        self.assertIsInstance(dm_records[1]['ptab'], pydarn.DmapArray)
        self.assertIsInstance(dm_records[7]['channel'].value, int)
        self.assertIsInstance(dm_records[2]['xcfd'].value, np.ndarray)
        self.assertEqual(dm_records[0]['xcfd'].dimension, 3)

    def test_read_fitacf(self):
        """
        Test reading records from fitacf.

        Checks:
            - returns correct data structures
            - returns expected values
        """
        file_path = fitacf_file
        dm = pydarn.SDarnRead(file_path)
        dm_records = dm.read_fitacf()
        dm_records = dm.get_dmap_records
        self.assertIsInstance(dm_records, collections.deque)
        self.assertIsInstance(dm_records[0], collections.OrderedDict)
        self.assertIsInstance(dm_records[4]['bmnum'], pydarn.DmapScalar)
        self.assertIsInstance(dm_records[1]['ptab'], pydarn.DmapArray)
        self.assertIsInstance(dm_records[7]['channel'].value, int)
        self.assertIsInstance(dm_records[2]['ltab'].value, np.ndarray)
        self.assertEqual(dm_records[0]['ptab'].dimension, 1)

    def test_read_grid(self):
        """
        Test reading records from grid file.

        Checks:
            - returns correct data structures
            - returns expected values
        """
        file_path = grid_file
        dm = pydarn.SDarnRead(file_path)
        _ = dm.read_grid()
        dm_records = dm.get_dmap_records
        self.assertIsInstance(dm_records, collections.deque)
        self.assertIsInstance(dm_records[0], collections.OrderedDict)
        self.assertIsInstance(dm_records[4]['start.year'], pydarn.DmapScalar)
        self.assertIsInstance(dm_records[1]['v.max'], pydarn.DmapArray)
        self.assertIsInstance(dm_records[7]['end.day'].value, int)
        self.assertIsInstance(dm_records[2]['stid'].value, np.ndarray)
        self.assertEqual(dm_records[0]['nvec'].dimension, 1)

    def test_read_map(self):
        """
        Test reading records from map file.

        Checks:
            - returns correct data structures
            - returns expected values
        """
        file_path = map_file
        dm = pydarn.SDarnRead(file_path)
        _ = dm.read_map()
        dm_records = dm.get_dmap_records
        self.assertIsInstance(dm_records, collections.deque)
        self.assertIsInstance(dm_records[0], collections.OrderedDict)
        self.assertIsInstance(dm_records[2]['IMF.flag'],
                              pydarn.io.datastructures.DmapScalar)
        self.assertIsInstance(dm_records[3]['stid'], pydarn.DmapArray)
        self.assertIsInstance(dm_records[8]['IMF.flag'].value, int)
        self.assertIsInstance(dm_records[10]['stid'].value, np.ndarray)
        self.assertEqual(dm_records[3]['stid'].dimension, 1)
        # this will be file dependent... future working test project.
        self.assertEqual(dm_records[0]['stid'].shape[0], 14)

    def test_read_corrupt_file1(self):
        """
        Test read_records on a corrupt file

        Expected behaviour: raises pydmap exception
        """
        dmap = pydarn.SDarnRead(corrupt_file1)
        with self.assertRaises(pydarn.dmap_exceptions.DmapDataTypeError):
            dmap.read_rawacf()

    def test_read_currupt_file2(self):
        """
        Test read_records on a corrupt file

        Expected behaviour: raises pydmap exception
        """
        dmap = pydarn.SDarnRead(corrupt_file2)
        with self.assertRaises(pydarn.dmap_exceptions.NegativeByteError):
            dmap.read_rawacf()

    def test_dmap_read_stream(self):
        """
        Test read_records on dmap data stream.
        The dmap data stream is formed from compressed
        bzip2 file that returns a bytes object.

         Checks:
            - returns correct data structures
            - returns expected values
        """
        # bz2 opens the compressed file into a data
        # stream of bytes without actually uncompressing the file
        with bz2.open(rawacf_stream) as fp:
            dmap_stream = fp.read()
        dmap = pydarn.SDarnRead(dmap_stream, True)
        dmap_data = dmap.read_rawacf()
        dmap_data = dmap.get_dmap_records
        self.assertIsInstance(dmap_data, collections.deque)
        self.assertIsInstance(dmap_data[0], collections.OrderedDict)
        self.assertIsInstance(dmap_data[4]['channel'], pydarn.DmapScalar)
        self.assertIsInstance(dmap_data[1]['ptab'], pydarn.DmapArray)
        self.assertIsInstance(dmap_data[7]['channel'].value, int)
        self.assertIsInstance(dmap_data[2]['xcfd'].value, np.ndarray)
        self.assertEqual(dmap_data[0]['xcfd'].dimension, 3)

    def test_dmap_read_corrupt_stream(self):
        """
        Test read_records on a corrupt stream. Read in compressed
        file which returns a byte object, then insert some random
        bytes to produce a corrupt stream.

        Expected behaviour: raises pydmap exception
        """
        with bz2.open(rawacf_stream) as fp:
            dmap_stream = fp.read()

        # need to convert to byte array for mutability
        # since bytes are immutable.
        corrupt_stream = bytearray(dmap_stream[0:36])
        corrupt_stream[36:40] = bytearray(str(os.urandom(4)).encode('utf-8'))
        corrupt_stream[40:] = dmap_stream[37:]
        dmap = pydarn.SDarnRead(corrupt_stream, True)
        with self.assertRaises(pydarn.dmap_exceptions.DmapDataError):
            dmap.read_rawacf()


@pytest.mark.skip
class TestDarnUtilities(unittest.TestCase):
    """
    Testing DarnUtilities class.
    Note
    ----
    All methods in this class are static so there is no constructor testing
    """
    def SetUp(self):
        pass

    def test_dict_key_diff(self):
        """
        Testing dict_key_diff - returns the difference in keys between two sets
        dictionaries

        Expected behaviour
        ------------------
        Returns the set difference between two dictionaries
        """
        a = {'a': 4, 'c': 5, 'd': 4}
        b = {'1': 'a', 'c': 'd', 'd': 4, 'z': 'dog'}
        solution_a_b = {'a'}
        solution_b_a = {'1', 'z'}
        diff_set = pydarn.SDarnUtilities.dict_key_diff(a, b)
        self.assertEqual(diff_set, solution_a_b)
        diff_set = pydarn.SDarnUtilities.dict_key_diff(b, a)
        self.assertEqual(diff_set, solution_b_a)

    def test_dict_list2set(self):
        """
        Tests the dict_list2set method - this method converts lists of
        dictionaries to concatenated full sets

        Expected behaviour
        ------------------
        Returns only a single set the comprises of the dictionary keys
        given in the list
        """
        dict1 = {'a': 1, 'b': 2, 'c': 3}
        dict2 = {'rst': '4.1', 'stid': 3, 'vel': [2.3, 4.5]}
        dict3 = {'fitacf': 'f', 'rawacf': 's', 'map': 'm'}

        complete_set = {'a', 'b', 'c',
                        'rst', 'stid', 'vel',
                        'fitacf', 'rawacf', 'map'}
        dict_set = pydarn.SDarnUtilities.dict_list2set([dict1, dict2, dict3])
        self.assertEqual(dict_set, complete_set)

    def test_extra_field_check_pass(self):
        """
        Test the extra_field_check method - this method checks if there are
        differences in the key sets of dictionaries that when passed a record
        and field names it will indicate if there is an extra field in the
        record key set

        Expected behaviour
        ------------------
        Nothing - if there are no differences in the key set then
        nothing returns
        """
        dict1 = {'a': 1, 'b': 2, 'c': 3}
        dict2 = {'rst': '4.1', 'stid': 3, 'vel': [2.3, 4.5]}
        dict3 = {'fitacf': 'f', 'rawacf': 's', 'map': 'm'}
        test_dict = {'a': 3, 'b': 3, 'c': 3, 'rst': 1, 'vel': 'd'}
        pydarn.SDarnUtilities.extra_field_check([dict1, dict2, dict3],
                                                test_dict, 1)

    def test_extra_field_check_fail(self):
        """
        Test the extra_field_check method - this method checks if there are
        differences in the key sets of dictionaries that when passed a record
        and field names it will indicate if there is an extra field in the
        record key set

        Expected behaviour
        -----------------
        Raises SuperDARNExtraFieldError because there are differences between
        the two dictionary sets
        """
        dict1 = {'a': 1, 'b': 2, 'c': 3}
        dict2 = {'rst': '4.1', 'stid': 3, 'vel': [2.3, 4.5]}
        dict3 = {'fitacf': 'f', 'rawacf': 's', 'map': 'm'}

        test_dict = {'a': 3, 'b': 3, 'c': 2, 'd': 3, 'rst': 1, 'vel': 'd'}
        try:
            pydarn.SDarnUtilities.extra_field_check([dict1, dict2, dict3],
                                                    test_dict, 1)
        except pydarn.superdarn_exceptions.SuperDARNExtraFieldError as err:
            self.assertEqual(err.fields, {'d'})

    def test_missing_field_check_pass_mixed_dict(self):
        """
        Testing missing_field_check - Reverse idea of the extra_field_check,
        should find missing fields in a record when compared to a key set of
        SuperDARN field names

        Expected behaviour
        ------------------
        Nothing - if there is not differences then nothing happens
        """
        dict1 = {'a': 1, 'b': 2, 'c': 3}
        dict2 = {'rst': '4.1', 'stid': 3, 'vel': [2.3, 4.5]}
        dict3 = {'fitacf': 'f', 'rawacf': 's', 'map': 'm'}
        test_dict = {}
        test_dict.update(dict1)
        test_dict.update(dict3)
        pydarn.SDarnUtilities.missing_field_check([dict1, dict2,
                                                  dict3],
                                                  test_dict, 1)

    def test_missing_field_check_pass_mixed_subset(self):
        """
        Testing missing_field_check - Reverse idea of the extra_field_check,
        should find missing fields in a record when compared to a key set of
        SuperDARN field names

        Expected behaviour
        ------------------
        Nothing - the missing_field_check should be able to handle subsets of
        of complete sets. Meaning it will not raise an error if it contains
        the full subsets of the dictionary keys but the full overall set.
        This is needed for Fitacf, Gird and Map files as they do not write
        all the fields in if data is bad or users do not use certain
        commands/options when processing the data.
        """
        dict1 = {'a': 1, 'b': 2, 'c': 3}
        dict2 = {'rst': '4.1', 'stid': 3, 'vel': [2.3, 4.5]}
        dict3 = {'fitacf': 'f', 'rawacf': 's', 'map': 'm'}

        test_dict = {'a': 3, 'b': 3, 'c': 2, 'd': 2,
                     'stid': 's', 'rst': 1, 'vel': 'd'}

        pydarn.SDarnUtilities.missing_field_check([dict1, dict2, dict3],
                                                  test_dict, 1)
        test_dict = {}
        test_dict.update(dict1)
        test_dict.update(dict3)
        pydarn.SDarnUtilities.missing_field_check([dict1, dict2, dict3],
                                                  test_dict, 1)

    def test_missing_field_check_fail2(self):
        """
        Testing missing_field_check - Reverse idea of the extra_field_check,
        should find missing fields in a record when compared to a key set of
        SuperDARN field names

        Expected behaviour
        ------------------
        Raise SuperDARNFieldMissingError - raised when there is a difference
        between dictionary key sets
        """

        dict1 = {'a': 1, 'b': 2, 'c': 3}
        dict2 = {'rst': '4.1', 'stid': 3, 'vel': [2.3, 4.5]}
        dict3 = {'fitacf': 'f', 'rawacf': 's', 'map': 'm'}

        test_dict = {'a': 3, 'b': 3, 'd': 2,
                     'stid': 's', 'vel': 'd',
                     'fitacf': 3, 'map': 4}

        try:
            pydarn.SDarnUtilities.missing_field_check([dict1, dict2, dict3],
                                                      test_dict, 1)
        except pydarn.superdarn_exceptions.SuperDARNFieldMissingError as err:
            self.assertEqual(err.fields, {'c', 'rst', 'rawacf'})

    def test_missing_field_check_fail(self):
        """
        Testing missing_field_check - Reverse idea of the extra_field_check,
        should find missing fields in a record when compared to a key set of
        SuperDARN field names

        Expected behaviour
        ------------------
        Raise SuperDARNFieldMissingError - raised when there is a difference
        between dictionary key sets
        """

        dict1 = {'a': 1, 'b': 2, 'c': 3}
        dict2 = {'rst': '4.1', 'stid': 3, 'vel': [2.3, 4.5]}
        dict3 = {'fitacf': 'f', 'rawacf': 's', 'map': 'm'}

        test_dict = {'a': 3, 'b': 3, 'd': 2,
                     'stid': 's', 'rst': 1, 'vel': 'd',
                     'fitacf': 3, 'map': 4}

        try:
            pydarn.SDarnUtilities.missing_field_check([dict1, dict2, dict3],
                                                      test_dict, 1)
        except pydarn.superdarn_exceptions.SuperDARNFieldMissingError as err:
            self.assertEqual(err.fields, {'c', 'rawacf'})

    def test_incorrect_types_check_pass(self):
        """
        Test incorrect_types_check - this method checks if the field data
        format type is not correct to specified SuperDARN field type.

        Note
        ----
        This method only works on pydarn DMAP record data structure

        Expected Behaviour
        ------------------
        Nothing - should not return or raise anything if the fields
        are the correct data format type
        """
        dict1 = {'a': 's', 'b': 'i', 'c': 'f'}
        dict3 = {'fitacf': 'f', 'rawacf': 's', 'map': 'm'}

        test_dict = {'a': pydarn.DmapScalar('a', 1, 1, 's'),
                     'b': pydarn.DmapScalar('a', 1, 1, 'i'),
                     'c': pydarn.DmapArray('a', np.array([2.4, 2.4]), 1,
                                           'f', 1, [3]),
                     'fitacf': pydarn.DmapScalar('a', 1, 1, 'f'),
                     'rawacf': pydarn.DmapScalar('a', 1, 1, 's'),
                     'map': pydarn.DmapScalar('a', 1, 1, 'm')}

        pydarn.SDarnUtilities.incorrect_types_check([dict1, dict3],
                                                    test_dict, 1)

    def test_incorrect_types_check_fail(self):
        """
        Test incorrect_types_check - this method checks if the field data
        format type is not correct to specified SuperDARN field type.

        Note
        ----
        This method only works on pydarn DMAP record data structure

        Expected Behaviour
        ------------------
        Raises SuperDARNDataFormatTypeError - because the field format types
        should not be the same.
        """

        dict1 = {'a': 's', 'b': 'i', 'c': 'f'}
        dict3 = {'fitacf': 'f', 'rawacf': 's', 'map': 'm'}

        test_dict = {'a': pydarn.DmapScalar('a', 1, 1, 's'),
                     'b': pydarn.DmapScalar('a', 1, 1, 'i'),
                     'c': pydarn.DmapArray('a', np.array([2.4, 2.4]),
                                           1, 'f', 1, [3]),
                     'fitacf': pydarn.DmapScalar('a', 1, 1, 's'),
                     'rawacf': pydarn.DmapScalar('a', 1, 1, 's'),
                     'map': pydarn.DmapScalar('a', 1, 1, 'm')}
        try:
            pydarn.SDarnUtilities.incorrect_types_check([dict1, dict3],
                                                        test_dict, 1)
        except pydarn.superdarn_exceptions.SuperDARNDataFormatTypeError as err:
            self.assertEqual(err.incorrect_params, {'fitacf': 'f'})


@pytest.mark.skip
class TestSDarnWrite(unittest.TestCase):
    """
    Tests SDarnWrite class
    """
    def setUp(self):
        pass

    def test_darn_write_constructor(self):
        """
        Tests SDarnWrite constructor

        Expected behaviour
        ------------------
        Contains file name of the data if given to it.
        """
        rawacf_data = copy.deepcopy(rawacf_data_sets.rawacf_data)
        darn = pydarn.SDarnWrite(rawacf_data, "rawacf_test.rawacf")
        self.assertEqual(darn.filename, "rawacf_test.rawacf")

    def test_empty_record(self):
        """
        Tests if an empty record is given. This will later be changed for
        real-time implementation.

        Expected behaviour
        ------------------
        Raise DmapDataError if no data is provided to the constructor
        """
        with self.assertRaises(pydarn.dmap_exceptions.DmapDataError):
            pydarn.SDarnWrite([], 'dummy_file.acf')

    def test_incorrect_filename_input_using_write_methods(self):
        """
        Tests if a file name is not provided to any of the write methods

        Expected behaviour
        ------------------
        All should raise a FilenameRequiredError - if no file name is given
        what do we write to.
        """
        rawacf_data = copy.deepcopy(rawacf_data_sets.rawacf_data)
        dmap_data = pydarn.SDarnWrite(rawacf_data)
        with self.assertRaises(pydarn.dmap_exceptions.FilenameRequiredError):
            dmap_data.write_rawacf()
            dmap_data.write_fitacf()
            dmap_data.write_iqdat()
            dmap_data.write_grid()
            dmap_data.write_map()
            dmap_data.write_dmap()

    def test_SDarnWrite_missing_field_rawacf(self):
        """
        Tests write_rawacf method - writes a rawacf structure file for the
        given data

        Expected behaviour
        ------------------
        Raises SuperDARNFieldMissingError - because the rawacf data is
        missing field nave
        """
        rawacf_missing_field = copy.deepcopy(rawacf_data_sets.rawacf_data)
        del rawacf_missing_field[2]['nave']

        dmap = pydarn.SDarnWrite(rawacf_missing_field)

        try:
            dmap.write_rawacf("test_rawacf.rawacf")
        except pydarn.superdarn_exceptions.SuperDARNFieldMissingError as err:
            self.assertEqual(err.fields, {'nave'})
            self.assertEqual(err.record_number, 2)

    def test_extra_field_rawacf(self):
        """
        Tests write_rawacf method - writes a rawacf structure file for the
        given data

        Expected behaviour
        ------------------
        Raises SuperDARNExtraFieldError because the rawacf data
        has an extra field dummy
        """
        rawacf_extra_field = copy.deepcopy(rawacf_data_sets.rawacf_data)
        rawacf_extra_field[1]['dummy'] = pydarn.DmapScalar('dummy', 'nothing',
                                                           chr(1), 's')
        dmap = pydarn.SDarnWrite(rawacf_extra_field)

        try:
            dmap.write_rawacf("test_rawacf.rawacf")
        except pydarn.superdarn_exceptions.SuperDARNExtraFieldError as err:
            self.assertEqual(err.fields, {'dummy'})
            self.assertEqual(err.record_number, 1)

    def test_incorrect_data_format_rawacf(self):
        """
        Tests write_rawacf method - writes a rawacf structure file for the
        given data

        Expected Behaviour
        -------------------
        Raises SuperDARNDataFormatTypeError because the rawacf data has the
        wrong type for the scan field
        """
        rawacf_incorrect_fmt = copy.deepcopy(rawacf_data_sets.rawacf_data)
        rawacf_incorrect_fmt[2]['scan'] = \
            rawacf_incorrect_fmt[2]['scan']._replace(data_type_fmt='c')
        dmap = pydarn.SDarnWrite(rawacf_incorrect_fmt)

        try:
            dmap.write_rawacf("test_rawacf.rawacf")
        except pydarn.superdarn_exceptions.SuperDARNDataFormatTypeError as err:
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

        dmap = pydarn.SDarnWrite(rawacf_data)

        dmap.write_rawacf("test_rawacf.rawacf")
        # only testing the file is created since it should only be created
        # at the last step after all checks have passed
        # Testing the integrity of the insides of the file will be part of
        # integration testing since we need SDarnRead for that.
        self.assertTrue(os.path.isfile("test_rawacf.rawacf"))
        os.remove("test_rawacf.rawacf")

    def test_writing_fitacf(self):
        """
        Tests write_fitacf method - writes a fitacf file

        Expected behaviour
        ------------------
        fitacf file is produced
        """
        fitacf_data = copy.deepcopy(fitacf_data_sets.fitacf_data)
        dmap = pydarn.SDarnWrite(fitacf_data)

        dmap.write_fitacf("test_fitacf.fitacf")
        self.assertTrue(os.path.isfile("test_fitacf.fitacf"))
        os.remove("test_fitacf.fitacf")

    def test_missing_fitacf_field(self):
        """
        Tests write_fitacf method - writes a fitacf structure file for the
        given data

        Expected behaviour
        ------------------
        Raises SuperDARNFieldMissingError - because the fitacf data is
        missing field stid
        """
        fitacf_missing_field = copy.deepcopy(fitacf_data_sets.fitacf_data)
        del fitacf_missing_field[0]['stid']
        dmap = pydarn.SDarnWrite(fitacf_missing_field)

        try:
            dmap.write_fitacf("test_fitacf.fitacf")
        except pydarn.superdarn_exceptions.SuperDARNFieldMissingError as err:
            self.assertEqual(err.fields, {'stid'})
            self.assertEqual(err.record_number, 0)

    def test_extra_fitacf_field(self):
        """
        Tests write_fitacf method - writes a fitacf structure file for the
        given data

        Expected behaviour
        ------------------
        Raises SuperDARNExtraFieldError because the fitacf data
        has an extra field dummy
        """
        fitacf_extra_field = copy.deepcopy(fitacf_data_sets.fitacf_data)
        fitacf_extra_field[1]['dummy'] = pydarn.DmapArray('dummy',
                                                          np.array([1, 2]),
                                                          chr(1), 'c', 1, [2])
        dmap = pydarn.SDarnWrite(fitacf_extra_field)

        try:
            dmap.write_fitacf("test_fitacf.fitacf")
        except pydarn.superdarn_exceptions.SuperDARNExtraFieldError as err:
            self.assertEqual(err.fields, {'dummy'})
            self.assertEqual(err.record_number, 1)

    def test_incorrect_fitacf_data_type(self):
        """
        Tests write_fitacf method - writes a fitacf structure file for the
        given data

        Expected Behaviour
        -------------------
        Raises SuperDARNDataFormatTypeError because the fitacf data has the
        wrong type for the ltab field
        """

        fitacf_incorrect_fmt = copy.deepcopy(fitacf_data_sets.fitacf_data)
        fitacf_incorrect_fmt[1]['ltab'] = \
            fitacf_incorrect_fmt[1]['ltab']._replace(data_type_fmt='s')
        dmap = pydarn.SDarnWrite(fitacf_incorrect_fmt)

        try:
            dmap.write_fitacf("test_fitacf.fitacf")
        except pydarn.superdarn_exceptions.SuperDARNDataFormatTypeError as err:
            self.assertEqual(err.incorrect_params['ltab'], 'h')
            self.assertEqual(err.record_number, 1)

    def test_writing_iqdat(self):
        """
        Tests write_iqdat method - writes a iqdat file

        Expected behaviour
        ------------------
        iqdat file is produced
        """
        iqdat_data = copy.deepcopy(iqdat_data_sets.iqdat_data)
        dmap = pydarn.SDarnWrite(iqdat_data)

        dmap.write_iqdat("test_iqdat.iqdat")
        self.assertTrue(os.path.isfile("test_iqdat.iqdat"))
        os.remove("test_iqdat.iqdat")

    def test_missing_iqdat_field(self):
        """
        Tests write_iqdat method - writes a iqdat structure file for the
        given data

        Expected behaviour
        ------------------
        Raises SuperDARNFieldMissingError - because the iqdat data is
        missing field chnnum
        """

        iqdat_missing_field = copy.deepcopy(iqdat_data_sets.iqdat_data)
        del iqdat_missing_field[1]['chnnum']
        dmap = pydarn.SDarnWrite(iqdat_missing_field)

        try:
            dmap.write_iqdat("test_iqdat.iqdat")
        except pydarn.superdarn_exceptions.SuperDARNFieldMissingError as err:
            self.assertEqual(err.fields, {'chnnum'})
            self.assertEqual(err.record_number, 1)

    def test_extra_iqdat_field(self):
        """
        Tests write_iqdat method - writes a iqdat structure file for the
        given data

        Expected behaviour
        ------------------
        Raises SuperDARNExtraFieldError because the iqdat data
        has an extra field dummy
        """
        iqdat_extra_field = copy.deepcopy(iqdat_data_sets.iqdat_data)
        iqdat_extra_field[2]['dummy'] = \
            pydarn.DmapArray('dummy', np.array([1, 2]), chr(1), 'c', 1, [2])
        dmap = pydarn.SDarnWrite(iqdat_extra_field)

        try:
            dmap.write_iqdat("test_iqdat.iqdat")
        except pydarn.superdarn_exceptions.SuperDARNExtraFieldError as err:
            self.assertEqual(err.fields, {'dummy'})
            self.assertEqual(err.record_number, 2)

    def test_incorrect_iqdat_data_type(self):
        """
        Tests write_iqdat method - writes a iqdat structure file for the
        given data

        Expected Behaviour
        -------------------
        Raises SuperDARNDataFormatTypeError because the iqdat data has the
        wrong type for the lagfr field
        """
        iqdat_incorrect_fmt = copy.deepcopy(iqdat_data_sets.iqdat_data)
        iqdat_incorrect_fmt[2]['lagfr'] = \
            iqdat_incorrect_fmt[2]['lagfr']._replace(data_type_fmt='d')
        dmap = pydarn.SDarnWrite(iqdat_incorrect_fmt)

        try:
            dmap.write_iqdat("test_iqdat.iqdat")
        except pydarn.superdarn_exceptions.SuperDARNDataFormatTypeError as err:
            self.assertEqual(err.incorrect_params['lagfr'], 'h')
            self.assertEqual(err.record_number, 2)

    def test_writing_map(self):
        """
        Tests write_map method - writes a map file

        Expected behaviour
        ------------------
        map file is produced
        """
        map_data = copy.deepcopy(map_data_sets.map_data)
        dmap = pydarn.SDarnWrite(map_data)

        dmap.write_map("test_map.map")
        self.assertTrue(os.path.isfile("test_map.map"))
        os.remove("test_map.map")

    def test_missing_map_field(self):
        """
        Tests write_map method - writes a map structure file for the
        given data

        Expected behaviour
        ------------------
        Raises SuperDARNFieldMissingError - because the map data is
        missing field stid
        """
        map_missing_field = copy.deepcopy(map_data_sets.map_data)
        del map_missing_field[0]['IMF.Kp']
        dmap = pydarn.SDarnWrite(map_missing_field)

        try:
            dmap.write_map("test_map.map")
        except pydarn.superdarn_exceptions.SuperDARNFieldMissingError as err:
            self.assertEqual(err.fields, {'IMF.Kp'})
            self.assertEqual(err.record_number, 0)

    def test_extra_map_field(self):
        """
        Tests write_map method - writes a map structure file for the
        given data

        Expected behaviour
        ------------------
        Raises SuperDARNExtraFieldError because the map data
        has an extra field dummy
        """
        map_extra_field = copy.deepcopy(map_data_sets.map_data)
        map_extra_field[1]['dummy'] = \
            pydarn.DmapArray('dummy', np.array([1, 2]), chr(1), 'c', 1, [2])
        dmap = pydarn.SDarnWrite(map_extra_field)

        try:
            dmap.write_map("test_map.map")
        except pydarn.superdarn_exceptions.SuperDARNExtraFieldError as err:
            self.assertEqual(err.fields, {'dummy'})
            self.assertEqual(err.record_number, 1)

    def test_incorrect_map_data_type(self):
        """
        Tests write_map method - writes a map structure file for the
        given data

        Expected Behaviour
        -------------------
        Raises SuperDARNDataFormatTypeError because the map data has the
        wrong type for the IMF.Bx field
        """
        map_incorrect_fmt = copy.deepcopy(map_data_sets.map_data)
        map_incorrect_fmt[2]['IMF.Bx'] = \
            map_incorrect_fmt[2]['IMF.Bx']._replace(data_type_fmt='i')
        dmap = pydarn.SDarnWrite(map_incorrect_fmt)

        try:
            dmap.write_map("test_map.map")
        except pydarn.superdarn_exceptions.SuperDARNDataFormatTypeError as err:
            self.assertEqual(err.incorrect_params.keys(), {'IMF.Bx'})
            self.assertEqual(err.record_number, 2)

    def test_writing_grid(self):
        """
        Tests write_grid method - writes a grid file

        Expected behaviour
        ------------------
        grid file is produced
        """
        grid_data = copy.deepcopy(grid_data_sets.grid_data)
        dmap = pydarn.SDarnWrite(grid_data)

        dmap.write_grid("test_grid.grid")
        self.assertTrue(os.path.isfile("test_grid.grid"))
        os.remove("test_grid.grid")

    def test_missing_grid_field(self):
        """
        Tests write_grid method - writes a grid structure file for the
        given data

        Expected behaviour
        ------------------
        Raises SuperDARNFieldMissingError - because the grid data is
        missing field stid
        """
        grid_missing_field = copy.deepcopy(grid_data_sets.grid_data)
        del grid_missing_field[1]['start.year']
        dmap = pydarn.SDarnWrite(grid_missing_field)

        try:
            dmap.write_grid("test_grid.grid")
        except pydarn.superdarn_exceptions.SuperDARNFieldMissingError as err:
            self.assertEqual(err.fields, {'start.year'})
            self.assertEqual(err.record_number, 1)

    def test_extra_grid_field(self):
        """
        Tests write_grid method - writes a grid structure file for the
        given data

        Expected behaviour
        ------------------
        Raises SuperDARNExtraFieldError because the grid data
        has an extra field dummy
        """
        grid_extra_field = copy.deepcopy(grid_data_sets.grid_data)
        grid_extra_field[0]['dummy'] = \
            pydarn.DmapArray('dummy', np.array([1, 2]), chr(1), 'c', 1, [2])
        dmap = pydarn.SDarnWrite(grid_extra_field)

        try:
            dmap.write_grid("test_grid.grid")
        except pydarn.superdarn_exceptions.SuperDARNExtraFieldError as err:
            self.assertEqual(err.fields, {'dummy'})
            self.assertEqual(err.record_number, 0)

    def test_incorrect_grid_data_type(self):
        """
        Tests write_grid method - writes a grid structure file for the
        given data

        Expected Behaviour
        -------------------
        Raises SuperDARNDataFormatTypeError because the grid data has the
        wrong type for the v.min field
        """
        grid_incorrect_fmt = copy.deepcopy(grid_data_sets.grid_data)
        grid_incorrect_fmt[2]['v.min'] = \
            grid_incorrect_fmt[2]['v.min']._replace(data_type_fmt='d')
        dmap = pydarn.SDarnWrite(grid_incorrect_fmt)

        try:
            dmap.write_grid("test_grid.grid")
        except pydarn.superdarn_exceptions.SuperDARNDataFormatTypeError as err:
            self.assertEqual(err.incorrect_params.keys(), {'v.min'})
            self.assertEqual(err.record_number, 2)


if __name__ == '__main__':
    """
    Runs the above class in a unittest system.
    Roughly takes 467 seconds.
    """
    pydarn_logger.info("Starting SuperDARN io testing")
    unittest.main()
