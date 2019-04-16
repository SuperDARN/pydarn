import deepdish as dd
import sys
import numpy as np
from datetime import datetime
import os

from dmap import DmapWrite
from pydarn import borealis_exceptions

code_to_stid = {
    "tst" : 0,
    "gbr" : 1,
    "sch" : 2,
    "kap" : 3,
    "hal" : 4,
    "sas" : 5,
    "pgr" : 6,
    "kod" : 7,
    "sto" : 8,
    "pyk" : 9,
    "han" : 10,
    "san" : 11,
    "sys" : 12,
    "sye" : 13,
    "tig" : 14,
    "ker" : 15,
    "ksr" : 16,
    "unw" : 18,
    "zho" : 19,
    "mcm" : 20,
    "fir" : 21,
    "sps" : 22,
    "bpk" : 24,
    "wal" : 32,
    "bks" : 33,
    "hok" : 40,
    "hkw" : 41,
    "inv" : 64,
    "rkn" : 65,
    "cly" : 66,
    "dce" : 96,
    "svb" : 128,
    "fhw" : 204,
    "fhe" : 205,
    "cvw" : 206,
    "cve" : 207,
    "adw" : 208,
    "ade" : 209,
    "azw" : 210,
    "aze" : 211,
    "sve" : 501,
    "svw" : 502,
    "ire" : 504,
    "irw" : 505,
    "kae" : 506,
    "kaw" : 507,
    "eje" : 508,
    "ejw" : 509,
    "she" : 510,
    "shw" : 511,
    "ekb" : 512,
}


class BorealisConversion():


	def __init__(filename, dmap_filetype):
		"""
		Attributes
		----------

		filename: name of file to read records from 
		origin_filetype: hdf5 filetype from borealis, indicating the record structure.
			ex. bfiq, output_ptrs_iq, ...
		dmap_filetype: intended SuperDARN legacy filetype to write to as dmap.
            Dmap file types, the following are supported:
                                     - 'iqdat' : SuperDARN file type
                                     - 'rawacf' : SuperDARN file type
                                     - 'fitacf' : SuperDARN file type
                                     - 'grid' : SuperDARN file type
                                     - 'map' : SuperDARN file type
                                     - 'dmap' : writes a file in DMAP format
                                     - 'stream' : writing to dmap data stream
		"""

		self.filename = filename
		self.records = read_records()

		self.origin_filetype = '.'.split(os.basename(self.filename))[-2]
		self.legacy_filetype = dmap_filetype

		self.dmap_records = convert_records_to_dmap()
		self.dmap_file = write_to_dmap()

	def read_records(self):

	    recs = dd.io.load(self.filename) 
	    return recs	

	def convert_records_to_dmap(self):

		if self.origin_filetype == 'bfiq':
			if self.dmap_filetype != 'iqdat':
				raise borealis_exceptions.BorealisConversionTypesError(self.filename, self.origin_filetype, self.dmap_filetype)






	    dmap_recs = []
	    for k, v in self.records.items():

	        reshaped_data = []
	        data = v['data'].reshape(v['data_dimensions'])
	        for i in range(v['num_sequences']):
	            arrays = [data[x][i] for x in range(data.shape[0])]
	            reshaped_data.append(np.ravel(np.column_stack(arrays)))

	        flattened_data = np.array(reshaped_data).flatten()

	        int_data = np.empty(flattened_data.size * 2, dtype=np.int32)
	        int_data[0::2] = flattened_data.real
	        int_data[1::2] = flattened_data.imag

	        offset = 2 * v['antenna_arrays_order'].shape[0] * v['num_samps']

	        dmap_recs.append({
	            'radar.revision.major' : np.int8(0),
	            'radar.revision.minor' : np.int8(0),
	            'origin.code' : np.int8(0),
	            'origin.time' : datetime.utcfromtimestamp(v['timestamp_of_write']).strftime("%c"),
	            'origin.command' : v['experiment_string'],
	            'cp' : np.int16(v['experiment_id']),
	            'stid' : np.int16(code_to_stid[v['station']]),
	            'time.yr' : np.int16(datetime.utcfromtimestamp(v['sqn_timestamps'][0]).year),
	            'time.mo' : np.int16(datetime.utcfromtimestamp(v['sqn_timestamps'][0]).month),
	            'time.dy' : np.int16(datetime.utcfromtimestamp(v['sqn_timestamps'][0]).day),
	            'time.hr' : np.int16(datetime.utcfromtimestamp(v['sqn_timestamps'][0]).hour),
	            'time.mt' : np.int16(datetime.utcfromtimestamp(v['sqn_timestamps'][0]).minute),
	            'time.sc' : np.int16(datetime.utcfromtimestamp(v['sqn_timestamps'][0]).second),
	            'time.us' : np.int16(datetime.utcfromtimestamp(v['sqn_timestamps'][0]).microsecond),
	            'txpow' : np.int16(0),
	            'nave' : np.int16(v['num_sequences']),
	            'atten' : np.int16(0),
	            'lagfr' : np.int16(v['first_range_rtt']),
	            'smsep' : np.int16(1e3/v['rx_sample_rate']),
	            'ercod' : np.int16(0),
	            'stat.agc' : np.int16(0),
	            'stat.lopwr' : np.int16(0),
	            'noise.search' : np.float32(0),
	            'noise.mean' : np.float32(0),
	            'channel' : np.int16(0),
	            'bmnum' : np.int16(v['beam_nums'][0]),
	            'bmazm' : np.float32(v['beam_azms'][0]),
	            'scan' : np.int16(v['scan_start_marker']),
	            'offset' : np.int16(0),
	            'rxrise' : np.int16(100),
	            'intt.sc' : np.int16(datetime.utcfromtimestamp(v['int_time']).second),
	            'intt.us' : np.int16(datetime.utcfromtimestamp(v['int_time']).microsecond),
	            'txpl' : np.int16(v['tx_pulse_len']),
	            'mpinc' : np.int16(v['tau_spacing']),
	            'mppul' : np.int16(v['num_pulses']),
	            'mplgs' : np.int16(v['num_lags']),
	            'nrang' : np.int16(v['num_ranges']),
	            'frang' : np.int16(v['first_range']),
	            'rsep' : np.int16(v['range_separation']),
	            'xcf' : np.int16(v['antenna_arrays_order'].shape[0] == 2),
	            'tfreq' : np.int16(v['freq']),
	            'mxpwr' : np.int32(0),
	            'lvmax' : np.int32(0),
	            'iqdata.revision.major' : np.int32(0),
	            'iqdata.revision.minor' : np.int32(0),
	            'combf' : v['comment'],
	            'seqnum' : np.int32(v['num_sequences']),
	            'chnnum' : np.int32(v['antenna_arrays_order'].shape[0]),
	            'smpnum' : np.int32(v['num_samps']),
	            'skpnum' : np.int32(6),
	            'ptab' : v['pulses'].astype(np.int16),
	            'ltab' : v['lags'].astype(np.int16),
	            'tsc' : np.array([datetime.utcfromtimestamp(x).second for x in v['sqn_timestamps']], dtype=np.int32),
	            'tus' : np.array([datetime.utcfromtimestamp(x).microsecond for x in v['sqn_timestamps']],dtype=np.int32),
	            'tatten' : np.array([0] * v['num_sequences'], dtype=np.int32),
	            'tnoise' : np.array([0] * v['num_sequences'], dtype=np.float32),
	            'toff' : np.array([i * offset for i in range(v['num_sequences'])], dtype=np.int32),
	            'tsze' : np.array([offset] * v['num_sequences'], dtype=np.int32),
	            'data' : int_data,
	        })

	    return dmap_recs

	def write_to_dmap(self):

	    #dm.dicts_to_file(dmap_recs,os.path.splitext(filename)[0]+".dmap",file_type='iqdat')

	    DmapWrite(self.dmap_records,os.path.splitext(filename)[0]+'.iqdat')

if __name__ == "__main__":
    main()