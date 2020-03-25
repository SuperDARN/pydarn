# Copyright (C) 2019 SuperDARN
# Author: Marina Schmidt
import bz2
import copy
import logging
import numpy as np
import os
import unittest

import pydarn

import fitacf_data_sets
import grid_data_sets
import iqdat_data_sets
import map_data_sets
import rawacf_data_sets
import rawacf_dict_sets

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


class IntegrationSuperdarnio(unittest.TestCase):
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
                elif isinstance(val_obj, pydarn.DmapArray):
                    self.compare_dmap_array(record2[field], val_obj)
                elif isinstance(val_obj, np.ndarray):
                    if np.array_equal(record2[field], val_obj):
                        self.assertTrue(np.array_equal(record2[field],
                                                       val_obj))
                    else:
                        self.assertTrue(np.allclose(record2[field], val_obj,
                                                    equal_nan=True))
                else:
                    self.assertEqual(val_obj, record2[field])

    def compare_dmap_array(self, dmaparr1, dmaparr2):
        try:
            self.assertEqual(dmaparr1.name, dmaparr2.name)
            self.assertEqual(dmaparr1.data_type, dmaparr2.data_type)
            self.assertEqual(dmaparr1.data_type_fmt, dmaparr2.data_type_fmt)
            self.assertEqual(dmaparr1.dimension, dmaparr2.dimension)
            value1 = np.reshape(dmaparr1.value, dmaparr1.shape)
            value2 = np.reshape(dmaparr2.value, dmaparr2.shape)
        except AttributeError:
            self.assertEqual(dmaparr1.key, dmaparr2.key)
        if np.array_equal(value1, value2):
            self.assertTrue(np.array_equal(value1, value2))
        else:
            self.assertTrue(np.allclose(value1, value2, equal_nan=True))

    def test_DmapRead_SDarnWrite_rawacf(self):
        """
        Test DmapRead reading an rawacf and SDarnWrite writing
        the rawacf file
        """
        dmap = pydarn.DmapRead(rawacf_file)
        dmap_data = dmap.read_records()
        dmap_write = pydarn.SDarnWrite(dmap_data)
        dmap_write.write_rawacf("test_rawacf.rawacf")
        self.assertTrue(os.path.isfile("test_rawacf.rawacf"))
        os.remove("test_rawacf.rawacf")

    def test_SDarnWrite_SDarnRead_rawacf(self):
        """
        Test SDarnWrite writing a rawacf file and SDarnRead reading the rawacf
        file
        """
        rawacf_data = copy.deepcopy(rawacf_data_sets.rawacf_data)
        rawacf_write = pydarn.SDarnWrite(rawacf_data, "test_rawacf.rawacf")
        rawacf_write.write_rawacf()

        rawacf_read = pydarn.SDarnRead("test_rawacf.rawacf")
        rawacf_read_data = rawacf_read.read_rawacf()
        self.dmap_compare(rawacf_read_data, rawacf_data)
        os.remove("test_rawacf.rawacf")

    def test_SDarnRead_stream_SDarnWrite_file_rawacf(self):
        """
        Test SDarnRead reads from a stream and SDarnWrite writes
        to a rawacf file
        """
        with bz2.open(rawacf_stream) as fp:
            dmap_stream = fp.read()
        dmap = pydarn.SDarnRead(dmap_stream, True)
        stream_data = dmap.read_rawacf()
        dmap_stream_data = dmap.get_dmap_records
        dmap_write = pydarn.SDarnWrite(stream_data)
        dmap_write.write_rawacf("test_rawacf.rawacf")
        dmap_read = pydarn.SDarnRead("test_rawacf.rawacf")
        _ = dmap_read.read_records()
        dmap_data = dmap_read.get_dmap_records
        self.dmap_compare(dmap_stream_data, dmap_data)
        os.remove("test_rawacf.rawacf")

    def test_DmapWrite_missing_SDarnRead_rawacf(self):
        """
        Test DmapWrite writes a rawacf file missing the field nave in record 2
        and SDarnRead reads the file

        Behaviour: Raise SuperDARNFieldMissingError
        """
        rawacf_missing_field = copy.deepcopy(rawacf_data_sets.rawacf_data)
        del rawacf_missing_field[0]['nave']
        dmap_write = pydarn.DmapWrite(rawacf_missing_field)
        dmap_write.write_dmap("test_missing_rawacf.rawacf")

        darn_read = pydarn.SDarnRead("test_missing_rawacf.rawacf")
        try:
            darn_read.read_rawacf()
        except pydarn.superdarn_exceptions.SuperDARNFieldMissingError as err:
            self.assertEqual(err.fields, {'nave'})
            self.assertEqual(err.record_number, 0)

        os.remove("test_missing_rawacf.rawacf")

    def test_DmapWrite_extra_SDarnRead_rawacf(self):
        """
        Test DmapWrite writes a rawacf file with an extra field and SDarnRead
        reads the file

        Behaviour: Raised SuperDARNExtraFieldError
        """
        rawacf_extra_field = copy.deepcopy(rawacf_data_sets.rawacf_data)
        rawacf_extra_field[0].update({'dummy': 'dummy'})
        rawacf_extra_field[0].move_to_end('dummy', last=False)
        dmap_write = pydarn.DmapWrite(rawacf_extra_field, )
        dmap_write.write_dmap("test_extra_rawacf.rawacf")

        darn_read = pydarn.SDarnRead("test_extra_rawacf.rawacf")
        try:
            darn_read.read_rawacf()
        except pydarn.superdarn_exceptions.SuperDARNExtraFieldError as err:
            self.assertEqual(err.fields, {'dummy'})
            self.assertEqual(err.record_number, 0)
        os.remove("test_extra_rawacf.rawacf")

    def test_dict2dmap_SDarnWrite_rawacf(self):
        """
        Test dict2dmap to convert a dictionary to dmap then SDarnWrite write
        rawacf file
        """
        rawacf_dict_data = copy.deepcopy(rawacf_dict_sets.rawacf_dict_data)
        dmap_rawacf = pydarn.dict2dmap(rawacf_dict_data)
        darn_read = pydarn.SDarnWrite(dmap_rawacf)
        darn_read.write_rawacf("test_rawacf.rawacf")
        dmap_read = pydarn.DmapRead("test_rawacf.rawacf")
        dmap_data = dmap_read.read_records()
        dmap_data = dmap_read.get_dmap_records
        self.dmap_compare(dmap_data, dmap_rawacf)
        os.remove("test_rawacf.rawacf")

    def test_SDarnWrite_incorrect_rawacf_from_dict(self):
        """
        Test convert dictionary with incorrect type to dmap and SDarnWrite
        write the rawacf file

        Behaviour: Raise SuperDARNDataFormatTypeError
        """
        rawacf_dict_data = copy.deepcopy(rawacf_dict_sets.rawacf_dict_data)
        rawacf_dict_data[0]['stid'] = np.int8(rawacf_dict_data[0]['stid'])
        dmap_rawacf = pydarn.dict2dmap(rawacf_dict_data)
        darn_write = pydarn.SDarnWrite(dmap_rawacf)
        with self.assertRaises(pydarn.superdarn_exceptions.
                               SuperDARNDataFormatTypeError):
            darn_write.write_rawacf("test_rawacf.rawacf")

    def test_DmapWrite_incorrect_SDarnRead_rawacf_from_dict(self):
        """
        Test write an incorrect data type from a dict converting from dict2dmap
        with DmapWrite then SDarnRead reads the file

        Behaviour: Raises SuperDARNDataFormatTypeError
        """
        rawacf_dict_data = copy.deepcopy(rawacf_dict_sets.rawacf_dict_data)
        rawacf_dict_data[0]['stid'] = np.int8(rawacf_dict_data[0]['stid'])
        dmap_rawacf = pydarn.dict2dmap(rawacf_dict_data)
        dmap_write = pydarn.DmapWrite(dmap_rawacf)
        dmap_write.write_dmap("test_incorrect_rawacf.rawacf")

        darn_read = pydarn.SDarnRead("test_incorrect_rawacf.rawacf")
        with self.assertRaises(pydarn.superdarn_exceptions.
                               SuperDARNDataFormatTypeError):
            darn_read.read_rawacf()

    def test_SDarnRead_SDarnWrite_fitacf(self):
        """
        Test DmapRead reading an fitacf and SDarnWrite writing
        the fitacf file
        """
        dmap = pydarn.SDarnRead(fitacf_file)
        dmap_data = dmap.read_fitacf()
        dmap_write = pydarn.SDarnWrite(dmap_data)
        dmap_write.write_fitacf("test_fitacf.fitacf")
        fitacf_read = pydarn.SDarnRead("test_fitacf.fitacf")
        fitacf_read_data = fitacf_read.read_fitacf()
        self.dmap_compare(dmap_data, fitacf_read_data)
        os.remove("test_fitacf.fitacf")

    def test_SDarnWrite_SDarnRead_fitacf(self):
        """
        Test SDarnWrite writing a fitacf file and SDarnRead reading the fitacf
        file
        """
        fitacf_data = copy.deepcopy(fitacf_data_sets.fitacf_data)
        fitacf_write = pydarn.SDarnWrite(fitacf_data, "test_fitacf.fitacf")
        fitacf_write.write_fitacf()
        fitacf_read = pydarn.SDarnRead("test_fitacf.fitacf")
        fitacf_read_data = fitacf_read.read_fitacf()
        self.dmap_compare(fitacf_read_data, fitacf_data)
        os.remove("test_fitacf.fitacf")

    def test_SDarnRead_stream_SDarnWrite_file_fitacf(self):
        """
        Test SDarnRead reads from a stream and SDarnWrite writes
        to a fitacf file
        """
        with bz2.open(fitacf_stream) as fp:
            dmap_stream = fp.read()
        dmap = pydarn.SDarnRead(dmap_stream, True)
        stream_data = dmap.read_fitacf()
        dmap_stream_data = dmap.get_dmap_records
        dmap_write = pydarn.SDarnWrite(stream_data)
        dmap_write.write_fitacf("test_fitacf.fitacf")
        self.assertTrue(os.path.isfile("test_fitacf.fitacf"))
        dmap = pydarn.SDarnRead("test_fitacf.fitacf")
        _ = dmap.read_fitacf()
        dmap_read_data = dmap.get_dmap_records
        self.dmap_compare(dmap_stream_data, dmap_read_data)

    def test_DmapRead_SDarnWrite_SDarnRead_fitacf(self):
        """
        Test DmapRead reading a fitacf file then writing it with SDarnWrite
        then reading it again with SDarnRead
        """
        dmap = pydarn.DmapRead(fitacf_file)
        dmap_data = dmap.read_records()
        dmap_write = pydarn.SDarnWrite(dmap_data)
        dmap_write.write_fitacf("test_fitacf.fitacf")
        darn_read = pydarn.SDarnRead("test_fitacf.fitacf")
        fitacf_data = darn_read.read_fitacf()
        self.dmap_compare(dmap_data, fitacf_data)
        os.remove("test_fitacf.fitacf")

    def test_SDarnWrite_file_SDarnRead_fitacf(self):
        """
        Test SDarnWrite to write a fitacf file then using
        SDarnRead to read the file
        """
        fitacf_data = copy.deepcopy(fitacf_data_sets.fitacf_data)
        fitacf_write = pydarn.SDarnWrite(fitacf_data, "test_fitacf.fitacf")
        fitacf_write.write_fitacf()

        fitacf_read = pydarn.SDarnRead("test_fitacf.fitacf")
        fitacf_read_data = fitacf_read.read_fitacf()
        self.dmap_compare(fitacf_read_data, fitacf_data)
        os.remove("test_fitacf.fitacf")

    def test_DmapWrite_SDarnRead_fitacf(self):
        """
        Test DmapWrite to write a fitacf file then using SDarnRead
        to read the file
        """
        fitacf_data = copy.deepcopy(fitacf_data_sets.fitacf_data)
        fitacf_write = pydarn.DmapWrite(fitacf_data, "test_fitacf.fitacf")
        fitacf_write.write_dmap()

        fitacf_read = pydarn.SDarnRead("test_fitacf.fitacf")
        fitacf_read_data = fitacf_read.read_fitacf()
        self.dmap_compare(fitacf_read_data, fitacf_data)
        os.remove("test_fitacf.fitacf")

    def test_SDarnRead_DmapWrite_stream_fitacf(self):
        """
        Test SDarnRead to read from a fitacf stream then
        DmapWrite to write a fitacf file from the stream
        """
        with bz2.open(fitacf_stream) as fp:
            dmap_stream = fp.read()
        dmap = pydarn.SDarnRead(dmap_stream, True)
        stream_data = dmap.read_fitacf()
        dmap_stream_data = dmap.get_dmap_records
        dmap_write = pydarn.DmapWrite()
        dmap_write_stream = dmap_write.write_dmap_stream(stream_data)
        dmap_read = pydarn.SDarnRead(dmap_write_stream, True)
        dmap_read_data = dmap_read.read_fitacf()
        dmap_read_data = dmap_read.get_dmap_records

        self.dmap_compare(dmap_stream_data, dmap_read_data)

    def test_DmapRead_stream_SDarnWrite_file_fitacf(self):
        """
        Test DmapRead to read in a stream then have SDarnWrite the
        stream to file
        """
        with bz2.open(fitacf_stream) as fp:
            dmap_stream = fp.read()
        dmap = pydarn.DmapRead(dmap_stream, True)
        stream_data = dmap.read_records()
        dmap_stream_data = dmap.get_dmap_records
        dmap_write = pydarn.SDarnWrite(stream_data)
        dmap_write.write_fitacf("test_fitacf.fitacf")
        dmap = pydarn.SDarnRead("test_fitacf.fitacf")
        dmap_data = dmap.read_fitacf()
        dmap_data = dmap.get_dmap_records
        self.dmap_compare(dmap_stream_data, dmap_data)
        os.remove("test_fitacf.fitacf")

    def test_DmapWrite_stream_SDarnRead_fitacf(self):
        """
        Test DmapWrite to write to a stream and have SDarnRead
        the fitacf stream
        """
        fitacf_data = copy.deepcopy(fitacf_data_sets.fitacf_data)
        fitacf_write = pydarn.DmapWrite()
        fitacf_stream = fitacf_write.write_dmap_stream(fitacf_data)

        fitacf_read = pydarn.SDarnRead(fitacf_stream, True)
        fitacf_read_data = fitacf_read.read_fitacf()
        self.dmap_compare(fitacf_read_data, fitacf_data)

    def test_DmapWrite_missing_SDarnRead_fitacf(self):
        """
        Test DmapWrite writes a fitacf file missing the field nave in record 2
        and SDarnRead reads the file

        Behaviour: Raise SuperDARNFieldMissingError
        """
        fitacf_missing_field = copy.deepcopy(fitacf_data_sets.fitacf_data)
        del fitacf_missing_field[0]['nave']
        dmap_write = pydarn.DmapWrite(fitacf_missing_field)
        dmap_write.write_dmap("test_missing_fitacf.fitacf")

        darn_read = pydarn.SDarnRead("test_missing_fitacf.fitacf")
        try:
            darn_read.read_fitacf()
        except pydarn.superdarn_exceptions.SuperDARNFieldMissingError as err:
            self.assertEqual(err.fields, {'nave'})
            self.assertEqual(err.record_number, 0)

        os.remove("test_missing_fitacf.fitacf")

    def test_DmapWrite_extra_SDarnRead_fitacf(self):
        """
        Test DmapWrite writes a fitacf file with an extra field and SDarnRead
        reads the file

        Behaviour: Raised SuperDARNExtraFieldError
        """

        fitacf_extra_field = copy.deepcopy(fitacf_data_sets.fitacf_data)
        fitacf_extra_field[0].update({'dummy': 'dummy'})
        fitacf_extra_field[0].move_to_end('dummy', last=False)
        dmap_write = pydarn.DmapWrite(fitacf_extra_field, )
        dmap_write.write_dmap("test_extra_fitacf.fitacf")

        darn_read = pydarn.SDarnRead("test_extra_fitacf.fitacf")
        try:
            darn_read.read_fitacf()
        except pydarn.superdarn_exceptions.SuperDARNExtraFieldError as err:
            self.assertEqual(err.fields, {'dummy'})
            self.assertEqual(err.record_number, 0)
        os.remove("test_extra_fitacf.fitacf")

    def test_SDarnRead_SDarnWrite_iqdat(self):
        """
        Test DmapRead reading an fitacf and SDarnWrite writing
        the fitacf file
        """
        dmap = pydarn.SDarnRead(iqdat_file)
        dmap_data = dmap.read_iqdat()
        dmap_write = pydarn.SDarnWrite(dmap_data)
        dmap_write.write_iqdat("test_iqdat.iqdat")
        iqdat_read = pydarn.SDarnRead("test_iqdat.iqdat")
        iqdat_read_data = iqdat_read.read_iqdat()
        self.dmap_compare(dmap_data, iqdat_read_data)
        os.remove("test_iqdat.iqdat")

    def test_SDarnWrite_SDarnRead_iqdat(self):
        """
        Test SDarnWrite writing a iqdat file and SDarnRead reading the iqdat
        file
        """
        iqdat_data = copy.deepcopy(iqdat_data_sets.iqdat_data)
        iqdat_write = pydarn.SDarnWrite(iqdat_data, "test_iqdat.iqdat")
        iqdat_write.write_iqdat()
        iqdat_read = pydarn.SDarnRead("test_iqdat.iqdat")
        iqdat_read_data = iqdat_read.read_iqdat()
        self.dmap_compare(iqdat_read_data, iqdat_data)
        os.remove("test_iqdat.iqdat")

    def test_SDarnRead_stream_SDarnWrite_file_iqdat(self):
        """
        Test SDarnRead reads from a stream and SDarnWrite writes
        to a iqdat file
        """
        with bz2.open(iqdat_stream) as fp:
            dmap_stream = fp.read()
        dmap = pydarn.SDarnRead(dmap_stream, True)
        stream_data = dmap.read_iqdat()
        dmap_stream_data = dmap.get_dmap_records
        dmap_write = pydarn.SDarnWrite(stream_data)
        dmap_write.write_iqdat("test_iqdat.iqdat")
        self.assertTrue(os.path.isfile("test_iqdat.iqdat"))
        dmap = pydarn.SDarnRead("test_iqdat.iqdat")
        _ = dmap.read_iqdat()
        dmap_read_data = dmap.get_dmap_records
        self.dmap_compare(dmap_stream_data, dmap_read_data)

    def test_DmapRead_SDarnWrite_SDarnRead_iqdat(self):
        """
        Test SDarnRead reads from a stream and SDarnWrite writes
        to a iqdat file
        """
        dmap = pydarn.DmapRead(iqdat_file)
        dmap_data = dmap.read_records()
        dmap_write = pydarn.SDarnWrite(dmap_data)
        dmap_write.write_iqdat("test_iqdat.iqdat")
        darn_read = pydarn.SDarnRead("test_iqdat.iqdat")
        iqdat_data = darn_read.read_iqdat()
        self.dmap_compare(dmap_data, iqdat_data)
        os.remove("test_iqdat.iqdat")

    def test_SDarnWrite_file_SDarnRead_iqdat(self):
        """
        Test SDarnWrite to write a iqdat file then using
        SDarnRead to read the file
        """
        iqdat_data = copy.deepcopy(iqdat_data_sets.iqdat_data)
        iqdat_write = pydarn.SDarnWrite(iqdat_data, "test_iqdat.iqdat")
        iqdat_write.write_iqdat()

        iqdat_read = pydarn.SDarnRead("test_iqdat.iqdat")
        iqdat_read_data = iqdat_read.read_iqdat()
        self.dmap_compare(iqdat_read_data, iqdat_data)
        os.remove("test_iqdat.iqdat")

    def test_DmapWrite_SDarnRead_iqdat(self):
        """
        Test DmapWrite to write a iqdat file then using SDarnRead
        to read the file
        """
        iqdat_data = copy.deepcopy(iqdat_data_sets.iqdat_data)
        iqdat_write = pydarn.DmapWrite(iqdat_data, "test_iqdat.iqdat")
        iqdat_write.write_dmap()

        iqdat_read = pydarn.SDarnRead("test_iqdat.iqdat")
        iqdat_read_data = iqdat_read.read_iqdat()
        self.dmap_compare(iqdat_read_data, iqdat_data)
        os.remove("test_iqdat.iqdat")

    def test_SDarnRead_DmapWrite_stream_iqdat(self):
        """
        Test SDarnRead to read from a iqdat stream then
        DmapWrite to write a iqdat file from the stream
        """
        with bz2.open(iqdat_stream) as fp:
            dmap_stream = fp.read()
        dmap = pydarn.SDarnRead(dmap_stream, True)
        dmap_stream_data = dmap.read_iqdat()
        dmap_write = pydarn.DmapWrite()
        dmap_write_stream = dmap_write.write_dmap_stream(dmap_stream_data)
        dmap_read = pydarn.SDarnRead(dmap_write_stream, True)
        dmap_read_data = dmap_read.read_iqdat()
        self.dmap_compare(dmap_stream_data, dmap_read_data)

    def test_DmapRead_stream_SDarnWrite_file_iqdat(self):
        """
        Test DmapRead to read in a stream then have SDarnWrite the
        stream to file
        """
        with bz2.open(iqdat_stream) as fp:
            dmap_stream = fp.read()
        dmap = pydarn.DmapRead(dmap_stream, True)
        dmap_stream_data = dmap.read_records()
        dmap_write = pydarn.SDarnWrite(dmap_stream_data)
        dmap_write.write_iqdat("test_iqdat.iqdat")
        dmap = pydarn.SDarnRead("test_iqdat.iqdat")
        dmap_data = dmap.read_iqdat()
        self.dmap_compare(dmap_stream_data, dmap_data)
        os.remove("test_iqdat.iqdat")

    def test_DmapWrite_stream_SDarnRead_iqdat(self):
        """
        Test DmapWrite to write to a stream and have SDarnRead
        the iqdat stream
        """
        iqdat_data = copy.deepcopy(iqdat_data_sets.iqdat_data)
        iqdat_write = pydarn.DmapWrite()
        iqdat_stream = iqdat_write.write_dmap_stream(iqdat_data)

        iqdat_read = pydarn.SDarnRead(iqdat_stream, True)
        iqdat_read_data = iqdat_read.read_iqdat()
        self.dmap_compare(iqdat_read_data, iqdat_data)

    def test_DmapWrite_missing_SDarnRead_iqdat(self):
        """
        Test DmapWrite writes a iqdat file missing the field nave in record 2
        and SDarnRead reads the file

        Behaviour: Raise SuperDARNFieldMissingError
        """
        iqdat_missing_field = copy.deepcopy(iqdat_data_sets.iqdat_data)
        del iqdat_missing_field[0]['nave']
        dmap_write = pydarn.DmapWrite(iqdat_missing_field)
        dmap_write.write_dmap("test_missing_iqdat.iqdat")

        darn_read = pydarn.SDarnRead("test_missing_iqdat.iqdat")
        try:
            darn_read.read_iqdat()
        except pydarn.superdarn_exceptions.SuperDARNFieldMissingError as err:
            self.assertEqual(err.fields, {'nave'})
            self.assertEqual(err.record_number, 0)

        os.remove("test_missing_iqdat.iqdat")

    def test_DmapWrite_extra_SDarnRead_iqdat(self):
        """
        Test DmapWrite writes a iqdat file with an extra field and SDarnRead
        reads the file

        Behaviour: Raised SuperDARNExtraFieldError
        """
        iqdat_extra_field = copy.deepcopy(iqdat_data_sets.iqdat_data)
        iqdat_extra_field[0].update({'dummy': 'dummy'})
        iqdat_extra_field[0].move_to_end('dummy', last=False)
        dmap_write = pydarn.DmapWrite(iqdat_extra_field, )
        dmap_write.write_dmap("test_extra_iqdat.iqdat")

        darn_read = pydarn.SDarnRead("test_extra_iqdat.iqdat")
        try:
            darn_read.read_iqdat()
        except pydarn.superdarn_exceptions.SuperDARNExtraFieldError as err:
            self.assertEqual(err.fields, {'dummy'})
            self.assertEqual(err.record_number, 0)
        os.remove("test_extra_iqdat.iqdat")

    def test_SDarnRead_SDarnWrite_grid(self):
        """
        Test DmapRead reading an grid and SDarnWrite writing
        the grid file
        """
        dmap = pydarn.SDarnRead(grid_file)
        dmap_data = dmap.read_grid()
        dmap_write = pydarn.SDarnWrite(dmap_data)
        dmap_write.write_grid("test_grid.grid")
        grid_read = pydarn.SDarnRead("test_grid.grid")
        grid_read_data = grid_read.read_grid()
        self.dmap_compare(dmap_data, grid_read_data)
        os.remove("test_grid.grid")

    def test_SDarnWrite_SDarnRead_grid(self):
        """
        Test SDarnWrite writing a grid file and SDarnRead reading the grid
        file
        """
        grid_data = copy.deepcopy(grid_data_sets.grid_data)
        grid_write = pydarn.SDarnWrite(grid_data, "test_grid.grid")
        grid_write.write_grid()

        grid_read = pydarn.SDarnRead("test_grid.grid")
        grid_read_data = grid_read.read_grid()
        self.dmap_compare(grid_read_data, grid_data)
        os.remove("test_grid.grid")

    def test_SDarnRead_stream_SDarnWrite_file_grid(self):
        """
        Test SDarnRead reads from a stream and SDarnWrite writes
        to a grid file
        """
        with bz2.open(grid_stream) as fp:
            dmap_stream = fp.read()
        dmap = pydarn.SDarnRead(dmap_stream, True)
        dmap_stream_data = dmap.read_grid()
        dmap_write = pydarn.SDarnWrite(dmap_stream_data)
        dmap_write.write_grid("test_grid.grid")
        self.assertTrue(os.path.isfile("test_grid.grid"))
        dmap = pydarn.SDarnRead("test_grid.grid")
        dmap_data = dmap.read_grid()
        self.dmap_compare(dmap_stream_data, dmap_data)

    def test_DmapRead_SDarnWrite_SDarnRead_grid(self):
        """
        Test DmapRead reading a grid file then writing it with SDarnWrite
        then reading it again with SDarnRead
        """
        dmap = pydarn.DmapRead(grid_file)
        dmap_data = dmap.read_records()
        dmap_write = pydarn.SDarnWrite(dmap_data)
        dmap_write.write_grid("test_grid.grid")
        darn_read = pydarn.SDarnRead("test_grid.grid")
        grid_data = darn_read.read_grid()
        self.dmap_compare(dmap_data, grid_data)
        os.remove("test_grid.grid")

    def test_SDarnWrite_file_SDarnRead_grid(self):
        """
        Test SDarnWrite to write a grid file then using
        SDarnRead to read the file
        """
        grid_data = copy.deepcopy(grid_data_sets.grid_data)
        grid_write = pydarn.SDarnWrite(grid_data, "test_grid.grid")
        grid_write.write_grid()

        grid_read = pydarn.SDarnRead("test_grid.grid")
        grid_read_data = grid_read.read_grid()
        self.dmap_compare(grid_read_data, grid_data)
        os.remove("test_grid.grid")

    def test_DmapWrite_SDarnRead_grid(self):
        """
        Test DmapWrite to write a grid file then using SDarnRead
        to read the file
        """
        grid_data = copy.deepcopy(grid_data_sets.grid_data)
        grid_write = pydarn.DmapWrite(grid_data, "test_grid.grid")
        grid_write.write_dmap()

        grid_read = pydarn.SDarnRead("test_grid.grid")
        grid_read_data = grid_read.read_grid()
        self.dmap_compare(grid_read_data, grid_data)
        os.remove("test_grid.grid")

    def test_SDarnRead_DmapWrite_stream_grid(self):
        """
        Test SDarnRead to read from a grid stream then
        DmapWrite to write a grid file from the stream
        """
        with bz2.open(grid_stream) as fp:
            dmap_stream = fp.read()
        dmap = pydarn.SDarnRead(dmap_stream, True)
        dmap_stream_data = dmap.read_grid()
        dmap_write = pydarn.DmapWrite()
        dmap_write_stream = dmap_write.write_dmap_stream(dmap_stream_data)
        dmap_read = pydarn.SDarnRead(dmap_write_stream, True)
        dmap_read_data = dmap_read.read_grid()
        self.dmap_compare(dmap_stream_data, dmap_read_data)

    def test_DmapRead_stream_SDarnWrite_file_grid(self):
        """
        Test DmapRead to read in a stream then have SDarnWrite the
        stream to file
        """
        with bz2.open(grid_stream) as fp:
            dmap_stream = fp.read()
        dmap = pydarn.DmapRead(dmap_stream, True)
        dmap_stream_data = dmap.read_records()
        dmap_write = pydarn.SDarnWrite(dmap_stream_data)
        dmap_write.write_grid("test_grid.grid")
        dmap = pydarn.SDarnRead("test_grid.grid")
        dmap_data = dmap.read_grid()
        self.dmap_compare(dmap_stream_data, dmap_data)
        os.remove("test_grid.grid")

    def test_DmapWrite_stream_SDarnRead_grid(self):
        """
        Test DmapWrite to write to a stream and have SDarnRead
        the grid stream
        """
        grid_data = copy.deepcopy(grid_data_sets.grid_data)
        grid_write = pydarn.DmapWrite()
        grid_stream = grid_write.write_dmap_stream(grid_data)

        grid_read = pydarn.SDarnRead(grid_stream, True)
        grid_read_data = grid_read.read_grid()
        self.dmap_compare(grid_read_data, grid_data)

    def test_DmapWrite_missing_SDarnRead_grid(self):
        """
        Test DmapWrite writes a grid file missing the field nave in record 2
        and SDarnRead reads the file

        Behaviour: Raise SuperDARNFieldMissingError
        """
        grid_missing_field = copy.deepcopy(grid_data_sets.grid_data)
        del grid_missing_field[0]['stid']
        dmap_write = pydarn.DmapWrite(grid_missing_field)
        dmap_write.write_dmap("test_missing_grid.grid")

        darn_read = pydarn.SDarnRead("test_missing_grid.grid")
        try:
            darn_read.read_grid()
        except pydarn.superdarn_exceptions.SuperDARNFieldMissingError as err:
            self.assertEqual(err.fields, {'stid'})
            self.assertEqual(err.record_number, 0)

        os.remove("test_missing_grid.grid")

    def test_DmapWrite_extra_SDarnRead_grid(self):
        """
        Test DmapWrite writes a grid file with an extra field and SDarnRead
        reads the file

        Behaviour: Raised SuperDARNExtraFieldError
        """
        grid_extra_field = copy.deepcopy(grid_data_sets.grid_data)
        grid_extra_field[0].update({'dummy': 'dummy'})
        grid_extra_field[0].move_to_end('dummy', last=False)
        dmap_write = pydarn.DmapWrite(grid_extra_field, )
        dmap_write.write_dmap("test_extra_grid.grid")

        darn_read = pydarn.SDarnRead("test_extra_grid.grid")
        try:
            darn_read.read_grid()
        except pydarn.superdarn_exceptions.SuperDARNExtraFieldError as err:
            self.assertEqual(err.fields, {'dummy'})
            self.assertEqual(err.record_number, 0)
        os.remove("test_extra_grid.grid")

    def test_SDarnRead_SDarnWrite_map(self):
        """
        Test DmapRead reading an map and SDarnWrite writing
        the map file
        """
        dmap = pydarn.SDarnRead(map_file)
        dmap_data = dmap.read_map()
        dmap_write = pydarn.SDarnWrite(dmap_data)
        dmap_write.write_map("test_map.map")
        map_read = pydarn.SDarnRead("test_map.map")
        map_read_data = map_read.read_map()
        self.dmap_compare(dmap_data, map_read_data)
        os.remove("test_map.map")

    def test_SDarnWrite_SDarnRead_map(self):
        """
        Test SDarnWrite writing a map file and SDarnRead reading the map
        file
        """
        map_data = copy.deepcopy(map_data_sets.map_data)
        map_write = pydarn.SDarnWrite(map_data, "test_map.map")
        map_write.write_map()

        map_read = pydarn.SDarnRead("test_map.map")
        map_read_data = map_read.read_map()
        self.dmap_compare(map_read_data, map_data)
        os.remove("test_map.map")

    def test_SDarnRead_stream_SDarnWrite_file_map(self):
        """
        Test SDarnRead reads from a stream and SDarnWrite writes
        to a map file
        """
        with bz2.open(map_stream) as fp:
            dmap_stream = fp.read()
        dmap = pydarn.SDarnRead(dmap_stream, True)
        dmap_stream_data = dmap.read_map()
        dmap_write = pydarn.SDarnWrite(dmap_stream_data)
        dmap_write.write_map("test_map.map")
        self.assertTrue(os.path.isfile("test_map.map"))
        dmap = pydarn.SDarnRead("test_map.map")
        dmap_data = dmap.read_map()
        self.dmap_compare(dmap_stream_data, dmap_data)

    def test_DmapRead_SDarnWrite_SDarnRead_map(self):
        """
        Test DmapRead reading a map file then writing it with SDarnWrite
        then reading it again with SDarnRead
        """
        dmap = pydarn.DmapRead(map_file)
        dmap_data = dmap.read_records()
        dmap_write = pydarn.SDarnWrite(dmap_data)
        dmap_write.write_map("test_map.map")
        darn_read = pydarn.SDarnRead("test_map.map")
        map_data = darn_read.read_map()
        self.dmap_compare(dmap_data, map_data)
        os.remove("test_map.map")

    def test_SDarnWrite_file_SDarnRead_map(self):
        """
        Test SDarnWrite to write a map file then using
        SDarnRead to read the file
        """
        map_data = copy.deepcopy(map_data_sets.map_data)
        map_write = pydarn.SDarnWrite(map_data, "test_map.map")
        map_write.write_map()

        map_read = pydarn.SDarnRead("test_map.map")
        map_read_data = map_read.read_map()
        self.dmap_compare(map_read_data, map_data)
        os.remove("test_map.map")

    def test_DmapWrite_SDarnRead_map(self):
        """
        Test DmapWrite to write a map file then using SDarnRead
        to read the file
        """
        map_data = copy.deepcopy(map_data_sets.map_data)
        map_write = pydarn.DmapWrite(map_data, "test_map.map")
        map_write.write_dmap()

        map_read = pydarn.SDarnRead("test_map.map")
        map_read_data = map_read.read_map()
        self.dmap_compare(map_read_data, map_data)
        os.remove("test_map.map")

    def test_SDarnRead_DmapWrite_stream_map(self):
        """
        Test SDarnRead to read from a map stream then
        DmapWrite to write a map file from the stream
        """
        with bz2.open(map_stream) as fp:
            dmap_stream = fp.read()
        dmap = pydarn.SDarnRead(dmap_stream, True)
        dmap_stream_data = dmap.read_map()
        dmap_write = pydarn.DmapWrite()
        dmap_write_stream = dmap_write.write_dmap_stream(dmap_stream_data)
        dmap_read = pydarn.SDarnRead(dmap_write_stream, True)
        dmap_read_data = dmap_read.read_map()
        self.dmap_compare(dmap_stream_data, dmap_read_data)

    def test_DmapRead_stream_SDarnWrite_file_map(self):
        """
        Test DmapRead to read in a stream then have SDarnWrite the
        stream to file
        """
        with bz2.open(map_stream) as fp:
            dmap_stream = fp.read()
        dmap = pydarn.DmapRead(dmap_stream, True)
        dmap_stream_data = dmap.read_records()
        dmap_write = pydarn.SDarnWrite(dmap_stream_data)
        dmap_write.write_map("test_map.map")
        dmap = pydarn.SDarnRead("test_map.map")
        dmap_data = dmap.read_map()
        self.dmap_compare(dmap_stream_data, dmap_data)
        os.remove("test_map.map")

    def test_DmapWrite_stream_SDarnRead_map(self):
        """
        Test DmapWrite to write to a stream and have SDarnRead
        the map stream
        """
        map_data = copy.deepcopy(map_data_sets.map_data)
        map_write = pydarn.DmapWrite()
        map_stream = map_write.write_dmap_stream(map_data)

        map_read = pydarn.SDarnRead(map_stream, True)
        map_read_data = map_read.read_map()
        self.dmap_compare(map_read_data, map_data)

    def test_DmapWrite_missing_SDarnRead_map(self):
        """
        Test DmapWrite writes a fitacf file missing the field nave in record 2
        and SDarnRead reads the file

        Behaviour: Raise SuperDARNFieldMissingError
        """
        map_missing_field = copy.deepcopy(map_data_sets.map_data)
        del map_missing_field[0]['stid']
        dmap_write = pydarn.DmapWrite(map_missing_field)
        dmap_write.write_dmap("test_missing_map.map")

        darn_read = pydarn.SDarnRead("test_missing_map.map")
        try:
            darn_read.read_map()
        except pydarn.superdarn_exceptions.SuperDARNFieldMissingError as err:
            self.assertEqual(err.fields, {'stid'})
            self.assertEqual(err.record_number, 0)

        os.remove("test_missing_map.map")

    def test_DmapWrite_extra_SDarnRead_map(self):
        """
        Test DmapWrite writes a map file with an extra field and SDarnRead
        reads the file

        Behaviour: Raised SuperDARNExtraFieldError
        """
        map_extra_field = copy.deepcopy(map_data_sets.map_data)
        map_extra_field[0].update({'dummy': 'dummy'})
        map_extra_field[0].move_to_end('dummy', last=False)
        dmap_write = pydarn.DmapWrite(map_extra_field, )
        dmap_write.write_dmap("test_extra_map.map")

        darn_read = pydarn.SDarnRead("test_extra_map.map")
        try:
            darn_read.read_map()
        except pydarn.superdarn_exceptions.SuperDARNExtraFieldError as err:
            self.assertEqual(err.fields, {'dummy'})
            self.assertEqual(err.record_number, 0)
        os.remove("test_extra_map.map")


if __name__ == '__main__':
    """
    Runs the above class in a unittest system.
    Roughly takes 467 seconds.
    """
    pydarn_logger.info("Starting DMAP testing")

    unittest.main()
