"""Copyright (C) 2016  SuperDARN Canada

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>."""

import unittest
import test_data
import numpy as np
import os
import random
import gc
import time
import logging

import pydarn

pydarn_logger = logging.getLogger('pydarn')
rawacf_file = "./testfiles/20170410.1801.00.sas.rawacf"
fitacf_file = "./testfiles/20180220.C0.rkn.fitacf"
map_file = "./testfiles/20170114.map"

def compare_arrays(arr1, arr2):
    for a, b in zip(arr1, arr2):
        if (isinstance(a, np.ndarray) or isinstance(a, list)) and \
         (isinstance(b, np.ndarray) or isinstance(b, list)):
            return compare_arrays(a, b)
        else:
            if (isinstance(a, np.float32) or isinstance(a, float)) and \
             (isinstance(a, np.float32) or isinstance(a, float)):
                if abs(a-b) > 1e-03:
                    return True
            else:
                if a != b:
                    return True

    return False


def test_write_integrity(parsed_record, dict_to_test):
        for k, v in dict_to_test.items():
            if isinstance(parsed_record[k], np.ndarray):
                if compare_arrays(parsed_record[k], v):
                    return k
            else:
                if isinstance(parsed_record[k], float):
                    if abs(parsed_record[k] - v) >= 1e-05:
                        return k
                else:
                    if parsed_record[k] != v:
                        return k
        return None


