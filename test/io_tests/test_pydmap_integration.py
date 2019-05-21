import pydarn
import unittest
import numpy as np
import logging
import bz2
import os

import rawacf_data_sets
import fitacf_data_sets
import iqdat_data_sets
import map_data_sets
import grid_data_sets
import dmap_data_sets
import copy


# Test files
rawacf_stream = "./testfiles/20170410.1801.00.sas.stream.rawacf.bz2"
rawacf_file = "./testfiles/20170410.1801.00.sas.rawacf"
fitacf_file = "./testfiles/20180220.C0.rkn.fitacf"
fitacf_stream = "./testfiles/20180220.C0.rkn.stream.fitacf.bz2"
map_file = "./testfiles/20170114.map"
map_stream = "./testfiles/20170114.stream.map.bz2"
iqdat_file = "testfiles/20160316.1945.01.rkn.iqdat"
iqdat_stream = "testfiles/20160316.1945.01.rkn.stream.iqdat.bz2"
grid_file = "./testfiles/20180220.C0.rkn.grid"
grid_stream = "./testfiles/20180220.C0.rkn.stream.grid.bz2"

pydarn_logger = logging.getLogger('pydarn')


class IntegrationPydmap(unittest.TestCase):
    def setUp(self):
        pass

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
            print(np.shape(dmaparr1.value), np.shape(dmaparr2.value))
            print(dmaparr1.value, dmaparr2.value)
            self.assertTrue(np.array_equal(dmaparr1.value, dmaparr2.value))

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
        with self.assertRaises(pydarn.pydmap_exceptions.DmapDataError):
            dmap_array = dmap.read_array(len(dmap_array_bytes))

    def test_read_write_rawacf(self):
        dmap = pydarn.DmapRead(rawacf_file)
        dmap_data = dmap.read_records()
        pydarn.DmapWrite(dmap_data, "test_rawacf.rawacf", "rawacf")
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
        dmap_write_stream = dmap_write.write_rawacf_stream(dmap_stream_data)
        dmap_read = pydarn.DmapRead(dmap_write_stream, True)
        dmap_read_data = dmap_read.read_records()
        self.dmap_compare(dmap_stream_data, dmap_read_data)

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
        rawacf_stream = rawacf_write.write_rawacf_stream(rawacf_data)

        rawacf_read = pydarn.DmapRead(rawacf_stream, True)
        rawacf_read_data = rawacf_read.read_records()
        self.dmap_compare(rawacf_read_data, rawacf_data)

    def test_read_write_fitacf(self):
        dmap = pydarn.DmapRead(fitacf_file)
        dmap_data = dmap.read_records()
        pydarn.DmapWrite(dmap_data, "test_fitacf.fitacf", "fitacf")
        self.assertTrue(os.path.isfile("test_fitacf.fitacf"))
        os.remove("test_fitacf.fitacf")

        dmap_write = pydarn.DmapWrite(dmap_data)
        dmap_write.write_fitacf("test_fitacf.fitacf")
        self.assertTrue(os.path.isfile("test_fitacf.fitacf"))
        os.remove("test_fitacf.fitacf")

    def test_write_read_fitacf(self):
        fitacf_data = copy.deepcopy(fitacf_data_sets.fitacf_data)
        fitacf_write = pydarn.DmapWrite(fitacf_data, "test_fitacf.fitacf")
        fitacf_write.write_fitacf()

        fitacf_read = pydarn.DmapRead("test_fitacf.fitacf")
        fitacf_read_data = fitacf_read.read_records()
        self.dmap_compare(fitacf_read_data, fitacf_data)

    def test_read_write_stream_fitacf(self):
        with bz2.open(fitacf_stream) as fp:
            dmap_stream = fp.read()
        dmap = pydarn.DmapRead(dmap_stream, True)
        dmap_stream_data = dmap.read_records()
        dmap_write = pydarn.DmapWrite()
        dmap_write_stream = dmap_write.write_fitacf_stream(dmap_stream_data)
        dmap_read = pydarn.DmapRead(dmap_write_stream, True)
        dmap_read_data = dmap_read.read_records()
        self.dmap_compare(dmap_stream_data, dmap_read_data)

    def test_read_stream_write_file_fitacf(self):
        with bz2.open(fitacf_stream) as fp:
            dmap_stream = fp.read()
        dmap = pydarn.DmapRead(dmap_stream, True)
        dmap_stream_data = dmap.read_records()
        dmap_write = pydarn.DmapWrite(dmap_stream_data)
        dmap_write.write_fitacf("test_fitacf.fitacf")
        self.assertTrue(os.path.isfile("test_fitacf.fitacf"))

        dmap = pydarn.DmapRead("test_fitacf.fitacf")
        dmap_data = dmap.read_records()
        self.dmap_compare(dmap_stream_data, dmap_data)

    def test_write_stream_read_fitacf(self):
        fitacf_data = copy.deepcopy(fitacf_data_sets.fitacf_data)
        fitacf_write = pydarn.DmapWrite()
        fitacf_stream = fitacf_write.write_fitacf_stream(fitacf_data)

        fitacf_read = pydarn.DmapRead(fitacf_stream, True)
        fitacf_read_data = fitacf_read.read_records()
        self.dmap_compare(fitacf_read_data, fitacf_data)

    def test_read_write_fitacf(self):
        dmap = pydarn.DmapRead(fitacf_file)
        dmap_data = dmap.read_records()
        pydarn.DmapWrite(dmap_data,"test_fitacf.fitacf","fitacf")
        self.assertTrue(os.path.isfile("test_fitacf.fitacf"))
        os.remove("test_fitacf.fitacf")

        dmap_write = pydarn.DmapWrite(dmap_data)
        dmap_write.write_fitacf("test_fitacf.fitacf")
        self.assertTrue(os.path.isfile("test_fitacf.fitacf"))
        os.remove("test_fitacf.fitacf")

    def test_write_read_fitacf(self):
        fitacf_data = copy.deepcopy(fitacf_data_sets.fitacf_data)
        fitacf_write = pydarn.DmapWrite(fitacf_data, "test_fitacf.fitacf")
        fitacf_write.write_fitacf()

        fitacf_read = pydarn.DmapRead("test_fitacf.fitacf")
        fitacf_read_data = fitacf_read.read_records()
        self.dmap_compare(fitacf_read_data, fitacf_data)

    def test_read_write_stream_fitacf(self):
        with bz2.open(fitacf_stream) as fp:
            dmap_stream = fp.read()
        dmap = pydarn.DmapRead(dmap_stream, True)
        dmap_stream_data = dmap.read_records()
        dmap_write = pydarn.DmapWrite()
        dmap_write_stream = dmap_write.write_fitacf_stream(dmap_stream_data)
        dmap_read = pydarn.DmapRead(dmap_write_stream, True)
        dmap_read_data = dmap_read.read_records()
        self.dmap_compare(dmap_stream_data, dmap_read_data)

    def test_read_stream_write_file_fitacf(self):
        with bz2.open(fitacf_stream) as fp:
            dmap_stream = fp.read()
        dmap = pydarn.DmapRead(dmap_stream, True)
        dmap_stream_data = dmap.read_records()
        dmap_write = pydarn.DmapWrite(dmap_stream_data)
        dmap_write.write_fitacf("test_fitacf.fitacf")
        self.assertTrue(os.path.isfile("test_fitacf.fitacf"))

        dmap = pydarn.DmapRead("test_fitacf.fitacf")
        dmap_data = dmap.read_records()
        self.dmap_compare(dmap_stream_data, dmap_data)

    def test_write_stream_read_fitacf(self):
        fitacf_data = copy.deepcopy(fitacf_data_sets.fitacf_data)
        fitacf_write = pydarn.DmapWrite()
        fitacf_stream = fitacf_write.write_fitacf_stream(fitacf_data)

        fitacf_read = pydarn.DmapRead(fitacf_stream, True)
        fitacf_read_data = fitacf_read.read_records()
        self.dmap_compare(fitacf_read_data, fitacf_data)

#    def test_read_write_iqdat(self):
#        dmap = pydarn.DmapRead(iqdat_file)
#        dmap_data = dmap.read_records()
#        pydarn.DmapWrite(dmap_data,"test_iqdat.iqdat","iqdat")
#        self.assertTrue(os.path.isfile("test_iqdat.iqdat"))
#        os.remove("test_iqdat.iqdat")
#
#        dmap_write = pydarn.DmapWrite(dmap_data)
#        dmap_write.write_iqdat("test_iqdat.iqdat")
#        self.assertTrue(os.path.isfile("test_iqdat.iqdat"))
#        os.remove("test_iqdat.iqdat")
#
#    def test_write_read_iqdat(self):
#        iqdat_data = copy.deepcopy(iqdat_data_sets.iqdat_data)
#        iqdat_write = pydarn.DmapWrite(iqdat_data, "test_iqdat.iqdat")
#        iqdat_write.write_iqdat()
#
#        iqdat_read = pydarn.DmapRead("test_iqdat.iqdat")
#        iqdat_read_data = iqdat_read.read_records()
#        self.dmap_compare(iqdat_read_data, iqdat_data)
#
#    def test_read_write_stream_iqdat(self):
#        with bz2.open(iqdat_stream) as fp:
#            dmap_stream = fp.read()
#        dmap = pydarn.DmapRead(dmap_stream, True)
#        dmap_stream_data = dmap.read_records()
#        dmap_write = pydarn.DmapWrite()
#        dmap_write_stream = dmap_write.write_iqdat_stream(dmap_stream_data)
#        dmap_read = pydarn.DmapRead(dmap_write_stream, True)
#        dmap_read_data = dmap_read.read_records()
#        self.dmap_compare(dmap_stream_data, dmap_read_data)
#
#    def test_read_stream_write_file_iqdat(self):
#        with bz2.open(iqdat_stream) as fp:
#            dmap_stream = fp.read()
#        dmap = pydarn.DmapRead(dmap_stream, True)
#        dmap_stream_data = dmap.read_records()
#        dmap_write = pydarn.DmapWrite(dmap_stream_data)
#        dmap_write.write_iqdat("test_iqdat.iqdat")
#        self.assertTrue(os.path.isfile("test_iqdat.iqdat"))
#
#        dmap = pydarn.DmapRead("test_iqdat.iqdat")
#        dmap_data = dmap.read_records()
#        self.dmap_compare(dmap_stream_data, dmap_data)
#
#    def test_write_stream_read_iqdat(self):
#        iqdat_data = copy.deepcopy(iqdat_data_sets.iqdat_data)
#        iqdat_write = pydarn.DmapWrite()
#        iqdat_stream = iqdat_write.write_iqdat_stream(iqdat_data)
#
#        iqdat_read = pydarn.DmapRead(iqdat_stream, True)
#        iqdat_read_data = iqdat_read.read_records()
#        self.dmap_compare(iqdat_read_data, iqdat_data)
#
#    def test_read_write_grid(self):
#        dmap = pydarn.DmapRead(grid_file)
#        dmap_data = dmap.read_records()
#        pydarn.DmapWrite(dmap_data,"test_grid.grid","grid")
#        self.assertTrue(os.path.isfile("test_grid.grid"))
#        os.remove("test_grid.grid")
#
#        dmap_write = pydarn.DmapWrite(dmap_data)
#        dmap_write.write_grid("test_grid.grid")
#        self.assertTrue(os.path.isfile("test_grid.grid"))
#        os.remove("test_grid.grid")
#
#    def test_write_read_grid(self):
#        grid_data = copy.deepcopy(grid_data_sets.grid_data)
#        grid_write = pydarn.DmapWrite(grid_data, "test_grid.grid")
#        grid_write.write_grid()
#
#        grid_read = pydarn.DmapRead("test_grid.grid")
#        grid_read_data = grid_read.read_records()
#        self.dmap_compare(grid_read_data, grid_data)
#
#    def test_read_write_stream_grid(self):
#        with bz2.open(grid_stream) as fp:
#            dmap_stream = fp.read()
#        dmap = pydarn.DmapRead(dmap_stream, True)
#        dmap_stream_data = dmap.read_records()
#        dmap_write = pydarn.DmapWrite()
#        dmap_write_stream = dmap_write.write_grid_stream(dmap_stream_data)
#        dmap_read = pydarn.DmapRead(dmap_write_stream, True)
#        dmap_read_data = dmap_read.read_records()
#        self.dmap_compare(dmap_stream_data, dmap_read_data)
#
#    def test_read_stream_write_file_grid(self):
#        with bz2.open(grid_stream) as fp:
#            dmap_stream = fp.read()
#        dmap = pydarn.DmapRead(dmap_stream, True)
#        dmap_stream_data = dmap.read_records()
#        dmap_write = pydarn.DmapWrite(dmap_stream_data)
#        dmap_write.write_grid("test_grid.grid")
#        self.assertTrue(os.path.isfile("test_grid.grid"))
#
#        dmap = pydarn.DmapRead("test_grid.grid")
#        dmap_data = dmap.read_records()
#        self.dmap_compare(dmap_stream_data, dmap_data)
#
#    def test_write_stream_read_grid(self):
#        grid_data = copy.deepcopy(grid_data_sets.grid_data)
#        grid_write = pydarn.DmapWrite()
#        grid_stream = grid_write.write_grid_stream(grid_data)
#
#        grid_read = pydarn.DmapRead(grid_stream, True)
#        grid_read_data = grid_read.read_records()
#        self.dmap_compare(grid_read_data, grid_data)
#
#    def test_read_write_map(self):
#        dmap = pydarn.DmapRead(map_file)
#        dmap_data = dmap.read_records()
#        pydarn.DmapWrite(dmap_data,"test_map.map","map")
#        self.assertTrue(os.path.isfile("test_map.map"))
#        os.remove("test_map.map")
#
#        dmap_write = pydarn.DmapWrite(dmap_data)
#        dmap_write.write_map("test_map.map")
#        self.assertTrue(os.path.isfile("test_map.map"))
#        os.remove("test_map.map")
#
#    def test_write_read_map(self):
#        map_data = copy.deepcopy(map_data_sets.map_data)
#        map_write = pydarn.DmapWrite(map_data, "test_map.map")
#        map_write.write_map()
#
#        map_read = pydarn.DmapRead("test_map.map")
#        map_read_data = map_read.read_records()
#        self.dmap_compare(map_read_data, map_data)
#
#    def test_read_write_stream_map(self):
#        with bz2.open(map_stream) as fp:
#            dmap_stream = fp.read()
#        dmap = pydarn.DmapRead(dmap_stream, True)
#        dmap_stream_data = dmap.read_records()
#        dmap_write = pydarn.DmapWrite()
#        dmap_write_stream = dmap_write.write_map_stream(dmap_stream_data)
#        dmap_read = pydarn.DmapRead(dmap_write_stream, True)
#        dmap_read_data = dmap_read.read_records()
#        self.dmap_compare(dmap_stream_data, dmap_read_data)
#
#    def test_read_stream_write_file_map(self):
#        with bz2.open(map_stream) as fp:
#            dmap_stream = fp.read()
#        dmap = pydarn.DmapRead(dmap_stream, True)
#        dmap_stream_data = dmap.read_records()
#        dmap_write = pydarn.DmapWrite(dmap_stream_data)
#        dmap_write.write_map("test_map.map")
#        self.assertTrue(os.path.isfile("test_map.map"))
#
#        dmap = pydarn.DmapRead("test_map.map")
#        dmap_data = dmap.read_records()
#        self.dmap_compare(dmap_stream_data, dmap_data)
#
#    def test_write_stream_read_map(self):
#        map_data = copy.deepcopy(map_data_sets.map_data)
#        map_write = pydarn.DmapWrite()
#        map_stream = map_write.write_map_stream(map_data)
#
#        map_read = pydarn.DmapRead(map_stream, True)
#        map_read_data = map_read.read_records()
#        self.dmap_compare(map_read_data, map_data)
#
#    def test_write_read_dmap(self):
#        dmap_data = copy.deepcopy(dmap_data_sets.dmap_data)
#        dmap_write = pydarn.DmapWrite(dmap_data, "test_dmap.dmap")
#        dmap_write.write_dmap()
#
#        dmap_read = pydarn.DmapRead("test_dmap.dmap")
#        dmap_read_data = dmap_read.read_records()
#        self.dmap_compare(dmap_read_data, dmap_data)
#
#    def test_write_stream_read_dmap(self):
#        dmap_data = copy.deepcopy(dmap_data_sets.dmap_data)
#        dmap_write = pydarn.DmapWrite()
#        dmap_stream = dmap_write.write_dmap_stream(dmap_data)
#
#        dmap_read = pydarn.DmapRead(dmap_stream, True)
#        dmap_read_data = dmap_read.read_records()
#        self.dmap_compare(dmap_read_data, dmap_data)



if __name__ == '__main__':
    """
    Runs the above class in a unittest system.
    Roughly takes 467 seconds.
    """
    pydarn_logger.info("Starting DMAP testing")

    unittest.main()
