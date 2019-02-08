from pydarn import DmapArray
from pydarn import DmapScalar
import numpy as np

dmap_data = [{'RST.version': DmapScalar('RST.version', '4.1', 1, 's'), 'stid': DmapScalar('stid', 3, 1, 'i'), 'FAC.vel': DmapArray('FAC.vel', np.array( [2.5,3.5,4.0]), 6, 'f', 1, [3])},
             {'RST.version': DmapScalar('RST.version', '4.1', 1, 's'), 'stid': DmapScalar('stid', 3, 1, 'i'), 'FAC.vel': DmapArray('FAC.vel', np.array( [5.5,6.7,8.8]), 6, 'f', 1, [3])},
             {'RST.version': DmapScalar('RST.version', '4.1', 1, 's'), 'stid': DmapScalar('stid', 3, 1, 'i'), 'FAC.vel': DmapArray('FAC.vel', np.array( [5.7,2.34,-0.2]), 6, 'f', 1, [3])}]


