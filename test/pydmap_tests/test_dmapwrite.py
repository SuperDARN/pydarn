# Copyright (C) 2016  SuperDARN Canada
# Authors: Marina Schmidt and Keith Kotyk


import unittest
import test_data
import numpy as np
import os
import random
import gc
import time
import logging

import pydarn
import rawacf_data_sets

pydarn_logger = logging.getLogger('pydarn')

def compare_arrays(arr1, arr2):
    for a, b in zip(arr1, arr2):
        if (isinstance(a, np.ndarray) or isinstance(a, list)) and \
         (isinstance(b, np.ndarray) or isinstance(b, list)):
            return compare_arrays(a, b)
        else:
            if (isinstance(a, np.float32) or isinstance(a, float)) and \
             (isinstance(a, np.float32) or isinstance(a, float)):
                if abs(a-b) > 1e-03:
                    return True
            else:
                if a != b:
                    return True

    return False


def test_write_integrity(parsed_record, dict_to_test):
        for k, v in dict_to_test.items():
            if isinstance(parsed_record[k], np.ndarray):
                if compare_arrays(parsed_record[k], v):
                    return k
            else:
                if isinstance(parsed_record[k], float):
                    if abs(parsed_record[k] - v) >= 1e-05:
                        return k
                else:
                    if parsed_record[k] != v:
                        return k
        return None

class TestDmapWrite(unittest.TestCase):
    def setUp(self):
        pass

    def test_wrong_file_format(self):
        rawacf_data = rawacf_data_sets.rawacf_data
        self.assertRaises(pydarn.pydmap_exceptions.DmapFileFormatType,
                          pydarn.DmapWrite(), rawacf_data,
                          "rawacf_test.rawacf", 'dog')

    def test_empty_record(self):
        self.assertRaises(pydarn.pydmap_exceptions.DmapDataError,
                          pydarn.DmapWrite([], 'dummy_file.acf', 'fitacf'))

    def test_incorrect_filename_input_using_DmapWrite(self):
        rawacf_data = rawacf_data_sets.rawacf_data
        self.assertRaises(pydarn.pydmap_exceptions.FilenameRequiredError,
                          pydarn.DmapWrite(), rawacf_data, "", 'fitacf')

    def test_incorrect_filename_input_using_write_methods(self):
        rawacf_data = rawacf_data_sets.rawacf_data
        dmap_data = pydarn.DmapWrite(rawacf_data)
        self.assertRaises(pydarn.pydmap_exceptions.FilenameRequiredError,
                          dmap_data.write_rawacf())
        self.assertRaises(pydarn.pydmap_exceptions.FilenameRequiredError,
                          dmap_data.write_fitacf)
        self.assertRaises(pydarn.pydmap_exceptions.FilenameRequiredError,
                          dmap_data.write_iqdat)
        self.assertRaises(pydarn.pydmap_exceptions.FilenameRequiredError,
                          dmap_data.write_grid)
        self.assertRaises(pydarn.pydmap_exceptions.FilenameRequiredError,
                          dmap_data.write_map)
        self.assertRaises(pydarn.pydmap_exceptions.FilenameRequiredError,
                          dmap_data.write_dmap)


    def test_RawDmapWrite_missing_field_rawacf(self):
        """
            Tests RawDmapWite to write to rawacf:
                Expected behaviour to raise a DmapDataError
                because the rawtacf file is missing field.
        """
        rawacf_data = rawacf_data_sets.missing_rawacf_field

        dmap = pydarn.DmapWrite(rawacf_data)

        self.assertRaises(pydarn.pydmap_exceptions.SuperDARNFieldMissing,
                          dmap.write_rawacf(), "test_rawacf.rawacf")
        self.assertRaises(pydarn.pydmap_exceptions.SuperDARNFieldMissing,
                          pydarn.DmapWrite(), rawacf_data,
                          "test_rawacf.rawacf", 'rawacf')


    def test_extra_field_rawacf(self):
        """
            Tests RawDmapWite to write to rawacf:
                Expected behaviour to raise a DmapDataError
                because the rawacf file data has an extra field.
        """
        rawacf_data = rawacf_data_sets.extra_rawacf_field

        dmap = pydarn.DmapWrite(rawacf_data)

        self.assertRaises(pydarn.pydmap_exceptions.SuperDARNFieldExtra,
                          dmap.write_rawacf(), "test_rawacf.rawacf")
        self.assertRaises(pydarn.pydmap_exceptions.SuperDARNFieldExtra,
                          pydarn.DmapWrite(), rawacf_data,
                          "test_rawacf.rawacf", 'rawacf')

    def test_incorrect_data_format_rawacf(self):
        rawacf_data = rawacf_data_sets.incorrect_data_type

        dmap = pydarn.DmapWrite(rawacf_data)

        self.assertRaises(pydarn.pydmap_exceptions.SuperDARNDataFormatError,
                          dmap.write_rawacf(), "test_rawacf.rawacf")
        self.assertRaises(pydarn.pydmap_exceptions.SuperDARNDataFormatError,
                          pydarn.DmapWrite(), rawacf_data,
                          "test_rawacf.rawacf", 'rawacf')


    def test_writing_to_rawacf(self):
        """tests using RawDmapWrite to write to rawacf"""
        rawacf_data = rawacf_data_sets.rawacf_data

        dmap = pydarn.DmapWrite(rawacf_data)

        dmap.write_rawacf("test_rawacf.rawacf")
        self.asserttrue(os.path.isfile("test_rawacf.rawacf"))
        os.remove("test_rawacf.rawacf")
        self.assertRaises(pydarn.pydmap_exceptions.SuperDARNFieldMissing,
                          pydarn.DmapWrite(), rawacf_data,
                          "test_rawacf.rawacf", 'rawacf')
        self.asserttrue(os.path.isfile("test_rawacf.rawacf"))
        os.remove("test_rawacf.rawacf")

if __name__ == '__main__':
    """
    Runs the above class in a unittest system.
    Roughly takes 467 seconds.
    """
    pydarn_logger.info("Starting DMAP testing")
    unittest.main()
