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

import pydarn

pydarn_logger = logging.getLogger('pydarn')

# Test files
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
        with self.assertRaises(pydarn.pydmap_exceptions.ZeroByteError):
            dmap.test_initial_data_integrity()

    def test_read_currupt_file2(self):
        """
        Test read_records on a corrupt file

        Expected bahaviour: raises pydmap expection
        """
        dmap = pydarn.DmapRead(corrupt_file2)
        with self.assertRaises(pydarn.pydmap_exceptions.ZeroByteError):
            dmap.read_records()

    # FIXME: have not gotten this test to work with the streaming. I believe it is an utf-8 problem
    #def test_dmap_read_through_randomization(self):
    #    """Randomly corrupts 5% of the data in a record and tries to parse.
    #        Fails if an non Dmap exception is thrown as this means there is a
    #        missing check against bad input. Increase the number of tests to
    #        stress test."""

    #    num_tests = 100
    #    file_path = fitacf_file
    #    dm = pydarn.DmapRead(file_path)
    #    dm.cursor = 0
    #    dm.read_record()

    #    dmap_length = dm.cursor
    #    dmap_to_randomize = dm.dmap_bytearr[0:dmap_length]

    #    seed = int(time.time())
    #    random.seed(seed)

    #    for x in range(0, num_tests):
    #        gc.collect()
    #        randomizer = [os.urandom(1) if random.randint(0, 100) >= 95
    #                      else '\x00' for j in range(0, dmap_length)]

    #        corrupted_dmap = [chr(a ^ ord(b))
    #                          for a, b in zip(dmap_to_randomize, randomizer)]
    #        self.assertRaises(pydarn.DmapDataError,pydarn.parse_dmap_format_from_stream, corrupted_dmap)
    #        del(records)
    #        del(randomizer)
    #        del(corrupted_dmap)


if __name__ == '__main__':
    """
    Runs the above class in a unittest system.
    Roughly takes 467 seconds.
    """
    pydarn_logger.info("Starting DMAP testing")
    unittest.main()
