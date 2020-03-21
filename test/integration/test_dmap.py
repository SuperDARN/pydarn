# Copyright (C) 2019 SuperDARN
# Authors: Marina Schmidt
import bz2
import copy
import logging
import numpy as np
import os
import unittest

import pydarn

import rawacf_data_sets
import dmap_data_sets

# Test files
rawacf_stream = "../testfiles/20170410.1801.00.sas.stream.rawacf.bz2"
rawacf_file = "../testfiles/20170410.1801.00.sas.rawacf"

pydarn_logger = logging.getLogger('pydarn')


class IntegrationDmap(unittest.TestCase):
    """
    Testing integration class between DmapRead and DmapWrite.
    This script also integrates with the utils conversion methods:
        dict2dmap
        dmap2dict
    """
    def setUp(self):
        pass

    # TODO: look into a way to be its own class or function for
    # other test scripts
    def dict_compare(self, dict1: list, dict2: list):
        """
        This method helps compare two dictionaries that
        contain numpy arrays to help test cases.
        """
        self.assertEqual(len(dict1), len(dict2))
        for d1, d2 in zip(dict1, dict2):
            diff_fields1 = set(d1) - set(d2)
            self.assertEqual(len(diff_fields1), 0)
            diff_fields2 = set(d2) - set(d1)
            self.assertEqual(len(diff_fields2), 0)
            for key1, value1 in d1.items():
                if isinstance(value1, np.ndarray):
                    self.assertTrue(np.array_equal(value1, d2[key1]))
                else:
                    self.assertEqual(value1, d2[key1])

    def dmap_compare(self, dmap1: list, dmap2: list):
        """
        This method compares two dmap record data structures
        to help test cases.
        """
        # Quick simple tests that can be done before looping
        # over the list
        self.assertEqual(len(dmap1), len(dmap2))
        # NamedTuple are comparison capabilities
        for record1, record2 in zip(dmap1, dmap2):
            diff_fields1 = set(record1) - set(record2)
            self.assertEqual(len(diff_fields1), 0)
            diff_fields2 = set(record2) - set(record1)
            self.assertEqual(len(diff_fields2), 0)
            for field, val_obj in record1.items():
                if isinstance(val_obj, pydarn.DmapScalar):
                    self.assertEqual(record2[field], val_obj)
                elif isinstance(val_obj, pydarn.DmapArray):
                    self.compare_dmap_array(record2[field], val_obj)
                elif isinstance(val_obj, np.ndarray):
                    if np.array_equal(record2[field], val_obj):
                        self.assertTrue(np.array_equal(record2[field],
                                                       val_obj))
                    else:
                        self.assertTrue(np.allclose(record2[field], val_obj))
                else:
                    self.assertEqual(val_obj, record2[field])

    def compare_dmap_array(self, dmaparr1, dmaparr2):
        """
        This method is used to compare DmapArrays because they need to
        use numpy.array_equal method for comparing the arrays.
        """
        self.assertEqual(dmaparr1.name, dmaparr2.name)
        self.assertEqual(dmaparr1.data_type, dmaparr2.data_type)
        self.assertEqual(dmaparr1.data_type_fmt, dmaparr2.data_type_fmt)
        self.assertEqual(dmaparr1.dimension, dmaparr2.dimension)
        if np.array_equal(dmaparr1.value, dmaparr2.value):
            self.assertTrue(np.array_equal(dmaparr1.value, dmaparr2.value))
        else:
            # This is hack to going back to the files and fixing their
            # dimensions.
            value1 = np.reshape(dmaparr1.value, dmaparr1.shape)
            value2 = np.reshape(dmaparr2.value, dmaparr2.shape)
            self.assertTrue(np.array_equal(value1, value2))

    def test_DmapWrite_DmapRead_scalar(self):
        """
        This test integrates DmapWrite and DmapRead for
        writing a single scalar and then reading it in.

        Behaviour: No change to the scalar being written then read in.
        """
        scalar = pydarn.DmapScalar('stid', 5, 3, 'i')
        dmap_write = pydarn.DmapWrite([{'stid': scalar}])
        dmap_scalar_bytes = dmap_write.dmap_scalar_to_bytes(scalar)
        dmap = pydarn.DmapRead(dmap_scalar_bytes, True)
        dmap = dmap.read_scalar()
        self.assertEqual(scalar, dmap)

    def test_DmapWrite_DmapRead_array(self):
        """
        This test integrates DmapWrite and DmapRead for
        writing and reading an array.

        Behaviour: No change to the array
        """
        array = pydarn.DmapArray('xcf',
                                 np.array([4.3, 3.5, 2.3], dtype=np.float32),
                                 4, 'f', 1, [3])
        dmap_write = pydarn.DmapWrite([{'xcf': array}])
        dmap_array_bytes = dmap_write.dmap_array_to_bytes(array)
        dmap = pydarn.DmapRead(dmap_array_bytes, True)
        dmap_array = dmap.read_array(len(dmap_array_bytes))
        self.compare_dmap_array(array, dmap_array)

    def test_write_read_int8_array(self):
        """
        Test integrates DmapWrite and DmapRead to write and read an
        int8 data type which is the char type for DMAP format.
        """
        array = pydarn.DmapArray('channel', np.array([1, 0, 1], dtype=np.int8),
                                 1, 'c', 1, [3])
        dmap_write = pydarn.DmapWrite([{'channel': array}])
        dmap_array_bytes = dmap_write.dmap_array_to_bytes(array)
        dmap = pydarn.DmapRead(dmap_array_bytes, True)
        dmap_array = dmap.read_array(len(dmap_array_bytes))
        self.compare_dmap_array(array, dmap_array)

    def test_DmapWrite_DmapRead_int8_scalar(self):
        """
        Test integration DmapWrite and DmapRead to write char array.
        """
        scalar = pydarn.DmapScalar('channel', 4, 1, 'c')
        dmap_write = pydarn.DmapWrite([{'channel': scalar}])
        dmap_scalar_bytes = dmap_write.dmap_scalar_to_bytes(scalar)
        dmap = pydarn.DmapRead(dmap_scalar_bytes, True)
        dmap_scalar = dmap.read_scalar()
        self.assertEqual(scalar, dmap_scalar)

    def test_DmapRead_DmapWrite_dmap_file(self):
        """
        Test integration between DmapRead reading a file and DmapWrite
        writing the file then reading it again to ensure the data didn't
        change.
        """
        dmap = pydarn.DmapRead(rawacf_file)
        dmap_data = dmap.read_records()
        writer = pydarn.DmapWrite(dmap_data, "test_rawacf.rawacf")
        writer.write_dmap()
        self.assertTrue(os.path.isfile("test_rawacf.rawacf"))
        os.remove("test_rawacf.rawacf")

        dmap_write = pydarn.DmapWrite(dmap_data)
        dmap_write.write_dmap("test_rawacf.rawacf")

        dmap_read = pydarn.DmapRead("test_rawacf.rawacf")
        _ = dmap_read.read_records()
        _ = dmap_read.get_dmap_records
        os.remove("test_rawacf.rawacf")

    def test_DmapWrite_DmapRead_dmap_file(self):
        """
        Test integration between DmapWrite and DmapRead from
        a rawacf data written as file then read in and compared against.
        """
        rawacf_data = copy.deepcopy(rawacf_data_sets.rawacf_data)
        rawacf_write = pydarn.DmapWrite(rawacf_data, "test_rawacf.rawacf")
        rawacf_write.write_dmap()
        rawacf_read = pydarn.DmapRead("test_rawacf.rawacf")
        rawacf_read_data = rawacf_read.read_records()
        self.dmap_compare(rawacf_read_data, rawacf_data)

    def test_DmapRead_DmapWrite_stream_dmap(self):
        """
        Test DmapRead and DmapWrite to read in a stream and write to a stream
        to be read in again and compared.
        """
        with bz2.open(rawacf_stream) as fp:
            dmap_stream = fp.read()
        dmap = pydarn.DmapRead(dmap_stream, True)
        stream_data = dmap.read_records()
        dmap_write = pydarn.DmapWrite()
        dmap_write_stream = dmap_write.write_dmap_stream(stream_data)
        dmap_read = pydarn.DmapRead(dmap_write_stream, True)
        dmap_read_data = dmap_read.read_records()
        self.dmap_compare(stream_data, dmap_read_data)

    def test_DmapRead_stream_DmapWrite_file(self):
        """
        Test DmapRead a stream in and DmapWrite to a file. DmapRead is
        used to read the file to compare values.
        """
        with bz2.open(rawacf_stream) as fp:
            dmap_stream = fp.read()
        dmap = pydarn.DmapRead(dmap_stream, True)
        stream_data = dmap.read_records()
        dmap_stream_data = dmap.get_dmap_records
        dmap_write = pydarn.DmapWrite(stream_data)
        dmap_write.write_dmap("test_rawacf.rawacf")
        self.assertTrue(os.path.isfile("test_rawacf.rawacf"))

        dmap = pydarn.DmapRead("test_rawacf.rawacf")
        _ = dmap.read_records()
        dmap_read_data = dmap.get_dmap_records
        self.dmap_compare(dmap_stream_data, dmap_read_data)

    def test_DmapWrite_stream_DmapRead_dmap(self):
        """
        Test DmapWrite write data to a stream, DmapRead read the stream.
        """
        rawacf_data = copy.deepcopy(rawacf_data_sets.rawacf_data)
        rawacf_write = pydarn.DmapWrite()
        rawacf_stream = rawacf_write.write_dmap_stream(rawacf_data)
        rawacf_read = pydarn.DmapRead(rawacf_stream, True)
        rawacf_read_data = rawacf_read.read_records()
        self.dmap_compare(rawacf_read_data, rawacf_data)

    def test_DmapRead_dmap2dict_dict2dmap(self):
        """
        Test DmapRead from a file and convert to a dictionary.
        """
        dmap_read = pydarn.DmapRead(rawacf_file)
        records = dmap_read.read_records()
        records = dmap_read.get_dmap_records
        dict_records = pydarn.dmap2dict(records)
        records_2 = pydarn.dict2dmap(dict_records)
        self.dmap_compare(records, records_2)

    def test_DmapWrite_DmapRead_dict2dmap_dict2dmap(self):
        """
        Test Convert dictionary to dmap from dict2dmap then
        write with DmapWrite to be read in with DmapRead and
        converted back to a dictionary with dmap2dict.
        """
        dmap_dict = [{'stid': 56,
                      'channel': 0,
                      'software': 'RST',
                      'xcf': np.array([2.5, 3.456, 34.56, -4.5],
                                      dtype=np.float32),
                      'gflg': np.array([1, 0, 4, 2], np.int8)}]
        dmap_records = pydarn.dict2dmap(dmap_dict)
        dmap_write = pydarn.DmapWrite(dmap_records, 'test_dmap.dmap')
        dmap_write.write_dmap()
        dmap_read = pydarn.DmapRead("test_dmap.dmap")
        records = dmap_read.read_records()
        self.dmap_compare(dmap_dict, records)
        dmap_dict2 = pydarn.dict2dmap(records)
        self.dmap_compare(dmap_records, dmap_dict2)

    def test_dict2dmap_DmapWrite_DmapRead_stream_dmap2dict(self):
        """
        Test convert dict to dmap with dict2dmap then DmapWrite to write
        to a stream to be read in by
        DmapRead and converted back to a dictionary
        with dict2dmap
        """
        dmap_dict = [{'stid': 56,
                      'channel': 0,
                      'software': 'RST',
                      'xcf': np.array([2.5, 3.456, 34.56, -4.5],
                                      dtype=np.float32),
                      'gflg': np.array([1, 0, 4, 2], np.int8)}]
        dmap_records = pydarn.dict2dmap(dmap_dict)
        dmap_write = pydarn.DmapWrite(dmap_records)
        dmap_stream = dmap_write.write_dmap_stream()
        dmap_read = pydarn.DmapRead(dmap_stream, True)
        records = dmap_read.read_records()
        self.dmap_compare(dmap_dict, records)
        dmap_dict2 = pydarn.dict2dmap(records)
        self.dmap_compare(dmap_records, dmap_dict2)

    def test_DmapWrite_DmapRead_dmap2dict(self):
        """
        Test DmapWrite writing a dmap data set to be read in by DmapRead
        and convert to a dictionary by dmap2dict and compared.
        """
        dmap_dict = [{'RST.version': '4.1',
                      'stid': 3,
                      'FAC.vel': np.array([2.5, 3.5, 4.0], dtype=np.float32)},
                     {'RST.version': '4.1',
                      'stid': 3,
                      'FAC.vel': np.array([1, 0, 1], dtype=np.int8)},
                     {'RST.version': '4.1',
                      'stid': 3,
                      'FAC.vel': np.array([5.7, 2.34, -0.2],
                                          dtype=np.float32)}]
        dmap_data = copy.deepcopy(dmap_data_sets.dmap_data)
        dmap_write = pydarn.DmapWrite(dmap_data)
        dmap_stream = dmap_write.write_dmap_stream()
        dmap_read = pydarn.DmapRead(dmap_stream, True)
        dmap_records = dmap_read.read_records()
        dmap_records = dmap_read.get_dmap_records
        self.dmap_compare(dmap_records, dmap_data)
        dmap_dict2 = pydarn.dmap2dict(dmap_records)
        self.dict_compare(dmap_dict, dmap_dict2)


if __name__ == '__main__':
    """
    Runs the above class in a unittest system.
    Roughly takes 467 seconds.
    """
    pydarn_logger.info("Starting DMAP testing")

    unittest.main()
