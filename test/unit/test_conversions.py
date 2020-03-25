# Copyright (C) 2019 SuperDARN Canada, University of Saskatchewan
# Author: Marina Schmidt


import unittest
import numpy as np
from collections import OrderedDict

import pydarn


class Test_Conversions(unittest.TestCase):
    """
    Class to test the conversion functions
    """
    def setUp(self):
        """
        Creates the testing data

        Attributes
        ----------
        dmap_list : List[dict]
            List of dictionaries containing fields and values
        dmap_records : List[dict]
            List of ordered dictionaries containing dmap data structure
            DmapScalar and DmapArray
        """
        self.dmap_list = [{'stid': 1, 'channel': 0,
                           'ptab': np.array([0, 9, 12,
                                             20, 22,
                                             26, 27], dtype=np.int64)},
                          {'bmnum': np.int16(15), 'combf': "$Id: twofsound",
                           'pwr0': np.array([58.081821, 52.241421, 32.936508,
                                             35.562561, 35.344330, 31.501854,
                                             25.313326, 13.731517, 3.482957,
                                             -5.032664, -9.496454, 3.254651],
                                            dtype=np.float32)},
                          {'radar.revision.major': np.int8(1),
                           'radar.revision.minor': np.int8(18),
                           'float test': float(3.5),
                           'float2 test': 3.65,
                           'channel': 'a',
                           'double test': np.array([[2.305015, 2.0251],
                                                   [16548548, 78687686]],
                                                   dtype=np.float64)},
                          {'time.us': 508473,
                           'negative int': -42,
                           'long int': np.int64(215610516132151613),
                           'unsigned char': np.uint8(3),
                           'unsigned short': np.uint16(45),
                           'unsigned int': np.uint32(100),
                           'unsigned long': np.uint64(1250000000000),
                           'list test': [np.int64(1), np.int64(2),
                                         np.int64(34), np.int64(45)]}]
        self.dmap_records = \
            [OrderedDict([('stid', pydarn.DmapScalar('stid', 1, 3, 'i')),
                          ('channel', pydarn.DmapScalar('channel', 0, 3, 'i')),
                          ('ptab', pydarn.DmapArray('ptab',
                                                    np.array([0, 9, 12, 20, 22,
                                                              26, 27],
                                                             dtype=np.int64),
                                                    10, 'q', 1, [7]))]),
             OrderedDict([('bmnum', pydarn.DmapScalar('bmnum', 15, 2, 'h')),
                          ('combf', pydarn.DmapScalar('combf',
                                                      "$Id: twofsound", 9,
                                                      's')),
                          ('pwr0', pydarn.DmapArray('pwr0',
                                                    np.array([58.081821,
                                                              52.241421,
                                                              32.936508,
                                                              35.562561,
                                                              35.344330,
                                                              31.501854,
                                                              25.313326,
                                                              13.731517,
                                                              3.482957,
                                                              -5.032664,
                                                              -9.496454,
                                                              3.254651],
                                                             dtype=np.float32),
                                                    4, 'f', 1, [12]))]),
             OrderedDict([('radar.revision.major',
                           pydarn.DmapScalar('radar.revision.major',
                                             np.int8(1), 1, 'c')),
                          ('radar.revision.minor',
                           pydarn.DmapScalar('radar.revision.minor',
                                             np.int8(18), 1, 'c')),
                          ('float test',
                           pydarn.DmapScalar('float test',
                                             float(3.5), 4, 'f')),
                          ('float2 test',
                           pydarn.DmapScalar('float2 test', 3.65, 4, 'f')),
                          ('channel', pydarn.DmapScalar('channel', 'a', 9,
                                                        's')),
                          ('double test',
                           pydarn.DmapArray('double test',
                                            np.array([[2.305015, 2.0251],
                                                     [16548548, 78687686]],
                                                     dtype=np.float64), 8,
                                            'd', 2, [2, 2]))]),
             OrderedDict([('time.us', pydarn.DmapScalar('time.us', 508473,
                                                        3, 'i')),
                          ('negative int',
                           pydarn.DmapScalar('negative int', -42, 3, 'i')),
                          ('long int',
                           pydarn.DmapScalar('long int',
                                             np.int64(215610516132151613),
                                             10, 'q')),
                          ('unsigned char', pydarn.DmapScalar('unsigned char',
                                                              np.uint8(3),
                                                              16, 'B')),
                          ('unsigned short',
                           pydarn.DmapScalar('unsigned short', np.uint16(45),
                                             17, 'H')),
                          ('unsigned int',
                           pydarn.DmapScalar('unsigned int', np.uint32(100),
                                             18, 'I')),
                          ('unsigned long',
                           pydarn.DmapScalar('unsigned long',
                                             np.uint64(1250000000000),
                                             19, 'Q')),
                          ('list test',
                           pydarn.DmapArray('list test',
                                            np.array([1, 2, 34, 45],
                                                     dtype=np.int64),
                                            10, 'q', 1, [4]))])]

    def dmap_compare(self, dmap1: list, dmap2: list):
        """
        compares dmap data structure records to ensure they are equivalent
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
                else:
                    self.compare_dmap_array(record2[field], val_obj)

    def compare_dmap_array(self, dmaparr1, dmaparr2):
        """
        Compares DmapArrays because np.arrays need to call a numpy comparison
        method to compare the elements
        """
        self.assertEqual(dmaparr1.name, dmaparr2.name)
        self.assertEqual(dmaparr1.data_type, dmaparr2.data_type)
        self.assertEqual(dmaparr1.data_type_fmt, dmaparr2.data_type_fmt)
        self.assertEqual(dmaparr1.dimension, dmaparr2.dimension)
        self.assertTrue(np.array_equal(dmaparr1.value, dmaparr2.value))

    def test_dict2dmap(self):
        """
        From utils package, testing dict2dmap function
        """
        dmap_records_test = pydarn.dict2dmap(self.dmap_list)
        self.dmap_compare(dmap_records_test, self.dmap_records)

    def test_dmap2dict(self):
        """
        From utils package, testing dmap2dict function
        """
        # need to break up the list of dictionaries to properly
        # compare each field value
        dmap_list_test = pydarn.dmap2dict(self.dmap_records)
        for j in range(len(dmap_list_test)):
            for key, value in dmap_list_test[j].items():
                if isinstance(value, np.ndarray):
                    self.assertTrue(np.array_equal(value,
                                                   self.dmap_list[j][key]))
                else:
                    self.assertEqual(value, self.dmap_list[j][key])


if __name__ == '__main__':

    """
    Runs the above class in a unittest system.
    Roughly takes 467 seconds.
    """

    unittest.main()
