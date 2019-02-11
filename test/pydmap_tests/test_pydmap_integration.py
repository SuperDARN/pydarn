import pydarn
import unittest
import numpy as np
import logging
import collections
import bz2
import os

import rawacf_data_sets
import fitacf_data_sets
import iqdat_data_sets
import map_data_sets
import grid_data_sets
import copy


# Test files
rawacf_stream = "./testfiles/20170410.1801.00.sas.stream.rawacf.bz2"
rawacf_file = "./testfiles/20170410.1801.00.sas.rawacf"
fitacf_file = "./testfiles/20180220.C0.rkn.fitacf"
map_file = "./testfiles/20170114.map"
iqdat_file = "testfiles/20160316.1945.01.rkn.iqdat"
zip_file = ""
# Black listed files
corrupt_file1 = "./testfiles/20070117.1001.00.han.rawacf"
corrupt_file2 = "./testfiles/20090320.1601.00.pgr.rawacf"

pydarn_logger = logging.getLogger('pydarn')

class IntegrationPydmap(unittest.TestCase):
    def setUp(self):
        pass

    def dmap_compare(self, dmap1: list, dmap2: list):
        # Quick simple tests that can be done before looping
        # over the list
        self.assertEqual(len(dmap1), len(dmap2))

        #NamedTuple are comparison capabilities
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
        if np.array_equiv(dmaparr1, dmaparr2):
            self.assertTrue(np.array_equal(dmaparr1.value, dmaparr2.value))
        else:
            print(np.shape(dmaparr1.value),np.shape(dmaparr2.value))
            print(dmaparr1.value, dmaparr2.value)
            self.assertTrue(np.array_equal(dmaparr1.value, dmaparr2.value))

    def test_dmap_write_read_scalar(self):
        scalar = pydarn.DmapScalar('stid', 5, 3, 'i')
        dmap_write = pydarn.DmapWrite()
        dmap_scalar_bytes = dmap_write.dmap_scalar_to_bytes(scalar)
        dmap = pydarn.DmapRead(dmap_scalar_bytes, True)
        dmap_scalar = dmap.read_scalar()
        print(dmap_scalar)
        self.assertEqual(scalar, dmap_scalar)

    def test_dmap_write_read_array(self):
        array = pydarn.DmapArray('xcf', np.array([4.3, 3.5, 2.3]),
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
        dmap_array = dmap.read_array(len(dmap_array_bytes))
        self.compare_dmap_array(dmap_array, array)

    def test_read_write_rawacf(self):
        dmap = pydarn.DmapRead(rawacf_file)
        dmap_data = dmap.read_records()
        pydarn.DmapWrite(dmap_data,"test_rawacf.rawacf","rawacf")
        self.assertTrue(os.path.isfile("test_rawacf.rawacf"))
        os.remove("test_rawacf.rawacf")

        dmap_write = pydarn.DmapWrite(dmap_data)
        dmap_write.write_rawacf("test_rawacf.rawacf")
        self.assertTrue(os.path.isfile("test_rawacf.rawacf"))
        os.remove("test_rawacf.rawacf")

    def test_write_read_rawacf(self):
        rawacf_data = copy.deepcopy(rawacf_data_sets.rawacf_data)
        rawacf_write = pydarn.DmapWrite(rawacf_data, "test_rawacf.rawacf")
        rawacf_write.write_rawacf()

        rawacf_read = pydarn.DmapRead("test_rawacf.rawacf")
        rawacf_read_data = rawacf_read.read_records()
        self.dmap_compare(rawacf_read_data, rawacf_data)

    def test_read_write_stream_rawacf(self):
        with bz2.open(rawacf_stream) as fp:
            dmap_stream = fp.read()
        dmap = pydarn.DmapRead(dmap_stream, True)
        dmap_stream_data = dmap.read_records()
        dmap_write = pydarn.DmapWrite()
        dmap_write_stream = dmap_write.write_dmap_stream(dmap_stream_data)
        self.assertEqual(dmap_write_stream, bytearray(dmap_stream))

    def test_read_stream_write_file_rawacf(self):
        with bz2.open(rawacf_stream) as fp:
            dmap_stream = fp.read()
        dmap = pydarn.DmapRead(dmap_stream, True)
        dmap_stream_data = dmap.read_records()
        dmap_write = pydarn.DmapWrite(dmap_stream_data)
        dmap_write.write_rawacf("test_rawacf.rawacf")
        self.assertTrue(os.path.isfile("test_rawacf.rawacf"))

        dmap = pydarn.DmapRead("test_rawacf.rawacf")
        dmap_data = dmap.read_records()
        self.dmap_compare(dmap_stream_data, dmap_data)

    def test_write_stream_read_rawacf(self):
        rawacf_data = copy.deepcopy(rawacf_data_sets.rawacf_data)
        rawacf_write = pydarn.DmapWrite()
        rawacf_stream = rawacf_write.write_dmap_stream(rawacf_data)

        rawacf_read = pydarn.DmapRead(rawacf_stream, True)
        rawacf_read_data = rawacf_read.read_records()
        self.dmap_compare(rawacf_read_data, rawacf_data)


if __name__ == '__main__':
    """
    Runs the above class in a unittest system.
    Roughly takes 467 seconds.
    """
    pydarn_logger.info("Starting DMAP testing")

    unittest.main()
