from pydarn import DmapArray
from pydarn import DmapScalar
import numpy as np

dmap_data = [{'RST.version': DmapScalar('RST.version', '4.1', 1, 's'), 'stid': DmapScalar('stid', 3, 3, 'i'), 'FAC.vel': DmapArray('FAC.vel', np.array( [2.5,3.5,4.0], dtype=np.float32), 4, 'f', 1, [3])},
             {'RST.version': DmapScalar('RST.version', '4.1', 1, 's'), 'stid': DmapScalar('stid', 3, 3, 'i'), 'FAC.vel': DmapArray('FAC.vel', np.array( ['c','b','a'], dtype='|S1'), 1, 'c', 1, [3])},
             {'RST.version': DmapScalar('RST.version', '4.1', 1, 's'), 'stid': DmapScalar('stid', 3, 3, 'i'), 'FAC.vel': DmapArray('FAC.vel', np.array( [5.7,2.34,-0.2], dtype=np.float32), 4, 'f', 1, [3])}]


