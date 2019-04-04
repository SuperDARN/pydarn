import pydarn
from pydarn import DmapScalar, DmapArray
import unittest
import numpy as np
import logging
import bz2
import os

import rawacf_data_sets
import dmap_data_sets
import copy
from collections import OrderedDict

# Test files
rawacf_stream = "../testfiles/20170410.1801.00.sas.stream.rawacf.bz2"
rawacf_file = "../testfiles/20170410.1801.00.sas.rawacf"

pydarn_logger = logging.getLogger('pydarn')


class IntegrationPydmap(unittest.TestCase):
    def setUp(self):
        pass

    def dict_compare(self, dict1: list, dict2: list):
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
                else:
                    self.compare_dmap_array(record2[field], val_obj)

    def compare_dmap_array(self, dmaparr1, dmaparr2):
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


    def test_dmap_write_read_scalar(self):
        scalar = pydarn.DmapScalar('stid', 5, 3, 'i')
        dmap_write = pydarn.DmapWrite()
        dmap_scalar_bytes = dmap_write.dmap_scalar_to_bytes(scalar)
        dmap = pydarn.DmapRead(dmap_scalar_bytes, True)
        dmap_scalar = dmap.read_scalar()
        self.assertEqual(scalar, dmap_scalar)

    def test_dmap_write_read_array(self):
        array = pydarn.DmapArray('xcf',
                                 np.array([4.3, 3.5, 2.3], dtype=np.float32),
                                 4, 'f', 1, [3])
        dmap_write = pydarn.DmapWrite()
        dmap_array_bytes = dmap_write.dmap_array_to_bytes(array)
        dmap = pydarn.DmapRead(dmap_array_bytes, True)
        dmap_array = dmap.read_array(len(dmap_array_bytes))
        self.compare_dmap_array(array, dmap_array)

    def test_write_read_string_array(self):
        array = pydarn.DmapArray('xcf', np.array(['dog', 'cat', 'mouse']),
                                 9, 's', 1, [3])
        dmap_write = pydarn.DmapWrite()
        dmap_array_bytes = dmap_write.dmap_array_to_bytes(array)
        dmap = pydarn.DmapRead(dmap_array_bytes, True)
        with self.assertRaises(pydarn.dmap_exceptions.DmapDataError):
            dmap.read_array(len(dmap_array_bytes))

    def test_write_read_character_array(self):
        array = pydarn.DmapArray('channel', np.array(['d', 'c', 'm']),
                                 1, 'c', 1, [3])
        dmap_write = pydarn.DmapWrite()
        dmap_array_bytes = dmap_write.dmap_array_to_bytes(array)
        dmap = pydarn.DmapRead(dmap_array_bytes, True)
        dmap.read_array(len(dmap_array_bytes))

    def test_dmap_write_read_char_scalar(self):
        scalar = pydarn.DmapScalar('channel', 'c', 1, 'c')
        dmap_write = pydarn.DmapWrite()
        with self.assertRaises(pydarn.dmap_exceptions.DmapCharError):
            dmap_write.dmap_scalar_to_bytes(scalar)

    def test_write_read_int8_array(self):
        array = pydarn.DmapArray('channel', np.array([1, 0, 1], dtype=np.int8),
                                 1, 'c', 1, [3])
        dmap_write = pydarn.DmapWrite()
        dmap_array_bytes = dmap_write.dmap_array_to_bytes(array)
        dmap = pydarn.DmapRead(dmap_array_bytes, True)
        dmap_array = dmap.read_array(len(dmap_array_bytes))
        self.compare_dmap_array(array, dmap_array)

    def test_dmap_write_read_int8_scalar(self):
        scalar = pydarn.DmapScalar('channel', 4, 1, 'c')
        dmap_write = pydarn.DmapWrite()
        dmap_scalar_bytes = dmap_write.dmap_scalar_to_bytes(scalar)
        dmap = pydarn.DmapRead(dmap_scalar_bytes, True)
        dmap_scalar = dmap.read_scalar()
        self.assertEqual(scalar, dmap_scalar)

    def test_read_write_dmap_file(self):
        dmap = pydarn.DmapRead(rawacf_file)
        dmap_data = dmap.read_records()
        pydarn.DmapWrite(dmap_data, "test_rawacf.rawacf")
        self.assertTrue(os.path.isfile("test_rawacf.rawacf"))
        os.remove("test_rawacf.rawacf")

        dmap_write = pydarn.DmapWrite(dmap_data)
        dmap_write.write_dmap("test_rawacf.rawacf")
        self.assertTrue(os.path.isfile("test_rawacf.rawacf"))
        os.remove("test_rawacf.rawacf")

    def test_write_read_dmap_file(self):
        rawacf_data = copy.deepcopy(rawacf_data_sets.rawacf_data)
        rawacf_write = pydarn.DmapWrite(rawacf_data, "test_rawacf.rawacf")
        rawacf_write.write_dmap()
        rawacf_read = pydarn.DmapRead("test_rawacf.rawacf")
        rawacf_read_data = rawacf_read.read_records()
        self.dmap_compare(rawacf_read_data, rawacf_data)

    def test_read_write_stream_dmap(self):
        with bz2.open(rawacf_stream) as fp:
            dmap_stream = fp.read()
        dmap = pydarn.DmapRead(dmap_stream, True)
        dmap_stream_data = dmap.read_records()
        dmap_write = pydarn.DmapWrite()
        dmap_write_stream = dmap_write.write_dmap_stream(dmap_stream_data)
        dmap_read = pydarn.DmapRead(dmap_write_stream, True)
        dmap_read_data = dmap_read.read_records()
        self.dmap_compare(dmap_stream_data, dmap_read_data)

    def test_read_stream_write_file_dmap(self):
        with bz2.open(rawacf_stream) as fp:
            dmap_stream = fp.read()
        dmap = pydarn.DmapRead(dmap_stream, True)
        dmap_stream_data = dmap.read_records()
        dmap_write = pydarn.DmapWrite(dmap_stream_data)
        dmap_write.write_dmap("test_rawacf.rawacf")
        self.assertTrue(os.path.isfile("test_rawacf.rawacf"))

        dmap = pydarn.DmapRead("test_rawacf.rawacf")
        dmap_data = dmap.read_records()
        self.dmap_compare(dmap_stream_data, dmap_data)

    def test_write_stream_read_dmap(self):
        rawacf_data = copy.deepcopy(rawacf_data_sets.rawacf_data)
        rawacf_write = pydarn.DmapWrite()
        rawacf_stream = rawacf_write.write_dmap_stream(rawacf_data)

        rawacf_read = pydarn.DmapRead(rawacf_stream, True)
        rawacf_read_data = rawacf_read.read_records()
        self.dmap_compare(rawacf_read_data, rawacf_data)

    def test_DmapRead_dmap2dict_dict2dmap(self):
        dmap_read = pydarn.DmapRead(rawacf_file)
        records = dmap_read.read_records()
        dict_records = pydarn.dmap2dict(records)
        records_2 = pydarn.dict2dmap(dict_records)
        self.dmap_compare(records, records_2)

    def test_DmapWrite_DmapRead_dict2dmap_dict2dmap(self):
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
        self.dmap_compare(dmap_records, records)
        dmap_dict2 = pydarn.dmap2dict(records)
        self.dict_compare(dmap_dict, dmap_dict2)

    def test_DmapWrite_DmapRead_stream_dmap2dict(self):
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
        self.dmap_compare(dmap_records, records)
        dmap_dict2 = pydarn.dmap2dict(records)
        self.dict_compare(dmap_dict, dmap_dict2)

    def test_DmapWrite_DmapRead_dmap2dict(self):
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
