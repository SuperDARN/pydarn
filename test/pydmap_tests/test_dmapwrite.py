# Copyright (C) 2016  SuperDARN Canada
# Author: Marina Schmidt


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
import fitacf_data_sets
import iqdat_data_sets
import map_data_sets
import grid_data_sets
import dmap_data_sets
import copy

pydarn_logger = logging.getLogger('pydarn')


class TestDmapWrite(unittest.TestCase):
    def setUp(self):
        pass

    def test_wrong_file_format(self):
        rawacf_data = copy.deepcopy(rawacf_data_sets.rawacf_data)
        with self.assertRaises(pydarn.pydmap_exceptions.DmapFileFormatType):
            pydarn.DmapWrite(rawacf_data, "rawacf_test.rawacf", 'dog')

    def test_empty_record(self):
        with self.assertRaises(pydarn.pydmap_exceptions.DmapDataError):
            pydarn.DmapWrite([], 'dummy_file.acf', 'fitacf')

    def test_incorrect_filename_input_using_DmapWrite(self):
        rawacf_data = copy.deepcopy(rawacf_data_sets.rawacf_data)
        with self.assertRaises(pydarn.pydmap_exceptions.FilenameRequiredError):
            pydarn.DmapWrite(rawacf_data, "", 'fitacf')

    def test_incorrect_filename_input_using_write_methods(self):
        rawacf_data = copy.deepcopy(rawacf_data_sets.rawacf_data)
        dmap_data = pydarn.DmapWrite(rawacf_data)
        with self.assertRaises(pydarn.pydmap_exceptions.FilenameRequiredError):
            dmap_data.write_rawacf()
            dmap_data.write_fitacf()
            dmap_data.write_iqdat()
            dmap_data.write_grid()
            dmap_data.write_map()
            dmap_data.write_dmap()

    def test_dict_list2set(self):
        dict1 = {'a': 1, 'b': 2, 'c': 3}
        dict2 = {'rst': '4.1', 'stid': 3, 'vel': [2.3, 4.5]}
        dict3 = {'fitacf': 'f', 'rawacf': 's', 'map': 'm'}

        complete_set = {'a', 'b', 'c',
                        'rst', 'stid', 'vel',
                        'fitacf', 'rawacf', 'map'}

        dmap_data = copy.deepcopy(dmap_data_sets.dmap_data)

        dmap = pydarn.DmapWrite(dmap_data)
        dict_set = dmap.dict_list2set([dict1, dict2, dict3])
        self.assertEqual(dict_set, complete_set)

    def test_extra_field_check_pass(self):
        dict1 = {'a': 1, 'b': 2, 'c': 3}
        dict2 = {'rst': '4.1', 'stid': 3, 'vel': [2.3, 4.5]}
        dict3 = {'fitacf': 'f', 'rawacf': 's', 'map': 'm'}

        test_dict = {'a': 3, 'b': 3, 'c': 3, 'rst': 1, 'vel': 'd'}

        dmap_data = copy.deepcopy(dmap_data_sets.dmap_data)

        dmap = pydarn.DmapWrite(dmap_data)
        dict_set = dmap.extra_field_check([dict1, dict2, dict3], test_dict)

    def test_extra_field_check_pass(self):
        dict1 = {'a': 1, 'b': 2, 'c': 3}
        dict2 = {'rst': '4.1', 'stid': 3, 'vel': [2.3, 4.5]}
        dict3 = {'fitacf': 'f', 'rawacf': 's', 'map': 'm'}

        test_dict = {'a': 3, 'b': 3, 'c': 2, 'd': 3, 'rst': 1, 'vel': 'd'}

        dmap_data = copy.deepcopy(dmap_data_sets.dmap_data)

        try:
            dmap = pydarn.DmapWrite(dmap_data)
            dict_set = dmap.extra_field_check([dict1, dict2, dict3], test_dict)
        except pydarn.pydmap_exceptions.SuperDARNFieldExtra as err:
            self.assertEqual(err.fields, {'d'})

    def test_missing_field_check_pass_mixed_dict(self):
        dict1 = {'a': 1, 'b': 2, 'c': 3}
        dict2 = {'rst': '4.1', 'stid': 3, 'vel': [2.3, 4.5]}
        dict3 = {'fitacf': 'f', 'rawacf': 's', 'map': 'm'}

        dmap_data = copy.deepcopy(dmap_data_sets.dmap_data)

        dmap = pydarn.DmapWrite(dmap_data)
        test_dict = {}
        test_dict.update(dict1)
        test_dict.update(dict3)
        dict_set = dmap.missing_field_check([dict1, dict2, dict3], test_dict)

    def test_missing_field_check_pass_mixed_subset(self):
        dict1 = {'a': 1, 'b': 2, 'c': 3}
        dict2 = {'rst': '4.1', 'stid': 3, 'vel': [2.3, 4.5]}
        dict3 = {'fitacf': 'f', 'rawacf': 's', 'map': 'm'}

        test_dict = {'a': 3, 'b': 3, 'c': 2, 'd': 2,
                     'stid': 's', 'rst': 1, 'vel': 'd'}

        dmap_data = copy.deepcopy(dmap_data_sets.dmap_data)

        dmap = pydarn.DmapWrite(dmap_data)
        dict_set = dmap.missing_field_check([dict1, dict2, dict3], test_dict)
        test_dict = {}
        test_dict.update(dict1)
        test_dict.update(dict3)
        dict_set = dmap.missing_field_check([dict1, dict2, dict3], test_dict)

    def test_missing_field_check_fail(self):
        dict1 = {'a': 1, 'b': 2, 'c': 3}
        dict2 = {'rst': '4.1', 'stid': 3, 'vel': [2.3, 4.5]}
        dict3 = {'fitacf': 'f', 'rawacf': 's', 'map': 'm'}

        test_dict = {'a': 3, 'b': 3, 'd': 2,
                     'stid': 's', 'rst': 1, 'vel': 'd',
                     'fitacf': 3, 'map': 4}

        dmap_data = copy.deepcopy(dmap_data_sets.dmap_data)

        dmap = pydarn.DmapWrite(dmap_data)
        try:
            dict_set = dmap.missing_field_check([dict1, dict2, dict3],
                                                test_dict)
        except pydarn.pydmap_exceptions.SuperDARNFieldMissing as err:
            self.assertEqual(err.fields, {'c', 'rawacf'})

    def test_incorrect_types_check_pass(self):
        dict1 = {'a': 's', 'b': 'i', 'c': 'f'}
        dict3 = {'fitacf': 'f', 'rawacf': 's', 'map': 'm'}

        test_dict = {'a': pydarn.DmapScalar('a', 1, 1, 's'),
                     'b': pydarn.DmapScalar('a', 1, 1, 'i'),
                     'c': pydarn.DmapArray('a', np.array([2.4, 2.4]), 1,
                                           'f', 1, [3]),
                     'fitacf': pydarn.DmapScalar('a', 1, 1, 'f'),
                     'rawacf': pydarn.DmapScalar('a', 1, 1, 's'),
                     'map': pydarn.DmapScalar('a', 1, 1, 'm')}

        dmap_data = copy.deepcopy(dmap_data_sets.dmap_data)

        dmap = pydarn.DmapWrite(dmap_data)
        dict_set = dmap.incorrect_types_check([dict1, dict3], test_dict)

    def test_incorrect_types_check_fail(self):
        dict1 = {'a': 's', 'b': 'i', 'c': 'f'}
        dict3 = {'fitacf': 'f', 'rawacf': 's', 'map': 'm'}

        test_dict = {'a': pydarn.DmapScalar('a', 1, 1, 's'),
                     'b': pydarn.DmapScalar('a', 1, 1, 'i'),
                     'c': pydarn.DmapArray('a', np.array([2.4, 2.4]),
                                           1, 'f', 1, [3]),
                     'fitacf': pydarn.DmapScalar('a', 1, 1, 's'),
                     'rawacf': pydarn.DmapScalar('a', 1, 1, 's'),
                     'map': pydarn.DmapScalar('a', 1, 1, 'm')}

        dmap_data = copy.deepcopy(dmap_data_sets.dmap_data)
        dmap = pydarn.DmapWrite(dmap_data)

        try:
            dict_set = dmap.incorrect_types_check([dict1, dict3], test_dict)
        except pydarn.pydmap_exceptions.SuperDARNDataFormatError as err:
            self.assertEqual(err.incorrect_params, {'fitacf','f'})

    def test_dict_diff(self):
        dict1 = {'a': 's', 'b': 'i', 'c': 'f'}
        dict3 = {'fitacf': 'f', 'rawacf': 's', 'map': 'm'}

        test_dict = {'a': pydarn.DmapScalar('a', 1, 1, 's'),
                     'b': pydarn.DmapScalar('a', 1, 1, 'i'),
                     'c': pydarn.DmapArray('a', np.array([2.4, 2.4]), 1,
                                           'f', 1, [3]),
                     'fitacf': pydarn.DmapScalar('a', 1, 1, 'f'),
                     'rawacf': pydarn.DmapScalar('a', 1, 1, 's'),
                     'map': pydarn.DmapScalar('a', 1, 1, 'm')}

        dmap_data = copy.deepcopy(dmap_data_sets.dmap_data)

        dmap = pydarn.DmapWrite(dmap_data)
        dict_set = dmap.incorrect_types_check([dict1, dict3], test_dict)

    def test_DmapWrite_missing_field_rawacf(self):
        """
            Tests RawDmapWite to write to rawacf:
                Expected behaviour to raise a DmapDataError
                because the rawtacf file is missing field.
        """
        rawacf_missing_field = copy.deepcopy(rawacf_data_sets.rawacf_data)
        del rawacf_missing_field[2]['nave']

        dmap = pydarn.DmapWrite(rawacf_missing_field)

        with self.assertRaises(pydarn.pydmap_exceptions.SuperDARNFieldMissing):
            dmap.write_rawacf("test_rawacf.rawacf")
            pydarn.DmapWrite(rawacf_missing_field, "test_rawacf.rawacf", 'rawacf')


    def test_extra_field_rawacf(self):
        """
            Tests RawDmapWite to write to rawacf:
                Expected behaviour to raise a DmapDataError
                because the rawacf file data has an extra field.
        """
        rawacf_extra_field = copy.deepcopy(rawacf_data_sets.rawacf_data)
        rawacf_extra_field[1]['dummy'] = pydarn.DmapScalar('dummy', 'nothing',
                                                           chr(1), 's')
        dmap = pydarn.DmapWrite(rawacf_extra_field)

        with self.assertRaises(pydarn.pydmap_exceptions.SuperDARNFieldExtra):
            dmap.write_rawacf("test_rawacf.rawacf")
            pydarn.DmapWrite(rawacf_extra_field, "test_rawacf.rawacf", 'rawacf')

    def test_incorrect_data_format_rawacf(self):
        rawacf_incorrect_fmt = copy.deepcopy(rawacf_data_sets.rawacf_data)
        rawacf_incorrect_fmt[2]['scan'] = rawacf_incorrect_fmt[2]['scan']._replace(data_type_fmt='c')
        dmap = pydarn.DmapWrite(rawacf_incorrect_fmt)

        with self.assertRaises(pydarn.pydmap_exceptions.SuperDARNDataFormatError):
            dmap.write_rawacf("test_rawacf.rawacf")
            pydarn.DmapWrite(rawacf_incorrect_fmt, "test_rawacf.rawacf", 'rawacf')

    def test_writing_to_rawacf(self):
        """tests using DmapWrite to write to rawacf"""
        rawacf_data = copy.deepcopy(rawacf_data_sets.rawacf_data)

        dmap = pydarn.DmapWrite(rawacf_data)

        dmap.write_rawacf("test_rawacf.rawacf")
        self.assertTrue(os.path.isfile("test_rawacf.rawacf"))

        os.remove("test_rawacf.rawacf")

        pydarn.DmapWrite(rawacf_data, "test_rawacf.rawacf", 'rawacf')
        self.assertTrue(os.path.isfile("test_rawacf.rawacf"))
        os.remove("test_rawacf.rawacf")

    def test_writing_to_fitacf(self):
        """tests using DmapWrite to write to rawacf"""
        fitacf_data = copy.deepcopy(fitacf_data_sets.fitacf_data)
        dmap = pydarn.DmapWrite(fitacf_data)

        dmap.write_fitacf("test_fitacf.fitacf")
        self.assertTrue(os.path.isfile("test_fitacf.fitacf"))

        os.remove("test_fitacf.fitacf")

        pydarn.DmapWrite(fitacf_data, "test_fitacf.fitacf", 'fitacf')
        self.assertTrue(os.path.isfile("test_fitacf.fitacf"))
        os.remove("test_fitacf.fitacf")

    def test_missing_fitacf_field(self):
        """tests using DmapWrite to write to rawacf"""
        fitacf_missing_field = copy.deepcopy(fitacf_data_sets.fitacf_data)
        del fitacf_missing_field[2]['stid']
        dmap = pydarn.DmapWrite(fitacf_missing_field)

        with self.assertRaises(pydarn.pydmap_exceptions.SuperDARNFieldMissing):
            dmap.write_fitacf("test_fitacf.fitacf")
            pydarn.DmapWrite(fitacf_data, "test_fitacf.fitacf", 'fitacf')

    def test_extra_fitacf_field(self):
        """tests using DmapWrite to write to rawacf"""
        fitacf_extra_field = copy.deepcopy(fitacf_data_sets.fitacf_data)
        fitacf_extra_field[2]['dummy'] = \
                pydarn.DmapArray('dummy', np.array([1,2]), chr(1), 'c', 1, [2])
        dmap = pydarn.DmapWrite(fitacf_extra_field)

        with self.assertRaises(pydarn.pydmap_exceptions.SuperDARNFieldExtra):
            dmap.write_fitacf("test_fitacf.fitacf")
            pydarn.DmapWrite(fitacf_extra_field, "test_fitacf.fitacf", 'fitacf')

    def test_incorrect_fitacf_data_type(self):
        """tests using DmapWrite to write to rawacf"""
        fitacf_incorrect_fmt = copy.deepcopy(fitacf_data_sets.fitacf_data)
        fitacf_incorrect_fmt[1]['ltab'] = fitacf_incorrect_fmt[1]['ltab']._replace(data_type_fmt='s')
        dmap = pydarn.DmapWrite(fitacf_incorrect_fmt)
        with self.assertRaises(pydarn.pydmap_exceptions.SuperDARNDataFormatError):
            dmap.write_fitacf("test_fitacf.fitacf")
            pydarn.DmapWrite(fitacf_incorrect_fmt, "test_fitacf.fitacf", 'fitacf')

    def test_writing_to_iqdat(self):
        """tests using DmapWrite to write to rawacf"""
        iqdat_data = copy.deepcopy(iqdat_data_sets.iqdat_data)
        dmap = pydarn.DmapWrite(iqdat_data)

        dmap.write_iqdat("test_iqdat.iqdat")
        self.assertTrue(os.path.isfile("test_iqdat.iqdat"))

        os.remove("test_iqdat.iqdat")

        pydarn.DmapWrite(iqdat_data, "test_iqdat.iqdat", 'iqdat')
        self.assertTrue(os.path.isfile("test_iqdat.iqdat"))
        os.remove("test_iqdat.iqdat")

    def test_missing_iqdat_field(self):
        """tests using DmapWrite to write to rawacf"""
        iqdat_missing_field = copy.deepcopy(iqdat_data_sets.iqdat_data)
        del iqdat_missing_field[1]['chnnum']
        dmap = pydarn.DmapWrite(iqdat_missing_field)

        with self.assertRaises(pydarn.pydmap_exceptions.SuperDARNFieldMissing):
            dmap.write_iqdat("test_iqdat.iqdat")
            pydarn.DmapWrite(iqdat_data, "test_iqdat.iqdat", 'iqdat')

    def test_extra_iqdat_field(self):
        """tests using DmapWrite to write to rawacf"""
        iqdat_extra_field = copy.deepcopy(iqdat_data_sets.iqdat_data)
        iqdat_extra_field[2]['dummy'] = \
                pydarn.DmapArray('dummy', np.array([1,2]), chr(1), 'c', 1, [2])
        dmap = pydarn.DmapWrite(iqdat_extra_field)

        with self.assertRaises(pydarn.pydmap_exceptions.SuperDARNFieldExtra):
            dmap.write_iqdat("test_iqdat.iqdat")
            pydarn.DmapWrite(iqdat_extra_field, "test_iqdat.iqdat", 'iqdat')

    def test_incorrect_iqdat_data_type(self):
        """tests using DmapWrite to write to rawacf"""
        iqdat_incorrect_fmt = copy.deepcopy(iqdat_data_sets.iqdat_data)
        iqdat_incorrect_fmt[2]['lagfr'] = iqdat_incorrect_fmt[2]['lagfr']._replace(data_type_fmt='d')
        dmap = pydarn.DmapWrite(iqdat_incorrect_fmt)
        with self.assertRaises(pydarn.pydmap_exceptions.SuperDARNDataFormatError):
            dmap.write_iqdat("test_iqdat.iqdat")
            pydarn.DmapWrite(iqdat_incorrect_fmt, "test_iqdat.iqdat", 'iqdat')

    def test_writing_to_map(self):
        """tests using DmapWrite to write to rawacf"""
        map_data = copy.deepcopy(map_data_sets.map_data)
        dmap = pydarn.DmapWrite(map_data)

        dmap.write_map("test_map.map")
        self.assertTrue(os.path.isfile("test_map.map"))

        os.remove("test_map.map")

        pydarn.DmapWrite(map_data, "test_map.map", 'map')
        self.assertTrue(os.path.isfile("test_map.map"))
        os.remove("test_map.map")

    def test_missing_map_field(self):
        """tests using DmapWrite to write to rawacf"""
        map_missing_field = copy.deepcopy(map_data_sets.map_data)
        del map_missing_field[0]['IMF.Kp']
        dmap = pydarn.DmapWrite(map_missing_field)

        with self.assertRaises(pydarn.pydmap_exceptions.SuperDARNFieldMissing):
            dmap.write_map("test_map.map")
            pydarn.DmapWrite(map_missing_field, "test_map.map", 'map')

    def test_extra_map_field(self):
        """tests using DmapWrite to write to rawacf"""
        map_extra_field = copy.deepcopy(map_data_sets.map_data)
        map_extra_field[1]['dummy'] = \
                pydarn.DmapArray('dummy', np.array([1,2]), chr(1), 'c', 1, [2])
        dmap = pydarn.DmapWrite(map_extra_field)

        with self.assertRaises(pydarn.pydmap_exceptions.SuperDARNFieldExtra):
            dmap.write_map("test_map.map")
            pydarn.DmapWrite(map_extra_field, "test_map.map", 'map')

    def test_incorrect_map_data_type(self):
        """tests using DmapWrite to write to rawacf"""
        map_incorrect_fmt = copy.deepcopy(map_data_sets.map_data)
        map_incorrect_fmt[2]['IMF.Bx'] = map_incorrect_fmt[2]['IMF.Bx']._replace(data_type_fmt='i')
        dmap = pydarn.DmapWrite(map_incorrect_fmt)
        with self.assertRaises(pydarn.pydmap_exceptions.SuperDARNDataFormatError):
            dmap.write_map("test_map.map")
            pydarn.DmapWrite(map_incorrect_fmt, "test_map.map", 'map')

    def test_writing_to_grid(self):
        """tests using DmapWrite to write to rawacf"""
        grid_data = copy.deepcopy(grid_data_sets.grid_data)
        dmap = pydarn.DmapWrite(grid_data)

        dmap.write_grid("test_grid.grid")
        self.assertTrue(os.path.isfile("test_grid.grid"))

        os.remove("test_grid.grid")

        pydarn.DmapWrite(grid_data, "test_grid.grid", 'grid')
        self.assertTrue(os.path.isfile("test_grid.grid"))
        os.remove("test_grid.grid")

    def test_missing_grid_field(self):
        """tests using DmapWrite to write to rawacf"""
        grid_missing_field = copy.deepcopy(grid_data_sets.grid_data)
        del grid_missing_field[1]['start.year']
        dmap = pydarn.DmapWrite(grid_missing_field)

        with self.assertRaises(pydarn.pydmap_exceptions.SuperDARNFieldMissing):
            dmap.write_grid("test_grid.grid")
            pydarn.DmapWrite(grid_data, "test_grid.grid", 'grid')

    def test_extra_grid_field(self):
        """tests using DmapWrite to write to rawacf"""
        grid_extra_field = copy.deepcopy(grid_data_sets.grid_data)
        grid_extra_field[0]['dummy'] = \
                pydarn.DmapArray('dummy', np.array([1,2]), chr(1), 'c', 1, [2])
        dmap = pydarn.DmapWrite(grid_extra_field)

        with self.assertRaises(pydarn.pydmap_exceptions.SuperDARNFieldExtra):
            dmap.write_grid("test_grid.grid")
            pydarn.DmapWrite(grid_extra_field, "test_grid.grid", 'grid')

    def test_incorrect_grid_data_type(self):
        """tests using DmapWrite to write to rawacf"""
        grid_incorrect_fmt = copy.deepcopy(grid_data_sets.grid_data)
        grid_incorrect_fmt[2]['v.min'] = grid_incorrect_fmt[2]['v.min']._replace(data_type_fmt='d')
        dmap = pydarn.DmapWrite(grid_incorrect_fmt)
        with self.assertRaises(pydarn.pydmap_exceptions.SuperDARNDataFormatError):
            dmap.write_grid("test_grid.grid")
            pydarn.DmapWrite(grid_incorrect_fmt, "test_grid.grid", 'grid')

    def test_writing_to_dmap(self):
        """tests using DmapWrite to write to rawacf"""
        dmap_data = copy.deepcopy(dmap_data_sets.dmap_data)
        dmap = pydarn.DmapWrite(dmap_data)

        dmap.write_dmap("test_dmap.dmap")
        self.assertTrue(os.path.isfile("test_dmap.dmap"))

        os.remove("test_dmap.dmap")

        pydarn.DmapWrite(dmap_data, "test_dmap.dmap", 'dmap')
        self.assertTrue(os.path.isfile("test_dmap.dmap"))
        os.remove("test_dmap.dmap")


if __name__ == '__main__':
    """
    Runs the above class in a unittest system.
    Roughly takes 467 seconds.
    """
    pydarn_logger.info("Starting DMAP testing")

    unittest.main()
