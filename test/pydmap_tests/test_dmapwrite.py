"""Copyright (C) 2016  SuperDARN Canada

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>."""

import unittest
import test_data
import numpy as np
import os
import random
import gc
import time
import logging

import pydarn

pydarn_logger = logging.getLogger('pydarn')
rawacf_file = "./testfiles/20170410.1801.00.sas.rawacf"
fitacf_file = "./testfiles/20180220.C0.rkn.fitacf"
map_file = "./testfiles/20170114.map"

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

    def test_RawDmapWrite_missing_field_rawacf(self):
        """
            Tests RawDmapWite to write to rawacf:
                Expected behaviour to raise a DmapDataError
                because the rawtacf file is missing field.
        """
        file_path = "test_rawacf.rawacf"

        dict_list = [test_data.rawacf_missing_field]

        self.assertRaises(pydarn.DmapDataError, pydarn.dicts_to_file,
                          dict_list, file_path, file_type='rawacf')


    def test_RawDmapWrite_extra_field_rawacf(self):
        """
            Tests RawDmapWite to write to rawacf:
                Expected behaviour to raise a DmapDataError
                because the rawacf file data has an extra field.
        """
        file_path = "test_rawacf.rawacf"

        dict_list = [test_data.rawacf_extra_field]

        self.assertRaises(pydarn.DmapDataError, pydarn.dicts_to_file,
                          dict_list, file_path, file_type='rawacf')


    def test_writing_to_rawacf(self):
        """tests using RawDmapWrite to write to rawacf"""
        dict_list = [test_data.good_rawacf]
        file_path = "test_rawacf.rawacf"

        pydarn.dicts_to_file(dict_list, file_path, file_type='rawacf')

        rec = pydarn.parse_dmap_format_from_file(file_path)

        parsed_record = rec[0]
        k = test_write_integrity(parsed_record, test_data.good_rawacf)

        if k is not None:
            self.fail("Parsed field {0} data does not match data to be written out".format(k))

        os.remove(file_path)

    def test_RawDmapWrite_missing_field(self):
        """
            Tests RawDmapWite to write to fitacf:
                Expected behaviour to raise a DmapDataError
                because the fitacf file is missing field.
        """
        file_path = "test_fitacf.fitacf"

        dict_list = [test_data.fitacf_missing_field]

        self.assertRaises(pydarn.DmapDataError, pydarn.dicts_to_file,
                          dict_list, file_path, file_type='fitacf')


    def test_RawDmapWrite_extra_field(self):
        """
            Tests RawDmapWite to write to fitacf:
                Expected behaviour to raise a DmapDataError
                because the fitacf file data has an extra field.
        """
        file_path = "test_fitacf.fitacf"

        dict_list = [test_data.fitacf_extra_field]

        self.assertRaises(pydarn.DmapDataError, pydarn.dicts_to_file,
                          dict_list, file_path, file_type='fitacf')


    def test_writing_to_fitacf(self):
        """
            tests using RawDmapWrite to write to fitacf
            Excpected behaviour test_fitacf.fitacf is produced
            with no errors.
        """

        file_path = "test_fitacf.fitacf"

        dict_list = [test_data.good_fitacf]
        pydarn.dicts_to_file(dict_list, file_path,'fitacf')
        rec = pydarn.parse_dmap_format_from_file(file_path)

        parsed_record = rec[0]

        k = test_write_integrity(parsed_record, test_data.good_fitacf)

        if k is not None:
            self.fail("Parsed field {0} data does not match data to be written out".format(k))

        os.remove(file_path)

    def test_writing_to_iq(self):
        """tests using RawDmapWrite to write to iqdat"""
        file_path = "test_iq.iqdat"

        dict_list = [test_data.iq_missing_field]

        self.assertRaises(pydarn.DmapDataError, pydarn.dicts_to_file, dict_list,
                          file_path, file_type='iqdat')

        dict_list = [test_data.iq_extra_field]

        self.assertRaises(pydarn.DmapDataError, pydarn.dicts_to_file,
                          dict_list, file_path, file_type='iqdat')

        dict_list = [test_data.good_iq]

        try:
            pydarn.dicts_to_file(dict_list, file_path,
                                 file_type='iqdat')
        except pydarn.DmapDataError as e:
            self.fail(str(e))

        try:
            rec = pydarn.parse_dmap_format_from_file(file_path)
        except pydarn.DmapDataError as e:
            self.fail(str(e))

        parsed_record = rec[0]

        k = test_write_integrity(parsed_record, test_data.good_iq)

        if k is not None:
            self.fail("Parsed field {0} data does not match data to be written out".format(k))

        os.remove(file_path)

    def test_writing_to_map(self):
        """tests using RawDmapWrite to write to map"""
        file_path = "test_map.map"

        dict_list = [test_data.map_missing_field]

        self.assertRaises(pydarn.DmapDataError, pydarn.dicts_to_file,
                          dict_list, file_path, file_type='map')

        dict_list = [test_data.map_extra_field]

        self.assertRaises(pydarn.DmapDataError, pydarn.dicts_to_file,
                          dict_list, file_path, file_type='map')

        dict_list = [test_data.good_map]

        try:
            pydarn.dicts_to_file(dict_list, file_path, file_type='map')
        except pydarn.DmapDataError as e:
            self.fail(str(e))

        try:
            rec = pydarn.parse_dmap_format_from_file(file_path)
        except pydarn.DmapDataError as e:
            self.fail(str(e))

        parsed_record = rec[0]

        k = test_write_integrity(parsed_record, test_data.good_map)

        if k is not None:
            self.fail("Parsed field {0} data does not match data to be written out".format(k))

        os.remove(file_path)

