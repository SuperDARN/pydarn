# Copyright (C) 2019 SuperDARN Canada, University of Saskatchewan
# Author: Marina Schmidt

import bz2
import collections
import copy
import logging
import numpy as np
import os
import pytest
import unittest

import pydarn

import dmap_data_sets

pydarn_logger = logging.getLogger('pydarn')

# Test files
rawacf_stream = "../testfiles/20170410.1801.00.sas.stream.rawacf.bz2"
rawacf_file = "../testfiles/20170410.1801.00.sas.rawacf"
fitacf_file = "../testfiles/20180220.C0.rkn.fitacf"
map_file = "../testfiles/20170114.map"
iqdat_file = "../testfiles/20160316.1945.01.rkn.iqdat"
grid_file = "../testfiles/20180220.C0.rkn.grid"
# Black listed files
corrupt_file1 = "../testfiles/20070117.1001.00.han.rawacf"
corrupt_file2 = "../testfiles/20090320.1601.00.pgr.rawacf"


@pytest.mark.skip
class TestDmapRead(unittest.TestCase):
    """
    Testing class for DmapRead class
    """
    def setUp(self):
        pass

    """
    Testing DmapRead's constructor
    """
    def test_incorrect_path(self):
        """
        Testing DmapRead's constructor with an non-existant folder.

        Expected behaviour: raise FileNotFoundError
        """
        self.assertRaises(FileNotFoundError, pydarn.DmapRead,
                          './dog/somefile.rawacf')

    def test_incorrect_file(self):
        """
        Tests if DmapRead's constructor with an non-existant file

        Expected bahaviour: raises FileNotFoundError
        """
        self.assertRaises(FileNotFoundError, pydarn.DmapRead,
                          '../testfiles/somefile.rawacf')

    def test_empty_file(self):
        """
        Tests if DmapRead's constructor with an empty file

        Expected behaviour: raise EmptyFileError
        """
        self.assertRaises(pydarn.dmap_exceptions.EmptyFileError,
                          pydarn.DmapRead, '../testfiles/empty.rawacf')

    def test_open_dmap_file(self):
        """
        Tests DmapRead's constructor on opening a rawacf.
        It should be able to open the file, read it and convert to bytearray.

        Checks:
            - bytearray instance is created from reading in the file
            - bytearray is not empty
        """
        file_path = fitacf_file
        dm = pydarn.DmapRead(file_path)
        self.assertIsInstance(dm.dmap_bytearr, bytearray)
        self.assertGreater(dm.dmap_end_bytes, 0)

    def test_integrity_check_dmap_file(self):
        """
        Tests DmapRead test_initial_data_integrity
        It should be able to read through the bytearray quickly
        ensureing no curruption has occured in the file.

        Behaviours: raising no exceptions
        """
        file_path = rawacf_file
        dm = pydarn.DmapRead(file_path)
        dm.test_initial_data_integrity()

    def test_read_dmap_file(self):
        """
        Tests DmapRead test read_dmap.

        Behaviour: raising no exceptions
        """
        file_path = fitacf_file
        dm = pydarn.DmapRead(file_path)
        dmap_records = dm.read_records()
        dmap_records = dm.get_dmap_records
        self.assertIsInstance(dmap_records, collections.deque)
        self.assertIsInstance(dmap_records[0], collections.OrderedDict)
        self.assertIsInstance(dmap_records[4]['bmnum'], pydarn.DmapScalar)
        self.assertIsInstance(dmap_records[1]['ptab'], pydarn.DmapArray)
        self.assertIsInstance(dmap_records[7]['channel'].value, int)
        self.assertIsInstance(dmap_records[2]['ltab'].value, np.ndarray)
        self.assertEqual(dmap_records[0]['ptab'].dimension, 1)
        self.assertEqual(dmap_records[50]['gflg'].value[1], 0)

    # TODO: Again dependent on the file used :/
    def test_integrity_check_corrupt_file1(self):
        """
        Test test_initial_data_integrity on a corrupt file

        Expected bahaviour: raises pydmap expection
        """
        dmap = pydarn.DmapRead(corrupt_file1)
        with self.assertRaises(pydarn.dmap_exceptions.MismatchByteError):
            dmap.test_initial_data_integrity()

    def test_read_corrupt_file1(self):
        """
        Test read_records on a corrupt file

        Expected bahaviour: raises pydmap expection
        """
        dmap = pydarn.DmapRead(corrupt_file1)
        with self.assertRaises(pydarn.dmap_exceptions.DmapDataTypeError):
            dmap.read_records()

    def test_integrity_check_corrupt_file2(self):
        """
        Test test_initial_data_integrity on a corrupt file

        Expected bahaviour: raises pydmap expection
        """
        dmap = pydarn.DmapRead(corrupt_file2)
        with self.assertRaises(pydarn.dmap_exceptions.NegativeByteError):
            dmap.test_initial_data_integrity()

    def test_read_currupt_file2(self):
        """
        Test read_records on a corrupt file

        Expected bahaviour: raises pydmap expection
        """
        dmap = pydarn.DmapRead(corrupt_file2)
        with self.assertRaises(pydarn.dmap_exceptions.NegativeByteError):
            dmap.read_records()

    def test_dmap_read_stream(self):
        """
        Test read_records on dmap data stream.
        The dmap data stream is formed from compressed
        bzip2 file that returns a bytes object.

         Checks:
            - returns correct data structures
            - returns excpected values
        """
        # bz2 opens the compressed file into a data
        # stream of bytes without actually uncompressing the file
        with bz2.open(rawacf_stream) as fp:
            dmap_stream = fp.read()
        dmap = pydarn.DmapRead(dmap_stream, True)
        dmap_data = dmap.read_records()
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

        Expected bahaviour: raises pydmap expection
        """
        with bz2.open(rawacf_stream) as fp:
            dmap_stream = fp.read()

        # need to convert to byte array for mutability
        # since bytes are immutable.
        corrupt_stream = bytearray(dmap_stream[0:36])
        corrupt_stream[36:40] = bytearray(str(os.urandom(4)).encode('utf-8'))
        corrupt_stream[40:] = dmap_stream[37:]
        dmap = pydarn.DmapRead(corrupt_stream, True)
        with self.assertRaises(pydarn.dmap_exceptions.DmapDataError):
            dmap.read_records()


@pytest.mark.skip
class TestDmapWrite(unittest.TestCase):
    """ Testing DmapWrite class"""
    def setUp(self):
        pass

    def test_incorrect_filename_input_using_write_methods(self):
        """
        Testing if a filename is not given to DmapWrite

        Expected behaviour
        ------------------
        Raises FilenameRequiredError - no filename was given to write and
        constructor
        """
        rawacf_data = copy.deepcopy(dmap_data_sets.dmap_data)
        dmap_data = pydarn.DmapWrite(rawacf_data)
        with self.assertRaises(pydarn.dmap_exceptions.FilenameRequiredError):
            dmap_data.write_dmap()

    def test_empty_data_check(self):
        """
        Testing if no data is given to DmapWrite

        Expected behaviour
        ------------------
        Raise DmapDataError - no data is given to write
        """
        with self.assertRaises(pydarn.dmap_exceptions.DmapDataError):
            dmap_write = pydarn.DmapWrite(filename="test.test")
            dmap_write.write_dmap()

    def test_writing_dmap(self):
        """
        Testing write_dmap method

        Expected behaviour
        ------------------
        File is produced
        """
        dmap_data = copy.deepcopy(dmap_data_sets.dmap_data)
        dmap = pydarn.DmapWrite(dmap_data)

        # Integration testing will test the integrity of the
        # writing procedure.
        dmap.write_dmap("test_dmap.dmap")
        self.assertTrue(os.path.isfile("test_dmap.dmap"))

        os.remove("test_dmap.dmap")

    def test_scalar(self):
        """
        Test DmapWrite writing a character scalar type.

        Behaviour: Raised DmapCharError
        Dmap cannot write characters as they are treated as strings and not
        int8 - RST standard for char types.
        """
        scalar = pydarn.DmapScalar('channel', 'c', 1, 'c')
        dmap_write = pydarn.DmapWrite([{'channel': scalar}])
        with self.assertRaises(pydarn.dmap_exceptions.DmapCharError):
            dmap_write.dmap_scalar_to_bytes(scalar)

    def test_String_array(self):
        """
        Test DmapWrite writing string arrays

        Behaviour: Raised DmapDataError
        DmapWrite doesn't support writing string arrays because DmapRead does
        not support string arrays.
        """
        array = pydarn.DmapArray('xcf', np.array(['dog', 'cat', 'mouse']),
                                 9, 's', 1, [3])
        dmap_write = pydarn.DmapWrite([{'xcf': array}])
        with self.assertRaises(pydarn.dmap_exceptions.DmapDataError):
            dmap_write.dmap_array_to_bytes(array)

    def test_character_array(self):
        """
        Test DmapWrite writing character arrays.

        Behaviour: Raised DmapCharError
        """
        array = pydarn.DmapArray('channel', np.array(['d', 'c', 'm']),
                                 1, 'c', 1, [3])
        dmap_write = pydarn.DmapWrite([{'channel': array}])
        with self.assertRaises(pydarn.dmap_exceptions.DmapCharError):
            dmap_write.dmap_array_to_bytes(array)


if __name__ == '__main__':
    """
    Runs the above class in a unittest system.
    Roughly takes 467 seconds.
    """
    pydarn_logger.info("Starting DMAP testing")

    unittest.main()
