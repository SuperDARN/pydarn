# Copyright (C) 2019 SuperDARN Canada, University of Saskatchewan
# Author: Marina Schmidt

import numpy as np

from pydarn import DmapArray, DmapScalar

dmap_data = [{'RST.version': DmapScalar('RST.version', '4.1', 9, 's'),
              'stid': DmapScalar('stid', 3, 3, 'i'),
              'FAC.vel': DmapArray('FAC.vel', np.array([2.5, 3.5, 4.0],
                                                       dtype=np.float32), 4,
                                   'f', 1, [3])},
             {'RST.version': DmapScalar('RST.version', '4.1', 9, 's'),
              'stid': DmapScalar('stid', 3, 3, 'i'),
              'FAC.vel': DmapArray('FAC.vel', np.array([1, 0, 1],
                                                       dtype=np.int8),
                                   1, 'c', 1, [3])},
             {'RST.version': DmapScalar('RST.version', '4.1', 9, 's'),
              'stid': DmapScalar('stid', 3, 3, 'i'),
              'FAC.vel': DmapArray('FAC.vel', np.array([5.7, 2.34, -0.2],
                                                       dtype=np.float32),
                                   4, 'f', 1, [3])}]
