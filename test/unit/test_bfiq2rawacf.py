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
import bz2
import collections
import copy
import filecmp
import logging
import numpy as np
import os
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

# Site Test files
borealis_site_bfiq_file = "../test_files/20190909.2200.02.sas.0.bfiq.hdf5.site"
borealis_site_rawacf_file = "../test_files/20190909.2200.02.sas.0.rawacf.hdf5.site"
borealis_site_antennas_iq_file = "../test_files/20190909.2200.02.sas.0.antennas_iq.hdf5.site"
borealis_site_rawrf_file = ""

# Array Test files
borealis_array_bfiq_file = "../test_files/20190909.2200.02.sas.0.bfiq.hdf5"
borealis_array_rawacf_file = "../test_files/20190909.2200.02.sas.0.rawacf.hdf5"

class TestBorealisBfiqToRawacfPostProcessor(unittest.TestCase):
    """
    Tests BorealisBfiqToRawacfPostProcessor class
    """

    # RESTRUCTURING TESTS
    def check_dictionaries_are_same(self, dict1, dict2):

        self.assertEqual(sorted(list(dict1.keys())), sorted(list(dict2.keys())))
        for key1, value1 in dict1.items():
            if isinstance(value1, dict) or isinstance(value1, OrderedDict):
                self.check_dictionaries_are_same(value1, dict2[key1])
            elif isinstance(value1, np.ndarray):
                self.assertTrue((value1 == dict2[key1]).all())
            elif key1 == 'experiment_comment':
                continue # comment has origin info inside, can differ
            else:
                self.assertEqual(value1, dict2[key1])

        return True

    def setUp(self):
        self.bfiq_site_file = borealis_site_bfiq_file
        self.bfiq_array_file = borealis_array_bfiq_file

        self.test_rawacf_site_file = 'test_bfiq2rawacf.rawacf.hdf5.site'
        self.test_rawacf_array_file = 'test_bfiq2rawacf.rawacf.hdf5'

        self.rawacf_site_file = borealis_site_rawacf_file
        rawacf_site_reader = pydarn.BorealisRead(self.rawacf_site_file, 'rawacf', 
                                            'site')
        self.source_rawacf_records = rawacf_site_reader.records
        self.rawacf_array_file = borealis_array_rawacf_file
        rawacf_array_reader = pydarn.BorealisRead(self.rawacf_array_file, 
                                            'rawacf', 'array')
        self.source_rawacf_arrays = rawacf_array_reader.arrays
        del rawacf_site_reader, rawacf_array_reader

    def test_site_bfiq_to_site_rawacf(self):
        """
        Test writing site bfiq data to site rawacf data.

        Checks:
            - bfiq site data can be written to rawacf site data
            - rawacf site data written is the same as generated by
                Borealis on-site (except experiment_comment which contains
                processing origin info)
        """
        write_rawacf = pydarn.BorealisBfiqToRawacfPostProcessor(
                                self.bfiq_site_file,
                                self.test_rawacf_site_file, 'site', 'site')
        self.assertTrue(os.path.isfile(self.test_rawacf_site_file))
        os.remove(self.test_rawacf_site_file)

        dictionaries_are_same = self.check_dictionaries_are_same(
                                    write_rawacf.rawacf_records,
                                    self.source_rawacf_records)
        self.assertTrue(dictionaries_are_same)

        del write_rawacf

    def test_site_bfiq_to_array_rawacf(self):
        """
        Test writing site bfiq data to array rawacf data.

        Checks:
            - bfiq site data can be written to rawacf array data
            - rawacf array data written is the same as generated by
                Borealis on-site and then restructured (except 
                experiment_comment which contains processing origin info)
        """
        write_rawacf = pydarn.BorealisBfiqToRawacfPostProcessor(
                                self.bfiq_site_file,
                                self.test_rawacf_array_file, 'site', 'array')
        self.assertTrue(os.path.isfile(self.test_rawacf_array_file))
        os.remove(self.test_rawacf_array_file)

        dictionaries_are_same = self.check_dictionaries_are_same(
                                    write_rawacf.rawacf_writer.arrays,
                                    self.source_rawacf_arrays)
        self.assertTrue(dictionaries_are_same)

        del write_rawacf

    def test_array_bfiq_to_array_rawacf(self):
        """
        Test writing array bfiq data to array rawacf data.

        Checks:
            - bfiq array data can be written to rawacf array data
            - rawacf array data written is the same as generated by
                Borealis on-site and then restructured (except 
                experiment_comment which contains processing origin info)
        """
        write_rawacf = pydarn.BorealisBfiqToRawacfPostProcessor(
                                self.bfiq_array_file,
                                self.test_rawacf_array_file, 'array', 'array')
        self.assertTrue(os.path.isfile(self.test_rawacf_array_file))
        os.remove(self.test_rawacf_array_file)
        dictionaries_are_same = self.check_dictionaries_are_same(
                                    write_rawacf.rawacf_writer.arrays,
                                    self.source_rawacf_arrays)
        self.assertTrue(dictionaries_are_same)

        del write_rawacf

    def test_array_bfiq_to_site_rawacf(self):
        """
        Test writing array bfiq data to site rawacf data.

        Checks:
            - bfiq array data can be written to rawacf site data
            - rawacf site data written is the same as generated by
                Borealis on-site (except experiment_comment which contains
                processing origin info)
        """
        write_rawacf = pydarn.BorealisBfiqToRawacfPostProcessor(
                                self.bfiq_array_file,
                                self.test_rawacf_site_file, 'array', 'site')
        self.assertTrue(os.path.isfile(self.test_rawacf_site_file))
        os.remove(self.test_rawacf_site_file)
        dictionaries_are_same = self.check_dictionaries_are_same(
                                    write_rawacf.rawacf_records,
                                    self.source_rawacf_records)
        self.assertTrue(dictionaries_are_same)

        del write_rawacf


if __name__ == '__main__':
    """
    Runs the above class in a unittest system.
    """
    pydarn_logger.info("Starting Borealis unit testing")

    unittest.main()
