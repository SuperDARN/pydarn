# Copyright (C) 2019 SuperDARN
# Author: Marina Schmidt

"""
Test suite is to test the implementation of data structures used in pydarn.
"""

import unittest
import pydarn
import numpy as np
import logging

pydarn_logger = logging.getLogger('pydarn')

class TestDmapDataStructures(unittest.TestCase):
    """
    Testing datastructures.py that contains pydarn data structures
    """
    def setUp(self):
        pass

    # Unit tests for DmapScalar
    def test_DmapScalar(self):
        scalar = pydarn.DmapScalar('radar','sas','s')
        self.assertEqual('radar', scalar.name)
        self.assertEqual('sas', scalar.value)
        self.assertEqual('s', scalar.data_type)

    def test_DmapArray(self):
        array = pydarn.DmapArray('xcfd', np.array([1,32,4]),'i', 1, [3])
        self.assertEqual('xcfd', array.name)
        self.assertEqual(32, array.value[1])
        self.assertEqual('i', array.data_type)
        self.assertEqual(1, array.dimension)
        self.assertEqual([3], array.shape)

if __name__ == '__main__':
    pydarn_logger.info("Starting pydarn data structures testing")
    unittest.main()
