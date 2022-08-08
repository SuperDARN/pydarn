#!/usr/bin/env python

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


class Gate(object):
    """Class object to hold each range cell value"""
    
    def __init__(self):
        """ initialize the instance """
        return    
    
class Beam(object):
    """Class to hold one radar beam"""

    def __init__(self):
        """ initialize the instance """
        return
    
    def set(self, time, d, s_params=["bmnum", "noise.sky", "tfreq", "scan", "nrang"],
            v_params=["v", "w_l", "gflg", "p_l", "slist", "v_e"]):
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
    
class Scan(object):
    """Class to hold one radar scans"""

    def __init__(self, beams=[]):
        """ initialize the instance """
        self.beams = beams
        return
    
    def update_time(self):
        """
        Update stime and etime of the scan.
        up: Update average parameters if True
        """
        if len(self.beams) > 0:
            self.stime = min([b.time for b in self.beams])
            self.etime = max([b.time for b in self.beams])
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

class Filter(object):
    """Class to filter data - Boxcar median filter."""

    def __init__(self, thresh=.7, w=None):
        """
        initialize variables

        thresh: Threshold of the weight matrix
        w: Weight matrix
        """
        self.thresh = thresh
        if w is None: w = np.array([[[1,2,1],[2,3,2],[1,2,1]],
                                    [[2,3,2],[3,5,3],[2,3,2]],
                                    [[1,2,1],[2,3,2],[1,2,1]]])
        self.w = w
        self._beams, self._scans = [], []
        return
    
    def compile_data(self, data, s_params=["bmnum", "noise.sky", "tfreq", "scan", "nrang"],
                         v_params=["v", "w_l", "gflg", "p_l", "slist", "v_e"]):
        """
        Set data and convert to scan objects
        
        data: List of dictionary
        s_param: other scalar params
        v_params: other list params
        """        
        for d in data:
            time = dt.datetime(d["time.yr"], d["time.mo"], d["time.dy"], d["time.hr"], d["time.mt"], d["time.sc"], d["time.us"])
            if time >= self.date_range[0] and time <= self.date_range[1]:
                bm = Beam()
                bm.set(time, d, s_params,  v_params)
                self._beams.append(bm)
        scan, sc =  0, Scan()
        sc.beams.append(_b[0])
        for _ix, d in enumerate(_b[1:]):
            if d.scan == 1 and d.time != self._beams[_ix].time:
                sc.update_time()
                self._scans.append(sc)
                sc = Scan()
                sc.beams.append(d)
            else: sc.beams.append(d)
        self._scans.append(sc)
        return
    
    def __extract_ordered_dict__(self, fscans):
        """
        Extract ordered_dict list from list of scans
        """
        ol = list()
        for s in fscans:
            for b in s.beams:
                ol.append(b.__dict__)
        return ol
    
    def __discard_repeting_beams__(self, scan, ch=True):
        """
        Discard all more than one repeting beams
        scan: SuperDARN scan
        """
        oscan = Scan(scan.stime, scan.etime, scan.s_mode)
        if ch: scan.beams = sorted(scan.beams, key=lambda bm: (bm.bmnum))
        else: scan.beams = sorted(scan.beams, key=lambda bm: (bm.bmnum, bm.time))
        bmnums = []
        for bm in scan.beams:
            if bm.bmnum not in bmnums:
                if hasattr(bm, "slist") and len(getattr(bm, "slist")) > 0:
                    oscan.beams.append(bm)
                    bmnums.append(bm.bmnum)
        if len(oscan.beams) > 0: oscan.update_time()
        oscan.beams = sorted(oscan.beams, key=lambda bm: bm.bmnum)
        return oscan
    
    def filter(self, params_to_run_filter=["v", "w_l", "p_l"]):
        """
        Median filter based on the weight given by matrix (3X3X3) w, and threshold based on thresh
    
        params_to_run_filter: List of parameters to run boxcar filter
        """
        self._fscans = []
        if len(self._scans) > 3:
            scans = copy.copy(self._scans)
            for idx_scan in range(1, len(scans)-2):
                rscans = scans[idx_scan-1:idx_scan+2]
                self._fscans.append(
                    self.__do_filter__(
                        rscans, 
                        params_to_run_filter
                    )
                )
        ol = self.__extract_ordered_dict__(self._fscans)
        return ol
    
    def __do_filter__(self, scans, params_to_run_filter=["v", "w_l", "p_l"]):
        """
        Median filter based on the weight given by matrix (3X3X3) weight, 
        and threshold based on thresh
    
        params_to_run_filter: List of parameters to run boxcar filter
        """
        rscans = [self.__discard_repeting_beams__(rs) for rs in scans]
        w, thresh = copy.copy(self.w), copy.copy(self.thresh)
        l_bmnum, r_bmnum = scans[1].beams[0].bmnum, scans[1].beams[-1].bmnum
        oscan = Scan()
        
        for b in scans[1].beams:
            bmnum = b.bmnum
            beam = Beam()
            beam.copy(b)
            
            for key in beam.__dict__.keys():
                if type(getattr(beam, key)) == np.ndarray: setattr(beam, key, [])
            
            for r in range(0,b.nrang):
                box = [[[None for j in range(3)] for k in range(3)] for n in range(3)]
                
                for j in range(0,3):# iterate through time
                    for k in range(-1,2):# iterate through beam
                        for n in range(-1,2):# iterate through gate
                            # get the scan we are working on
                            s = scans[j]
                            if s == None: continue
                            # get the beam we are working on
                            if s == None: continue
                            # get the beam we are working on
                            tbm = None
                            for bm in s.beams:
                                if bm.bmnum == bmnum + k: tbm = bm
                            if tbm == None: continue
                            # check if target gate number is in the beam
                            if r+n in tbm.slist:
                                ind = np.array(tbm.slist).tolist().index(r + n)
                                box[j][k+1][n+1] = Gate(tbm, ind, gflg_type=gflg_type)
                            else: box[j][k+1][n+1] = 0
                            
                pts = 0.0
                tot = 0.0
                v, w_l, p_l = list(), list(), list()
                
                for j in range(0,3):# iterate through time
                    for k in range(0,3):# iterate through beam
                        for n in range(0,3):# iterate through gate
                            bx = box[j][k][n]
                            if bx == None: continue
                            wt = w[j][k][n]
                            tot += wt
                            if bx != 0:
                                pts += wt
                                for m in range(0, wt):
                                    v.append(bx.v)
                                    w_l.append(bx.w_l)
                                    p_l.append(bx.p_l)
                if pts / tot >= self.thresh:# check if we meet the threshold
                    beam.slist.append(r)
                    beam.v.append(np.median(v))
                    beam.w_l.append(np.median(w_l))
                    beam.p_l.append(np.median(p_l))
            oscan.beams.append(beam)
        if len(oscan.beams) > 0:
            oscan.update_time()
            sorted(oscan.beams, key=lambda bm: bm.bmnum)
        return oscan