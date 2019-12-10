# Copyright (C) 2019 SuperDARN
# Author: Marina Schmidt

"""
Test data sets for DmapWrite
"""
import numpy as np

from collections import OrderedDict

from pydarn import DmapScalar, DmapArray
iqdat_data = [OrderedDict([('radar.revision.major', np.int8(1)), ('radar.revision.minor', np.int8(17)), ('origin.code', np.int8(0)), ('origin.time', 'Wed Mar 16 19:45:04 2016'), ('origin.command', ''), ('cp', np.int16(-3560)), ('stid', np.int16(65)), ('time.yr', np.int16(2016)), ('time.mo', np.int16(3)), ('time.dy', np.int16(16)), ('time.hr', np.int16(19)), ('time.mt', np.int16(45)), ('time.sc', np.int16(1)), ('time.us', 277995), ('txpow', np.int16(9000)), ('nave', np.int16(16)), ('atten',
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      np.int16(0)),
                           ('lagfr', np.int16(600)), ('smsep', np.int16(100)), ('ercod', np.int16(0)), ('stat.agc', np.int16(0)), ('stat.lopwr', np.int16(0)), ('noise.search', np.float(1478.2957763671875)), ('noise.mean', np.float(456224.625)), ('channel', np.int16(0)), ('bmnum', np.int16(7)), ('bmazm', np.float(4.090000152587891)), ('scan', np.int16(1)), ('offset', np.int16(0)), ('rxrise', np.int16(100)), ('intt.sc', np.int16(2)), ('intt.us', 900000), ('txpl', np.int16(100)), ('mpinc',
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        np.int16(2400)),
                           ('mppul', np.int16(7)), ('mplgs', np.int16(18)), ('nrang', np.int16(75)), ('frang', np.int16(90)), ('rsep', np.int16(15)), ('xcf', np.int16(1)), ('tfreq', np.int16(12275)), ('mxpwr', 1073741824), ('lvmax', 20000), ('iqdata.revision.major', 0), ('iqdata.revision.minor', 0), ('combf', '$Id: multifonebm.c,v 1.0 2016/01/19 18:00:00 KKrieger Exp $'), ('seqnum', 16), ('chnnum', 2), ('smpnum', 729), ('skpnum', 7), ('ptab', np.array([ 0,  9, 12, 20, 22, 26, 27], dtype=np.int16)), ('ltab', np.array([[ 0,  0],
       [26, 27],
       [20, 22],
       [ 9, 12],
       [22, 26],
       [22, 27],
       [20, 26],
       [20, 27],
       [12, 20],
       [ 0,  9],
       [12, 22],
       [ 9, 20],
       [ 0, 12],
       [ 9, 22],
       [12, 26],
       [12, 27],
       [ 9, 26],
       [ 9, 27],
       [27, 27]], dtype=np.int16)), ('tsc', np.array([1458157502, 1458157502, 1458157502, 1458157502, 1458157502,
       1458157503, 1458157503, 1458157503, 1458157503, 1458157503,
       1458157503, 1458157503, 1458157503, 1458157503, 1458157504,
       1458157504], dtype=np.int32)), ('tus', np.array([ 562719,  769514,  872911,  979638, 1079705,  183702,  287083,
        390468,  496666,  597247,  703386,  804577,  907966, 1014047,
        114749,  220806], dtype=np.int32)), ('tatten', np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.int16)), ('tnoise', np.array([1478.2958, 1478.2958, 1478.2958, 1478.2958, 1478.2958, 1478.2958,
       1478.2958, 1478.2958, 1478.2958, 1478.2958, 1478.2958, 1478.2958,
       1478.2958, 1478.2958, 1478.2958, 1478.2958], dtype=np.float32)), ('toff', np.array([    0,  2916,  5832,  8748, 11664, 14580, 17496, 20412, 23328,
       26244, 29160, 32076, 34992, 37908, 40824, 43740], dtype=np.int32)), ('tsze', np.array([2916, 2916, 2916, 2916, 2916, 2916, 2916, 2916, 2916, 2916, 2916,
       2916, 2916, 2916, 2916, 2916], dtype=np.int32)), ('data', np.array([ -5, -11,   1,  -25, -11,  54], dtype=np.int16))]),]
