# Copyright 2019 SuperDARN Canada, University of Saskatchewan
# Author: Marci Detwiller
"""
This file contains classes and functions for
converting of Borealis file types.

Classes
-------
BorealisConvert: Writes Borealis SuperDARN files types to
    SuperDARN SDARN files with DMap record structure

Exceptions
----------
BorealisFileTypeError
BorealisFieldMissingError
BorealisExtraFieldError
BorealisDataFormatTypeError
BorealisConversionTypesError
BorealisConvert2IqdatError
BorealisConvert2RawacfError

Notes
-----
BorealisConvert makes use of SDARNWrite to write to SuperDARN file types

See Also
--------
BorealisRead
BorealisWrite
BorealisSiteRead
BorealisSiteWrite
BorealisArrayRead
BorealisArrayWrite

For more information on Borealis data files and how they convert to dmap,
see: https://borealis.readthedocs.io/en/latest/

Future Work
-----------
Remove requirement for hdf5 filename by fixing Borealis datawrite so that
    slice_id is written. This must be fixed in the Borealis code.
Update noise values in SDarn fields when these can be calculated.

"""
import logging
import math
import numpy as np

from datetime import datetime
from typing import Union

from pydarn import (borealis_exceptions, BorealisRead, SDarnWrite, dict2dmap)

pydarn_log = logging.getLogger('pydarn')

# 3 letter radar code, mapped to station id for SDarn files conversion.
# TODO: when merged with plotting, remove this dictionary and call the
#    one in the plotting folder... also move Radars.py to a more
#    central location.
code_to_stid = {
    "tst": 0,
    "gbr": 1,
    "sch": 2,
    "kap": 3,
    "hal": 4,
    "sas": 5,
    "pgr": 6,
    "kod": 7,
    "sto": 8,
    "pyk": 9,
    "han": 10,
    "san": 11,
    "sys": 12,
    "sye": 13,
    "tig": 14,
    "ker": 15,
    "ksr": 16,
    "unw": 18,
    "zho": 19,
    "mcm": 20,
    "fir": 21,
    "sps": 22,
    "bpk": 24,
    "wal": 32,
    "bks": 33,
    "hok": 40,
    "hkw": 41,
    "inv": 64,
    "rkn": 65,
    "cly": 66,
    "dce": 96,
    "svb": 128,
    "fhw": 204,
    "fhe": 205,
    "cvw": 206,
    "cve": 207,
    "adw": 208,
    "ade": 209,
    "ekb": 512,
}


class BorealisConvert(BorealisRead):
    """
    Class for converting Borealis filetypes to SDARN DMap filetypes.

    See Also
    --------
    BorealisRawacf
    BorealisBfiq
    Rawacf
    Iqdat
    BorealisRead
    BorealisSiteRead
    BorealisArrayRead
    SDarnWrite

    Attributes
    ----------
    allowed_conversions: dict
        Mapping of allowed Borealis types to their corresponding
        SDARN DMap converted types.
    filename: str; borealis_filename: str
        The filename of the Borealis HDF5 file being read.
    borealis_filetype: str
        The type of Borealis file. Types include:
        'bfiq'
        'rawacf'
    reader: Union[BorealisSiteWrite, BorealisArrayWrite]
        the wrapped BorealisSiteRead or BorealisArrayRead instance
    borealis_file_structure: Union[str, None]
        The structure of the file read, 'site' or 'array'. Default None.
    records: OrderedDict{dict}; borealis_records: OrderedDict{dict}
        The Borealis data in a dictionary of records, according to the
        site file format. The conversion functions use
        record format only as that is what is used by SDARN DMap
        files.
    arrays: dict
        The Borealis data in a dictionary of arrays, according to the
        restructured array file format.
    record_names: list[str]
        A sorted list of the set of record names in the HDF5 file read.
        These correspond to Borealis file record write times (in ms since
        epoch), and are equal to the group names in the site file types.
    sdarn_filename: str
        The filename of the SDARN DMap file to be written.
    sdarn_dmap_records: list[dict]
        The converted DMap records to write to file.
    sdarn_dict: dict
        The dictionary of SDARN records before the conversion to DMap format.
    sdarn_filetype: str
        The dmap filetype converted to. 'rawacf' and 'iqdat' are allowed.
    borealis_slice_id: int
        The slice id of the file being converted. Used as channel identifier
        in SDARN DMap records.
    """

    __allowed_conversions = {'rawacf': 'rawacf', 'bfiq': 'iqdat'}

    def __init__(self, borealis_filename: str, borealis_filetype: str,
                 sdarn_filename: str, borealis_slice_id: int,
                 borealis_file_structure: Union[str, None] = None):
        """
        Convert HDF5 Borealis records to a given SDARN file with DMap format.

        Parameters
        ----------
        borealis_filename: str
            file name containing Borealis hdf5 data. Name contains slice id
            and allows the file read.
        borealis_filetype: str
            The type of Borealis file. Types allowed to convert:
            'bfiq' -> 'iqdat'
            'rawacf' -> 'rawacf'
        sdarn_filename: str
            The filename of the SDARN DMap file to be written.
        borealis_slice_id: int
            The slice id of the file being converted.
        borealis_file_structure: Union[str, None]
            The write structure of the file provided. Possible types are
            'site', 'array', or None. If None (default), array read will be
            attempted first followed by site.

        Raises
        ------
        BorealisConversionTypesError
        ConvertFileOverWriteError
        """

        super(BorealisConvert, self).__init__(borealis_filename,
                                              borealis_filetype,
                                              borealis_file_structure)

        # Attributes written in the parent init (BorealisRead):
        #   filename : str
        #   borealis_filetype : str
        #   reader: Union[BorealisSiteRead, BorealisArrayRead]
        #   borealis_file_structure : str
        #   records : dict (of data)
        #   arrays : dict (of data)

        self.borealis_records = self.records
        self.sdarn_filename = sdarn_filename
        self.borealis_filename = self.filename
        self._borealis_slice_id = borealis_slice_id
        self._sdarn_dmap_records = {}
        self._sdarn_dict = {}
        try:
            self._sdarn_filetype = self.__allowed_conversions[
                    self.borealis_filetype]
        except KeyError:
            raise borealis_exceptions.BorealisConversionTypesError(
                self.sdarn_filename, self.borealis_filetype,
                self.__allowed_conversions)

        if self.borealis_filename == self.sdarn_filename:
            raise borealis_exceptions.ConvertFileOverWriteError(
                    self.borealis_filename)
        self._write_to_sdarn()

    def __repr__(self):
        """ for representation of the class object"""

        return "{class_name}({records}{borealis_filetype}{sdarn_filename})"\
               "".format(class_name=self.__class__.__name__,
                         records=self.records,
                         borealis_filetype=self.borealis_filetype,
                         sdarn_filename=self.sdarn_filename)

    def __str__(self):
        """ for printing of the class object"""

        return "Converting {total_records} {borealis_filetype} records into "\
               "DMap SDARN records and writing to file {sdarn_filename}."\
               "".format(total_records=len(self.borealis_records.keys()),
                         borealis_filetype=self.borealis_filetype,
                         sdarn_filename=self.sdarn_filename)

    @property
    def sdarn_dmap_records(self):
        """
        The converted SDARN DMap records to write to file.
        """
        return self._sdarn_dmap_records

    @property
    def sdarn_dict(self):
        """
        The converted SDARN records as a dictionary, before being converted
        to DMap.
        """
        return self._sdarn_dict

    @property
    def sdarn_filetype(self):
        """
        The dmap filetype converted to. 'rawacf' and 'iqdat' are allowed.
        """
        return self._sdarn_filetype

    @property
    def borealis_slice_id(self):
        """
        The slice id of the file being converted. Used as channel identifier
        in SDARN DMap records.
        """
        return self._borealis_slice_id

    def _write_to_sdarn(self) -> str:
        """
        Write the Borealis records as SDARN DMap records to a file using PyDARN
        IO.

        Returns
        -------
        sdarn_filename, the name of the SDARN file written.
        """

        self._convert_records_to_dmap()
        sdarn_writer = SDarnWrite(self._sdarn_dmap_records,
                                  self.sdarn_filename)
        if self.sdarn_filetype == 'iqdat':
            sdarn_writer.write_iqdat(self.sdarn_filename)
        elif self.sdarn_filetype == 'rawacf':
            sdarn_writer.write_rawacf(self.sdarn_filename)
        return self.sdarn_filename

    def _convert_records_to_dmap(self):
        """
        Convert the Borealis records to the a DMap filetype according to
        the origin filetype.

        Raises
        ------
        BorealisConversionTypesError
        """
        if self.sdarn_filetype == 'iqdat':
            if self._is_convertible_to_iqdat():
                self._convert_bfiq_to_iqdat()
        elif self.sdarn_filetype == 'rawacf':
            if self._is_convertible_to_rawacf():
                self._convert_rawacf_to_rawacf()
        else:  # nothing else is currently supported
            raise borealis_exceptions.BorealisConversionTypesError(
                self.sdarn_filename, self.borealis_filetype,
                self.__allowed_conversions)

    def _is_convertible_to_iqdat(self) -> bool:
        """
        Checks if the file is convertible to iqdat.

        The file is convertible if:
            - the origin filetype is bfiq
            - the blanked_samples array = pulses array for all records
            - the pulse_phase_offset array contains all zeroes for all records

        Raises
        ------
        BorealisConversionTypesError
        BorealisConvert2IqdatError

        Returns
        -------
        True if convertible
        """
        if self.borealis_filetype != 'bfiq':
            raise borealis_exceptions.BorealisConversionTypesError(
                self.sdarn_filename, self.borealis_filetype,
                self.__allowed_conversions)
        else:  # There are some specific things to check
            for k, v in self.borealis_records.items():
                if not np.array_equal(v['blanked_samples'],
                                      v['pulses'] *
                                      int(v['tau_spacing']/v['tx_pulse_len'])):
                    raise borealis_exceptions.\
                            BorealisConvert2IqdatError('Increased complexity:'
                                                       ' Borealis bfiq file'
                                                       ' record {}'
                                                       ' blanked_samples {}'
                                                       ' does not equal pulses'
                                                       ' array {}'
                                                       ''.format(k,
                                                                 v['blanked_samples'],
                                                                 v['pulses']))
                if not all([x == 0 for x in v['pulse_phase_offset']]):
                    raise borealis_exceptions.\
                            BorealisConvert2IqdatError('Increased complexity:'
                                                       ' Borealis bfiq file'
                                                       ' record {}'
                                                       ' pulse_phase_offset {}'
                                                       ' contains non-zero'
                                                       ' values.'
                                                       ''.format(k,
                                                                 v['pulse_phase_offset']))
        return True

    def _is_convertible_to_rawacf(self) -> bool:
        """
        Checks if the file is convertible to rawacf.

        The file is convertible if:
            - the origin filetype is rawacf
            - the blanked_samples array = pulses array for all records
            - the pulse_phase_offset array contains all zeroes for all records

        TODO: should this fail for multiple beams in the same
        integration time. IE, is it ok for dmap files to have multiple
        records with same origin time and timestamps due to a different
        beam azimuth.

        Raises
        ------
        BorealisConversionTypesError
        BorealisConvert2RawacfError

        Returns
        -------
        True if convertible
        """
        if self.borealis_filetype != 'rawacf':
            raise borealis_exceptions.\
                    BorealisConversionTypesError(self.sdarn_filename,
                                                 self.borealis_filetype,
                                                 self.__allowed_conversions)
        else:  # There are some specific things to check
            for k, v in self.borealis_records.items():
                if not np.array_equal(v['blanked_samples'],
                                      v['pulses'] *
                                      int(v['tau_spacing']/v['tx_pulse_len'])):
                    raise borealis_exceptions.\
                            BorealisConvert2RawacfError('Increased complexity:'
                                                        ' Borealis rawacf file'
                                                        ' record {}'
                                                        ' blanked_samples {}'
                                                        'does not equal'
                                                        ' pulses array {}'
                                                        ''.format(k,
                                                                  v['blanked_samples'],
                                                                  v['pulses']))

        return True

    def _convert_bfiq_to_iqdat(self):
        """
        Conversion for bfiq to iqdat SDARN DMap records.

        See Also
        --------
        https://superdarn.github.io/rst/superdarn/src.doc/rfc/0027.html
        https://borealis.readthedocs.io/en/latest/
        BorealisBfiq
        Iqdat

        Raises
        ------
        BorealisConvert2IqdatError

        Returns
        -------
        dmap_recs, the records converted to DMap format
        """
        try:
            recs = []
            for record in self.borealis_records.items():
                record_dict = \
                        self.__convert_bfiq_record(self.borealis_slice_id,
                                                   record,
                                                   self.borealis_filename)
                recs.append(record_dict)
            self._sdarn_dict = recs
            self._sdarn_dmap_records = dict2dmap(recs)
        except Exception as e:
            raise borealis_exceptions.BorealisConvert2IqdatError(e) from e

    @staticmethod
    def __convert_bfiq_record(borealis_slice_id: int,
                              borealis_bfiq_record: tuple,
                              origin_string: str) -> dict:
        """
        Converts a single record dict of Borealis bfiq data to a SDARN DMap
        record dict.

        Parameters
        ----------
        borealis_slice_id : int
            slice id integer of the borealis data, for conversion. Used
            as SDARN DMap channel identifier.
        borealis_bfiq_record : tuple(str, dict)
            Key is bfiq record timestamp, value is dictionary of bfiq
            record data.
        origin_string : str
            String representing origin of the Borealis data, typically
            Borealis filename.
        """

        # key value pair from Borealis bfiq record.
        (k, v) = borealis_bfiq_record

        # data_descriptors (dimensions) are num_antenna_arrays,
        # num_sequences, num_beams, num_samps
        # scale by normalization and then scale to integer max as per
        # dmap style
        data = v['data'].reshape(v['data_dimensions']).astype(np.complex128) / \
            v['data_normalization_factor'] * np.iinfo(np.int16).max

        # Borealis git tag version numbers. If not a tagged version,
        # then use 255.255
        if v['borealis_git_hash'][0] == 'v' and \
                v['borealis_git_hash'][2] == '.':

            borealis_major_revision = v['borealis_git_hash'][1]
            borealis_minor_revision = v['borealis_git_hash'][3]
        else:
            borealis_major_revision = 255
            borealis_minor_revision = 255

        # base offset for setting the toff field in SDARN DMap iqdat file.
        offset = 2 * v['antenna_arrays_order'].shape[0] * v['num_samps']

        for beam_index, beam in enumerate(v['beam_nums']):
            # grab this beam's data
            # shape is now num_antenna_arrays x num_sequences
            # x num_samps
            this_data = data[:, :, beam_index, :]
            # iqdat shape is num_sequences x num_antennas_arrays x
            # num_samps x 2 (real, imag), flattened
            reshaped_data = []
            for i in range(v['num_sequences']):
                # get the samples for each array 1 after the other
                arrays = [this_data[x, i, :]
                          for x in range(this_data.shape[0])]
                # append
                reshaped_data.append(np.ravel(np.column_stack(arrays)))

            # (num_sequences x num_antenna_arrays x num_samps,
            # flattened)
            flattened_data = np.array(reshaped_data).flatten()

            int_data = np.empty(flattened_data.size * 2, dtype=np.int16)
            int_data[0::2] = flattened_data.real
            int_data[1::2] = flattened_data.imag

            # flattening done in convert_to_dmap_datastructures
            record_dict = {
                'radar.revision.major': np.int8(borealis_major_revision),
                'radar.revision.minor': np.int8(borealis_minor_revision),
                'origin.code': np.int8(100),  # indicating Borealis
                'origin.time': datetime.\
                utcfromtimestamp(v['sqn_timestamps'][0]).strftime("%c"),
                'origin.command': 'Borealis ' + v['borealis_git_hash'] + \
                ' ' + v['experiment_name'],
                'cp': np.int16(v['experiment_id']),
                'stid': np.int16(code_to_stid[v['station']]),
                'time.yr': np.int16(datetime.
                                    utcfromtimestamp(v['sqn_timestamps'][0]).
                                    year),
                'time.mo': np.int16(datetime.
                                    utcfromtimestamp(v['sqn_timestamps'][0]).
                                    month),
                'time.dy': np.int16(datetime.
                                    utcfromtimestamp(v['sqn_timestamps'][0]).
                                    day),
                'time.hr': np.int16(datetime.
                                    utcfromtimestamp(v['sqn_timestamps'][0]).
                                    hour),
                'time.mt': np.int16(datetime.
                                    utcfromtimestamp(v['sqn_timestamps'][0]).
                                    minute),
                'time.sc': np.int16(datetime.
                                    utcfromtimestamp(v['sqn_timestamps'][0]).
                                    second),
                'time.us': np.int32(datetime.
                                    utcfromtimestamp(v['sqn_timestamps'][0]).
                                    microsecond),
                'txpow': np.int16(-1),
                'nave': np.int16(v['num_sequences']),
                'atten': np.int16(0),
                'lagfr': np.int16(v['first_range_rtt']),
                # smsep is in us; conversion from seconds
                'smsep': np.int16(1e6 / v['rx_sample_rate']),
                'ercod': np.int16(0),
                # TODO: currently not implemented
                'stat.agc': np.int16(0),
                # TODO: currently not implemented
                'stat.lopwr': np.int16(0),
                # TODO: currently not implemented
                'noise.search': np.float32(v['noise_at_freq'][0]),
                # TODO: currently not implemented
                'noise.mean': np.float32(0),
                'channel': np.int16(borealis_slice_id),
                'bmnum': np.int16(beam),
                'bmazm': np.float32(v['beam_azms'][beam_index]),
                'scan': np.int16(v['scan_start_marker']),
                # no digital receiver offset or rxrise required in
                # Borealis
                'offset': np.int16(0),
                'rxrise': np.int16(0),
                'intt.sc': np.int16(math.floor(v['int_time'])),
                'intt.us': np.int32(math.fmod(v['int_time'], 1.0) * 1e6),
                'txpl': np.int16(v['tx_pulse_len']),
                'mpinc': np.int16(v['tau_spacing']),
                'mppul': np.int16(len(v['pulses'])),
                # an alternate lag-zero will be given, so subtract 1.
                'mplgs': np.int16(v['lags'].shape[0] - 1),
                'nrang': np.int16(v['num_ranges']),
                'frang': np.int16(round(v['first_range'])),
                'rsep': np.int16(round(v['range_sep'])),
                'xcf': np.int16('intf' in v['antenna_arrays_order']),
                'tfreq': np.int16(v['freq']),
                # mxpwr filler; cannot specify this information
                'mxpwr': np.int32(-1),
                # lvmax RST default
                'lvmax': np.int32(20000),
                'iqdata.revision.major': np.int32(1),
                'iqdata.revision.minor': np.int32(0),
                'combf': 'Converted from Borealis file: ' + origin_string +\
                         ' record ' + str(k) + \
                         ' ; Number of beams in record: ' + \
                         str(len(v['beam_nums'])) + ' ; ' + \
                         v['experiment_comment'] + ' ; ' + \
                         v['slice_comment'],
                'seqnum': np.int32(v['num_sequences']),
                'chnnum': np.int32(v['antenna_arrays_order'].shape[0]),
                'smpnum': np.int32(v['num_samps']),
                # NOTE: The following is a hack. This is currently how
                # iqdat files are being processed . RST make_raw does
                # not use first range information at all, only skip
                # number.
                # However ROS provides the number of ranges to the
                # first range as the skip number. Skip number is
                # documented as number to identify bad ranges due
                # to digital receiver rise time. Borealis skpnum should
                # in theory =0 as the first sample from Borealis
                # decimated (prebfiq) data is centred on the first
                # pulse.
                'skpnum': np.int32(v['first_range'] / v['range_sep']),
                'ptab': v['pulses'].astype(np.int16),
                'ltab': v['lags'].astype(np.int16),
                # timestamps in ms, convert to seconds and us.
                'tsc': np.array([math.floor(x/1e3) for x in
                                 v['sqn_timestamps']], dtype=np.int32),
                'tus': np.array([math.fmod(x, 1000.0) * 1e3 for x in
                                 v['sqn_timestamps']], dtype=np.int32),
                'tatten': np.array([0] * v['num_sequences'],
                                   dtype=np.int16),
                'tnoise': v['noise_at_freq'].astype(np.float32),
                'toff': np.array([i * offset for i in
                                  range(v['num_sequences'])], dtype=np.int32),
                'tsze': np.array([offset] * v['num_sequences'],
                                 dtype=np.int32),
                'data': int_data
            }
        return record_dict

    def _convert_rawacf_to_rawacf(self):
        """
        Conversion for Borealis hdf5 rawacf to SDARN DMap rawacf files.

        See Also
        --------
        __convert_rawacf_record
        https://superdarn.github.io/rst/superdarn/src.doc/rfc/0008.html
        https://borealis.readthedocs.io/en/latest/
        BorealisRawacf
        Rawacf

        Raises
        ------
        BorealisConvert2RawacfError

        Returns
        -------
        dmap_recs, the records converted to DMap format
        """
        try:
            recs = []
            for record in self.borealis_records.items():
                record_dict = \
                        self.__convert_rawacf_record(self.borealis_slice_id,
                                                     record,
                                                     self.borealis_filename)
                recs.append(record_dict)
            self._sdarn_dict = recs
            self._sdarn_dmap_records = dict2dmap(recs)
        except Exception as e:
            raise borealis_exceptions.BorealisConvert2RawacfError(e) from e

    @staticmethod
    def __convert_rawacf_record(borealis_slice_id: int,
                                borealis_rawacf_record: tuple,
                                origin_string: str) -> dict:
        """
        Converts a single record dict of Borealis rawacf data to a SDARN DMap
        record dict.

        Parameters
        ----------
        borealis_slice_id : int
            slice id integer of the borealis data, for conversion. Used
            as SDARN DMap channel identifier.
        borealis_rawacf_record : tuple(str, dict)
            Key is rawacf record timestamp, value is dictionary of rawacf
            record data.
        origin_string : str
            String representing origin of the Borealis data, typically
            Borealis filename.
        """

        # key value pair from Borealis record dictionary
        (k, v) = borealis_rawacf_record

        shaped_data = {}
        # correlation_descriptors are num_beams, num_ranges, num_lags
        # scale by the scale squared to make up for the multiply
        # in correlation (integer max squared)
        shaped_data['main_acfs'] = v['main_acfs'].reshape(
            v['correlation_dimensions']).astype(
            np.complex128) * ((np.iinfo(np.int16).max**2) /
                              (v['data_normalization_factor']**2))

        if 'intf_acfs' in v.keys():
            shaped_data['intf_acfs'] = v['intf_acfs'].reshape(
                v['correlation_dimensions']).astype(np.complex128) * \
                    ((np.iinfo(np.int16).max**2) /
                     (v['data_normalization_factor']**2))
        if 'xcfs' in v.keys():
            shaped_data['xcfs'] = v['xcfs'].reshape(
                v['correlation_dimensions']).astype(np.complex128) *\
                    ((np.iinfo(np.int16).max**2) /
                     (v['data_normalization_factor']**2))

        # Borealis git tag version numbers. If not a tagged version,
        # then use 255.255
        if v['borealis_git_hash'][0] == 'v' and \
                v['borealis_git_hash'][2] == '.':
            borealis_major_revision = v['borealis_git_hash'][1]
            borealis_minor_revision = v['borealis_git_hash'][3]
        else:
            borealis_major_revision = 255
            borealis_minor_revision = 255

        for beam_index, beam in enumerate(v['beam_nums']):
            # this beam, all ranges lag 0
            lag_zero = shaped_data['main_acfs'][beam_index, :, 0]
            lag_zero[-10:] = shaped_data['main_acfs'][beam_index, -10:, -1]
            lag_zero_power = (lag_zero.real**2 + lag_zero.imag**2)**0.5

            correlation_dict = {}
            for key in shaped_data:
                # num_ranges x num_lags (complex)
                this_correlation = shaped_data[key][beam_index, :, :-1]
                # set the lag0 to the alternate lag0 for the end of the
                # array (when interference of first pulse would occur)
                this_correlation[-10:, 0] = \
                    shaped_data[key][beam_index, -10:, -1]
                # shape num_beams x num_ranges x num_la gs, now
                # num_ranges x num_lags-1 b/c alternate lag-0 combined
                # with lag-0 (only used for last ranges)

                # (num_ranges x num_lags, flattened)
                flattened_data = np.array(this_correlation).flatten()

                int_data = np.empty(flattened_data.size * 2, dtype=np.float32)
                int_data[0::2] = flattened_data.real
                int_data[1::2] = flattened_data.imag
                # num_ranges x num_lags x 2; num_lags is one less than
                # in Borealis file because Borealis keeps alternate
                # lag0
                new_data = int_data.reshape(v['correlation_dimensions'][1],
                                            v['correlation_dimensions'][2]-1,
                                            2)
                # NOTE: Flattening happening in
                # convert_to_dmap_datastructures
                # place the SDARN-style array in the dict
                correlation_dict[key] = new_data

            record_dict = {
                'radar.revision.major': np.int8(borealis_major_revision),
                'radar.revision.minor': np.int8(borealis_minor_revision),
                'origin.code': np.int8(100),  # indicating Borealis
                'origin.time': datetime.\
                utcfromtimestamp(v['sqn_timestamps'][0]).strftime("%c"),
                'origin.command': 'Borealis ' + v['borealis_git_hash'] +\
                ' ' + v['experiment_name'],
                'cp': np.int16(v['experiment_id']),
                'stid': np.int16(code_to_stid[v['station']]),
                'time.yr': np.int16(datetime.
                                    utcfromtimestamp(v['sqn_timestamps'][0]).
                                    year),
                'time.mo': np.int16(datetime.
                                    utcfromtimestamp(v['sqn_timestamps'][0]).
                                    month),
                'time.dy': np.int16(datetime.
                                    utcfromtimestamp(v['sqn_timestamps'][0]).
                                    day),
                'time.hr': np.int16(datetime.
                                    utcfromtimestamp(v['sqn_timestamps'][0]).
                                    hour),
                'time.mt': np.int16(datetime.
                                    utcfromtimestamp(v['sqn_timestamps'][0]).
                                    minute),
                'time.sc': np.int16(datetime.
                                    utcfromtimestamp(v['sqn_timestamps'][0]).
                                    second),
                'time.us': np.int32(datetime.
                                    utcfromtimestamp(v['sqn_timestamps'][0]).
                                    microsecond),
                'txpow': np.int16(-1),
                # see Borealis documentation
                'nave': np.int16(v['num_sequences']),
                'atten': np.int16(0),
                'lagfr': np.int16(v['first_range_rtt']),
                'smsep': np.int16(1e6/v['rx_sample_rate']),
                'ercod': np.int16(0),
                # TODO: currently not implemented
                'stat.agc': np.int16(0),
                # TODO: currently not implemented
                'stat.lopwr': np.int16(0),
                # TODO: currently not implemented
                'noise.search': np.float32(v['noise_at_freq'][0]),
                # TODO: currently not implemented
                'noise.mean': np.float32(0),
                'channel': np.int16(borealis_slice_id),
                'bmnum': np.int16(beam),
                'bmazm': np.float32(v['beam_azms'][beam_index]),
                'scan': np.int16(v['scan_start_marker']),
                # no digital receiver offset or rxrise required in
                # Borealis
                'offset': np.int16(0),
                'rxrise': np.int16(0),
                'intt.sc': np.int16(math.floor(v['int_time'])),
                'intt.us': np.int32(math.fmod(v['int_time'], 1.0) * 1e6),
                'txpl': np.int16(v['tx_pulse_len']),
                'mpinc': np.int16(v['tau_spacing']),
                'mppul': np.int16(len(v['pulses'])),
                # an alternate lag-zero will be given.
                'mplgs': np.int16(v['lags'].shape[0] - 1),
                'nrang': np.int16(v['correlation_dimensions'][1]),
                'frang': np.int16(round(v['first_range'])),
                'rsep': np.int16(round(v['range_sep'])),
                # False if list is empty.
                'xcf': np.int16(bool('xcfs' in v.keys())),
                'tfreq': np.int16(v['freq']),
                'mxpwr': np.int32(-1),
                'lvmax': np.int32(20000),
                'rawacf.revision.major': np.int32(1),
                'rawacf.revision.minor': np.int32(0),
                'combf': 'Converted from Borealis file: ' + origin_string + \
                         ' record ' + str(k) + \
                         ' ; Number of beams in record: ' + \
                         str(len(v['beam_nums'])) + ' ; ' + \
                         v['experiment_comment'] + ' ; ' + v['slice_comment'],
                'thr': np.float32(0),
                'ptab': v['pulses'].astype(np.int16),
                'ltab': v['lags'].astype(np.int16),
                'pwr0': lag_zero_power.astype(np.float32),
                # list from 0 to num_ranges
                'slist': np.array(list(range(0,
                                             v['correlation_dimensions'][1]))).astype(np.int16),
                'acfd': correlation_dict['main_acfs'],
                'xcfd': correlation_dict['xcfs']
            }

        return record_dict
