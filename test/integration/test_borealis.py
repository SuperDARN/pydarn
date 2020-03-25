# Copyright 2019 SuperDARN Canada, University of Saskatchewan
# Author: Marci Detwiller
"""
This test suite is to test the integration for the following classes:
    BorealisRead/BorealisWrite
    BorealisRestructureUtilities (implemented within
    BorealisRead/BorealisWrite)
    BorealisConvert/SDarnRead
Support for the following Borealis file types:
    rawrf
    antennas_iq
    bfiq
    rawacf
And supports conversion of the following Borealis -> SDARN DMap types:
    bfiq -> iqdat
    rawacf -> rawacf
"""
import copy
import gc
import logging
import numpy as np
import os
import unittest

from collections import OrderedDict

from borealis_rawacf_data_sets import borealis_array_rawacf_data
from borealis_bfiq_data_sets import borealis_array_bfiq_data
import pydarn

pydarn_logger = logging.getLogger('pydarn')

# Site Test files
borealis_site_bfiq_file = "../test_files/20190909.2200.02.sas.0.bfiq.hdf5.site"
borealis_site_rawacf_file =\
        "../test_files/20190909.2200.02.sas.0.rawacf.hdf5.site"
borealis_site_antennas_iq_file =\
        "../test_files/20190909.2200.02.sas.0.antennas_iq.hdf5.site"
borealis_site_rawrf_file = ""

# Array Test files
borealis_array_bfiq_file = "../test_files/20190909.2200.02.sas.0.bfiq.hdf5"
borealis_array_rawacf_file = "../test_files/20190909.2200.02.sas.0.rawacf.hdf5"
borealis_array_antennas_iq_file =\
        "../test_files/20190909.2200.02.sas.0.antennas_iq.hdf5"

# Problem files TODO
borealis_site_extra_field_file = ""
borealis_site_missing_field_file = ""
borealis_site_incorrect_data_format_file = ""

borealis_array_extra_field_file = ""
borealis_array_missing_field_file = ""
borealis_array_incorrect_data_format_file = ""
borealis_array_num_records_error_file = ""
borealis_empty_file = "../test_files/empty.rawacf"


class IntegrationBorealis(unittest.TestCase):
    """
    Testing class for integrations of BorealisRead/Write including
    restructuring code.
    """

    # RESTRUCTURING TESTS
    def check_dictionaries_are_same(self, dict1, dict2):

        self.assertEqual(sorted(list(dict1.keys())),
                         sorted(list(dict2.keys())))
        for key1, value1 in dict1.items():
            if isinstance(value1, dict) or isinstance(value1, OrderedDict):
                self.check_dictionaries_are_same(value1, dict2[key1])
            elif isinstance(value1, np.ndarray):
                self.assertTrue((value1 == dict2[key1]).all())
            elif key1 == 'experiment_comment':
                continue  # combf has filename inside, can differ
            else:
                self.assertEqual(value1, dict2[key1])

        return True

    def setUp(self):
        self.source_rawacf_site_file = borealis_site_rawacf_file
        self.write_rawacf_site_file = 'test_rawacf.rawacf.hdf5.site'
        self.source_rawacf_array_file = borealis_array_rawacf_file
        self.write_rawacf_array_file = 'test_rawacf.rawacf.hdf5'

        self.source_bfiq_site_file = borealis_site_bfiq_file
        self.write_bfiq_site_file = 'test_bfiq.bfiq.hdf5.site'
        self.source_bfiq_array_file = borealis_array_bfiq_file
        self.write_bfiq_array_file = 'test_bfiq.bfiq.hdf5.array'

        self.source_antennas_iq_site_file = borealis_site_antennas_iq_file
        self.write_antennas_iq_site_file =\
            'test_antennas_iq.antennas_iq.hdf5.site'
        self.source_antennas_iq_array_file = borealis_array_antennas_iq_file
        self.write_antennas_iq_array_file =\
            'test_antennas_iq.antennas_iq.hdf5.array'

    def test_read_write_site_rawacf(self):
        """
        Test reading and then writing site rawacf data to a file.

        Checks:
            - records that pass the read from a file can then be written
            - records written and then read are the same as original
        """
        dm = pydarn.BorealisRead(self.source_rawacf_site_file, 'rawacf',
                                 'site')
        records = dm.records
        _ = pydarn.BorealisWrite(self.write_rawacf_site_file,
                                 records, 'rawacf', 'site')
        self.assertTrue(os.path.isfile(self.write_rawacf_site_file))
        dm2 = pydarn.BorealisRead(self.write_rawacf_site_file, 'rawacf',
                                  'site')
        new_records = dm2.records
        dictionaries_are_same = self.check_dictionaries_are_same(records,
                                                                 new_records)
        self.assertTrue(dictionaries_are_same)

        os.remove(self.write_rawacf_site_file)
        del dm, dm2, records, new_records

    def test_read_write_array_rawacf(self):
        """
        Test reading and then writing array structured rawacf data to a file.

        Checks:
            - arrays that pass the read from a file can then be written
            - arrays written and then read are the same as original
        """
        dm = pydarn.BorealisRead(self.source_rawacf_array_file, 'rawacf',
                                 'array')
        arrays = dm.arrays
        _ = pydarn.BorealisWrite(self.write_rawacf_array_file,
                                 arrays, 'rawacf',
                                 'array')
        self.assertTrue(os.path.isfile(self.write_rawacf_array_file))
        dm2 = pydarn.BorealisRead(self.write_rawacf_array_file, 'rawacf',
                                  'array')
        new_arrays = dm2.arrays
        dictionaries_are_same = self.check_dictionaries_are_same(arrays,
                                                                 new_arrays)
        self.assertTrue(dictionaries_are_same)

        os.remove(self.write_rawacf_array_file)
        del dm, dm2, arrays, new_arrays

    def test_read_site_write_array_rawacf(self):
        """
        Test reading, restructuring, writing, restructuring rawacf.

        Checks:
            - records that pass the read from a file can then be written
                as arrays
            - records restructured, written as arrays, read as arrays,
                restructured back to records are the same as original records
        """
        dm = pydarn.BorealisRead(self.source_rawacf_site_file, 'rawacf',
                                 'site')
        records = dm.records

        arrays = dm.arrays  # restructuring happens here
        _ = pydarn.BorealisWrite(self.write_rawacf_array_file,
                                 arrays, 'rawacf',
                                 'array')
        del dm, arrays
        self.assertTrue(os.path.isfile(self.write_rawacf_array_file))
        dm2 = pydarn.BorealisRead(self.write_rawacf_array_file, 'rawacf',
                                  'array')

        new_records = dm2.records  # restructuring happens here
        dictionaries_are_same = self.check_dictionaries_are_same(records,
                                                                 new_records)
        self.assertTrue(dictionaries_are_same)

        os.remove(self.write_rawacf_array_file)
        del dm2, records, new_records

    def test_read_array_write_site_rawacf(self):
        """
        Test reading, restructuring, writing, restructuring rawacf.

        Checks:
            - arrays that pass the read from a file can then be written
                as records
            - arrays restructured, written as records, read as records,
                restructured back to arrays are the same as original arrays
        """
        dm = pydarn.BorealisRead(self.source_rawacf_array_file, 'rawacf',
                                 'array')
        arrays = dm.arrays

        records = dm.records  # restructuring happens here
        _ = pydarn.BorealisWrite(self.write_rawacf_site_file, records,
                                 'rawacf', 'site')
        del dm, records
        self.assertTrue(os.path.isfile(self.write_rawacf_site_file))
        dm2 = pydarn.BorealisRead(self.write_rawacf_site_file, 'rawacf',
                                  'site')

        new_arrays = dm2.arrays  # restructuring happens here
        dictionaries_are_same = self.check_dictionaries_are_same(arrays,
                                                                 new_arrays)
        self.assertTrue(dictionaries_are_same)

        os.remove(self.write_rawacf_site_file)
        del dm2, arrays, new_arrays

    def test_read_write_site_bfiq(self):
        """
        Test reading and then writing site bfiq data to a file.

        Checks:
            - records that pass the read from a file can then be written
            - records written and then read are the same as original
        """
        dm = pydarn.BorealisRead(self.source_bfiq_site_file, 'bfiq',
                                 'site')
        records = dm.records
        _ = pydarn.BorealisWrite(self.write_bfiq_site_file,
                                 records, 'bfiq',
                                 'site')
        self.assertTrue(os.path.isfile(self.write_bfiq_site_file))
        dm2 = pydarn.BorealisRead(self.write_bfiq_site_file, 'bfiq',
                                  'site')
        new_records = dm2.records
        dictionaries_are_same = self.check_dictionaries_are_same(records,
                                                                 new_records)
        self.assertTrue(dictionaries_are_same)

        os.remove(self.write_bfiq_site_file)
        del dm, dm2, records, new_records

    def test_read_write_array_bfiq(self):
        """
        Test reading and then writing array structured bfiq data to a file.

        Checks:
            - arrays that pass the read from a file can then be written
            - arrays written and then read are the same as original
        """
        dm = pydarn.BorealisRead(self.source_bfiq_array_file, 'bfiq',
                                 'array')
        arrays = dm.arrays
        _ = pydarn.BorealisWrite(self.write_bfiq_array_file,
                                 arrays, 'bfiq',
                                 'array')
        self.assertTrue(os.path.isfile(self.write_bfiq_array_file))
        dm2 = pydarn.BorealisRead(self.write_bfiq_array_file, 'bfiq',
                                  'array')
        new_arrays = dm2.arrays
        dictionaries_are_same = self.check_dictionaries_are_same(arrays,
                                                                 new_arrays)
        self.assertTrue(dictionaries_are_same)

        os.remove(self.write_bfiq_array_file)
        del dm, dm2, arrays, new_arrays

    def test_read_site_write_array_bfiq(self):
        """
        Test reading, restructuring, writing, restructuring bfiq.

        Checks:
            - records that pass the read from a file can then be written
                as arrays
            - records restructured, written as arrays, read as arrays,
                restructured back to records are the same as original records
        """
        dm = pydarn.BorealisRead(self.source_bfiq_site_file, 'bfiq',
                                 'site')
        records = dm.records

        arrays = dm.arrays  # restructuring happens here
        _ = pydarn.BorealisWrite(self.write_bfiq_array_file,
                                 arrays, 'bfiq',
                                 'array')
        del dm, arrays
        self.assertTrue(os.path.isfile(self.write_bfiq_array_file))
        dm2 = pydarn.BorealisRead(self.write_bfiq_array_file, 'bfiq',
                                  'array')

        new_records = dm2.records  # restructuring happens here
        dictionaries_are_same = self.check_dictionaries_are_same(records,
                                                                 new_records)
        self.assertTrue(dictionaries_are_same)

        os.remove(self.write_bfiq_array_file)
        del dm2, records, new_records

    def test_read_array_write_site_bfiq(self):
        """
        Test reading, restructuring, writing, restructuring bfiq.

        Checks:
            - arrays that pass the read from a file can then be written
                as records
            - arrays restructured, written as records, read as records,
                restructured back to arrays are the same as original arrays
        """
        dm = pydarn.BorealisRead(self.source_bfiq_array_file, 'bfiq',
                                 'array')
        arrays = dm.arrays

        records = dm.records  # restructuring happens here
        _ = pydarn.BorealisWrite(self.write_bfiq_site_file,
                                 records, 'bfiq',
                                 'site')
        del dm, records
        self.assertTrue(os.path.isfile(self.write_bfiq_site_file))
        dm2 = pydarn.BorealisRead(self.write_bfiq_site_file, 'bfiq',
                                  'site')

        new_arrays = dm2.arrays  # restructuring happens here
        dictionaries_are_same = self.check_dictionaries_are_same(arrays,
                                                                 new_arrays)
        self.assertTrue(dictionaries_are_same)

        os.remove(self.write_bfiq_site_file)
        del dm2, arrays, new_arrays

    def test_read_write_site_antennas_iq(self):
        """
        Test reading and then writing site antennas_iq data to a file.

        Checks:
            - records that pass the read from a file can then be written
            - records written and then read are the same as original
        """
        dm = pydarn.BorealisRead(self.source_antennas_iq_site_file,
                                 'antennas_iq',
                                 'site')
        records = dm.records
        _ = pydarn.BorealisWrite(self.write_antennas_iq_site_file,
                                 records, 'antennas_iq',
                                 'site')
        self.assertTrue(os.path.isfile(self.write_antennas_iq_site_file))
        dm2 = pydarn.BorealisRead(self.write_antennas_iq_site_file,
                                  'antennas_iq',
                                  'site')
        new_records = dm2.records
        dictionaries_are_same = self.check_dictionaries_are_same(records,
                                                                 new_records)
        self.assertTrue(dictionaries_are_same)

        os.remove(self.write_antennas_iq_site_file)
        del dm, dm2, records, new_records

    def test_read_write_array_antennas_iq(self):
        """
        Test reading and then writing array structured
        antennas_iq data to a file.

        Checks:
            - arrays that pass the read from a file can then be written
            - arrays written and then read are the same as original
        """
        dm = pydarn.BorealisRead(self.source_antennas_iq_array_file,
                                 'antennas_iq',
                                 'array')
        arrays = dm.arrays
        _ = pydarn.BorealisWrite(self.write_antennas_iq_array_file,
                                 arrays, 'antennas_iq',
                                 'array')
        self.assertTrue(os.path.isfile(self.write_antennas_iq_array_file))
        dm2 = pydarn.BorealisRead(self.write_antennas_iq_array_file,
                                  'antennas_iq',
                                  'array')
        new_arrays = dm2.arrays
        dictionaries_are_same = self.check_dictionaries_are_same(arrays,
                                                                 new_arrays)
        self.assertTrue(dictionaries_are_same)

        os.remove(self.write_antennas_iq_array_file)
        del dm, dm2, arrays, new_arrays

    def test_read_site_write_array_antennas_iq(self):
        """
        Test reading, restructuring, writing, restructuring antennas_iq.

        Checks:
            - records that pass the read from a file can then be written
                as arrays
            - records restructured, written as arrays, read as arrays,
                restructured back to records are the same as original records
        """
        dm = pydarn.BorealisRead(self.source_antennas_iq_site_file,
                                 'antennas_iq',
                                 'site')
        records = dm.records

        arrays = dm.arrays  # restructuring happens here
        del dm
        gc.collect()
        writer = pydarn.BorealisWrite(self.write_antennas_iq_array_file,
                                      arrays, 'antennas_iq',
                                      'array')
        del arrays, writer
        gc.collect()
        self.assertTrue(os.path.isfile(self.write_antennas_iq_array_file))
        dm2 = pydarn.BorealisRead(self.write_antennas_iq_array_file,
                                  'antennas_iq',
                                  'array')

        new_records = dm2.records  # restructuring happens here
        dictionaries_are_same = self.check_dictionaries_are_same(records,
                                                                 new_records)
        self.assertTrue(dictionaries_are_same)

        os.remove(self.write_antennas_iq_array_file)
        del dm2, records, new_records

    def test_read_array_write_site_antennas_iq(self):
        """
        Test reading, restructuring, writing, restructuring antennas_iq.

        Checks:
            - arrays that pass the read from a file can then be written
                as records
            - arrays restructured, written as records, read as records,
                restructured back to arrays are the same as original arrays
        """
        dm = pydarn.BorealisRead(self.source_antennas_iq_array_file,
                                 'antennas_iq',
                                 'array')
        arrays = dm.arrays

        writer = pydarn.BorealisWrite(self.write_antennas_iq_site_file,
                                      dm.records, 'antennas_iq',
                                      'site')
        del dm, writer
        gc.collect()
        self.assertTrue(os.path.isfile(self.write_antennas_iq_site_file))
        dm2 = pydarn.BorealisRead(self.write_antennas_iq_site_file,
                                  'antennas_iq',
                                  'site')

        new_arrays = dm2.arrays  # restructuring happens here
        dictionaries_are_same = self.check_dictionaries_are_same(arrays,
                                                                 new_arrays)
        self.assertTrue(dictionaries_are_same)

        os.remove(self.write_antennas_iq_site_file)
        del dm2, arrays, new_arrays


class IntegrationBorealisSDARN(unittest.TestCase):
    """
    Testing class for integrations of BorealisConvert and
    SDarnRead.
    """

    # RESTRUCTURING TESTS
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

    def setUp(self):
        self.rawacf_array_data = copy.deepcopy(
            borealis_array_rawacf_data)
        self.bfiq_array_data = copy.deepcopy(
            borealis_array_bfiq_data)

        self.bfiq_file = 'test_bfiq.bfiq.hdf5'
        self.rawacf_file = 'test_rawacf.rawacf.hdf5'

        self.iqdat_array_darn_file = './test_iqdat_array_file.dmap'
        self.rawacf_array_darn_file = './test_rawacf_array_file.dmap'

        _ = pydarn.BorealisWrite(self.bfiq_file,
                                 self.bfiq_array_data, 'bfiq', 'array')

        bfiq_reader = pydarn.BorealisRead(self.bfiq_file, 'bfiq', 'array')
        self.bfiq_site_data = bfiq_reader.records
        self.iqdat_site_darn_file = './test_iqdat_site_file.dmap'

        _ = pydarn.BorealisWrite(self.rawacf_file,
                                 self.rawacf_array_data, 'rawacf',
                                 'array')

        rawacf_reader = pydarn.BorealisRead(self.rawacf_file, 'rawacf',
                                            'array')
        self.rawacf_site_data = rawacf_reader.records
        self.rawacf_site_darn_file = './test_rawacf_site_file.dmap'

    # CONVERT TESTS
    def test_bfiq2darniqdat(self):
        """
        Test BorealisConvert by providing both site data and array data.
        Test that the dmap records are the same for both (site data and
        array data are from the same source, should produce same dmap output.)
        This tests that the restructuring is working before the dmap conversion
        """
        # self.bfiq_file already written in setUp
        array_converter =\
            pydarn.BorealisConvert(self.bfiq_file, "bfiq",
                                   self.iqdat_array_darn_file, 0,
                                   borealis_file_structure='array')
        self.assertTrue(os.path.isfile(self.iqdat_array_darn_file))
        darn_reader = pydarn.SDarnRead(self.iqdat_array_darn_file)
        iqdat_array_records = darn_reader.read_iqdat()
        os.remove(self.iqdat_array_darn_file)
        os.remove(self.bfiq_file)

        _ = pydarn.BorealisWrite(self.bfiq_file,
                                 self.bfiq_site_data, 'bfiq', 'site')
        site_converter =\
            pydarn.BorealisConvert(self.bfiq_file, "bfiq",
                                   self.iqdat_site_darn_file, 0,
                                   borealis_file_structure='site')
        self.assertTrue(os.path.isfile(self.iqdat_site_darn_file))
        darn_reader = pydarn.SDarnRead(self.iqdat_site_darn_file)
        iqdat_site_records = darn_reader.read_iqdat()
        os.remove(self.iqdat_site_darn_file)
        os.remove(self.bfiq_file)

        for record_num, record in enumerate(array_converter.sdarn_dict):
            dictionaries_are_same =\
                    self.check_dictionaries_are_same(record,
                                                     site_converter.
                                                     sdarn_dict[record_num])
            self.assertTrue(dictionaries_are_same)

        del (array_converter, site_converter, darn_reader, iqdat_site_records,
             iqdat_array_records)

    def test_rawacf2darnrawacf(self):
        """
        Test BorealisConvert by providing both site data and array data.
        Test that the dmap records are the same for both (site data and
        array data are from the same source, should produce same dmap output.)
        This tests that the restructuring is working before the dmap conversion
        """
        # self.rawacf_file already written in setUp
        array_converter =\
            pydarn.BorealisConvert(self.rawacf_file, "rawacf",
                                   self.rawacf_array_darn_file, 0,
                                   borealis_file_structure='array')
        self.assertTrue(os.path.isfile(self.rawacf_array_darn_file))
        darn_reader = pydarn.SDarnRead(self.rawacf_array_darn_file)
        rawacf_array_records = darn_reader.read_rawacf()
        os.remove(self.rawacf_array_darn_file)
        os.remove(self.rawacf_file)

        _ = pydarn.BorealisWrite(self.rawacf_file,
                                 self.rawacf_site_data, 'rawacf', 'site')
        site_converter =\
            pydarn.BorealisConvert(self.rawacf_file, "rawacf",
                                   self.rawacf_site_darn_file, 0,
                                   borealis_file_structure='site')
        self.assertTrue(os.path.isfile(self.rawacf_site_darn_file))
        darn_reader = pydarn.SDarnRead(self.rawacf_site_darn_file)
        rawacf_site_records = darn_reader.read_rawacf()
        os.remove(self.rawacf_site_darn_file)
        os.remove(self.rawacf_file)

        for record_num, record in enumerate(array_converter.sdarn_dict):
            dictionaries_are_same =\
                    self.check_dictionaries_are_same(record,
                                                     site_converter.
                                                     sdarn_dict[record_num])
            self.assertTrue(dictionaries_are_same)

        del (array_converter, site_converter, darn_reader, rawacf_site_records,
             rawacf_array_records)


# TODO ADD FAILURE TESTS FOR CONVERT (converting to wrong filetype, etc.)
if __name__ == '__main__':
    """
    Runs the above class in a unittest system.
    """
    pydarn_logger.info("Starting Borealis unit testing")

    unittest.main()
