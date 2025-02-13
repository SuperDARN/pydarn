# Copyright (C) 2023 SuperDARN Canada, University of Saskatchewan
# Author: Shibaji Chakraborty
#
# Modifications:
# 20230202 - CJM: Integrate code into pyDARN
#
# Disclaimer:
# pyDARN is under the LGPL v3 license found in the root directory LICENSE.md
# Everyone is permitted to copy and distribute verbatim copies of this license
# document, but changing it is not allowed.
#
# This version of the GNU Lesser General Public License incorporates the terms
# and conditions of version 3 of the GNU General Public License,
# supplemented by the additional permissions listed below.


"""filters.py: Module is dedicated to filters used on FITACF SuperDARN data."""

import copy
import datetime as dt
import numpy as np
import warnings

from pydarn import standard_warning_format

warnings.formatwarning = standard_warning_format

class Gate(object):
    """Class object to hold each range cell value

    Methods
    -------
    NA
    """
    def __init__(self, bm, i, params=["v", "w_l", "gflg", "p_l", "v_e", "elv"],
                 gflg_type=-1):
        """
        Initialize the parameters which will be stored in Gate
        Parameters
        ----------
        bm : beam object
            A collection of data from the filtering process
        i : int
            Index to store in collection
        params :
            Parameters to store in collection
        Returns
        -------
        NA
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
    """Class to hold one radar beam

    Methods
    -------
    set
    copy
    """
    def __init__(self):
        """ Initialize the instance """
        return

    def set(self, time, d,
            s_params=["bmnum", "noise.sky", "tfreq", "scan", "nrang"],
            v_params=["v", "w_l", "gflg", "p_l", "slist", "v_e", "elv"], k=None):
        """
        Parameters
        ----------
        time : datetime object
            Time of data in beam
        d : Dict
            Containing data for other parameters in beam
        s_params : list
            Other scalar params
        v_params : list
            Other vector params
        """
        for p in s_params:
            if p in d.keys():
                if p == "scan" and d[p] != 0:
                    setattr(self, p, 1)
                else:
                    setattr(self, p, d[p]) if k is None else setattr(self, p,
                                                                     d[p][k])
            else:
                setattr(self, p, None)
        for p in v_params:
            if p in d.keys():
                setattr(self, p, d[p])
            else:
                setattr(self, p, [])
        self.time = time
        return

    def copy(self, bm):
        """Copy all parameters"""
        for p in bm.__dict__.keys():
            setattr(self, p, getattr(bm, p))
        return


class Scan(object):
    """Class to hold one radar scans

    Methods
    -------
    update_time
    """
    def __init__(self):
        """ Initialize the instance """
        self.beams = []
        return

    def update_time(self):
        """
        Update stime and etime of the scan.
        """
        if len(self.beams) > 0:
            self.stime = min([b.time for b in self.beams])
            self.etime = max([b.time for b in self.beams])
        self.scan_time = 60 * np.rint((self.etime - self.stime)
                                      .total_seconds() / 60)
        return


class FetchData(object):
    """Class to fetch data from fitacf files

    Methods
    -------
    parse_data
    """
    def __init__(self, beam_sounds):
        """
        Initialize the variables in a fitacf file
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
        self.v_params = ["v", "w_l", "gflg", "p_l", "slist", "v_e", "elv"]
        self.scans, self.beams = [], []
        return

    def parse_data(self, by="scan"):
        """
        Parse data by data type

        Parameters
        ----------
        by: str
            "scan" - no other options for now

        Returns
        -------
        NA
        """
        for d in self.beam_sounds:
            time = dt.datetime(
                d["time.yr"],
                d["time.mo"],
                d["time.dy"],
                d["time.hr"],
                d["time.mt"],
                d["time.sc"],
                d["time.us"]
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


class Boxcar(object):
    """Class to filter data - Boxcar median filter.

    Methods
    -------
    format_data_for_pydarn
    run_filter
    __discard_repeating_beams__
    __do_filter__
    """
    def __init__(self, thresh=0.7, w=None, gflg_type=-1):
        """
        Initialize variables

        Parameters
        ----------
        thresh: float
            Threshold of the weight matrix
        w: list(list)
            Weight matrix
        pbnd: float
            Lower and upper bounds of IS / GS probability
        pth: float
            Probability of the threshold

        Returns
        -------
        NA
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

    def format_data_for_pydarn(self, original_data):
        """
        Place filtered data into original data structure for pyDARN
        only changing the data fields that were filtered

        Parameters
        ----------
        original_data: List[Dict]
            List of SuperDARN fitacf data

        Returns
        -------
        NA
        """
        # Deep copy original fitacf data
        self.copied_data = copy.deepcopy(original_data)
        # For each record in the fitacf data, find matching time in
        # filtered data, replace with the new filtered data
        for r, record in enumerate(original_data):
            # Track to see if match is found or not
            match_found = False
            record_time = dt.datetime(record["time.yr"], record["time.mo"],
                                      record["time.dy"], record["time.hr"],
                                      record["time.mt"], record["time.sc"],
                                      record["time.us"])
            for frec in self.filtered_data["beam_sounds"]:
                if record_time == frec['time']:
                    match_found = True
                    if not bool(frec['slist']):
                        # If new data is empty remove it from dictionary
                        self.copied_data[r].pop('slist', None)
                        self.copied_data[r].pop('v', None)
                        self.copied_data[r].pop('w_l', None)
                        self.copied_data[r].pop('p_l', None)
                        self.copied_data[r].pop('elv', None)
                        self.copied_data[r].pop('gflg', None)
                    else:
                        # Replace the data with new filtered data if there is
                        # new data to replace it
                        self.copied_data[r]['slist'] = np.array(frec['slist'])
                        self.copied_data[r]['v'] = np.array(frec['v'])
                        self.copied_data[r]['w_l'] = np.array(frec['w_l'])
                        self.copied_data[r]['p_l'] = np.array(frec['p_l'])
                        self.copied_data[r]['elv'] = np.array(frec['elv'])
                        self.copied_data[r]['gflg'] = np.array(frec['gflg'])
            # If no match is found for the record, then
            # empty the fields, new data needs to be empty
            if not match_found:
                self.copied_data[r].pop('slist', None)
                self.copied_data[r].pop('v', None)
                self.copied_data[r].pop('w_l', None)
                self.copied_data[r].pop('elv', None)
                self.copied_data[r].pop('gflg', None)
        return

    def run_filter(self, beam_sounds, cpus=1):
        """
        Set data and convert to scan objects

        Parameters
        ----------
        beam_sounds: List[Dict]
            List of SuperDARN fitacf data
        cpus: int
            Number of cpus available/rdesired
            to run in parallel (UNUSED)

        Returns
        -------
        copied_data: List[Dict]
            List of dictionaries that contain
            the new filtered data
        """
        warnings.warn('The boxcar filter may take 5-10 minutes to filter a ' +
                      'two hour FITACF file. For more information on this ' +
                      'filter see the documentation at ' +
                      'https://pydarn.readthedocs.io/en/main/') 
        warnings.warn('The boxcar filter may not be applicable to all data, '+
                      'for example, the boxcar filter should not be applied '+
                      'to twofsound data.')
        fd = FetchData(beam_sounds)
        fd.parse_data()
        self.scan_stacks = [fd.scans[i - 1: i + 2]
                            for i in range(1, len(fd.scans) - 1)]
        self.filtered_data = {"scans": [], "beams": [], "beam_sounds": []}
        if cpus > 1:
            # TODO: Parallel processing options
            # ray.init(num_cpus=cpus)
            # futures = [
            #    self.bx.doFilter.remote(scan_stack, comb=comb,
            #                            gflg_type=gflg_type)
            #    for scan_stack in scan_stacks
            # ]
            # self.filtered_data["scans"] = ray.get(futures)
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
            # Format the data for pyDARN plotting and return the new
            # filtered version of the fitacf data
            self.format_data_for_pydarn(beam_sounds)
        return self.copied_data

    def __discard_repeating_beams__(self, scan, ch=True):
        """
        Discard all more than one repeating beams

        Parameters
        ----------
        scan: Object
            Object containing a single SuperDARN scan

        Returns
        -------
        oscan: Object
            Object containing a single SuperDARN scan
            without repeating beams
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

    def __do_filter__(self, scans, params_to_run_filter=["v", "w_l",
                                                         "p_l", "elv"]):
        """
        Median filter based on the weight given by matrix (3X3X3) weight,
        and threshold based on thresh

        Parameters
        ----------
        scans: Object
            Object containing SuperDARN data in scans
        params_to_run_filter: list
            List of parameters to run boxcar filter

        Returns
        -------
        oscan: Object
            Object containing SuperDARN scans
        """
        scans = [self.__discard_repeating_beams__(s) for s in scans]
        if len(scans) == 3:
            w = self.w
            oscan = Scan()

            for b in scans[1].beams:
                bmnum = b.bmnum
                beam = Beam()
                beam.copy(b)

                for key in beam.__dict__.keys():
                    if type(getattr(beam, key)) is np.ndarray:
                        setattr(beam, key, [])

                for r in range(0, b.nrang):
                    box = [[[None for j in range(3)]
                            for k in range(3)] for n in range(3)]

                    # Iterate through time
                    for j in range(0, 3):
                        # Iterate through beam
                        for k in range(-1, 2):
                            # Iterate through gate
                            for n in range(-1, 2):
                                # Get the scan we are working on
                                s = scans[j]
                                if s is None:
                                    continue
                                # Get the beam we are working on
                                if s is None:
                                    continue
                                # Get the beam we are working on
                                tbm = None
                                for bm in s.beams:
                                    if bm.bmnum == bmnum + k:
                                        tbm = bm
                                if tbm is None:
                                    continue
                                # Check if target gate number is in the beam
                                if r + n in tbm.slist:
                                    ind = np.array(tbm.slist).tolist()\
                                            .index(r + n)
                                    box[j][k + 1][n + 1] = Gate(
                                        tbm, ind, gflg_type=self.gflg_type
                                    )
                                else:
                                    box[j][k + 1][n + 1] = 0
                    pts = 0.0
                    tot = 0.0
                    v, w_l, p_l, elv, gfx = \
                        list(), list(), list(), list(), list()

                    # Iterate through time
                    for j in range(0, 3):
                        # Iterate through beam
                        for k in range(0, 3):
                            # Iterate through gate
                            for n in range(0, 3):
                                bx = box[j][k][n]
                                if bx is None:
                                    continue
                                wt = w[j][k][n]
                                tot += wt
                                if bx != 0:
                                    pts += wt
                                    for m in range(0, wt):
                                        v.append(bx.v)
                                        w_l.append(bx.w_l)
                                        p_l.append(bx.p_l)
                                        elv.append(bx.elv)
                                        gfx = bx.gflg
                    # Check if we meet the threshold
                    if pts / tot >= self.thresh:
                        beam.slist.append(r)
                        beam.v.append(np.median(v))
                        beam.w_l.append(np.median(w_l))
                        beam.p_l.append(np.median(p_l))
                        beam.elv.append(np.median(elv))
                        beam.gflg.append(gfx)
                oscan.beams.append(beam)

            if len(oscan.beams) > 0:
                oscan.update_time()
                sorted(oscan.beams, key=lambda bm: bm.bmnum)
        else:
            oscan = Scan()
        return oscan
