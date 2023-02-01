#!/usr/bin/env python

# Author: Shibaji Chakraborty
#
# Disclaimer:
# pyDARN is under the LGPL v3 license found in the root directory LICENSE.md
# Everyone is permitted to copy and distribute verbatim copies of this license
# document, but changing it is not allowed.
#
# This version of the GNU Lesser General Public License incorporates the terms
# and conditions of version 3 of the GNU General Public License,
# supplemented by the additional permissions listed below.
#
# Modifications:
#


"""boxcar_filter.py: Module is dedicated to run 3X3X3 boxcar filtering."""

__author__ = "Chakraborty, S."
__credits__ = []
__version__ = "1.0."
__maintainer__ = "Chakraborty, S."
__email__ = "shibaji7@vt.edu"
__status__ = "Research"
__copyright__ = ""
__license__ = ""

import datetime as dt
import numpy as np
import copy


class Gate(object):
    """Class object to hold each range cell value"""

    def __init__(self, bm, i, params=["v", "w_l", "gflg", "p_l", "v_e"], gflg_type=-1):
        """
        initialize the parameters which will be stored
        bm: beam object
        i: index to store
        params: parameters to store
        """
        for p in params:
            if len(getattr(bm, p)) > i:
                setattr(self, p, getattr(bm, p)[i])
            else:
                setattr(self, p, np.nan)
        if gflg_type >= 0 and len(getattr(bm, "gsflg")[gflg_type]) > 0:
            setattr(self, "gflg", getattr(bm, "gsflg")[gflg_type][i])
        return  
    
class Beam(object):
    """Class to hold one radar beam"""

    def __init__(self):
        """ initialize the instance """
        return
    
    def set(self, time, d, s_params=["bmnum", "noise.sky", "tfreq", "scan", "nrang"],
            v_params=["v", "w_l", "gflg", "p_l", "slist", "v_e"], k=None):
        """
        Set all parameters
        time: datetime of beam
        d: data dict for other parameters
        s_param: other scalar params
        v_params: other list params
        """
        for p in s_params:
            if p in d.keys():
                if p == "scan" and d[p] != 0: setattr(self, p, 1)
                else: setattr(self, p, d[p]) if k is None else setattr(self, p, d[p][k])
            else: setattr(self, p, None)
        for p in v_params:
            if p in d.keys(): setattr(self, p, d[p])
            else: setattr(self, p, [])
        self.time = time
        return
    
    def copy(self, bm):
        """Copy all parameters"""
        for p in bm.__dict__.keys():
            setattr(self, p, getattr(bm, p))
        return
    
class Scan(object):
    """Class to hold one radar scans"""

    def __init__(self):
        """ initialize the instance """
        self.beams = []
        return
    
    def update_time(self):
        """
        Update stime and etime of the scan.
        up: Update average parameters if True
        """
        if len(self.beams) > 0:
            self.stime = min([b.time for b in self.beams])
            self.etime = max([b.time for b in self.beams])
        self.scan_time = 60 * np.rint((self.etime - self.stime).total_seconds() / 60)
        return
    
class FetchData(object):
    """Class to fetch data from fitacf files for one radar for atleast a day"""

    def __init__(
        self, beam_sounds
    ):
        """
        initialize the vars
        """
        self.beam_sounds = beam_sounds
        self.s_params = [
            "bmnum",
            "noise.sky",
            "tfreq",
            "scan",
            "nrang",
            "intt.sc",
            "intt.us",
            "mppul",
            "rsep",
            "cp",
            "frang",
            "smsep",
            "lagfr",
            "channel",
            "mplgs",
            "nave",
            "noise.search",
            "mplgexs",
            "xcf",
            "noise.mean",
            "ifmode",
            "bmazm",
            "rxrise",
            "mpinc",
        ]
        self.v_params = ["v", "w_l", "gflg", "p_l", "slist", "v_e"]
        self.scans, self.beams = [], []
        return
    
    def parse_data(self, by="scan"):
        """
        Parse data by data type
        """
        for d in self.beam_sounds:
            time = dt.datetime(
                d["time.yr"],
                d["time.mo"],
                d["time.dy"],
                d["time.hr"],
                d["time.mt"],
                d["time.sc"],
                d["time.us"],
            )
            bm = Beam()
            bm.set(time, d, self.s_params, self.v_params)
            self.beams.append(bm)
        if by == "scan":
            sc = Scan()
            sc.beams.append(self.beams[0])
            for _ix, d in enumerate(self.beams[1:]):
                if d.scan == 1:
                    sc.update_time()
                    self.scans.append(sc)
                    del sc
                    sc = Scan()
                    sc.beams.append(d)
                else:
                    sc.beams.append(d)
            self.scans.append(sc)
        return

def create_gaussian_weights(mu, sigma, _kernel=3, base_w=5):
    """
    Method used to create gaussian weights
    mu: n 1D list of all mean values
    sigma: n 1D list of sigma matrix
    """
    _k = (_kernel-1)/2
    _kNd = np.zeros((3,3,3))
    for i in range(_kernel):
        for j in range(_kernel):
            for k in range(_kernel):
                _kNd[i,j,k] = np.exp(-((float(i-_k)**2/(2*sigma[0]**2)) +\
                                       (float(j-_k)**2/(2*sigma[1]**2)) +\
                                       (float(k-_k)**2/(2*sigma[2]**2))))
    _kNd = np.floor(_kNd * base_w).astype(int)
    return _kNd

class Boxcar(object):
    """Class to filter data - Boxcar median filter."""

    def __init__(
        self,
        thresh=0.7,
        w=None,
        gflg_type=-1,
    ):
        """
        initialize variables

        thresh: Threshold of the weight matrix
        w: Weight matrix
        pbnd: Lower and upper bounds of IS / GS probability
        pth: Probability of the threshold
        """
        self.thresh = thresh
        if w is None:
            w = np.array(
                [
                    [[1, 2, 1], [2, 3, 2], [1, 2, 1]],
                    [[2, 3, 2], [3, 5, 3], [2, 3, 2]],
                    [[1, 2, 1], [2, 3, 2], [1, 2, 1]],
                ]
            )
        self.w = w
        self.gflg_type = gflg_type
        return
    
    def run_filter(self, beam_sounds, cpus=1):
        """
        Set data and convert to scan objects
        """
        fd = FetchData(beam_sounds)
        fd.parse_data()
        self.scan_stacks = [fd.scans[i - 1 : i + 2] for i in range(1, len(fd.scans) - 1)]
        self.filtered_data = {"scans": [], "beams": [], "beam_sounds": []}
        if cpus > 1:
#             ray.init(num_cpus=cpus)
#             futures = [
#                 self.bx.doFilter.remote(scan_stack, comb=comb, gflg_type=gflg_type)
#                 for scan_stack in scan_stacks
#             ]
#             self.filtered_data["scans"] = ray.get(futures)
            # TODO
            pass
        else:
            from collections import OrderedDict
            scans = [
                self.__do_filter__(scan_stack)
                for scan_stack in self.scan_stacks
            ]
            beams = []
            for s in scans:
                beams.extend(s.beams)
            self.filtered_data["scans"] = scans
            self.filtered_data["beams"] = beams
            self.filtered_data["beam_sounds"] = [
                OrderedDict([(k, getattr(b, k)) for k in b.__dict__.keys()])
                for b in beams
            ]
        return

    def __discard_repeting_beams__(self, scan, ch=True):
        """
        Discard all more than one repeting beams
        scan: SuperDARN scan
        """
        oscan = Scan()
        if ch:
            scan.beams = sorted(scan.beams, key=lambda bm: (bm.bmnum))
        else:
            scan.beams = sorted(scan.beams, key=lambda bm: (bm.bmnum, bm.time))
        bmnums = []
        for bm in scan.beams:
            if bm.bmnum not in bmnums:
                if hasattr(bm, "slist") and len(getattr(bm, "slist")) > 0:
                    oscan.beams.append(bm)
                    bmnums.append(bm.bmnum)
        if len(oscan.beams) > 0:
            oscan.update_time()
        oscan.beams = sorted(oscan.beams, key=lambda bm: bm.bmnum)
        return oscan

    def __do_filter__(self, scans, params_to_run_filter=["v", "w_l", "p_l"]):
        """
        Median filter based on the weight given by matrix (3X3X3) weight, 
        and threshold based on thresh
    
        params_to_run_filter: List of parameters to run boxcar filter
        """
        print(f"Date>>>{scans[1].stime}")
        scans = [self.__discard_repeting_beams__(s) for s in scans]
        if len(scans) == 3:
            w = self.w
            oscan = Scan()
            l_bmnum, r_bmnum = scans[1].beams[0].bmnum, scans[1].beams[-1].bmnum

            for b in scans[1].beams:
                bmnum = b.bmnum
                beam = Beam()
                beam.copy(b)

                for key in beam.__dict__.keys():
                    if type(getattr(beam, key)) == np.ndarray:
                        setattr(beam, key, [])

                for r in range(0, b.nrang):
                    box = [
                        [[None for j in range(3)] for k in range(3)] for n in range(3)
                    ]

                    for j in range(0, 3):  # iterate through time
                        for k in range(-1, 2):  # iterate through beam
                            for n in range(-1, 2):  # iterate through gate
                                # get the scan we are working on
                                s = scans[j]
                                if s == None:
                                    continue
                                # get the beam we are working on
                                if s == None:
                                    continue
                                # get the beam we are working on
                                tbm = None
                                for bm in s.beams:
                                    if bm.bmnum == bmnum + k:
                                        tbm = bm
                                if tbm == None:
                                    continue
                                # check if target gate number is in the beam
                                if r + n in tbm.slist:
                                    ind = np.array(tbm.slist).tolist().index(r + n)
                                    box[j][k + 1][n + 1] = Gate(
                                        tbm, ind, gflg_type=self.gflg_type
                                    )
                                else:
                                    box[j][k + 1][n + 1] = 0
                    pts = 0.0
                    tot = 0.0
                    v, w_l, p_l, gfx = list(), list(), list(), list()

                    for j in range(0, 3):  # iterate through time
                        for k in range(0, 3):  # iterate through beam
                            for n in range(0, 3):  # iterate through gate
                                bx = box[j][k][n]
                                if bx == None:
                                    continue
                                wt = w[j][k][n]
                                tot += wt
                                if bx != 0:
                                    pts += wt
                                    for m in range(0, wt):
                                        v.append(bx.v)
                                        w_l.append(bx.w_l)
                                        p_l.append(bx.p_l)
                                        gfx.append(bx.gflg)
                    if pts / tot >= self.thresh:  # check if we meet the threshold
                        beam.slist.append(r)
                        beam.v.append(np.median(v))
                        beam.w_l.append(np.median(w_l))
                        beam.p_l.append(np.median(p_l))
                oscan.beams.append(beam)

            if len(oscan.beams) > 0:
                oscan.update_time()
                sorted(oscan.beams, key=lambda bm: bm.bmnum)
        else:
            oscan = Scan()
        return oscan