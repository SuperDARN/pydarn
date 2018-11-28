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
        for k, v in dict_to_test.iteritems():
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


class TestDmap(unittest.TestCase):
    def setUp(self):
        pass

    def test_incorrect_file(self):
        """tests whether the file is empty or missing"""
        self.assertRaises(pydarn.EmptyFileError, pydarn.RawDmapRead, '/tmp/somefile.rawacf')
        self.assertRaises(pydarn.EmptyFileError,
                          pydarn.RawDmapRead,
                          'testfiles/emptytestfile')

    def test_open_rawacf(self):
        """tests opening a rawacf file using RawDmapRead"""
        file_path = rawacf_file

        # fail if any changes cause an exception to be thrown
        try:
            dm = pydarn.RawDmapRead(file_path)
        except pydarn.DmapDataError as e:
            self.fail(str(e))

        # will fail if there are no records
        self.assertTrue(dm.get_records())

    def test_open_fitacf(self):
        """tests opening a fitacf file using RawDmapRead"""
        file_path = fitacf_file

        # fail if any changes cause an exception to be thrown
        try:
            dm = pydarn.RawDmapRead(file_path)
        except pydarn.DmapDataError as e:
            self.fail(str(e))

        # will fail if there are no records
        self.assertTrue(dm.get_records())

    def test_open_map(self):
        """tests opening a map file using RawDmapRead"""
        file_path = map_file

        # fail if any changes cause an exception to be thrown
        try:
            dm = pydarn.RawDmapRead(file_path)
        except pydarn.DmapDataError as e:
            self.fail(str(e))

        # will fail if there are no records
        self.assertTrue(dm.get_records())

    def test_open_iqdat(self):
        """tests opening a map file using RawDmapRead"""
        file_path = "testfiles/20160316.1945.01.rkn.iqdat"

        # fail if any changes cause an exception to be thrown
        try:
            dm = pydarn.RawDmapRead(file_path)
        except pydarn.DmapDataError as e:
            self.fail(str(e))

        # will fail if there are no records
        self.assertTrue(dm.get_records())

    def test_parse_dmap_from_file_function(self):
        """tests the overarching function used to open dmap based files
        and returns a list of parsed items"""
        file_path = map_file

        # fail if any changes cause an exception to be thrown
        try:
            records = pydarn.parse_dmap_format_from_file(file_path)
        except pydarn.DmapDataError as e:
            self.fail(str(e))

        self.assertIsInstance(records, list)
        self.assertIsInstance(records[0], dict)

    def test_writing_to_rawacf(self):
        """tests using RawDmapWrite to write to rawacf"""
        file_path = "test_rawacf.rawacf"

        dict_list = [test_data.rawacf_missing_field]

        self.assertRaises(pydarn.DmapDataError, pydarn.dicts_to_file,
                          dict_list, file_path, file_type='rawacf')

        dict_list = [test_data.rawacf_extra_field]

        self.assertRaises(pydarn.DmapDataError, pydarn.dicts_to_file, dict_list,
                          file_path, file_type='rawacf')

        dict_list = [test_data.good_rawacf]

        try:
            pydarn.dicts_to_file(dict_list, file_path, file_type='rawacf')
        except pydarn.DmapDataError as e:
            self.fail(str(e))

        try:
            rec = pydarn.parse_dmap_format_from_file(file_path)
        except pydarn.DmapDataError as e:
            self.fail(str(e))

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
        pydarn.parse_dmap_format_from_file(file_path)

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

    def test_dmap_read_through_randomization(self):
        """Randomly corrupts 5% of the data in a record and tries to parse.
            Fails if an non Dmap exception is thrown as this means there is a
            missing check against bad input. Increase the number of tests to
            stress test."""

        num_tests = 100

        file_path = fitacf_file
        print("read file")
        dm = pydarn.parse_dmap_format_from_file(file_path, raw_dmap=True)
        print("done reading file")
        dm.cursor = 0
        dm.parse_record()

        dmap_length = dm.cursor

        dmap_to_randomize = dm.dmap_bytearr[0:dmap_length]

        seed = int(time.time())
        random.seed(seed)

        for x in range(0, num_tests):
            gc.collect()
            randomizer = [os.urandom(1) if random.randint(0, 100) >= 95
                          else '\x00' for j in range(0, dmap_length)]

            corrupted_dmap = [chr(a ^ ord(b))
                              for a, b in zip(dmap_to_randomize, randomizer)]
            try:
                self.assertRaises(pydarn.DmapDataError,pydarn.parse_dmap_format_from_stream, corrupted_dmap)
                del(records)
            #except pydarn.DmapDataError as e:
            #    pass
            except Exception as e:
                pydarn_logger.debug("New exception thrown by DMAP")
                message = "Corruption not handled."\
                          " Seed {0}. New exception thrown".format(seed)
                self.fail(message)

            del(randomizer)
            del(corrupted_dmap)


if __name__ == '__main__':
    pydarn_logger.info("Starting DMAP testing")
    unittest.main()
