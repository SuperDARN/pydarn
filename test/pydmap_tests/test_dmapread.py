# Copyright (C) 2018  SuperDARN
# Authors: Keith Kotyk and Marina Schmidt

"""
This test suite is to test the implementation of the DmapRead class that reads SuperDARN
DMAP files: rawacf, fitacf, map, ... etc
"""

import unittest
import numpy as np
import logging
import collections
import bz2
import os

import pydarn

pydarn_logger = logging.getLogger('pydarn')

# Test files
rawacf_stream = "./testfiles/20170410.1801.00.sas.stream.rawacf.bz2"
rawacf_file = "./testfiles/20170410.1801.00.sas.rawacf"
fitacf_file = "./testfiles/20180220.C0.rkn.fitacf"
map_file = "./testfiles/20170114.map"
iqdat_file = "testfiles/20160316.1945.01.rkn.iqdat"
# Black listed files
corrupt_file1 = "./testfiles/20070117.1001.00.han.rawacf"
corrupt_file2 = "./testfiles/20090320.1601.00.pgr.rawacf"


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
        self.assertRaises(FileNotFoundError, pydarn.DmapRead, './dog/somefile.rawacf')

    def test_incorrect_file(self):
        """
        Tests if DmapRead's constructor with an non-existant file

        Expected bahaviour: raises FileNotFoundError
        """
        self.assertRaises(FileNotFoundError, pydarn.DmapRead, './testfiles/somefile.rawacf')

    def test_empty_file(self):
        """
        Tests if DmapRead's constructor with an empty file

        Expected behaviour: raise EmptyFileError
        """
        self.assertRaises(pydarn.pydmap_exceptions.EmptyFileError, pydarn.DmapRead, './testfiles/empty.rawacf')

    def test_open_rawacf(self):
        """
        Tests DmapRead's constructor on opening a rawacf.
        It should be able to open the file, read it and convert to bytearray.

        Checks:
            - bytearray instance is created from reading in the file
            - bytearray is not empty
        """
        file_path = rawacf_file
        dm = pydarn.DmapRead(file_path)
        self.assertIsInstance(dm.dmap_bytearr, bytearray)
        self.assertGreater(dm.dmap_end_bytes, 0)

    def test_open_fitacf(self):
        """
        Tests DmapRead's constructor on opening a fitacf.
        It should be able to open the file, read it and convert to bytearray.

        Checks:
            - bytearray instance is created from reading in the file
            - bytearray is not empty
        """
        file_path = fitacf_file
        dm = pydarn.DmapRead(file_path)
        self.assertIsInstance(dm.dmap_bytearr, bytearray)
        self.assertGreater(dm.dmap_end_bytes, 0)

    def test_open_map(self):
        """
        Tests DmapRead's constructor on opening a map.
        It should be able to open the file, read it and convert to bytearray.

        Checks:
            - bytearray instance is created from reading in the file
            - bytearray is not empty
        """
        file_path = map_file
        dm = pydarn.DmapRead(file_path)
        self.assertIsInstance(dm.dmap_bytearr, bytearray)
        self.assertGreater(dm.dmap_end_bytes, 0)

    def test_open_iqdat(self):
        """
        Tests DmapRead's constructor on opening a iqdat.
        It should be able to open the file, read it and convert to bytearray.

        Checks:
            - bytearray instance is created from reading in the file
            - bytearray is not empty
        """
        file_path = iqdat_file
        dm = pydarn.DmapRead(file_path)
        self.assertIsInstance(dm.dmap_bytearr, bytearray)
        self.assertGreater(dm.dmap_end_bytes, 0)

    def test_integrity_check_rawacf(self):
        """
        Tests DmapRead test_initial_data_integrity
        It should be able to read through the bytearray quickly
        ensureing no curruption has occured in the file.

        Behaviours: raising no exceptions
        """
        file_path = rawacf_file
        dm = pydarn.DmapRead(file_path)
        dm.test_initial_data_integrity()

    def test_integrity_check_fitacf(self):
        """
        Tests DmapRead test_initial_data_integrity
        It should be able to read through the bytearray quickly
        ensureing no curruption has occured in the file.

        Behaviours: raising no exceptions
        """
        file_path = fitacf_file
        dm = pydarn.DmapRead(file_path)
        dm.test_initial_data_integrity()

    def test_integrity_check_map(self):
        """
        Tests DmapRead test_initial_data_integrity
        It should be able to read through the bytearray quickly
        ensureing no curruption has occured in the file.

        Behaviours: raising no exceptions
        """
        file_path = map_file
        dm = pydarn.DmapRead(file_path)
        dm.test_initial_data_integrity()

    def test_integrity_check_iqdat(self):
        """
        Tests DmapRead test_initial_data_integrity
        It should be able to read through the bytearray quickly
        ensureing no curruption has occured in the file.

        Behaviours: raising no exceptions
        """
        file_path = iqdat_file
        dm = pydarn.DmapRead(file_path)
        dm.test_initial_data_integrity()

    # TODO: potential issue if files change and the values are not the same :/
    def test_read_iqdat(self):
        """
        Test reading records from iqdat.

        Checks:
            - returns correct data structures
            - returns excpected values
        """
        file_path = iqdat_file
        dm = pydarn.DmapRead(file_path)
        dm_records = dm.read_records()
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
            - returns excpected values
        """
        file_path = rawacf_file
        dm = pydarn.DmapRead(file_path)
        dm_records = dm.read_records()
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
            - returns excpected values
        """
        file_path = fitacf_file
        dm = pydarn.DmapRead(file_path)
        dm_records = dm.read_records()
        self.assertIsInstance(dm_records, collections.deque)
        self.assertIsInstance(dm_records[0], collections.OrderedDict)
        self.assertIsInstance(dm_records[2]['channel'], pydarn.DmapScalar)
        self.assertIsInstance(dm_records[5]['ptab'], pydarn.DmapArray)
        self.assertIsInstance(dm_records[9]['channel'].value, int)
        self.assertIsInstance(dm_records[4]['ptab'].value, np.ndarray)
        self.assertEqual(dm_records[0]['scan'].value, 1)
        self.assertEqual(dm_records[7]['ltab'].dimension, 2)

    def test_read_map(self):
        """
        Test reading records from map file.

        Checks:
            - returns correct data structures
            - returns excpected values
        """
        file_path = map_file
        dm = pydarn.DmapRead(file_path)
        dm_records = dm.read_records()
        self.assertIsInstance(dm_records, collections.deque)
        self.assertIsInstance(dm_records[0], collections.OrderedDict)
        self.assertIsInstance(dm_records[2]['IMF.flag'], pydarn.pydmap.datastructures.DmapScalar)
        self.assertIsInstance(dm_records[3]['stid'], pydarn.DmapArray)
        self.assertIsInstance(dm_records[8]['IMF.flag'].value, int)
        self.assertIsInstance(dm_records[10]['stid'].value, np.ndarray)
        self.assertEqual(dm_records[3]['stid'].dimension, 1)
        self.assertEqual(dm_records[0]['stid'].shape[0], 14)  # this will be file dependent... future working test project.

    # TODO: Again dependent on the file used :/
    def test_integrity_check_corrupt_file1(self):
        """
        Test test_initial_data_integrity on a corrupt file

        Expected bahaviour: raises pydmap expection
        """
        dmap = pydarn.DmapRead(corrupt_file1)
        with self.assertRaises(pydarn.pydmap_exceptions.MismatchByteError):
            dmap.test_initial_data_integrity()

    def test_read_corrupt_file1(self):
        """
        Test read_records on a corrupt file

        Expected bahaviour: raises pydmap expection
        """
        dmap = pydarn.DmapRead(corrupt_file1)
        with self.assertRaises(pydarn.pydmap_exceptions.DmapDataTypeError):
            dmap.read_records()

    def test_integrity_check_corrupt_file2(self):
        """
        Test test_initial_data_integrity on a corrupt file

        Expected bahaviour: raises pydmap expection
        """
        dmap = pydarn.DmapRead(corrupt_file2)
        with self.assertRaises(pydarn.pydmap_exceptions.NegativeByteError):
            dmap.test_initial_data_integrity()

    def test_read_currupt_file2(self):
        """
        Test read_records on a corrupt file

        Expected bahaviour: raises pydmap expection
        """
        dmap = pydarn.DmapRead(corrupt_file2)
        with self.assertRaises(pydarn.pydmap_exceptions.NegativeByteError):
            dmap.read_records()

    def test_dmap_read_stream(self):
        # bz2 opens the compressed file into a data
        # stream of bytes without actually uncompressing the file
        with bz2.open(rawacf_stream) as fp:
            dmap_stream = fp.read()
        dmap = pydarn.DmapRead(dmap_stream, True)
        dmap_data = dmap.read_records()
        self.assertIsInstance(dmap_data, collections.deque)
        self.assertIsInstance(dmap_data[0], collections.OrderedDict)
        self.assertIsInstance(dmap_data[4]['channel'], pydarn.DmapScalar)
        self.assertIsInstance(dmap_data[1]['ptab'], pydarn.DmapArray)
        self.assertIsInstance(dmap_data[7]['channel'].value, int)
        self.assertIsInstance(dmap_data[2]['xcfd'].value, np.ndarray)
        self.assertEqual(dmap_data[0]['xcfd'].dimension, 3)

    def test_dmap_read_corrupt_stream(self):
        with bz2.open(rawacf_stream) as fp:
            dmap_stream = fp.read()

        corrupt_stream = bytearray(dmap_stream[0:36])
        corrupt_stream[36:40] = bytearray(str(os.urandom(4)).encode('utf-8'))
        corrupt_stream[40:] = dmap_stream[37:]
        dmap = pydarn.DmapRead(corrupt_stream, True)
        with self.assertRaises(pydarn.pydmap_exceptions.DmapDataError):
            dmap_data = dmap.read_records()


if __name__ == '__main__':
    """
    Runs the above class in a unittest system.
    Roughly takes 467 seconds.
    """
    pydarn_logger.info("Starting DMAP testing")
    unittest.main()
