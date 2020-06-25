# Copyright 2018 SuperDARN
# Authors: Marina Schmidt
"""
This file contains several class pertaining to dmap format types
that are used by SuperDARN.

For description of these fields and their units see the following reference
materials:
    https://superdarn.github.io/rst/superdarn/src.doc/rfc/index.html
    https://radar-software-toolkit-rst.readthedocs.io/en/latest/
"""


class Rawacf():
    """
    Class containing Rawacf fields
    """
    types = {
        'radar.revision.major': 'c',
        'radar.revision.minor': 'c',
        'origin.code': 'c',
        'origin.time': 's',
        'origin.command': 's',
        'cp': 'h',
        'stid': 'h',
        'time.yr': 'h',
        'time.mo': 'h',
        'time.dy': 'h',
        'time.hr': 'h',
        'time.mt': 'h',
        'time.sc': 'h',
        'time.us': 'i',
        'txpow': 'h',
        'nave': 'h',
        'atten': 'h',
        'lagfr': 'h',
        'smsep': 'h',
        'ercod': 'h',
        'stat.agc': 'h',
        'stat.lopwr': 'h',
        'noise.search': 'f',
        'noise.mean': 'f',
        'channel': 'h',
        'bmnum': 'h',
        'bmazm': 'f',
        'scan': 'h',
        'offset': 'h',
        'rxrise': 'h',
        'intt.sc': 'h',
        'intt.us': 'i',
        'txpl': 'h',
        'mpinc': 'h',
        'mppul': 'h',
        'mplgs': 'h',
        'nrang': 'h',
        'frang': 'h',
        'rsep': 'h',
        'xcf': 'h',
        'tfreq': 'h',
        'mxpwr': 'i',
        'lvmax': 'i',
        'rawacf.revision.major': 'i',
        'rawacf.revision.minor': 'i',
        'combf': 's',
        'thr': 'f',
        'ptab': 'h',
        'ltab': 'h',
        'slist': 'h',
        'pwr0': 'f'
        }
    correlation_field = {
        'acfd': 'f'
        }
    digitizing_field = {
            'ifmode': 'h'
            }
    fittex_field = {
            'mplgexs': 'h'
            }
    cross_correlation_field = {
            'xcfd': 'f'
            }


class Fitacf():
    """
    Class containing Fitacf fields
    """
    # Standard fields
    types = {
        'radar.revision.major': 'c',
        'radar.revision.minor': 'c',
        'origin.code': 'c',
        'origin.time': 's',
        'origin.command': 's',
        'cp': 'h',
        'stid': 'h',
        'time.yr': 'h',
        'time.mo': 'h',
        'time.dy': 'h',
        'time.hr': 'h',
        'time.mt': 'h',
        'time.sc': 'h',
        'time.us': 'i',
        'txpow': 'h',
        'nave': 'h',
        'atten': 'h',
        'lagfr': 'h',
        'smsep': 'h',
        'ercod': 'h',
        'stat.agc': 'h',
        'stat.lopwr': 'h',
        'noise.search': 'f',
        'noise.mean': 'f',
        'channel': 'h',
        'bmnum': 'h',
        'bmazm': 'f',
        'scan': 'h',
        'offset': 'h',
        'rxrise': 'h',
        'intt.sc': 'h',
        'intt.us': 'i',
        'txpl': 'h',
        'mpinc': 'h',
        'mppul': 'h',
        'mplgs': 'h',
        'nrang': 'h',
        'frang': 'h',
        'rsep': 'h',
        'xcf': 'h',
        'tfreq': 'h',
        'mxpwr': 'i',
        'lvmax': 'i',
        'combf': 's',
        'fitacf.revision.major': 'i',
        'fitacf.revision.minor': 'i',
        'noise.sky': 'f',
        'noise.lag0': 'f',
        'noise.vel': 'f',
        'ptab': 'h',
        'ltab': 'h',
        'pwr0': 'f'}
    extra_fields = {
            'ifmode': 'h',
            'mplgexs': 'h',
            }
    # Fields added if the data is good and can be
    # fitted
    fitted_fields = {
        'slist': 'h',
        'nlag': 'h',
        'qflg': 'c',
        'gflg': 'c',
        'p_l': 'f',
        'p_l_e': 'f',
        'p_s': 'f',
        'p_s_e': 'f',
        'v': 'f',
        'v_e': 'f',
        'w_l': 'f',
        'w_l_e': 'f',
        'w_s': 'f',
        'w_s_e': 'f',
        'sd_l': 'f',
        'sd_s': 'f',
        'sd_phi': 'f'}

    elevation_fields = {
        'x_qflg': 'c',
        'x_gflg': 'c',
        'x_p_l': 'f',
        'x_p_l_e': 'f',
        'x_p_s': 'f',
        'x_p_s_e': 'f',
        'x_v': 'f',
        'x_v_e': 'f',
        'x_w_l': 'f',
        'x_w_l_e': 'f',
        'x_w_s': 'f',
        'x_w_s_e': 'f',
        'phi0': 'f',
        'phi0_e': 'f',
        'elv': 'f',
        'elv_low': 'f',
        'elv_high': 'f',
        'x_sd_l': 'f',
        'x_sd_s': 'f',
        'x_sd_phi': 'f'
    }


class Grid():
    """
    Class containing the Grid fields
    """
    # Standard fields
    types = {
        'start.year': 'h',
        'start.month': 'h',
        'start.day': 'h',
        'start.hour': 'h',
        'start.minute': 'h',
        'start.second': 'd',
        'end.year': 'h',
        'end.month': 'h',
        'end.day': 'h',
        'end.hour': 'h',
        'end.minute': 'h',
        'end.second': 'd',
        'stid': 'h',
        'channel': 'h',
        'nvec': 'h',
        'freq': 'f',
        'major.revision': 'h',
        'minor.revision': 'h',
        'program.id': 'h',
        'noise.mean': 'f',
        'noise.sd': 'f',
        'gsct': 'h',
        'v.min': 'f',
        'v.max': 'f',
        'p.min': 'f',
        'p.max': 'f',
        'w.min': 'f',
        'w.max': 'f',
        've.min': 'f',
        've.max': 'f'}
    # Fields added if the data is good and was fitted
    # in the generation process of fitacf
    fitted_fields = {'vector.mlat': 'f',
                     'vector.vel.median': 'f',
                     'vector.channel': 'h',
                     'vector.stid': 'h',
                     'vector.vel.sd': 'f',
                     'vector.index': 'i',
                     'vector.kvect': 'f',
                     'vector.mlon': 'f'}
    # Extra fields if you include -ext in grid generation process
    extra_fields = {
        'vector.pwr.median': 'f',
        'vector.pwr.sd': 'f',
        'vector.wdt.median': 'f',
        'vector.wdt.sd': 'f'
    }


class Map():
    """
    Class containing possible Map fields
    """
    # Standard fields
    types = {
        'start.year': 'h',
        'start.month': 'h',
        'start.day': 'h',
        'start.hour': 'h',
        'start.minute': 'h',
        'start.second': 'd',
        'end.year': 'h',
        'end.month': 'h',
        'end.day': 'h',
        'end.hour': 'h',
        'end.minute': 'h',
        'end.second': 'd',
        'map.major.revision': 'h',
        'map.minor.revision': 'h',
        'doping.level': 'h',
        'model.wt': 'h',
        'error.wt': 'h',
        'IMF.flag': 'h',
        'IMF.delay': 'h',
        'IMF.Bx': 'd',
        'IMF.By': 'd',
        'IMF.Bz': 'd',
        'IMF.Vx': 'd',
        'IMF.tilt': 'd',
        'IMF.Kp': 'd',
        'hemisphere': 'h',
        'noigrf': 'h',
        'fit.order': 'h',
        'latmin': 'f',
        'chi.sqr': 'd',
        'chi.sqr.dat': 'd',
        'rms.err': 'd',
        'lon.shft': 'f',
        'lat.shft': 'f',
        'mlt.start': 'd',
        'mlt.end': 'd',
        'mlt.av': 'd',
        'pot.drop': 'd',
        'pot.drop.err': 'd',
        'pot.max': 'd',
        'pot.max.err': 'd',
        'pot.min': 'd',
        'pot.min.err': 'd',
        'stid': 'h',
        'channel': 'h',
        'nvec': 'h',
        'freq': 'f',
        'major.revision': 'h',
        'minor.revision': 'h',
        'program.id': 'h',
        'noise.mean': 'f',
        'noise.sd': 'f',
        'gsct': 'h',
        'v.min': 'f',
        'v.max': 'f',
        'p.min': 'f',
        'p.max': 'f',
        'w.min': 'f',
        'w.max': 'f',
        've.min': 'f',
        've.max': 'f',
        'vector.mlat': 'f',
        'vector.mlon': 'f',
        'vector.kvect': 'f',
        'vector.stid': 'h',
        'vector.channel': 'h',
        'vector.index': 'i',
        'vector.vel.median': 'f',
        'vector.vel.sd': 'f',
        }
    # Additional fields if you use map_addhmb
    hmb_fields = {
        'model.mlat': 'f',
        'model.mlon': 'f',
        'model.kvect': 'f',
        'model.vel.median': 'f',
        'boundary.mlat': 'f',
        'boundary.mlon': 'f',
    }
    # Additional fields if you use map_addmodel
    model_fields = {
         'model.angle': 's',
         'model.level': 's',
         'model.tilt': 's',
         'model.name': 's',
    }
    # Additional fields if you use map_addfit
    fit_fields = {
        'source': 's',
        'N': 'd',
        'N+1': 'd',
        'N+2': 'd',
        'N+3': 'd',
    }
    # Additional fields if you add -ext when
    # creating the map file in RST
    extra_fields = {
        'vector.pwr.median': 'f',
        'vector.pwr.sd': 'f',
        'vector.wdt.median': 'f',
        'vector.wdt.sd': 'f',
    }


class Iqdat():
    """
    Class contains Iqdat fields
    """
    # Standard Iqdat fields
    types = {
        'radar.revision.major': 'c',
        'radar.revision.minor': 'c',
        'origin.code': 'c',
        'origin.time': 's',
        'origin.command': 's',
        'cp': 'h',
        'stid': 'h',
        'time.yr': 'h',
        'time.mo': 'h',
        'time.dy': 'h',
        'time.hr': 'h',
        'time.mt': 'h',
        'time.sc': 'h',
        'time.us': 'i',
        'txpow': 'h',
        'nave': 'h',
        'atten': 'h',
        'lagfr': 'h',
        'smsep': 'h',
        'ercod': 'h',
        'stat.agc': 'h',
        'stat.lopwr': 'h',
        'noise.search': 'f',
        'noise.mean': 'f',
        'channel': 'h',
        'bmnum': 'h',
        'bmazm': 'f',
        'scan': 'h',
        'offset': 'h',
        'rxrise': 'h',
        'intt.sc': 'h',
        'intt.us': 'i',
        'txpl': 'h',
        'mpinc': 'h',
        'mppul': 'h',
        'mplgs': 'h',
        'nrang': 'h',
        'frang': 'h',
        'rsep': 'h',
        'xcf': 'h',
        'tfreq': 'h',
        'mxpwr': 'i',
        'lvmax': 'i',
        'iqdata.revision.major': 'i',
        'iqdata.revision.minor': 'i',
        'combf': 's',
        'seqnum': 'i',
        'chnnum': 'i',
        'smpnum': 'i',
        'skpnum': 'i',
        'ptab': 'h',
        'ltab': 'h',
        'tsc': 'i',
        'tus': 'i',
        'tatten': 'h',
        'tnoise': 'f',
        'toff': 'i',
        'tsze': 'i',
        'data': 'h',
        }
