import pydarn
import unittest
import numpy as np
import logging
import bz2
import os

import rawacf_data_sets
import rawacf_dict_sets
import fitacf_data_sets
import iqdat_data_sets
import map_data_sets
import grid_data_sets
import dmap_data_sets
import copy


# Test files
rawacf_stream = "../testfiles/20170410.1801.00.sas.stream.rawacf.bz2"
rawacf_file = "../testfiles/20170410.1801.00.sas.rawacf"
fitacf_file = "../testfiles/20180220.C0.rkn.fitacf"
fitacf_stream = "../testfiles/20180220.C0.rkn.stream.fitacf.bz2"
map_file = "../testfiles/20170114.map"
map_stream = "../testfiles/20170114.stream.map.bz2"
iqdat_file = "../testfiles/20160316.1945.01.rkn.iqdat"
iqdat_stream = "../testfiles/20160316.1945.01.rkn.stream.iqdat.bz2"
grid_file = "../testfiles/20180220.C0.rkn.grid"
grid_stream = "../testfiles/20180220.C0.rkn.stream.grid.bz2"

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
        value1 = np.reshape(dmaparr1.value, dmaparr1.shape)
        value2 = np.reshape(dmaparr2.value, dmaparr2.shape)
        if np.array_equal(value1, value2):
            self.assertTrue(np.array_equal(value1, value2))
        else:
            self.assertTrue(np.allclose(value1, value2, equal_nan=True))

    def test_Dmapread_DarnWrite_rawacf(self):
        dmap = pydarn.DmapRead(rawacf_file)
        dmap_data = dmap.read_records()
        dmap_write = pydarn.DarnWrite(dmap_data)
        dmap_write.write_rawacf("test_rawacf.rawacf")
        self.assertTrue(os.path.isfile("test_rawacf.rawacf"))
        os.remove("test_rawacf.rawacf")

    def test_DarnWrite_DarnRead_rawacf(self):
        rawacf_data = copy.deepcopy(rawacf_data_sets.rawacf_data)
        rawacf_write = pydarn.DarnWrite(rawacf_data, "test_rawacf.rawacf")
        rawacf_write.write_rawacf()

        rawacf_read = pydarn.DarnRead("test_rawacf.rawacf")
        rawacf_read_data = rawacf_read.read_rawacf()
        self.dmap_compare(rawacf_read_data, rawacf_data)
        os.remove("test_rawacf.rawacf")

    def test_DarnRead_stream_DarnWrite_file_rawacf(self):
        with bz2.open(rawacf_stream) as fp:
            dmap_stream = fp.read()
        dmap = pydarn.DarnRead(dmap_stream, True)
        dmap_stream_data = dmap.read_rawacf()
        dmap_write = pydarn.DarnWrite(dmap_stream_data)
        dmap_write.write_rawacf("test_rawacf.rawacf")
        dmap_read = pydarn.DarnRead("test_rawacf.rawacf")
        dmap_read_data = dmap_read.read_records()
        self.dmap_compare(dmap_stream_data, dmap_read_data)
        os.remove("test_rawacf.rawacf")

    def test_DmapWrite_missing_DarnRead_rawacf(self):
        rawacf_missing_field = copy.deepcopy(rawacf_data_sets.rawacf_data)
        del rawacf_missing_field[2]['nave']
        dmap_write = pydarn.DmapWrite(rawacf_missing_field)
        dmap_write.write_dmap("test_missing_rawacf.rawacf")

        darn_read = pydarn.DarnRead("test_missing_rawacf.rawacf")
        try:
            darn_read.read_rawacf()
        except pydarn.superdarn_exceptions.SuperDARNFieldMissingError as err:
            self.assertEqual(err.fields, {'nave'})
            self.assertEqual(err.record_number, 2)

        os.remove("test_missing_rawacf.rawacf")

    def test_DmapWrite_extra_DarnRead_rawacf(self):
        rawacf_extra_field = copy.deepcopy(rawacf_data_sets.rawacf_data)
        rawacf_extra_field[1].update({'dummy': pydarn.DmapScalar('dummy',
                                                                 'nothing',
                                                                 9, 's')})
        rawacf_extra_field[1].move_to_end('dummy', last=False)
        dmap_write = pydarn.DmapWrite(rawacf_extra_field, )
        dmap_write.write_dmap("test_extra_rawacf.rawacf")

        darn_read = pydarn.DarnRead("test_extra_rawacf.rawacf")
        try:
            darn_read.read_rawacf()
        except pydarn.superdarn_exceptions.SuperDARNExtraFieldError as err:
            self.assertEqual(err.fields, {'dummy'})
            self.assertEqual(err.record_number, 1)
        os.remove("test_extra_rawacf.rawacf")

    def test_dict2dmap_DarnWrite_rawacf(self):
        rawacf_dict_data = copy.deepcopy(rawacf_dict_sets.rawacf_dict_data)
        dmap_rawacf = pydarn.dict2dmap(rawacf_dict_data)
        darn_read = pydarn.DarnWrite(dmap_rawacf)
        darn_read.write_rawacf("test_rawacf.rawacf")
        dmap_read = pydarn.DmapRead("test_rawacf.rawacf")
        dmap_data = dmap_read.read_records()
        self.dmap_compare(dmap_data, dmap_rawacf)
        os.remove("test_rawacf.rawacf")

    def test_DarnWrite_incorrect_rawacf_from_dict(self):
        rawacf_dict_data = copy.deepcopy(rawacf_dict_sets.rawacf_dict_data)
        rawacf_dict_data[0]['stid'] = np.int8(rawacf_dict_data[0]['stid'])
        dmap_rawacf = pydarn.dict2dmap(rawacf_dict_data)
        darn_write = pydarn.DarnWrite(dmap_rawacf)
        with self.assertRaises(pydarn.superdarn_exceptions.SuperDARNDataFormatTypeError):
            darn_write.write_rawacf("test_rawacf.rawacf")

    def test_DmapWrite_incorrect_DarnRead_rawacf_from_dict(self):
        rawacf_dict_data = copy.deepcopy(rawacf_dict_sets.rawacf_dict_data)
        rawacf_dict_data[0]['stid'] = np.int8(rawacf_dict_data[0]['stid'])
        dmap_rawacf = pydarn.dict2dmap(rawacf_dict_data)
        dmap_write = pydarn.DmapWrite(dmap_rawacf)
        dmap_write.write_dmap("test_incorrect_rawacf.rawacf")

        darn_read = pydarn.DarnRead("test_incorrect_rawacf.rawacf")
        with self.assertRaises(pydarn.superdarn_exceptions.SuperDARNDataFormatTypeError):
            darn_read.read_rawacf()

    def test_Darnread_DarnWrite_fitacf(self):
        dmap = pydarn.DarnRead(fitacf_file)
        dmap_data = dmap.read_fitacf()
        dmap_write = pydarn.DarnWrite(dmap_data)
        dmap_write.write_fitacf("test_fitacf.fitacf")
        fitacf_read = pydarn.DarnRead("test_fitacf.fitacf")
        fitacf_read_data = fitacf_read.read_fitacf()
        self.dmap_compare(dmap_data, fitacf_read_data)
        os.remove("test_fitacf.fitacf")

    def test_DarnWrite_Darnread_fitacf(self):
        fitacf_data = copy.deepcopy(fitacf_data_sets.fitacf_data)
        fitacf_write = pydarn.DarnWrite(fitacf_data, "test_fitacf.fitacf")
        fitacf_write.write_fitacf()

        fitacf_read = pydarn.DarnRead("test_fitacf.fitacf")
        fitacf_read_data = fitacf_read.read_fitacf()
        self.dmap_compare(fitacf_read_data, fitacf_data)
        os.remove("test_fitacf.fitacf")

    def test_DarnRead_stream_DarnWrite_file_fitacf(self):
        with bz2.open(fitacf_stream) as fp:
            dmap_stream = fp.read()
        dmap = pydarn.DarnRead(dmap_stream, True)
        dmap_stream_data = dmap.read_fitacf()
        dmap_write = pydarn.DarnWrite(dmap_stream_data)
        dmap_write.write_fitacf("test_fitacf.fitacf")
        self.assertTrue(os.path.isfile("test_fitacf.fitacf"))
        dmap = pydarn.DarnRead("test_fitacf.fitacf")
        dmap_data = dmap.read_fitacf()
        self.dmap_compare(dmap_stream_data, dmap_data)

    def test_DmapRead_DarnWrite_DarnRead_fitacf(self):
        dmap = pydarn.DmapRead(fitacf_file)
        dmap_data = dmap.read_records()
        dmap_write = pydarn.DarnWrite(dmap_data)
        dmap_write.write_fitacf("test_fitacf.fitacf")
        darn_read = pydarn.DarnRead("test_fitacf.fitacf")
        fitacf_data = darn_read.read_fitacf()
        self.dmap_compare(dmap_data, fitacf_data)
        os.remove("test_fitacf.fitacf")

    def test_DarnWrite_file_Darnread_fitacf(self):
        fitacf_data = copy.deepcopy(fitacf_data_sets.fitacf_data)
        fitacf_write = pydarn.DarnWrite(fitacf_data, "test_fitacf.fitacf")
        fitacf_write.write_fitacf()

        fitacf_read = pydarn.DarnRead("test_fitacf.fitacf")
        fitacf_read_data = fitacf_read.read_fitacf()
        self.dmap_compare(fitacf_read_data, fitacf_data)
        os.remove("test_fitacf.fitacf")

    def test_DmapWrite_Darnread_fitacf(self):
        fitacf_data = copy.deepcopy(fitacf_data_sets.fitacf_data)
        fitacf_write = pydarn.DmapWrite(fitacf_data, "test_fitacf.fitacf")
        fitacf_write.write_dmap()

        fitacf_read = pydarn.DarnRead("test_fitacf.fitacf")
        fitacf_read_data = fitacf_read.read_fitacf()
        self.dmap_compare(fitacf_read_data, fitacf_data)
        os.remove("test_fitacf.fitacf")

    def test_DarRead_Dmapwrite_stream_fitacf(self):
        with bz2.open(fitacf_stream) as fp:
            dmap_stream = fp.read()
        dmap = pydarn.DarnRead(dmap_stream, True)
        dmap_stream_data = dmap.read_fitacf()
        dmap_write = pydarn.DmapWrite()
        dmap_write_stream = dmap_write.write_dmap_stream(dmap_stream_data)
        dmap_read = pydarn.DarnRead(dmap_write_stream, True)
        dmap_read_data = dmap_read.read_fitacf()
        self.dmap_compare(dmap_stream_data, dmap_read_data)

    def test_Dmapread_stream_Darnwrite_file_fitacf(self):
        with bz2.open(fitacf_stream) as fp:
            dmap_stream = fp.read()
        dmap = pydarn.DmapRead(dmap_stream, True)
        dmap_stream_data = dmap.read_records()
        dmap_write = pydarn.DarnWrite(dmap_stream_data)
        dmap_write.write_fitacf("test_fitacf.fitacf")
        dmap = pydarn.DarnRead("test_fitacf.fitacf")
        dmap_data = dmap.read_fitacf()
        self.dmap_compare(dmap_stream_data, dmap_data)
        os.remove("test_fitacf.fitacf")

    def test_DmapWrite_stream_DarnRead_fitacf(self):
        fitacf_data = copy.deepcopy(fitacf_data_sets.fitacf_data)
        fitacf_write = pydarn.DmapWrite()
        fitacf_stream = fitacf_write.write_dmap_stream(fitacf_data)

        fitacf_read = pydarn.DarnRead(fitacf_stream, True)
        fitacf_read_data = fitacf_read.read_fitacf()
        self.dmap_compare(fitacf_read_data, fitacf_data)

    def test_DmapWrite_missing_DarnRead_fitacf(self):
        fitacf_missing_field = copy.deepcopy(fitacf_data_sets.fitacf_data)
        del fitacf_missing_field[0]['nave']
        dmap_write = pydarn.DmapWrite(fitacf_missing_field)
        dmap_write.write_dmap("test_missing_fitacf.fitacf")

        darn_read = pydarn.DarnRead("test_missing_fitacf.fitacf")
        try:
            darn_read.read_fitacf()
        except pydarn.superdarn_exceptions.SuperDARNFieldMissingError as err:
            self.assertEqual(err.fields, {'nave'})
            self.assertEqual(err.record_number, 0)

        os.remove("test_missing_fitacf.fitacf")

    def test_DmapWrite_extra_DarnRead_fitacf(self):
        fitacf_extra_field = copy.deepcopy(fitacf_data_sets.fitacf_data)
        fitacf_extra_field[1].update({'dummy': pydarn.DmapScalar('dummy',
                                                                 'nothing',
                                                                 9, 's')})
        fitacf_extra_field[1].move_to_end('dummy', last=False)
        dmap_write = pydarn.DmapWrite(fitacf_extra_field, )
        dmap_write.write_dmap("test_extra_fitacf.fitacf")

        darn_read = pydarn.DarnRead("test_extra_fitacf.fitacf")
        try:
            darn_read.read_fitacf()
        except pydarn.superdarn_exceptions.SuperDARNExtraFieldError as err:
            self.assertEqual(err.fields, {'dummy'})
            self.assertEqual(err.record_number, 1)
        os.remove("test_extra_fitacf.fitacf")

    def test_Darnread_DarnWrite_iqdat(self):
        dmap = pydarn.DarnRead(iqdat_file)
        dmap_data = dmap.read_iqdat()
        dmap_write = pydarn.DarnWrite(dmap_data)
        dmap_write.write_iqdat("test_iqdat.iqdat")
        iqdat_read = pydarn.DarnRead("test_iqdat.iqdat")
        iqdat_read_data = iqdat_read.read_iqdat()
        self.dmap_compare(dmap_data, iqdat_read_data)
        os.remove("test_iqdat.iqdat")

    def test_DarnWrite_Darnread_iqdat(self):
        iqdat_data = copy.deepcopy(iqdat_data_sets.iqdat_data)
        iqdat_write = pydarn.DarnWrite(iqdat_data, "test_iqdat.iqdat")
        iqdat_write.write_iqdat()

        iqdat_read = pydarn.DarnRead("test_iqdat.iqdat")
        iqdat_read_data = iqdat_read.read_iqdat()
        self.dmap_compare(iqdat_read_data, iqdat_data)
        os.remove("test_iqdat.iqdat")

    def test_DarnRead_stream_DarnWrite_file_iqdat(self):
        with bz2.open(iqdat_stream) as fp:
            dmap_stream = fp.read()
        dmap = pydarn.DarnRead(dmap_stream, True)
        dmap_stream_data = dmap.read_iqdat()
        dmap_write = pydarn.DarnWrite(dmap_stream_data)
        dmap_write.write_iqdat("test_iqdat.iqdat")
        self.assertTrue(os.path.isfile("test_iqdat.iqdat"))
        dmap = pydarn.DarnRead("test_iqdat.iqdat")
        dmap_data = dmap.read_iqdat()
        self.dmap_compare(dmap_stream_data, dmap_data)

    def test_DmapRead_DarnWrite_DarnRead_iqdat(self):
        dmap = pydarn.DmapRead(iqdat_file)
        dmap_data = dmap.read_records()
        dmap_write = pydarn.DarnWrite(dmap_data)
        dmap_write.write_iqdat("test_iqdat.iqdat")
        darn_read = pydarn.DarnRead("test_iqdat.iqdat")
        iqdat_data = darn_read.read_iqdat()
        self.dmap_compare(dmap_data, iqdat_data)
        os.remove("test_iqdat.iqdat")

    def test_DarnWrite_file_Darnread_iqdat(self):
        iqdat_data = copy.deepcopy(iqdat_data_sets.iqdat_data)
        iqdat_write = pydarn.DarnWrite(iqdat_data, "test_iqdat.iqdat")
        iqdat_write.write_iqdat()

        iqdat_read = pydarn.DarnRead("test_iqdat.iqdat")
        iqdat_read_data = iqdat_read.read_iqdat()
        self.dmap_compare(iqdat_read_data, iqdat_data)
        os.remove("test_iqdat.iqdat")

    def test_DmapWrite_Darnread_iqdat(self):
        iqdat_data = copy.deepcopy(iqdat_data_sets.iqdat_data)
        iqdat_write = pydarn.DmapWrite(iqdat_data, "test_iqdat.iqdat")
        iqdat_write.write_dmap()

        iqdat_read = pydarn.DarnRead("test_iqdat.iqdat")
        iqdat_read_data = iqdat_read.read_iqdat()
        self.dmap_compare(iqdat_read_data, iqdat_data)
        os.remove("test_iqdat.iqdat")

    def test_DarRead_Dmapwrite_stream_iqdat(self):
        with bz2.open(iqdat_stream) as fp:
            dmap_stream = fp.read()
        dmap = pydarn.DarnRead(dmap_stream, True)
        dmap_stream_data = dmap.read_iqdat()
        dmap_write = pydarn.DmapWrite()
        dmap_write_stream = dmap_write.write_dmap_stream(dmap_stream_data)
        dmap_read = pydarn.DarnRead(dmap_write_stream, True)
        dmap_read_data = dmap_read.read_iqdat()
        self.dmap_compare(dmap_stream_data, dmap_read_data)

    def test_Dmapread_stream_Darnwrite_file_iqdat(self):
        with bz2.open(iqdat_stream) as fp:
            dmap_stream = fp.read()
        dmap = pydarn.DmapRead(dmap_stream, True)
        dmap_stream_data = dmap.read_records()
        dmap_write = pydarn.DarnWrite(dmap_stream_data)
        dmap_write.write_iqdat("test_iqdat.iqdat")
        dmap = pydarn.DarnRead("test_iqdat.iqdat")
        dmap_data = dmap.read_iqdat()
        self.dmap_compare(dmap_stream_data, dmap_data)
        os.remove("test_iqdat.iqdat")

    def test_DmapWrite_stream_DarnRead_iqdat(self):
        iqdat_data = copy.deepcopy(iqdat_data_sets.iqdat_data)
        iqdat_write = pydarn.DmapWrite()
        iqdat_stream = iqdat_write.write_dmap_stream(iqdat_data)

        iqdat_read = pydarn.DarnRead(iqdat_stream, True)
        iqdat_read_data = iqdat_read.read_iqdat()
        self.dmap_compare(iqdat_read_data, iqdat_data)

    def test_DmapWrite_missing_DarnRead_iqdat(self):
        iqdat_missing_field = copy.deepcopy(iqdat_data_sets.iqdat_data)
        del iqdat_missing_field[0]['nave']
        dmap_write = pydarn.DmapWrite(iqdat_missing_field)
        dmap_write.write_dmap("test_missing_iqdat.iqdat")

        darn_read = pydarn.DarnRead("test_missing_iqdat.iqdat")
        try:
            darn_read.read_iqdat()
        except pydarn.superdarn_exceptions.SuperDARNFieldMissingError as err:
            self.assertEqual(err.fields, {'nave'})
            self.assertEqual(err.record_number, 0)

        os.remove("test_missing_iqdat.iqdat")

    def test_DmapWrite_extra_DarnRead_iqdat(self):
        iqdat_extra_field = copy.deepcopy(iqdat_data_sets.iqdat_data)
        iqdat_extra_field[1].update({'dummy': pydarn.DmapScalar('dummy',
                                                                 'nothing',
                                                                 9, 's')})
        iqdat_extra_field[1].move_to_end('dummy', last=False)
        dmap_write = pydarn.DmapWrite(iqdat_extra_field, )
        dmap_write.write_dmap("test_extra_iqdat.iqdat")

        darn_read = pydarn.DarnRead("test_extra_iqdat.iqdat")
        try:
            darn_read.read_iqdat()
        except pydarn.superdarn_exceptions.SuperDARNExtraFieldError as err:
            self.assertEqual(err.fields, {'dummy'})
            self.assertEqual(err.record_number, 1)
        os.remove("test_extra_iqdat.iqdat")

    def test_Darnread_DarnWrite_grid(self):
        dmap = pydarn.DarnRead(grid_file)
        dmap_data = dmap.read_grid()
        dmap_write = pydarn.DarnWrite(dmap_data)
        dmap_write.write_grid("test_grid.grid")
        grid_read = pydarn.DarnRead("test_grid.grid")
        grid_read_data = grid_read.read_grid()
        self.dmap_compare(dmap_data, grid_read_data)
        os.remove("test_grid.grid")

    def test_DarnWrite_Darnread_grid(self):
        grid_data = copy.deepcopy(grid_data_sets.grid_data)
        grid_write = pydarn.DarnWrite(grid_data, "test_grid.grid")
        grid_write.write_grid()

        grid_read = pydarn.DarnRead("test_grid.grid")
        grid_read_data = grid_read.read_grid()
        self.dmap_compare(grid_read_data, grid_data)
        os.remove("test_grid.grid")

    def test_DarnRead_stream_DarnWrite_file_grid(self):
        with bz2.open(grid_stream) as fp:
            dmap_stream = fp.read()
        dmap = pydarn.DarnRead(dmap_stream, True)
        dmap_stream_data = dmap.read_grid()
        dmap_write = pydarn.DarnWrite(dmap_stream_data)
        dmap_write.write_grid("test_grid.grid")
        self.assertTrue(os.path.isfile("test_grid.grid"))
        dmap = pydarn.DarnRead("test_grid.grid")
        dmap_data = dmap.read_grid()
        self.dmap_compare(dmap_stream_data, dmap_data)

    def test_DmapRead_DarnWrite_DarnRead_grid(self):
        dmap = pydarn.DmapRead(grid_file)
        dmap_data = dmap.read_records()
        dmap_write = pydarn.DarnWrite(dmap_data)
        dmap_write.write_grid("test_grid.grid")
        darn_read = pydarn.DarnRead("test_grid.grid")
        grid_data = darn_read.read_grid()
        self.dmap_compare(dmap_data, grid_data)
        os.remove("test_grid.grid")

    def test_DarnWrite_file_Darnread_grid(self):
        grid_data = copy.deepcopy(grid_data_sets.grid_data)
        grid_write = pydarn.DarnWrite(grid_data, "test_grid.grid")
        grid_write.write_grid()

        grid_read = pydarn.DarnRead("test_grid.grid")
        grid_read_data = grid_read.read_grid()
        self.dmap_compare(grid_read_data, grid_data)
        os.remove("test_grid.grid")

    def test_DmapWrite_Darnread_grid(self):
        grid_data = copy.deepcopy(grid_data_sets.grid_data)
        grid_write = pydarn.DmapWrite(grid_data, "test_grid.grid")
        grid_write.write_dmap()

        grid_read = pydarn.DarnRead("test_grid.grid")
        grid_read_data = grid_read.read_grid()
        self.dmap_compare(grid_read_data, grid_data)
        os.remove("test_grid.grid")

    def test_DarRead_Dmapwrite_stream_grid(self):
        with bz2.open(grid_stream) as fp:
            dmap_stream = fp.read()
        dmap = pydarn.DarnRead(dmap_stream, True)
        dmap_stream_data = dmap.read_grid()
        dmap_write = pydarn.DmapWrite()
        dmap_write_stream = dmap_write.write_dmap_stream(dmap_stream_data)
        dmap_read = pydarn.DarnRead(dmap_write_stream, True)
        dmap_read_data = dmap_read.read_grid()
        self.dmap_compare(dmap_stream_data, dmap_read_data)

    def test_Dmapread_stream_Darnwrite_file_grid(self):
        with bz2.open(grid_stream) as fp:
            dmap_stream = fp.read()
        dmap = pydarn.DmapRead(dmap_stream, True)
        dmap_stream_data = dmap.read_records()
        dmap_write = pydarn.DarnWrite(dmap_stream_data)
        dmap_write.write_grid("test_grid.grid")
        dmap = pydarn.DarnRead("test_grid.grid")
        dmap_data = dmap.read_grid()
        self.dmap_compare(dmap_stream_data, dmap_data)
        os.remove("test_grid.grid")

    def test_DmapWrite_stream_DarnRead_grid(self):
        grid_data = copy.deepcopy(grid_data_sets.grid_data)
        grid_write = pydarn.DmapWrite()
        grid_stream = grid_write.write_dmap_stream(grid_data)

        grid_read = pydarn.DarnRead(grid_stream, True)
        grid_read_data = grid_read.read_grid()
        self.dmap_compare(grid_read_data, grid_data)

    def test_DmapWrite_missing_DarnRead_grid(self):
        grid_missing_field = copy.deepcopy(grid_data_sets.grid_data)
        del grid_missing_field[0]['stid']
        dmap_write = pydarn.DmapWrite(grid_missing_field)
        dmap_write.write_dmap("test_missing_grid.grid")

        darn_read = pydarn.DarnRead("test_missing_grid.grid")
        try:
            darn_read.read_grid()
        except pydarn.superdarn_exceptions.SuperDARNFieldMissingError as err:
            self.assertEqual(err.fields, {'stid'})
            self.assertEqual(err.record_number, 0)

        os.remove("test_missing_grid.grid")

    def test_DmapWrite_extra_DarnRead_grid(self):
        grid_extra_field = copy.deepcopy(grid_data_sets.grid_data)
        grid_extra_field[1].update({'dummy': pydarn.DmapScalar('dummy',
                                                                 'nothing',
                                                                 9, 's')})
        grid_extra_field[1].move_to_end('dummy', last=False)
        dmap_write = pydarn.DmapWrite(grid_extra_field, )
        dmap_write.write_dmap("test_extra_grid.grid")

        darn_read = pydarn.DarnRead("test_extra_grid.grid")
        try:
            darn_read.read_grid()
        except pydarn.superdarn_exceptions.SuperDARNExtraFieldError as err:
            self.assertEqual(err.fields, {'dummy'})
            self.assertEqual(err.record_number, 1)
        os.remove("test_extra_grid.grid")

    def test_Darnread_DarnWrite_map(self):
        dmap = pydarn.DarnRead(map_file)
        dmap_data = dmap.read_map()
        dmap_write = pydarn.DarnWrite(dmap_data)
        dmap_write.write_map("test_map.map")
        map_read = pydarn.DarnRead("test_map.map")
        map_read_data = map_read.read_map()
        self.dmap_compare(dmap_data, map_read_data)
        os.remove("test_map.map")

    def test_DarnWrite_Darnread_map(self):
        map_data = copy.deepcopy(map_data_sets.map_data)
        map_write = pydarn.DarnWrite(map_data, "test_map.map")
        map_write.write_map()

        map_read = pydarn.DarnRead("test_map.map")
        map_read_data = map_read.read_map()
        self.dmap_compare(map_read_data, map_data)
        os.remove("test_map.map")

    def test_DarnRead_stream_DarnWrite_file_map(self):
        with bz2.open(map_stream) as fp:
            dmap_stream = fp.read()
        dmap = pydarn.DarnRead(dmap_stream, True)
        dmap_stream_data = dmap.read_map()
        dmap_write = pydarn.DarnWrite(dmap_stream_data)
        dmap_write.write_map("test_map.map")
        self.assertTrue(os.path.isfile("test_map.map"))
        dmap = pydarn.DarnRead("test_map.map")
        dmap_data = dmap.read_map()
        self.dmap_compare(dmap_stream_data, dmap_data)

    def test_DmapRead_DarnWrite_DarnRead_map(self):
        dmap = pydarn.DmapRead(map_file)
        dmap_data = dmap.read_records()
        dmap_write = pydarn.DarnWrite(dmap_data)
        dmap_write.write_map("test_map.map")
        darn_read = pydarn.DarnRead("test_map.map")
        map_data = darn_read.read_map()
        self.dmap_compare(dmap_data, map_data)
        os.remove("test_map.map")

    def test_DarnWrite_file_Darnread_map(self):
        map_data = copy.deepcopy(map_data_sets.map_data)
        map_write = pydarn.DarnWrite(map_data, "test_map.map")
        map_write.write_map()

        map_read = pydarn.DarnRead("test_map.map")
        map_read_data = map_read.read_map()
        self.dmap_compare(map_read_data, map_data)
        os.remove("test_map.map")

    def test_DmapWrite_Darnread_map(self):
        map_data = copy.deepcopy(map_data_sets.map_data)
        map_write = pydarn.DmapWrite(map_data, "test_map.map")
        map_write.write_dmap()

        map_read = pydarn.DarnRead("test_map.map")
        map_read_data = map_read.read_map()
        self.dmap_compare(map_read_data, map_data)
        os.remove("test_map.map")

    def test_DarRead_Dmapwrite_stream_map(self):
        with bz2.open(map_stream) as fp:
            dmap_stream = fp.read()
        dmap = pydarn.DarnRead(dmap_stream, True)
        dmap_stream_data = dmap.read_map()
        dmap_write = pydarn.DmapWrite()
        dmap_write_stream = dmap_write.write_dmap_stream(dmap_stream_data)
        dmap_read = pydarn.DarnRead(dmap_write_stream, True)
        dmap_read_data = dmap_read.read_map()
        self.dmap_compare(dmap_stream_data, dmap_read_data)

    def test_Dmapread_stream_Darnwrite_file_map(self):
        with bz2.open(map_stream) as fp:
            dmap_stream = fp.read()
        dmap = pydarn.DmapRead(dmap_stream, True)
        dmap_stream_data = dmap.read_records()
        dmap_write = pydarn.DarnWrite(dmap_stream_data)
        dmap_write.write_map("test_map.map")
        dmap = pydarn.DarnRead("test_map.map")
        dmap_data = dmap.read_map()
        self.dmap_compare(dmap_stream_data, dmap_data)
        os.remove("test_map.map")

    def test_DmapWrite_stream_DarnRead_map(self):
        map_data = copy.deepcopy(map_data_sets.map_data)
        map_write = pydarn.DmapWrite()
        map_stream = map_write.write_dmap_stream(map_data)

        map_read = pydarn.DarnRead(map_stream, True)
        map_read_data = map_read.read_map()
        self.dmap_compare(map_read_data, map_data)

    def test_DmapWrite_missing_DarnRead_map(self):
        map_missing_field = copy.deepcopy(map_data_sets.map_data)
        del map_missing_field[0]['stid']
        dmap_write = pydarn.DmapWrite(map_missing_field)
        dmap_write.write_dmap("test_missing_map.map")

        darn_read = pydarn.DarnRead("test_missing_map.map")
        try:
            darn_read.read_map()
        except pydarn.superdarn_exceptions.SuperDARNFieldMissingError as err:
            self.assertEqual(err.fields, {'stid'})
            self.assertEqual(err.record_number, 0)

        os.remove("test_missing_map.map")

    def test_DmapWrite_extra_DarnRead_map(self):
        map_extra_field = copy.deepcopy(map_data_sets.map_data)
        map_extra_field[1].update({'dummy': pydarn.DmapScalar('dummy',
                                                                 'nothing',
                                                                 9, 's')})
        map_extra_field[1].move_to_end('dummy', last=False)
        dmap_write = pydarn.DmapWrite(map_extra_field, )
        dmap_write.write_dmap("test_extra_map.map")

        darn_read = pydarn.DarnRead("test_extra_map.map")
        try:
            darn_read.read_map()
        except pydarn.superdarn_exceptions.SuperDARNExtraFieldError as err:
            self.assertEqual(err.fields, {'dummy'})
            self.assertEqual(err.record_number, 1)
        os.remove("test_extra_map.map")


if __name__ == '__main__':
    """
    Runs the above class in a unittest system.
    Roughly takes 467 seconds.
    """
    pydarn_logger.info("Starting DMAP testing")

    unittest.main()
