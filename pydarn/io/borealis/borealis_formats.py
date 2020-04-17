# Copyright 2019 SuperDARN Canada, University of Saskatchewan
# Author: Marci Detwiller
"""
This file contains several classes with the fields that pertain to
SuperDARN Borealis HDF5 files.

Classes
-------
BaseFormat
BorealisRawacf
BorealisBfiq
BorealisAntennasIq
BorealisRawrf
as well as previous versions of these classes.

Globals
-------
borealis_version_dict
    A lookup table for [version][filetype] that provides the appropriate class.

Notes
-----
- Debug data files such as Borealis stage iq data (an intermediate
  product that can be generated during filtering and decimating, showing
  progression from rawrf to output ptrs iq files) will not be included here.
  This is a debug format only and should not be used for higher level
  data products.
- 'borealis_git_hash' is a necessary field for all versions, as its use is
  hardcoded into the code in order to determine the format version to use.


See Also
--------
For more information on Borealis data files, see:
https://borealis.readthedocs.io/en/latest/
"""

from datetime import datetime
import numpy as np

from collections import OrderedDict


class BaseFormat():
    """
    Static Methods
    --------------
    find_max_sequences(records): int
        Find the max number of sequences between records in a site file, for
        restructuring to arrays.
    find_max_beams(records): int
        Find the max number of beams between records in a site file, for
        restructuring to arrays.
    find_max_blanked_samples(records): int
        Find the max number of blanked samples between records in a site file,
        for restructuring to arrays.
    reshape_site_arrays(records): OrderedDict
        Returns the site data with the arrays reshaped. Some site data arrays
        may be stored in linear dimensions, so this reshapes any if needed.
        Should be overwritten by the child class.

    Class Methods
    -------------
    All classes built from this class should have these functions overwritten
    according to their type:

    single_element_types(): dict
        Dictionary of data field name to type expected in that field for a
        dictionary of Borealis data.
    array_dtypes(): dict
        Dictionary of data field name to array of given numpy dtype expected
        in the field for a dictionary of Borealis data.
    shared_fields(): list
        List of the fields that are common (shared) across records. This
        means that they can be reduced to a single value/array per file when
        they are array restructured.
    unshared_fields_dims_array(): dict
        Unshared field: dimensions per record in array structure. Unshared
        fields are not common across records. In array structure the first
        dimension will be num_records followed by these dimensions. Dimensions
        are provided as functions that will calculate the dimension given the
        records (site data dictionary)
    unshared_fields_dims_site(): dict
        Unshared field: dimensions per record in site structure. Unshared
        fields are not common across records. These dimensions can vary per
        record so the functions take the arrays data and the record number.
    array_specific_fields_generate(): dict
        Any fields that are array specific or require specific function to
        generate. The values in the dictionary are the functions that take the
        records (site data dictionary) to generate.
    site_specific_fields_generate(): dict
        Any fields that are site specific or require specific function to
        generate. The values in the dictionary are the functions that take the
        arrays (array data dictionary) and the record_num to generate.

    These methods use the single_element_types, array_dtypes, shared_fields,
    unshared_fields_dims_array, unshared_fields_dims_site,
    array_specific_fields_generate, and
    site_specific_fields_generate methods to generate their values:

    unshared_fields: list
        List of the fields that are not common across records.
    array_specific_fields: list
        List of fields that are only present in array files.
    site_specific_fields: list
        List of fields that are only present in site files.
    site_fields: list
        List of all fields that are in the site file type.
    array_fields: list
        List of all fields that are in the array file type.
    site_single_element_fields : list
        List of fields in the site files that are single element types.4
    site_single_element_types: dict
        subset of single_element_types with only site keys.
    site_array_dtypes_fields : list
        List of fields in the site files that are made of numpy arrays.
    site_array_dtypes: dict
        subset of array_dtypes with only site keys.
    array_single_element_fields : list
        List of fields in the array files that are single element types
        (unless unshared in which they are converted to the numpy array of
        that type)
    array_single_element_types: dict
        subset of single_element_types with only array fields.
    array_array_dtypes_fields : list
        List of fields in the array files that are made of numpy arrays.
        Includes fields that are single element but are unshared so are
        converted to arrays in the array file.
    array_array_dtypes: dict
        fields in the array files that are made of numpy arrays, with their
        given data type.

    _site_to_array(data_dict): dict
        Convert an OrderedDict of site data to array data using the information
        provided for the data format.
    _array_to_site(data_dict): OrderedDict
        Convert a dictionary of array data to site data using the information
        provided for the data format.

    Notes
    -----
    single_element_types.keys() + array_dtypes.keys() = all known fields
    shared_fields + unshared_fields + array_only_fields = all fields in
        array file
    shared_fields + unshared_fields + site_only_fields = all fields in
        site file
    """

    @staticmethod
    def find_max_sequences(records: OrderedDict) -> int:
        """
        Finds the maximum number of sequences between records in a Borealis
        site style records file.

        Parameters
        ----------
        records
            Site formatted records from a Borealis file, organized as one
            record for each slice

        Returns
        -------
        max_seqs
            The largest number of sequences found in one record from the
            file
        """
        max_seqs = 0
        for k in records:
            if max_seqs < records[k]["num_sequences"]:
                max_seqs = records[k]["num_sequences"]
        return max_seqs

    @staticmethod
    def find_max_beams(records: OrderedDict) -> int:
        """
        Finds the maximum number of beams between records in a Borealis
        site style records file.

        Parameters
        ----------
        records
            Site formatted records from a Borealis file, organized as one
            record for each slice

        Returns
        -------
        max_beams
            The largest number of beams found in one record from the
            file
        """
        max_beams = 0
        for k in records:
            if max_beams < len(records[k]["beam_nums"]):
                max_beams = len(records[k]["beam_nums"])
        return max_beams

    @staticmethod
    def find_max_blanked_samples(records: OrderedDict) -> int:
        """
        Finds the maximum number of blanked samples between records in a
        Borealis site style records file.

        Parameters
        ----------
        records
            Site formatted records from a Borealis file, organized as one
            record for each slice

        Returns
        -------
        max_beams
            The largest number of beams found in one record from the
            file
        """
        max_blanked_samples = 0
        for k in records:
            if max_blanked_samples < len(records[k]["blanked_samples"]):
                max_blanked_samples = len(records[k]["blanked_samples"])
        return max_blanked_samples

    @staticmethod
    def reshape_site_arrays(records: OrderedDict) -> OrderedDict:
        """
        This is a necessary function for interpreting site data, as
        some arrays in site data have been flattened in the file and
        need to be reshaped to be interpreted correctly.

        This reshapes them to the correct dimensions. Some formats may not
        have this issue, in which case this function does not need to be
        updated by the child class.

        This function is used in the _site_to_array restructuring which
        is common to all formats.

        Parameters
        ----------
        records
            site-style records dictionary.

        Returns
        -------
        records
            site-style records dictionary with any data field arrays reshaped
            as required by the format. The BaseFormat does not contain
            any fields that need to be reshaped but some child classes do.
        """
        return records

    @staticmethod
    def flatten_site_arrays(records: OrderedDict) -> OrderedDict:
        """
        This is a necessary function for writing site data, as
        some arrays in site data are flattened in the file and
        have been reshaped to be interpreted correctly.

        This flattens the data correctly for the file. Some formats may not
        have this issue, in which case this function does not need to be
        updated by the child class.

        This function is used in the _array_to_site restructuring which
        is common to all formats.

        Parameters
        ----------
        records
            site-style records dictionary.

        Returns
        -------
        records
            site-style records dictionary with any data field arrays flattened
            as required by the format to be written to file. The BaseFormat
            does not contain any fields that need to be flattened for writing
            but some child classes do.
        """
        return records

    # initialize these methods, which should be rewritten by the format.
    @classmethod
    def single_element_types(cls):
        return {
            # Identifies the version of Borealis that made this data.
            # Necessary for all versions and formats.
            "borealis_git_hash": np.unicode_,
            }

    @classmethod
    def array_dtypes(cls):
        """
        The following fields are necessary for ALL FORMATS.
        """
        return {
            # A list of GPS timestamps of the beginning of transmission for
            # each sampling period in the integration time. Seconds since
            # epoch. Necessary for all formats.
            "sqn_timestamps": np.float64,
            }

    @classmethod
    def shared_fields(cls):
        return []

    @classmethod
    def unshared_fields_dims_array(cls):
        return {}

    @classmethod
    def unshared_fields_dims_site(cls):
        return {}

    @classmethod
    def array_specific_fields_generate(cls):
        return {}

    @classmethod
    def site_specific_fields_generate(cls):
        return {}

    # these methods build off of the above.
    @classmethod
    def unshared_fields(cls):
        return list(cls.unshared_fields_dims_array().keys())

    @classmethod
    def array_specific_fields(cls):
        return list(cls.array_specific_fields_generate().keys())

    @classmethod
    def site_specific_fields(cls):
        return list(cls.site_specific_fields_generate().keys())

    @classmethod
    def site_fields(cls):
        """ All site fields """
        return cls.shared_fields() + cls.unshared_fields() + \
            cls.site_specific_fields()

    @classmethod
    def array_fields(cls):
        """ All array fields """
        return cls.shared_fields() + cls.unshared_fields() + \
            cls.array_specific_fields()

    @classmethod
    def site_single_element_fields(cls):
        """ All site fields that are single element in a list """
        return [k for k in cls.site_fields() if k in
                list(cls.single_element_types().keys())]

    @classmethod
    def site_single_element_types(cls):
        """ Dict of site single element field: type"""
        return {k: cls.single_element_types()[k]
                for k in cls.site_single_element_fields()}

    @classmethod
    def site_array_dtypes_fields(cls):
        """ All site fields that are arrays in a list """
        return [k for k in cls.site_fields() if k in
                list(cls.array_dtypes().keys())]

    @classmethod
    def site_array_dtypes(cls):
        """ Dict of site array field : dtype """
        return {k: cls.array_dtypes()[k] for k in
                cls.site_array_dtypes_fields()}

    # for single element fields in the array filetypes, they must
    # be a shared field.
    @classmethod
    def array_single_element_fields(cls):
        """ List of array restructured single element fields """
        return [k for k in cls.array_fields() if
                k in list(cls.single_element_types().keys()) and k in
                cls.shared_fields()]

    @classmethod
    def array_single_element_types(cls):
        """ Dict of array restructured single element field : type """
        return {k: cls.single_element_types()[k]
                for k in cls.array_single_element_fields()}

    # for array filetypes, there are more array dtypes for any unshared
    # fields. If the field was a single_element_type and is unshared,
    # it is now an array of num_records length.
    @classmethod
    def array_array_dtypes_fields(cls):
        """ List of array restructured array fields """
        return [k for k in cls.array_fields() if
                k in list(cls.array_dtypes().keys())] + \
               [k for k in cls.array_fields() if k in
                list(cls.single_element_types().keys()) and
                ((k in cls.unshared_fields()) or
                 (k in cls.array_specific_fields()))]

    @classmethod
    def array_array_dtypes(cls):
        """ Dict of array restructured array field : dtype """
        array_array_dtypes = {k: cls.array_dtypes()[k] for k in
                              cls.array_array_dtypes_fields() if k in
                              list(cls.array_dtypes().keys())}

        array_array_dtypes.update(
            {k: cls.single_element_types()[k] for
             k in cls.array_array_dtypes_fields() if k in
             list(cls.single_element_types().keys())})

        return array_array_dtypes

    @classmethod
    def _site_to_array(cls, data_dict: OrderedDict) -> dict:
        """
        Base function for converting site Borealis data to
        restructured array format.

        Parameters
        ----------
        data_dict: OrderedDict
            a dict of timestamped records loaded from an hdf5 Borealis site
            file

        Returns
        -------
        new_data_dict
            A dictionary containing the data from data_dict
            reformatted to be stored entirely in array style, or as
            one entry if the field does not change between records.
            This means that for fields that change between records,
            the first dimension in the array will equal num_records
            (these are called unshared_fields). For fields common to all
            records, there will only be the one value that applies (these
            are known as shared_fields).
        """
        new_data_dict = dict()
        num_records = len(data_dict)

        # some fields are linear in site style and need to be reshaped.
        data_dict = cls.reshape_site_arrays(data_dict)

        # write shared fields to dictionary
        first_key = list(data_dict.keys())[0]
        for field in cls.shared_fields():
            new_data_dict[field] = data_dict[first_key][field]

        # write array specific fields using the given functions.
        for field in cls.array_specific_fields():
            new_data_dict[field] = cls.array_specific_fields_generate(
                )[field](data_dict)

        # write the unshared fields, initializing empty arrays to start.
        temp_array_dict = dict()

        # get array dims of the unshared fields arrays
        field_dimensions = {}
        for field in cls.unshared_fields():
            dims = [dimension_function(data_dict) for
                    dimension_function in
                    cls.unshared_fields_dims_array()[field]]
            field_dimensions[field] = dims

        # all fields to become arrays
        for field, dims in field_dimensions.items():
            array_dims = [num_records] + dims
            array_dims = tuple(array_dims)

            if field in cls.single_element_types():
                datatype = cls.single_element_types()[field]
            else:  # field in array_dtypes
                datatype = cls.array_dtypes()[field]
            empty_array = np.empty(array_dims, dtype=datatype)
            # initialize all values to NaN; some indices may not be filled
            # do to dimensions that are max values (num sequences, etc can
            # change between records)
            empty_array[:] = np.NaN
            temp_array_dict[field] = empty_array

        # iterate through the records, filling the unshared and array only
        # fields
        for rec_idx, k in enumerate(data_dict.keys()):
            for field in cls.unshared_fields():  # all unshared fields
                empty_array = temp_array_dict[field]
                if type(data_dict[first_key][field]) == np.ndarray:
                    # only fill the correct length, appended NaNs occur for
                    # dims with a determined max value
                    data_buffer = data_dict[k][field]
                    buffer_shape = data_buffer.shape
                    index_slice = [slice(0, i) for i in buffer_shape]
                    # insert record index at start of array's slice list
                    index_slice.insert(0, rec_idx)
                    index_slice = tuple(index_slice)
                    # place data buffer in the correct place
                    empty_array[index_slice] = data_buffer
                else:  # not an array, num_records is the only dimension
                    empty_array[rec_idx] = data_dict[k][field]

        new_data_dict.update(temp_array_dict)

        return new_data_dict

    @classmethod
    def _array_to_site(cls, data_dict: dict) -> OrderedDict:
        """
        Base function for converting array Borealis data to
        site format.

        Parameters
        ----------
        data_dict: dictionary of array restructured Borealis data.

        Returns
        -------
        new_data_dict
            An OrderedDict of timestamped records as if loaded from
            the original site file.
        """
        timestamp_dict = OrderedDict()
        for record_num, seq_timestamp in \
                enumerate(data_dict["sqn_timestamps"]):
            # format dictionary key in the same way it is done
            # in datawrite on site
            seq_datetime = datetime.utcfromtimestamp(seq_timestamp[0])
            epoch = datetime.utcfromtimestamp(0)
            key = str(int((seq_datetime - epoch).total_seconds() * 1000))

            timestamp_dict[key] = dict()
            # populate shared fields in each record,
            for field in cls.shared_fields():
                timestamp_dict[key][field] = data_dict[field]

            # populate site specific fields using given functions
            # that take both the arrays data and the record number
            for field in cls.site_specific_fields():
                timestamp_dict[key][field] = cls.site_specific_fields_generate(
                    )[field](data_dict, record_num)

            for field in cls.unshared_fields():
                if field in cls.single_element_types():
                    datatype = cls.single_element_types()[field]
                    # field is not an array, single element per record.
                    # unshared_field_dims_site should give empty list.
                    timestamp_dict[key][field] = datatype(data_dict[field]
                                                          [record_num])
                else:  # field in array_dtypes
                    datatype = cls.array_dtypes()[field]
                    # need to get the dims correct, not always equal to the max
                    site_dims = [dimension_function(data_dict, record_num)
                                 for dimension_function in
                                 cls.unshared_fields_dims_site()[field]]
                    index_slice = [slice(0, i) for i in site_dims]
                    index_slice.insert(0, record_num)
                    index_slice = tuple(index_slice)
                    timestamp_dict[key][field] = data_dict[field][index_slice]

        timestamp_dict = cls.flatten_site_arrays(timestamp_dict)

        return timestamp_dict


class BorealisRawacfv0_4(BaseFormat):
    """
    Class containing Borealis Rawacf data fields and their types.

    Rawacf data has been mixed, filtered, and decimated; beamformed and
    combined into antenna arrays; then autocorrelated and correlated between
    antenna arrays to produce matrices of num_ranges x num_lags.

    Static Methods
    --------------
    is_restructureable: bool
        Returns True, this format can be restructured to arrays.
    find_num_ranges(OrderedDict): int
        Returns num ranges in the data for use in finding dimensions
    find_num_lags(OrderedDict): int
        Returns the num lags in the data for use in finding dimensions
    reshape_site_arrays(OrderedDict): OrderedDict
        Reshapes the main_acfs, intf_acfs, xcfs fields.
    """

    @staticmethod
    def is_restructureable() -> bool:
        return True

    @staticmethod
    def find_num_ranges(records: OrderedDict) -> int:
        """
        Find the number of ranges given the records dictionary, for

        restructuring to arrays.
        Num_ranges is unique to a slice so cannot change inside file.
        """
        first_key = list(records.keys())[0]
        num_ranges = records[first_key]['correlation_dimensions'][1]
        return num_ranges

    @staticmethod
    def find_num_lags(records: OrderedDict) -> int:
        """
        Find the number of lags given the records dictionary, for
        restructuring to arrays.
        Num_lags is unique to a slice so cannot change inside file.
        """
        first_key = list(records.keys())[0]
        num_lags = records[first_key]['correlation_dimensions'][2]
        return num_lags

    @staticmethod
    def reshape_site_arrays(records: OrderedDict) -> OrderedDict:
        """
        Sometimes arrays in the site style have been reduced to
        linear arrays with given dimensions. This function returns
        the site data with all arrays restructured correctly as
        per the format.
        """

        # main_acfs, intf_acfs, and xcfs to be reshaped.
        # dimensions provided in correlation_dimensions field as num_beams,
        # num_ranges, num_lags.
        for key in list(records.keys()):
            record_dimensions = records[key]['correlation_dimensions']
            for field in ['main_acfs', 'intf_acfs', 'xcfs']:
                records[key][field] = records[key][field].\
                                        reshape(record_dimensions)

        return records

    @staticmethod
    def flatten_site_arrays(records: OrderedDict) -> OrderedDict:
        """
        Sometimes arrays in the site style have been reduced to
        linear arrays with given dimensions. This function returns
        the site data with all arrays flattened as desired for
        storing in the site format.
        """
        for key in list(records.keys()):
            for field in ['main_acfs', 'intf_acfs', 'xcfs']:
                records[key][field] = records[key][field].flatten()

        return records

    @classmethod
    def single_element_types(cls):
        """ See BaseFormat class for description. """
        return {
            # Identifies the version of Borealis that made this data. Necessary
            # for all versions.
            "borealis_git_hash": np.unicode_,
            # Number used to identify experiment.
            "experiment_id": np.int64,
            # Name of the experiment file.
            "experiment_name": np.unicode_,
            # Comment about the whole experiment
            "experiment_comment": np.unicode_,
            # Additional text comment that describes the slice.
            "slice_comment": np.unicode_,
            # Number of slices in the experiment at this integration time.
            "num_slices": np.int64,
            # Three letter radar identifier.
            "station": np.unicode_,
            # Number of sampling periods in the integration time.
            "num_sequences": np.int64,
            # range gate separation (equivalent distance between samples), km.
            "range_sep": np.float32,
            # Round trip time of flight to first range in microseconds.
            "first_range_rtt": np.float32,
            # Distance to first range in km.
            "first_range": np.float32,
            # Sampling rate of the samples being written to file in Hz.
            "rx_sample_rate": np.float64,
            # Designates if the record is the first in a scan.
            "scan_start_marker": np.bool_,
            # Integration time in seconds.
            "int_time": np.float32,
            # Length of the pulse in microseconds.
            "tx_pulse_len": np.uint32,
            # The minimum spacing between pulses, spacing between pulses is
            # always a multiple of this in microseconds.
            "tau_spacing": np.uint32,
            # Number of main array antennas.
            "main_antenna_count": np.uint32,
            # Number of interferometer array antennas.
            "intf_antenna_count": np.uint32,
            # The frequency used for this experiment slice in kHz.
            "freq": np.uint32,
            # str denoting C data type of the samples included in the data
            # array, such as 'complex float'.
            "samples_data_type": np.unicode_,
            # data normalization factor determined by the filter scaling in the
            # decimation scheme.
            "data_normalization_factor": np.float64,
            # number of beams calculated for the integration time.
            "num_beams": np.uint32
            }

    @classmethod
    def array_dtypes(cls):
        """ See BaseFormat class for description. """
        return {
            # The pulse sequence in multiples of the tau_spacing.
            "pulses": np.uint32,
            # The lags created from combined pulses.
            "lags": np.uint32,
            # Samples that have been blanked during TR switching.
            "blanked_samples": np.uint32,
            # A list of GPS timestamps of the beginning of transmission for
            # each sampling period in the integration time. Seconds since
            # epoch.
            "sqn_timestamps": np.float64,
            # A list of beam numbers used in this slice.
            "beam_nums": np.uint32,
            # A list of the beams azimuths for each beam in degrees.
            "beam_azms": np.float64,
            # Noise at the receive frequency, should be an array
            # (one value per sequence) (TODO units??) (TODO document
            # FFT resolution bandwidth for this value, should be =
            # output_sample rate?)
            "noise_at_freq": np.float64,
            # Denotes what each acf/xcf dimension represents. = "num_beams",
            # "num_ranges", "num_lags" in site rawacf files.
            "correlation_descriptors": np.unicode_,
            # The dimensions in which to reshape the acf/xcf data.
            "correlation_dimensions": np.uint32,
            # Main array autocorrelations
            "main_acfs": np.complex64,
            # Interferometer array autocorrelations
            "intf_acfs": np.complex64,
            # Crosscorrelations between main and interferometer arrays
            "xcfs": np.complex64
            }

    # we don't need to know dimension info for these fields because dims
    # will be the same for site and restructured files.
    @classmethod
    def shared_fields(cls):
        """ See BaseFormat class for description. """
        return ['blanked_samples', 'borealis_git_hash',
                'data_normalization_factor', 'experiment_comment',
                'experiment_id', 'experiment_name', 'first_range',
                'first_range_rtt', 'freq', 'intf_antenna_count', 'lags',
                'main_antenna_count', 'pulses', 'range_sep',
                'rx_sample_rate', 'samples_data_type',
                'slice_comment', 'station', 'tau_spacing',
                'tx_pulse_len']

    @classmethod
    def unshared_fields_dims_array(cls):
        """ See BaseFormat class for description. """
        return {  # functions take records dictionary
            'num_sequences': [],
            'int_time': [],
            'sqn_timestamps': [cls.find_max_sequences],
            'noise_at_freq': [cls.find_max_sequences],
            'main_acfs': [cls.find_max_beams, cls.find_num_ranges,
                          cls.find_num_lags],
            'intf_acfs': [cls.find_max_beams, cls.find_num_ranges,
                          cls.find_num_lags],
            'xcfs': [cls.find_max_beams, cls.find_num_ranges,
                     cls.find_num_lags],
            'scan_start_marker': [],
            'beam_nums': [cls.find_max_beams],
            'beam_azms': [cls.find_max_beams],
            'num_slices': []
        }

    @classmethod
    def unshared_fields_dims_site(cls):
        """ See BaseFormat class for description. """
        return {  # functions take arrays dictionary and record_num
            'num_sequences': [],
            'int_time': [],
            'sqn_timestamps': [lambda arrays, record_num:
                               arrays['num_sequences'][record_num]],
            'noise_at_freq': [lambda arrays, record_num:
                              arrays['num_sequences'][record_num]],
            'main_acfs': [lambda arrays, record_num:
                          arrays['num_beams'][record_num],
                          lambda arrays, record_num:
                          arrays['main_acfs'].shape[2],
                          lambda arrays, record_num:
                          arrays['main_acfs'].shape[3]],
            'intf_acfs': [lambda arrays, record_num:
                          arrays['num_beams'][record_num],
                          lambda arrays, record_num:
                          arrays['main_acfs'].shape[2],
                          lambda arrays, record_num:
                          arrays['main_acfs'].shape[3]],
            'xcfs': [lambda arrays, record_num:
                     arrays['num_beams'][record_num],
                     lambda arrays, record_num:
                     arrays['main_acfs'].shape[2],
                     lambda arrays, record_num:
                     arrays['main_acfs'].shape[3]],
            'scan_start_marker': [],
            'beam_nums': [lambda arrays, record_num:
                          arrays['num_beams'][record_num]],
            'beam_azms': [lambda arrays, record_num:
                          arrays['num_beams'][record_num]],
            'num_slices': []
            }

    @classmethod
    def array_specific_fields_generate(cls):
        """ See BaseFormat class for description. """
        return {
            'num_beams': lambda records: np.array(
                [len(record['beam_nums']) for key, record in records.items()],
                dtype=np.uint32),
            'correlation_descriptors': lambda records: np.array(
                ['num_records', 'max_num_beams', 'num_ranges', 'num_lags'])
            }

    @classmethod
    def site_specific_fields_generate(cls):
        """ See BaseFormat class for description. """
        return {
            'correlation_descriptors': lambda arrays, record_num: np.array(
                ['num_beams', 'num_ranges', 'num_lags']),
            'correlation_dimensions': lambda arrays, record_num: np.array(
                [arrays['num_beams'][record_num], arrays['main_acfs'].shape[2],
                 arrays['main_acfs'].shape[3]], dtype=np.uint32)
            }


class BorealisBfiqv0_4(BaseFormat):
    """
    Class containing Borealis Bfiq data fields and their types.

    Bfiq data is beamformed i and q data. It has been mixed, filtered,
    decimated to the final output receive rate, and it has been beamformed
    and all channels have been combined into their arrays. No correlation
    or averaging has occurred.

    Static Methods
    --------------
    is_restructureable: bool
        Returns True, this format can be restructured to arrays.
    find_num_antenna_arrays(OrderedDict): int
        Returns number of arrays in the data for use in finding dimensions
    find_num_samps(OrderedDict): int
        Returns the number of samples in the data for use in finding dimensions
    reshape_site_arrays(OrderedDict): OrderedDict
        Reshapes the data field according to data dimensions.
    """

    @staticmethod
    def is_restructureable() -> bool:
        return True

    @staticmethod
    def find_num_antenna_arrays(records: OrderedDict) -> int:
        """
        Find the number of antenna arrays given the records dictionary, for
        restructuring to arrays.
        """
        first_key = list(records.keys())[0]
        num_arrays = records[first_key]['data_dimensions'][0]
        return num_arrays

    @staticmethod
    def find_num_samps(records: OrderedDict) -> int:
        """
        Find the number of samples given the records dictionary, for
        restructuring to arrays.
        """
        first_key = list(records.keys())[0]
        num_samps = records[first_key]['data_dimensions'][3]
        return num_samps

    @staticmethod
    def reshape_site_arrays(records: OrderedDict) -> OrderedDict:
        """
        Sometimes arrays in the site style have been reduced to
        linear arrays with given dimensions. This function returns
        the site data with all arrays reshaped correctly as
        per the format.
        """
        for key in list(records.keys()):
            record_dimensions = records[key]['data_dimensions']
            for field in ['data']:
                records[key][field] = records[key][field].\
                        reshape(record_dimensions)

        return records

    @staticmethod
    def flatten_site_arrays(records: OrderedDict) -> OrderedDict:
        """
        Sometimes arrays in the site style have been reduced to
        linear arrays with given dimensions. This function returns
        the site data with all arrays flattened as desired for
        storing in the site format.
        """
        for key in list(records.keys()):
            for field in ['data']:
                records[key][field] = records[key][field].flatten()

        return records

    @classmethod
    def single_element_types(cls):
        """ See BaseFormat class for description. """
        return {
            # Identifies the version of Borealis that made this data. Necessary
            # for all versions.
            "borealis_git_hash": np.unicode_,
            # Number used to identify experiment.
            "experiment_id": np.int64,
            # Name of the experiment file.
            "experiment_name": np.unicode_,
            # Comment about the whole experiment
            "experiment_comment": np.unicode_,
            # Additional text comment that describes the slice.
            "slice_comment": np.unicode_,
            # Number of slices in the experiment at this integration time.
            "num_slices": np.int64,
            # Three letter radar identifier.
            "station": np.unicode_,
            # Number of sampling periods in the integration time.
            "num_sequences": np.int64,
            # Sampling rate of the samples being written to file in Hz.
            "rx_sample_rate": np.float64,
            # Designates if the record is the first in a scan.
            "scan_start_marker": np.bool_,
            # Integration time in seconds.
            "int_time": np.float32,
            # Length of the pulse in microseconds.
            "tx_pulse_len": np.uint32,
            # The minimum spacing between pulses, spacing between pulses is
            # always a multiple of this. In microseconds.
            "tau_spacing": np.uint32,
            # Number of main array antennas.
            "main_antenna_count": np.uint32,
            # Number of interferometer array antennas.
            "intf_antenna_count": np.uint32,
            # The frequency used for this experiment slice in kHz.
            "freq": np.uint32,
            # str denoting C data type of the samples included in the data
            # array, such as 'complex float'.
            "samples_data_type": np.unicode_,
            # Number of samples in the sampling period.
            "num_samps": np.uint32,
            # range gate separation (equivalent distance between samples), km
            "range_sep": np.float32,
            # Round trip time of flight to first range in microseconds.
            "first_range_rtt": np.float32,
            # Distance to first range in km.
            "first_range": np.float32,
            # Number of ranges to calculate correlations for.
            "num_ranges": np.uint32,
            # data normalization factor determined by the filter scaling in the
            # decimation scheme.
            "data_normalization_factor": np.float64,
            # number of beams calculated for the integration time.
            "num_beams": np.uint32
            }

    @classmethod
    def array_dtypes(cls):
        """ See BaseFormat class for description. """
        return {
            # The pulse sequence in multiples of the tau_spacing.
            "pulses": np.uint32,
            # The lags created from combined pulses.
            "lags": np.uint32,
            # Samples that have been blanked during TR switching.
            "blanked_samples": np.uint32,
            # For pulse encoding phase, in degrees offset.
            # Contains one phase offset per pulse in pulses.
            "pulse_phase_offset": np.float32,
            # A list of GPS timestamps of the beginning of transmission for
            # each sampling period in the integration time. Seconds since
            # epoch.
            "sqn_timestamps": np.float64,
            # A list of beam numbers used in this slice.
            "beam_nums": np.uint32,
            # A list of the beams azimuths for each beam in degrees.
            "beam_azms": np.float64,
            # Noise at the receive frequency, should be an array (one value per
            # sequence) (TODO units??) (TODO document FFT resolution
            # bandwidth for this value, should be = output_sample rate?)
            "noise_at_freq": np.float64,
            # States what order the data is in. Describes the data layout.
            "antenna_arrays_order": np.unicode_,
            # Denotes what each data dimension represents. =
            # "num_antenna_arrays", "num_sequences", "num_beams", "num_samps"
            # for site bfiq.
            "data_descriptors": np.unicode_,
            # The dimensions in which to reshape the data.
            "data_dimensions": np.uint32,
            # A contiguous set of samples (complex float) at given sample rate
            "data": np.complex64
            }

    @classmethod
    def shared_fields(cls):
        """ See BaseFormat class for description. """
        return ['antenna_arrays_order', 'blanked_samples',
                'borealis_git_hash',
                'data_normalization_factor',
                'experiment_comment', 'experiment_id', 'experiment_name',
                'first_range', 'first_range_rtt', 'freq',
                'intf_antenna_count', 'lags', 'main_antenna_count',
                'num_ranges', 'num_samps',
                'pulse_phase_offset', 'pulses', 'range_sep',
                'rx_sample_rate', 'samples_data_type',
                'slice_comment', 'station', 'tau_spacing',
                'tx_pulse_len']

    @classmethod
    def unshared_fields_dims_array(cls):
        """ See BaseFormat class for description. """
        return {
            'num_sequences': [],
            'int_time': [],
            'sqn_timestamps': [cls.find_max_sequences],
            'noise_at_freq': [cls.find_max_sequences],
            'data': [cls.find_num_antenna_arrays,
                     cls.find_max_sequences, cls.find_max_beams,
                     cls.find_num_samps],
            'scan_start_marker': [],
            'beam_nums': [cls.find_max_beams],
            'beam_azms': [cls.find_max_beams],
            'num_slices': []
            }

    @classmethod
    def unshared_fields_dims_site(cls):
        """ See BaseFormat class for description. """
        return {
            'num_sequences': [],
            'int_time': [],
            'sqn_timestamps': [lambda arrays, record_num:
                               arrays['num_sequences'][record_num]],
            'noise_at_freq': [lambda arrays, record_num:
                              arrays['num_sequences'][record_num]],
            'data': [lambda arrays, record_num: arrays['data'].shape[1],
                     lambda arrays, record_num:
                     arrays['num_sequences'][record_num],
                     lambda arrays, record_num:
                     arrays['num_beams'][record_num],
                     lambda arrays, record_num: arrays['data'].shape[4]],
            'scan_start_marker': [],
            'beam_nums': [lambda arrays, record_num:
                          arrays['num_beams'][record_num]],
            'beam_azms': [lambda arrays, record_num:
                          arrays['num_beams'][record_num]],
            'num_slices': []
            }

    @classmethod
    def array_specific_fields_generate(cls):
        """ See BaseFormat class for description. """
        return {
            'num_beams': lambda records: np.array(
                [len(record['beam_nums']) for key, record in records.items()],
                dtype=np.uint32),
            'data_descriptors': lambda records: np.array(
                ['num_records', 'num_antenna_arrays', 'max_num_sequences',
                 'max_num_beams', 'num_samps'])
            }

    @classmethod
    def site_specific_fields_generate(cls):
        """ See BaseFormat class for description. """
        return {
            'data_descriptors': lambda arrays, record_num: np.array(
                ['num_antenna_arrays', 'num_sequences', 'num_beams',
                 'num_samps']),
            'data_dimensions': lambda arrays, record_num: np.array(
                [arrays['data'].shape[1], arrays['num_sequences'][record_num],
                 arrays['num_beams'][record_num], arrays['data'].shape[4]],
                dtype=np.uint32)
            }


class BorealisAntennasIqv0_4(BaseFormat):
    """
    Class containing Borealis Antennas iq data fields and their types.

    Antennas iq data is data with all channels separated. It has been mixed
    and filtered, but it has not been beamformed or combined into the
    entire antenna array data product.

    Static Methods
    --------------
    is_restructureable: bool
        Returns True, this format can be restructured to arrays.
    find_num_antennas(OrderedDict): int
        Returns number of antennas in the data for use in finding dimensions
    find_num_samps(OrderedDict): int
        Returns the number of samples in the data for use in finding dimensions
    reshape_site_arrays(OrderedDict): OrderedDict
        Reshapes the data field according to data dimensions.
    """

    @staticmethod
    def is_restructureable() -> bool:
        return True

    @staticmethod
    def find_num_antennas(records: OrderedDict) -> int:
        """
        Find the number of antennas given the records dictionary, for
        restructuring to arrays.
        """
        first_key = list(records.keys())[0]
        num_antennas = records[first_key]['data_dimensions'][0]
        return num_antennas

    @staticmethod
    def find_num_samps(records: OrderedDict) -> int:
        """
        Find the number of samples given the records dictionary, for
        restructuring to arrays.
        """
        first_key = list(records.keys())[0]
        num_samps = records[first_key]['data_dimensions'][2]
        return num_samps

    @staticmethod
    def reshape_site_arrays(records: OrderedDict) -> OrderedDict:
        """
        Sometimes arrays in the site style have been reduced to
        linear arrays with given dimensions. This function returns
        the site data with all arrays reshaped correctly as
        per the format.
        """
        for key in list(records.keys()):
            record_dimensions = records[key]['data_dimensions']
            for field in ['data']:
                records[key][field] = records[key][field].\
                        reshape(record_dimensions)

        return records

    @staticmethod
    def flatten_site_arrays(records: OrderedDict) -> OrderedDict:
        """
        Sometimes arrays in the site style have been reduced to
        linear arrays with given dimensions. This function returns
        the site data with all arrays flattened as desired for
        storing in the site format.
        """
        for key in list(records.keys()):
            for field in ['data']:
                records[key][field] = records[key][field].flatten()

        return records

    @classmethod
    def single_element_types(cls):
        """ See BaseFormat class for description. """
        return {
            # Identifies the version of Borealis that made this data. Necessary
            # for all versions.
            "borealis_git_hash": np.unicode_,
            # Number used to identify experiment.
            "experiment_id": np.int64,
            # Name of the experiment file.
            "experiment_name": np.unicode_,
            # Comment about the whole experiment
            "experiment_comment": np.unicode_,
            # Additional text comment that describes the slice.
            "slice_comment": np.unicode_,
            # Number of slices in the experiment at this integration time.
            "num_slices": np.int64,
            # Three letter radar identifier.
            "station": np.unicode_,
            # Number of sampling periods in the integration time.
            "num_sequences": np.int64,
            # Sampling rate of the samples being written to file in Hz.
            "rx_sample_rate": np.float64,
            # Designates if the record is the first in a scan.
            "scan_start_marker": np.bool_,
            # Integration time in seconds.
            "int_time": np.float32,
            # Length of the pulse in microseconds.
            "tx_pulse_len": np.uint32,
            # The minimum spacing between pulses, spacing between pulses is
            # always a multiple of this in microseconds.
            "tau_spacing": np.uint32,
            # Number of main array antennas.
            "main_antenna_count": np.uint32,
            # Number of interferometer array antennas.
            "intf_antenna_count": np.uint32,
            # The frequency used for this experiment slice in kHz.
            "freq": np.uint32,
            # str denoting C data type of the samples included in the data
            # array, such as 'complex float'.
            "samples_data_type": np.unicode_,
            # Number of samples in the sampling period.
            "num_samps": np.uint32,
            # data normalization factor determined by the filter scaling in the
            # decimation scheme.
            "data_normalization_factor": np.float64,
            # number of beams to be calculated for the integration time.
            "num_beams": np.uint32
            }

    @classmethod
    def array_dtypes(cls):
        """ See BaseFormat class for description. """
        return {
            # The pulse sequence in multiples of the tau_spacing.
            "pulses": np.uint32,
            # For pulse encoding phase, in desgrees offset. Contains one phase
            # offset per pulse in pulses.
            "pulse_phase_offset": np.float32,
            # A list of GPS timestamps of the beginning of transmission for
            # each sampling period in the integration time. Seconds since
            # epoch.
            "sqn_timestamps": np.float64,
            # A list of beam numbers used in this slice.
            "beam_nums": np.uint32,
            # A list of the beams azimuths for each beam in degrees.
            "beam_azms": np.float64,
            # Noise at the receive frequency, should be an array (one value
            # per sequence) (TODO units??) (TODO document FFT resolution
            # bandwidth for this value, should be = output_sample rate?)
            "noise_at_freq": np.float64,
            # States what order the data is in. Describes the data layout.
            "antenna_arrays_order": np.unicode_,
            # Denotes what each data dimension represents. = "num_antennas",
            # "num_sequences", "num_samps" in site antennas_iq.
            "data_descriptors": np.unicode_,
            # The dimensions in which to reshape the data.
            "data_dimensions": np.uint32,
            # A contiguous set of samples (complex float) at given sample rate
            "data": np.complex64
            }

    @classmethod
    def shared_fields(cls):
        """ See BaseFormat class for description. """
        return ['antenna_arrays_order',
                'borealis_git_hash',
                'data_normalization_factor', 'experiment_comment',
                'experiment_id', 'experiment_name', 'freq',
                'intf_antenna_count', 'main_antenna_count', 'num_samps',
                'pulse_phase_offset', 'pulses',
                'rx_sample_rate', 'samples_data_type',
                'slice_comment', 'station', 'tau_spacing',
                'tx_pulse_len']

    @classmethod
    def unshared_fields_dims_array(cls):
        """ See BaseFormat class for description. """
        return {
            'num_sequences': [],
            'int_time': [],
            'sqn_timestamps': [cls.find_max_sequences],
            'noise_at_freq': [cls.find_max_sequences],
            'data': [cls.find_num_antennas, cls.find_max_sequences,
                     cls.find_num_samps],
            'scan_start_marker': [],
            'beam_nums': [cls.find_max_beams],
            'beam_azms': [cls.find_max_beams],
            'num_slices': []
            }

    @classmethod
    def unshared_fields_dims_site(cls):
        """ See BaseFormat class for description. """
        return {
            'num_sequences': [],
            'int_time': [],
            'sqn_timestamps': [lambda arrays, record_num:
                               arrays['num_sequences'][record_num]],
            'noise_at_freq': [lambda arrays, record_num:
                              arrays['num_sequences'][record_num]],
            'data': [lambda arrays, record_num: arrays['data'].shape[1],
                     lambda arrays, record_num:
                     arrays['num_sequences'][record_num],
                     lambda arrays, record_num: arrays['data'].shape[3]],
            'scan_start_marker': [],
            'beam_nums': [lambda arrays, record_num:
                          arrays['num_beams'][record_num]],
            'beam_azms': [lambda arrays, record_num:
                          arrays['num_beams'][record_num]],
            'num_slices': []
            }

    @classmethod
    def array_specific_fields_generate(cls):
        """ See BaseFormat class for description. """
        return {
            'num_beams': lambda records: np.array(
                [len(record['beam_nums']) for key, record in records.items()],
                dtype=np.uint32),
            'data_descriptors': lambda records: np.array(
                ['num_records', 'num_antennas', 'max_num_sequences',
                 'num_samps'])
            }

    @classmethod
    def site_specific_fields_generate(cls):
        """ See BaseFormat class for description. """
        return {
            'data_descriptors': lambda arrays, record_num: np.array(
                ['num_antennas', 'num_sequences', 'num_samps']),
            'data_dimensions': lambda arrays, record_num: np.array(
                [arrays['data'].shape[1], arrays['num_sequences'][record_num],
                 arrays['data'].shape[3]], dtype=np.uint32)
            }


class BorealisRawrfv0_4(BaseFormat):
    """
    Class containing Borealis Rawrf data fields and their types.

    This filetype only has site files and cannot be restructured.

    Rawrf data is data that has been produced at the original receive bandwidth
    and has not been mixed, filtered, or decimated.

    Static Methods
    --------------
    is_restructureable: bool
        Returns False, this format cannot be restructured.
    reshape_site_arrays(OrderedDict): OrderedDict
        Reshapes the data field according to data dimensions.
    """

    @staticmethod
    def is_restructureable() -> bool:
        return False

    @staticmethod
    def reshape_site_arrays(records: OrderedDict) -> OrderedDict:
        """
        Sometimes arrays in the site style have been reduced to
        linear arrays with given dimensions. This function returns
        the site data with all arrays reshaped correctly as
        per the format.
        """
        for key in list(records.keys()):
            record_dimensions = records[key]['data_dimensions']
            for field in ['data']:
                records[key][field] = records[key][field].\
                                        reshape(record_dimensions)

        return records

    @staticmethod
    def flatten_site_arrays(records: OrderedDict) -> OrderedDict:
        """
        Sometimes arrays in the site style have been reduced to
        linear arrays with given dimensions. This function returns
        the site data with all arrays flattened as desired for
        storing in the site format.
        """
        for key in list(records.keys()):
            for field in ['data']:
                records[key][field] = records[key][field].flatten()

        return records

    @classmethod
    def single_element_types(cls):
        """ See BaseFormat class for description. """
        return {
            # Identifies the version of Borealis that made this data. Necessary
            # for all versions.
            "borealis_git_hash": np.unicode_,
            # Number used to identify experiment.
            "experiment_id": np.int64,
            # Name of the experiment file.
            "experiment_name": np.unicode_,
            # Comment about the whole experiment
            "experiment_comment": np.unicode_,
            # Number of slices in the experiment at this integration time.
            "num_slices": np.int64,
            # Three letter radar identifier.
            "station": np.unicode_,
            # Number of sampling periods in the integration time.
            "num_sequences": np.int64,
            # Sampling rate of the samples being written to file in Hz.
            "rx_sample_rate": np.float64,
            # Designates if the record is the first in a scan.
            "scan_start_marker": np.bool_,
            # Integration time in seconds.
            "int_time": np.float32,
            # Number of main array antennas.
            "main_antenna_count": np.uint32,
            # Number of interferometer array antennas.
            "intf_antenna_count": np.uint32,
            # str denoting C data type of the samples included in the data
            # array, such as 'complex float'.
            "samples_data_type": np.unicode_,
            # The center frequency of this data in kHz
            "rx_center_freq": np.float64,
            # Number of samples in the sampling period.
            "num_samps": np.uint32
            }

    @classmethod
    def array_dtypes(cls):
        """ See BaseFormat class for description. """
        return {
            # A list of GPS timestamps of the beginning of transmission for
            # each sampling period in the integration time. Seconds since
            # epoch.
            "sqn_timestamps": np.float64,
            # Denotes what each data dimension represents. = "num_sequences",
            # "num_antennas", "num_samps" for rawrf.
            "data_descriptors": np.unicode_,
            # The dimensions in which to reshape the data.
            "data_dimensions": np.uint32,
            # A contiguous set of samples (complex float) at given sample rate
            "data": np.complex64
            }


# The following are the currently used classes, with additions according
# to Borealis updates.

class BorealisRawacf(BorealisRawacfv0_4):
    """
    Class containing Borealis Rawacf data fields and their types for the
    current version of Borealis (v0.5).

    See Also
    --------
    BaseFormat
    BorealisRawacfv0_4

    Notes
    -----
    Rawacf data has been mixed, filtered, and decimated; beamformed and
    combined into antenna arrays; then autocorrelated and correlated between
    antenna arrays to produce matrices of num_ranges x num_lags.

    See BaseFormat for description of classmethods and how they
    are used to verify format files and restructure Borealis files to
    array and site formats.

    In v0.5, the following fields were added:
    slice_id, slice_interfacing, scheduling_mode, and averaging_method.
    As well, blanked_samples was changed from shared to unshared in the array
    restructuring.
    """

    # New fields added in v0.5 to shared fields:

    @classmethod
    def single_element_types(cls):
        """ See BaseFormat class for description. """
        single_element_types = super(BorealisRawacf,
                                     cls).single_element_types()
        single_element_types.update({
            # the slice id of the file and dataset.
            "slice_id": np.uint32,
            # the interfacing of this slice to other slices.
            "slice_interfacing": np.unicode_,
            # A string describing the type of scheduling time at the time of
            # this dataset.
            "scheduling_mode": np.unicode_,
            # A string describing the averaging method, ex. mean, median
            "averaging_method": np.unicode_,
            # number of blanked samples in the sequence.
            "num_blanked_samples": np.uint32
            })
        return single_element_types

    @classmethod
    def shared_fields(cls):
        """ See BaseFormat class for description. """
        shared = super(BorealisRawacf, cls).shared_fields() + \
            ['slice_id', 'scheduling_mode', 'averaging_method']
        shared.remove('blanked_samples')
        return shared

    @classmethod
    def unshared_fields_dims_array(cls):
        """ See BaseFormat class for description. """
        unshared_fields_dims = super(BorealisRawacf,
                                     cls).unshared_fields_dims_array()
        unshared_fields_dims.update({
            'blanked_samples': [cls.find_max_blanked_samples],
            'slice_interfacing': []
            })
        return unshared_fields_dims

    @classmethod
    def unshared_fields_dims_site(cls):
        """ See BaseFormat class for description. """
        unshared_fields_dims = super(BorealisRawacf,
                                     cls).unshared_fields_dims_site()
        unshared_fields_dims.update({
            'blanked_samples': [lambda arrays, record_num:
                                arrays['num_blanked_samples'][record_num]],
            'slice_interfacing': []
            })
        return unshared_fields_dims

    @classmethod
    def array_specific_fields_generate(cls):
        """ See BaseFormat class for description. """
        array_specific = super(BorealisRawacf,
                               cls).array_specific_fields_generate()
        array_specific.update({
            'num_blanked_samples': lambda records: np.array(
                [len(record['blanked_samples']) for key, record in
                 records.items()], dtype=np.uint32)
            })
        return array_specific


class BorealisBfiq(BorealisBfiqv0_4):
    """
    Class containing Borealis Bfiq data fields and their types for the
    current version of Borealis (v0.5).

    Bfiq data is beamformed i and q data. It has been mixed, filtered,
    decimated to the final output receive rate, and it has been beamformed
    and all channels have been combined into their arrays. No correlation
    or averaging has occurred.

    See base class for description of attributes and notes.

    In v0.5, the following fields were added:
    slice_id, slice_interfacing, and scheduling_mode.
    As well, blanked_samples was changed from shared to unshared in the array
    restructuring.
    """

    # New fields added in v0.5 to shared fields:

    @classmethod
    def single_element_types(cls):
        """ See BaseFormat class for description. """
        single_element_types = super(BorealisBfiq,
                                     cls).single_element_types()
        single_element_types.update({
            # the slice id of the file and dataset.
            "slice_id": np.uint32,
            # the interfacing of this slice to other slices.
            "slice_interfacing": np.unicode_,
            # A string describing the type of scheduling time at the time of
            # this dataset.
            "scheduling_mode": np.unicode_,
            # number of blanked samples in the sequence.
            "num_blanked_samples": np.uint32
            })
        return single_element_types

    @classmethod
    def shared_fields(cls):
        """ See BaseFormat class for description. """
        shared = super(BorealisBfiq, cls).shared_fields() + \
            ['slice_id', 'scheduling_mode']
        shared.remove('blanked_samples')
        return shared

    @classmethod
    def unshared_fields_dims_array(cls):
        """ See BaseFormat class for description. """
        unshared_fields_dims = super(BorealisBfiq,
                                     cls).unshared_fields_dims_array()
        unshared_fields_dims.update({
            'blanked_samples': [cls.find_max_blanked_samples],
            'slice_interfacing': []
            })
        return unshared_fields_dims

    @classmethod
    def unshared_fields_dims_site(cls):
        """ See BaseFormat class for description. """
        unshared_fields_dims = super(BorealisBfiq,
                                     cls).unshared_fields_dims_site()
        unshared_fields_dims.update({
            'blanked_samples': [lambda arrays, record_num:
                                arrays['num_blanked_samples'][record_num]],
            'slice_interfacing': []
            })
        return unshared_fields_dims

    @classmethod
    def array_specific_fields_generate(cls):
        """ See BaseFormat class for description. """
        array_specific = super(BorealisBfiq,
                               cls).array_specific_fields_generate()
        array_specific.update({
            'num_blanked_samples': lambda records: np.array(
                [len(record['blanked_samples']) for key, record in
                 records.items()], dtype=np.uint32)
            })
        return array_specific


class BorealisAntennasIq(BorealisAntennasIqv0_4):
    """
    Class containing Borealis Antennas iq data fields and their types for
    Borealis current version (v0.5).

    Antennas iq data is data with all channels separated. It has been mixed
    and filtered, but it has not been beamformed or combined into the
    entire antenna array data product.

    See base class for description of attributes and notes.
    In v0.5, the following fields were added:
    slice_id, slice_interfacing, scheduling_mode, and blanked_samples.
    """

    # New fields added in v0.5 to shared fields:

    @classmethod
    def single_element_types(cls):
        """ See BaseFormat class for description. """
        single_element_types = super(BorealisAntennasIq,
                                     cls).single_element_types()
        single_element_types.update({
            # the slice id of the file and dataset.
            "slice_id": np.uint32,
            # the interfacing of this slice to other slices.
            "slice_interfacing": np.unicode_,
            # A string describing the type of scheduling time at the time of
            # this dataset.
            "scheduling_mode": np.unicode_,
            # number of blanked samples in the sequence.
            "num_blanked_samples": np.uint32
            })
        return single_element_types

    @classmethod
    def array_dtypes(cls):
        """ See BaseFormat class for description. """
        array_dtypes = super(BorealisAntennasIq, cls).array_dtypes()
        array_dtypes.update({
            # Samples that occur during TR switching (transmission times)
            "blanked_samples": np.uint32
            })
        return array_dtypes

    @classmethod
    def shared_fields(cls):
        """ See BaseFormat class for description. """
        shared = super(BorealisAntennasIq, cls).shared_fields() + \
            ['slice_id', 'scheduling_mode']
        return shared

    @classmethod
    def unshared_fields_dims_array(cls):
        """ See BaseFormat class for description. """
        unshared_fields_dims = super(BorealisAntennasIq,
                                     cls).unshared_fields_dims_array()
        unshared_fields_dims.update({
            'blanked_samples': [cls.find_max_blanked_samples],
            'slice_interfacing': []
            })
        return unshared_fields_dims

    @classmethod
    def unshared_fields_dims_site(cls):
        """ See BaseFormat class for description. """
        unshared_fields_dims = super(BorealisAntennasIq,
                                     cls).unshared_fields_dims_site()
        unshared_fields_dims.update({
            'blanked_samples': [lambda arrays, record_num:
                                arrays['num_blanked_samples'][record_num]],
            'slice_interfacing': []
            })
        return unshared_fields_dims

    @classmethod
    def array_specific_fields_generate(cls):
        """ See BaseFormat class for description. """
        array_specific = super(BorealisAntennasIq,
                               cls).array_specific_fields_generate()
        array_specific.update({
            'num_blanked_samples': lambda records: np.array(
                [len(record['blanked_samples']) for key, record in
                 records.items()], dtype=np.uint32)
            })
        return array_specific


class BorealisRawrf(BorealisRawrfv0_4):
    """
    Class containing Borealis Rawrf data fields and their types for current
    Borealis version (v0.5).

    See base class for description of attributes and notes.
    In v0.5, the following fields were added:
    slice_id, slice_interfacing, scheduling_mode, and blanked_samples.
    """

    # New fields added in v0.5 to shared fields:

    @classmethod
    def single_element_types(cls):
        """ See BaseFormat class for description. """
        single_element_types = super(BorealisRawrf,
                                     cls).single_element_types()
        single_element_types.update({
            # A string describing the type of scheduling time at the time of
            # this dataset.
            "scheduling_mode": np.unicode_
            })
        return single_element_types

    @classmethod
    def array_dtypes(cls):
        """ See BaseFormat class for description. """
        array_dtypes = super(BorealisRawrf, cls).array_dtypes()
        array_dtypes.update({
            # Samples that occur during TR switching (transmission times)
            "blanked_samples": np.uint32
            })
        return array_dtypes


# borealis versions
borealis_version_dict = {
    'v0.2': {
        'bfiq': BorealisBfiqv0_4,
        'rawacf': BorealisRawacfv0_4,
        'antennas_iq': BorealisAntennasIqv0_4,
        'rawrf': BorealisRawrfv0_4
        },
    'v0.3': {
        'bfiq': BorealisBfiqv0_4,
        'rawacf': BorealisRawacfv0_4,
        'antennas_iq': BorealisAntennasIqv0_4,
        'rawrf': BorealisRawrfv0_4
        },
    'v0.4': {
        'bfiq': BorealisBfiqv0_4,
        'rawacf': BorealisRawacfv0_4,
        'antennas_iq': BorealisAntennasIqv0_4,
        'rawrf': BorealisRawrfv0_4
        },
    'v0.5': {
        'bfiq': BorealisBfiq,
        'rawacf': BorealisRawacf,
        'antennas_iq': BorealisAntennasIq,
        'rawrf': BorealisRawrf
    }
}
