import pydarn
import unittest
import numpy as np
import logging
import collection

import rawacf_data_sets
import fitacf_data_sets
import iqdat_data_sets
import map_data_sets
import grid_data_sets
import copy


# Test files
rawacf_file = "./testfiles/20170410.1801.00.sas.rawacf"
fitacf_file = "./testfiles/20180220.C0.rkn.fitacf"
map_file = "./testfiles/20170114.map"
iqdat_file = "testfiles/20160316.1945.01.rkn.iqdat"
zip_file = ""
# Black listed files
corrupt_file1 = "./testfiles/20070117.1001.00.han.rawacf"
corrupt_file2 = "./testfiles/20090320.1601.00.pgr.rawacf"

class IntegrationPydmap(unittest.TestCase):
    def setUp(self):
        pass

    def test_dmap_read_write_scalar(self):
        pass

    def test_dmap_read_write_array(self):
        pass

    def test_read_write_rawacf(self):
        pass

    def test_write_read_rawacf(self):
        pass

    def test_read_stream_write_rawacf(self):
        pass

    def test_write_stream_read_rawacf(self):
        pass



if __name__ == '__main__':
    """
    Runs the above class in a unittest system.
    Roughly takes 467 seconds.
    """
    pydarn_logger.info("Starting DMAP testing")

    unittest.main()
