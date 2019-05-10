# Copyright 2019 SuperDARN
# Author: Marci Detwiller
"""
This file contains classes for reading, writing, and converting of Borealis file types.
The file types that are supported:
    - 


Classes:
--------
BorealisUtilities: utilites class that contains static methods for
SuperDARN file type checking
BorealisRead : Reads Borealis SuperDARN file types (hdf5)
BorealisWrite : Writes Borealis SuperDARN file types (hdf5
BorealisConvert : Writes Borealis SuperDARN files types to 
SuperDARN legacy files with dmap record structure 


Exceptions:
-----------
BorealisFileTypeError
BorealisFieldMissingError
BorealisExtraFieldError
BorealisDataFormatTypeError
BorealisConversionTypesError 
BorealisConvert2IqdatError
BorealisConvert2RawacfError

Future work
-----------


Notes
-----
BorealisConvert makes use of DarnWrite to write to SuperDARN file types
"""



import sys
import numpy as np
from datetime import datetime
import os
import h5py
import deepdish as dd
import logging
from typing import Union, List
import math

from pydarn.exceptions import borealis_exceptions
from pydarn.io.superdarn import DarnWrite
from pydarn.borealis_io import borealis_formats
from pydarn.io import superdarn_formats

pydarn_log = logging.getLogger('pydarn')

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


class BorealisUtilities():
    """
    Utility class that contains static methods that does dictionary set
    calculations used for determining if there is any missing or extra
    fields in Borealis file types. Also, does data format type checks
    for Borealis file types.

    Static Methods
    ----------------
        dict_key_diff(dict1, dict2)
            Returns a set of the difference between dict1 and dict2 keys
        dict_list2set(dict_list)
            Converts a list of dictionaries to a set containing their keys
        missing_field_check(file_struct_list, record, record_name)
            Checks if there is any missing fields in the record from
            a list of possible file fields
        extra_field_check(file_struct_list, record, record_name)
            Checks if there is any extra fields in the record from
            a list of possible file fields
        incorrect_types_check(file_struct_list, record_name)
            Checks if there is any incorrect types in the record from
            a list of possible file fields and their data type formats


    """
    @staticmethod
    def dict_key_diff(dict1: Union[dict, set],
                      dict2: Union[dict, set]) -> set:
        """
        Determines the difference in the key set from the
        first dictionary to the second dictionary.
        ex) Let A = {a, b, c} and B = {d, a, b}
        Then A - B = {c}

        Parameters:
        -----------
        dict1 : dict or set
            dictionary or set to subtract from
        dict2 : dict or set
            dictionary or set subtracting from dict1

        Return:
        ------
        dict_diff : set
            difference between dict1 and dict2 keys or the sets
        """
        diff_dict = set(dict1) - set(dict2)
        return diff_dict


    @staticmethod
    def dict_list2set(dict_list: List[dict]) -> set:
        """
        Converts a list of dictionaries to list of sets

        Parameters:
        -----------
        dict_list : list
            list of dictionaries

        Return:
        ------
        complete_set : set
            set containing all dictionary key from the list of dicts
        """
        # convert dictionaries to set to do some set magic
        sets = [set(dic) for dic in dict_list]  
        # create a complete set list
        # * - expands the list out into multiple set arguments
        # then the union operator creates it into a full unique set
        # example: s = [{'a','v'}, {'v','x'}] => set.union(*s) = {'a', 'v', 'x'}
        complete_set = set.union(*sets)
        return complete_set


    @staticmethod
    def missing_field_check(file_struct_list: List[dict],
                            record: dict, record_name: int):
        """
        Checks if any fields are missing from the record compared to the file
        structure.

        Parameters:
        -----------
        file_struct_list : List[dict]
            List of dictionaries for the possible file structure fields
        record : dict
            Dictionary representing the dmap record
        record_name : int
            The name of the record (first sequence start time)

        Raises:
        -------
        BorealisFieldMissing
        """
        """
        We have to check the subsets. Any missing fields is a problem because Borealis 
        field names are well-defined.
        """
        missing_fields = set()
        for file_struct in file_struct_list:
            diff_fields = BorealisUtilities.dict_key_diff(file_struct, record)
            if len(diff_fields) != 0:
                missing_fields = missing_fields.union(diff_fields)

        if len(missing_fields) > 0:
            raise borealis_exceptions.BorealisFieldMissingError(record_name,
                                                                  missing_fields)

    @staticmethod
    def extra_field_check(file_struct_list: List[dict],
                          record: dict, record_name: int):
        """
        Check if there is an extra field in the file structure list and record.

        Parameters
        -----------
        file_struct_list : List[dict]
            List of dictionaries for the possible file structure fields
        record : dict
            Dmap record
        record_name : int
            Record name for better error message information

        Raises
        -------
        BorealisExtraField

        """
        file_struct = BorealisUtilities.dict_list2set(file_struct_list)
        extra_fields = BorealisUtilities.dict_key_diff(record, file_struct)

        if len(extra_fields) > 0:
            raise borealis_exceptions.BorealisExtraFieldError(record_name,
                                                                extra_fields)


    @staticmethod
    def incorrect_types_check(attributes_type_dict: dict, 
                              datasets_type_dict: dict,
                              record: dict,
                              record_name: int):
        """
        Checks if the file structure fields data type formats are correct
        in the record.

        Parameters
        ----------
        attributes_type_dict : dict
            Dictionary with the required types for the attributes in the file.
        datasets_type_dict : dict
            Dictionary with the require dtypes for the numpy arrays in the file.
        record : dict
            Dmap record
        record_name : int
            Record name for a better error message information

        Raises
        ------
        BorealisFileFormatError
        """
        # check the attributes
        incorrect_types_check = {param: str(attributes_type_dict[param])
                             for param in attributes_type_dict.keys()
                             if type(record[param]) != attributes_type_dict[param]}
        # the rest of the parameters in the record are numpy arrays (HDF5 datasets)
        incorrect_types_check.update({param: 'np.ndarray of ' + str(record[param].dtype) #str(datasets_type_dict[param])
                             for param in datasets_type_dict.keys()
                             if record[param].dtype.type != datasets_type_dict[param]})
        if len(incorrect_types_check) > 0:
            raise borealis_exceptions.BorealisDataFormatTypeError(incorrect_types_check,
                                                                    record_name)


class BorealisRead():

    def __init__(self, borealis_file: str):
        """
        Reads SuperDARN Borealis file types into a dictionary for reading methods.

        Parameters
        ----------
        borealis_file : str
            file name containing Borealis hdf5 data.

        Raises
        ------
        OSError
            Unable to open file
        """
        self.borealis_file = borealis_file

        with h5py.File(self.borealis_file, 'r') as f:
            self._group_names = sorted(list(f.keys()))
            # list of group keys in the HDF5 file, to allow partial read.

        self._current_record_name = '' # Current HDF5 record group name.

        # Records are private to avoid tampering.
        self._records = {}


    @property
    def current_record_name(self):
        return self._current_record_name


    @property
    def records(self):
        return self._records


    def read_file(self, borealis_filetype: str):
        """
        Reads the specified Borealis file using the other functions.

        Returns
        -------
        records : dict{dict}
            records of borealis data. Keys are timestamps of write.

        Raises
        ------
        BorealisFileTypeError
        """

        if borealis_filetype == 'bfiq':
            self.read_bfiq()
            return self._records
        elif borealis_filetype == 'rawacf':
            self.read_rawacf()
            return self._records
        elif borealis_filetype == 'output_ptrs_iq':
            self.read_output_ptrs_iq()
            return self._records
        elif borealis_filetype == 'rawrf':
            self.read_rawrf()
            return self._records
        else:
            raise borealis_exceptions.BorealisFileTypeError(self.borealis_file, borealis_filetype)


    def read_bfiq(self) -> dict:
        """
        Reads Borealis bfiq file

        Returns
        -------
        records : dict{dict}
            records of beamformed iq data. Keys are timestamps of write.
        """
        pydarn_log.debug("Reading Borealis bfiq file: {}".format(self.borealis_file))
        attribute_types = borealis_formats.BorealisBfiq.single_element_types
        dataset_types = borealis_formats.BorealisBfiq.array_dtypes
        self._read_borealis_records(attribute_types, dataset_types)
        return self._records


    def read_rawacf(self) -> dict:
        """
        Reads Borealis rawacf file

        Returns
        -------
        records : dict{dict}
            records of borealis rawacf data. Keys are timestamps of write.
        """
        pydarn_log.debug("Reading Borealis rawacf file: {}".format(self.borealis_file))
        attribute_types = borealis_formats.BorealisRawacf.single_element_types
        dataset_types = borealis_formats.BorealisRawacf.array_dtypes
        self._read_borealis_records(attribute_types, dataset_types)
        return self._records


    def read_output_ptrs_iq(self) -> dict:
        """
        Reads Borealis output_ptrs_iq file

        Returns
        -------
        records : dict{dict}
            records of borealis rawacf data. Keys are timestamps of write.
        """
        pydarn_log.debug("Reading Borealis output_ptrs_iq file: {}".format(self.borealis_file))
        attribute_types = borealis_formats.BorealisOutputPtrsIq.single_element_types
        dataset_types = borealis_formats.BorealisOutputPtrsIq.array_dtypes
        self._read_borealis_records(attribute_types, dataset_types)
        return self._records


    def read_rawrf(self) -> dict:
        """
        Reads Borealis rawrf file

        Returns
        -------
        records : dict{dict}
            records of borealis rawacf data. Keys are timestamps of write.
        """
        pydarn_log.debug("Reading Borealis rawrf file: {}".format(self.borealis_file))
        attribute_types = borealis_formats.BorealisRawrf.single_element_types
        dataset_types = borealis_formats.BorealisRawrf.array_dtypes
        self._read_borealis_records(attribute_types, dataset_types)
        return self._records


    def _read_borealis_records(self, attribute_types : dict, dataset_types : dict):
        """
        Read the entire file while checking all 

        Parameters
        ----------
        attributes_type_dict : dict
            Dictionary with the required types for the attributes in the file.
        datasets_type_dict : dict
            Dictionary with the require dtypes for the numpy arrays in the file.        

        """

        for record_name in self._group_names:
            self._current_record_name = record_name
            self._read_borealis_record(attribute_types, dataset_types)


    def _read_borealis_record(self, attribute_types : dict, dataset_types : dict):
        """
        Read a Borealis HDF5 record. Several Borealis
        field checks are done to insure the integrity of the file. Append
        to the records dictionary.

        Parameters
        ----------
        attributes_type_dict : dict
            Dictionary with the required types for the attributes in the file.
        datasets_type_dict : dict
            Dictionary with the require dtypes for the numpy arrays in the file.

        Raises:
        -------
        OSError: file does not exist
        BorealisFieldMissingError - when a field is missing from the Borealis
                                file/stream type
        BorealisExtraFieldError - when an extra field is present in the
                                Borealis file/stream type
        BorealisDataFormatTypeError - when a field has the incorrect
                                field type for the Borealis file/stream type

        See Also
        --------
        missing_field_check(format_fields, record, record_name) - checks
                        for missing fields. See this method for information
                        on why we use format_fields.
        extra_field_check(format_fields, record, record_name) - checks for
                        extra fields in the record
        incorrect_types_check(attribute_types_dict, dataset_types_dict, record, record_name) - checks
                        for incorrect data types for file fields
        """

        all_format_fields = [attribute_types, dataset_types]

        record = dd.io.load(self.borealis_file, group='/'+self._current_record_name)
        BorealisUtilities.missing_field_check(all_format_fields, record, self._current_record_name)
        BorealisUtilities.extra_field_check(all_format_fields, record, self._current_record_name)
        BorealisUtilities.incorrect_types_check(attribute_types, dataset_types, record, self._current_record_name)
        self._records[self._current_record_name] = record


class BorealisWrite():

    def __init__(self, borealis_records: dict = {}, filename: str = ""):
        """
        Write borealis records to a file. 

        Parameters
        ----------
        borealis_records : List[dict]
            List of borealis records
        filename : str
            Name of the file the user wants to write to
        """
        self.borealis_records = borealis_records
        self.filename = filename
        self._group_names = sorted(list(borealis_records.keys()))
        # list of group keys for partial write
        self._current_record_name = ''


    def write_file(self, borealis_filetype) -> str:
        """
        Write Borealis records to a file given filetype.

        Parameters
        ----------
        borealis_filetype
            filetype to write as. Currently supported:
                - bfiq
                - rawacf
                - output_ptrs_iq
                - rawrf
        """

        if borealis_filetype == 'bfiq':
            self.write_bfiq()
        elif borealis_filetype == 'rawacf':
            self.write_rawacf()
        elif borealis_filetype == 'output_ptrs_iq':
            self.write_output_ptrs_iq()
        elif borealis_filetype == 'rawrf':
            self.write_rawrf()
        else:
            raise borealis_exceptions.BorealisFileTypeError(self.borealis_file, borealis_filetype)


    def write_bfiq(self) -> str:
        """
        Writes Borealis bfiq file

        Returns
        -------
        filename: str
            Filename of written file.
        """
        pydarn_log.debug("Writing Borealis bfiq file: {}".format(self.filename))
        attribute_types = borealis_formats.BorealisBfiq.single_element_types
        dataset_types = borealis_formats.BorealisBfiq.array_dtypes
        self._write_borealis_records(attribute_types, dataset_types)
        return self.filename


    def write_rawacf(self) -> str:
        """
        Writes Borealis rawacf file

        Returns
        -------
        filename: str
            Filename of written file.
        """
        pydarn_log.debug("Writing Borealis rawacf file: {}".format(self.filename))
        attribute_types = borealis_formats.BorealisRawacf.single_element_types
        dataset_types = borealis_formats.BorealisRawacf.array_dtypes
        self._write_borealis_records(attribute_types, dataset_types)
        return self.filename


    def read_output_ptrs_iq(self) -> str:
        """
        Writes Borealis output_ptrs_iq file

        Returns
        -------
        filename: str
            Filename of written file.
        """
        pydarn_log.debug("Writing Borealis output_ptrs_iq file: {}".format(self.filename))
        attribute_types = borealis_formats.BorealisOutputPtrsIq.single_element_types
        dataset_types = borealis_formats.BorealisOutputPtrsIq.array_dtypes
        self._write_borealis_records(attribute_types, dataset_types)
        return self.filename


    def read_rawrf(self) -> str:
        """
        Writes Borealis rawrf file

        Returns
        -------
        filename: str
            Filename of written file.
        """
        pydarn_log.debug("Writing Borealis rawrf file: {}".format(self.filename))
        attribute_types = borealis_formats.BorealisRawrf.single_element_types
        dataset_types = borealis_formats.BorealisRawrf.array_dtypes
        self._write_borealis_records(attribute_types, dataset_types)
        return self.filename


    def _write_borealis_records(self, attribute_types : dict, dataset_types : dict):
        """
        Write the file record by record checking each record as we go.

        Parameters
        ----------
        attributes_type_dict : dict
            Dictionary with the required types for the attributes in the file.
        datasets_type_dict : dict
            Dictionary with the require dtypes for the numpy arrays in the file.        

        Raises
        --------
        OSError: file does not exist

        """
        for record_name in self._group_names:
            self._current_record_name = record_name
            self._write_borealis_record(attribute_types, dataset_types)


    def _write_borealis_record(self, attribute_types : dict, dataset_types : dict):
        """
        Writes a Borealis HDF5 record. Several Borealis
        field checks are done to insure the integrity of the file. Append
        to the file.

        Parameters
        ----------
        attributes_type_dict : dict
            Dictionary with the required types for the attributes in the file.
        datasets_type_dict : dict
            Dictionary with the require dtypes for the numpy arrays in the file.

        Raises:
        -------
        BorealisFieldMissingError - when a field is missing from the Borealis
                                file/stream type
        BorealisExtraFieldError - when an extra field is present in the
                                Borealis file/stream type
        BorealisDataFormatTypeError - when a field has the incorrect
                                field type for the Borealis file/stream type

        See Also
        --------
        missing_field_check(format_fields, record, record_name) - checks
                        for missing fields. See this method for information
                        on why we use format_fields.
        extra_field_check(format_fields, record, record_name) - checks for
                        extra fields in the record
        incorrect_types_check(attribute_types_dict, dataset_types_dict, record, record_name) - checks
                        for incorrect data types for file fields
        """

        all_format_fields = [attribute_types, dataset_types]
        record = self.borealis_records[self._current_record_name]
        BorealisUtilities.missing_field_check(all_format_fields, record, self._current_record_name)
        BorealisUtilities.extra_field_check(all_format_fields, record, self._current_record_name)
        BorealisUtilities.incorrect_types_check(attribute_types, dataset_types, record, self._current_record_name)
        dd.io.save(self.file_name, {self._current_record_name : record}, compression=None)


class BorealisConvert():

    def __init__(self, filename):
        """
        Convert HDF5 Borealis records to a given SuperDARN legacy file with dmap format.

        Attributes
        ----------

        filename: name of file to read records from 
        records: the records in the file provided
        origin_filetype: hdf5 filetype from borealis, indicating the record structure.
            ex. bfiq, output_ptrs_iq, ...

        """

        self.filename = filename
        borealis_reader = BorealisRead(self.filename)
        self._origin_filetype = os.path.basename(self.filename).split('.')[-2]
        self._borealis_records = borealis_reader.read_file(self.origin_filetype)
        self._dmap_records = {}


    @property
    def borealis_records(self):
        return self._borealis_records


    @property
    def origin_filetype(self):
        return self._origin_filetype


    def write_to_dmap(self, dmap_filetype) -> str:
        """
        Write the Borealis records as dmap records to a dmap file using PyDARN IO. Return dmap filename.

        Parameters
        ----------
        dmap_filetype: intended SuperDARN legacy filetype to write to as dmap.
        Dmap file types, the following are supported:
                                     - 'iqdat' : SuperDARN file type
                                     - 'rawacf' : SuperDARN file type

        Returns
        -------
        dmap_filename, the name of the DARN file written.
        """

        dmap_filename = os.path.splitext(self.filename)[0]+'.'+dmap_filetype
        self._convert_records_to_dmap(dmap_filetype)
        DarnWrite(self._dmap_records, dmap_filename)
        return dmap_filename


    def _convert_records_to_dmap(self, dmap_filetype):
        """
        Convert the Borealis records to the dmap filetype, if possible.

        Parameters
        ----------
        dmap_filetype: intended SuperDARN legacy filetype to write to as dmap.
        Dmap file types, the following are supported:
                                     - 'iqdat' : SuperDARN file type
                                     - 'rawacf' : SuperDARN file type

        Raises
        ------
        BorealisConversionTypesError

        """

        if dmap_filetype == 'iqdat':
            if self._is_convertible_to_iqdat():
                self._convert_bfiq_to_iqdat()
        elif dmap_filetype == 'rawacf':
            if self._is_convertible_to_rawacf():
                self._convert_rawacf_to_rawacf()    
        else:  # nothing else is currently supported
            raise borealis_exceptions.BorealisConversionTypesError(self.filename, self.origin_filetype, dmap_filetype)


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

        if self.origin_filetype != 'bfiq':
            raise borealis_exceptions.BorealisConversionTypesError(self.filename, self.origin_filetype, dmap_filetype)
        else: # There are some specific things to check 
            for k, v in self._borealis_records.items():
                if not np.array_equal(v['blanked_samples'], v['pulses']*int(v['tau_spacing']/v['tx_pulse_len'])):
                    raise borealis_exceptions.BorealisConvert2IqdatError('Borealis bfiq file record {} blanked_samples {} '\
                        'does not equal pulses array {}'.format(k, v['blanked_samples'], v['pulses']))
                if not all([x==0 for x in v['pulse_phase_offset']]):
                    raise borealis_exceptions.BorealisConvert2IqdatError('Borealis bfiq file record {} pulse_phase_offset {} '\
                        'contains non-zero values.'.format(k, v['pulse_phase_offset']))     

        return True         


    def _is_convertible_to_rawacf(self) -> bool:
        """
        Checks if the file is convertible to rawacf. 

        The file is convertible if:
            - the origin filetype is rawacf
            - the blanked_samples array = pulses array for all records
            - the pulse_phase_offset array contains all zeroes for all records

        Raises
        ------
        BorealisConversionTypesError
        BorealisConvert2RawacfError

        Returns
        -------
        True if convertible
        """

        if self.origin_filetype != 'rawacf':
            raise borealis_exceptions.BorealisConversionTypesError(self.filename, self.origin_filetype, dmap_filetype)
        else: # There are some specific things to check 
            for k, v in self._borealis_records.items():
                if not np.array_equal(v['blanked_samples'], v['pulses']):
                    raise borealis_exceptions.BorealisConvert2IqdatError('Borealis rawacf file record {} blanked_samples {} '\
                        'does not equal pulses array {}'.format(k, v['blanked_samples'], v['pulses']))
                if not all([x==0 for x in v['pulse_phase_offset']]):
                    raise borealis_exceptions.BorealisConvert2IqdatError('Borealis rawacf file record {} pulse_phase_offset {} '\
                        'contains non-zero values.'.format(k, v['pulse_phase_offset']))     

        return True     


    def _convert_bfiq_to_iqdat(self):
        """
        Conversion for bfiq to iqdat records.

        """

        dmap_recs = []
        for k, v in self._borealis_records.items():
            data = v['data'].reshape(v['data_dimensions']) # data_descriptors are num_antenna_arrays, num_sequences, num_beams, num_samps

            if v['borealis_git_hash'][0] == 'v' and v['borealis_git_hash'][2] == '.':
                borealis_major_revision = v['borealis_git_hash'][1]
                borealis_minor_revision = v['borealis_git_hash'][3]
            else:
                borealis_major_revision = 255
                borealis_minor_revision = 255                       

            slice_id = os.path.basename(self.filename).split('.')[-3]
            offset = 2 * v['antenna_arrays_order'].shape[0] * v['num_samps']
            
            for beam_index, beam in enumerate(v['beam_nums']):

                # grab this beam's data
                this_data = data[:,:,beam_index,:] # shape is num_antenna_arrays x num_sequences x num_samps
                # iqdat shape is num_sequences x num_antennas_arrays x num_samps x 2 (real, imag), flattened
                reshaped_data = []                  
                for i in range(v['num_sequences']):
                    arrays = [this_data[x,i,:] for x in range(this_data.shape[0])] # get the samples for each array 1 after the other
                    reshaped_data.append(np.ravel(np.column_stack(arrays))) # append 

                flattened_data = np.array(reshaped_data).flatten() #(num_sequences x num_antenna_arrays x num_samps, flattened)

                int_data = np.empty(flattened_data.size * 2, dtype=np.int32)

                int_data[0::2] = flattened_data.real
                int_data[1::2] = flattened_data.imag

                dmap_recs.append({
                    'radar.revision.major' : np.int8(borealis_major_revision),
                    'radar.revision.minor' : np.int8(borealis_minor_revision),
                    'origin.code' : np.int8(100), # indicating Borealis origin
                    'origin.time' : datetime.utcfromtimestamp(v['timestamp_of_write']).strftime("%c"),
                    'origin.command' : 'Borealis ' + v['borealis_git_hash'] + ' ' + v['experiment_name'],
                    'cp' : np.int16(v['experiment_id']),
                    'stid' : np.int16(code_to_stid[v['station']]),
                    'time.yr' : np.int16(datetime.utcfromtimestamp(v['sqn_timestamps'][0]).year),
                    'time.mo' : np.int16(datetime.utcfromtimestamp(v['sqn_timestamps'][0]).month),
                    'time.dy' : np.int16(datetime.utcfromtimestamp(v['sqn_timestamps'][0]).day),
                    'time.hr' : np.int16(datetime.utcfromtimestamp(v['sqn_timestamps'][0]).hour),
                    'time.mt' : np.int16(datetime.utcfromtimestamp(v['sqn_timestamps'][0]).minute),
                    'time.sc' : np.int16(datetime.utcfromtimestamp(v['sqn_timestamps'][0]).second),
                    'time.us' : np.int16(datetime.utcfromtimestamp(v['sqn_timestamps'][0]).microsecond),
                    'txpow' : np.int16(-1),
                    'nave' : np.int16(v['num_sequences']),
                    'atten' : np.int16(0),
                    'lagfr' : np.int16(v['first_range_rtt']),
                    'smsep' : np.int16(1e6/v['rx_sample_rate']),
                    'ercod' : np.int16(0),
                    'stat.agc' : np.int16(0),
                    'stat.lopwr' : np.int16(0),
                    'noise.search' : np.float32(v['noise_at_freq'][0]),
                    'noise.mean' : np.float32(0),
                    'channel' : np.int16(slice_id),
                    'bmnum' : np.int16(beam),
                    'bmazm' : np.float32(v['beam_azms'][beam_index]),
                    'scan' : np.int16(v['scan_start_marker']),
                    'offset' : np.int16(0),
                    'rxrise' : np.int16(0),
                    'intt.sc' : np.int16(math.floor(v['int_time'])),
                    'intt.us' : np.int16(math.fmod(v['int_time'], 1.0) * 1e6),
                    'txpl' : np.int16(v['tx_pulse_len']),
                    'mpinc' : np.int16(v['tau_spacing']),
                    'mppul' : np.int16(len(v['pulses'])),
                    'mplgs' : np.int16(v['lags'].shape[0]),
                    'nrang' : np.int16(v['num_ranges']),
                    'frang' : np.int16(v['first_range']),
                    'rsep' : np.int16(v['range_sep']),
                    'xcf' : np.int16('intf' in v['antenna_arrays_order']),
                    'tfreq' : np.int16(v['freq']),
                    'mxpwr' : np.int32(-1),
                    'lvmax' : np.int32(20000),
                    'iqdata.revision.major' : np.int32(1),
                    'iqdata.revision.minor' : np.int32(0),
                    'combf' : 'Converted from Borealis file: ' + self.filename + ' ; Number of beams in record: ' 
                              + str(len(v['beam_nums'])) + ' ; ' + v['experiment_comment'] + ' ; ' + v['slice_comment'],
                    'seqnum' : np.int32(v['num_sequences']),
                    'chnnum' : np.int32(v['antenna_arrays_order'].shape[0]),
                    'smpnum' : np.int32(v['num_samps']),
                    'skpnum' : np.int32(0),
                    'ptab' : v['pulses'].astype(np.int16),
                    'ltab' : np.transpose(v['lags']).astype(np.int16),
                    'tsc' : np.array([math.floor(x/1e3) for x in v['sqn_timestamps']], dtype=np.int32), # timestamps in ms
                    'tus' : np.array([math.fmod(x, 1000.0) * 1e3 for x in v['sqn_timestamps']],dtype=np.int32),
                    'tatten' : np.array([0] * v['num_sequences'], dtype=np.int32),
                    'tnoise' : v['noise_at_freq'].astype(np.float32),
                    'toff' : np.array([i * offset for i in range(v['num_sequences'])], dtype=np.int32),
                    'tsze' : np.array([offset] * v['num_sequences'], dtype=np.int32),
                    'data' : int_data,
                    })

        self._dmap_records = dmap_recs


    def _convert_rawacf_to_rawacf(self):
        """
        Conversion for Borealis hdf5 rawacf to DARN legacy dmap rawacf files.
        """

        dmap_recs = []
        for k, v in self._borealis_records.items():
            shaped_data = {}
            shaped_data['main_acfs'] = v['main_acfs'].reshape(v['correlation_dimensions']) # data_descriptors are num_beams, num_ranges, num_lags
            if v['intf_acfs']:
                shaped_data['intf_acfs'] = v['intf_acfs'].reshape(v['correlation_dimensions'])
            if v['xcfs']:
                shaped_data['xcfs'] = v['xcfs'].reshape(v['correlation_dimensions'])

            if v['borealis_git_hash'][0] == 'v' and v['borealis_git_hash'][2] == '.':
                borealis_major_revision = v['borealis_git_hash'][1]
                borealis_minor_revision = v['borealis_git_hash'][3]
            else:
                borealis_major_revision = 255
                borealis_minor_revision = 255                       

            slice_id = os.path.basename(self.filename).split('.')[-3]
            
            for beam_index, beam in enumerate(v['beam_nums']):
                lag_zero = main_acfs[beam_index,:,0] # this beam, all ranges lag 0
                lag_zero_power = (lag_zero.real**2 + lag_zero.imag**2)**0.5

                # rawacf shape is 2 x num_lags x num_ranges
                correlation_dict = {}
                for key in shaped_data: # all available correlation types have been included here   
                    reshaped_data = []
                    this_correlation = shaped_data[key][beam_index,:,:] # shape num_beams x num_ranges x num_lags, now num_ranges x num_Lags
                    for i in range(v['correlation_dimensions'][2]): # loop over num_lags
                        arrays = [this_correlation[x,i] for x in range(v['correlation_dimensions'][1])] # get the samples for each range in the lag
                        reshaped_data.append(np.ravel(np.column_stack(arrays))) # append lags x ranges

                    flattened_data = np.array(reshaped_data).flatten() #(num_lags x num_ranges, flattened)

                    int_data = np.empty(flattened_data.size * 2, dtype=np.int32)
                    int_data[0::2] = flattened_data.real
                    int_data[1::2] = flattened_data.imag
                    correlation_dict[key] = int_data  # place the darn-style array in the dict

                dmap_recs.append({
                    'radar.revision.major' : np.int8(borealis_major_revision),
                    'radar.revision.minor' : np.int8(borealis_minor_revision),
                    'origin.code' : np.int8(100), # indicating Borealis origin
                    'origin.time' : datetime.utcfromtimestamp(v['timestamp_of_write']).strftime("%c"),
                    'origin.command' : 'Borealis ' + v['borealis_git_hash'] + ' ' + v['experiment_name'],
                    'cp' : np.int16(v['experiment_id']),
                    'stid' : np.int16(code_to_stid[v['station']]),
                    'time.yr' : np.int16(datetime.utcfromtimestamp(v['sqn_timestamps'][0]).year),
                    'time.mo' : np.int16(datetime.utcfromtimestamp(v['sqn_timestamps'][0]).month),
                    'time.dy' : np.int16(datetime.utcfromtimestamp(v['sqn_timestamps'][0]).day),
                    'time.hr' : np.int16(datetime.utcfromtimestamp(v['sqn_timestamps'][0]).hour),
                    'time.mt' : np.int16(datetime.utcfromtimestamp(v['sqn_timestamps'][0]).minute),
                    'time.sc' : np.int16(datetime.utcfromtimestamp(v['sqn_timestamps'][0]).second),
                    'time.us' : np.int16(datetime.utcfromtimestamp(v['sqn_timestamps'][0]).microsecond),
                    'txpow' : np.int16(-1),
                    'nave' : np.int16(v['num_sequences']),
                    'atten' : np.int16(0),
                    'lagfr' : np.int16(v['first_range_rtt']),
                    'smsep' : np.int16(1e6/v['rx_sample_rate']),
                    'ercod' : np.int16(0),
                    'stat.agc' : np.int16(0),
                    'stat.lopwr' : np.int16(0),
                    'noise.search' : np.float32(v['noise_at_freq'][0]),
                    'noise.mean' : np.float32(0),
                    'channel' : np.int16(slice_id),
                    'bmnum' : np.int16(beam),
                    'bmazm' : np.float32(v['beam_azms'][beam_index]),
                    'scan' : np.int16(v['scan_start_marker']),
                    'offset' : np.int16(0),
                    'rxrise' : np.int16(0),
                    'intt.sc' : np.int16(math.floor(v['int_time'])),
                    'intt.us' : np.int16(math.fmod(v['int_time'], 1.0) * 1e6),
                    'txpl' : np.int16(v['tx_pulse_len']),
                    'mpinc' : np.int16(v['tau_spacing']),
                    'mppul' : np.int16(len(v['pulses'])),
                    'mplgs' : np.int16(v['lags'].shape[0]),
                    'nrang' : np.int16(v['correlation_dimensions'][1]),
                    'frang' : np.int16(v['first_range']),
                    'rsep' : np.int16(v['range_sep']),
                    'xcf' : np.int16(bool(v['xcfs'])), # False is list is empty.
                    'tfreq' : np.int16(v['freq']),
                    'rawacf.revision.major' : np.int32(1),
                    'rawacf.revision.minor' : np.int32(0),
                    'combf' : 'Converted from Borealis file: ' + self.filename + ' ; Number of beams in record: ' 
                              + str(len(v['beam_nums'])) + ' ; ' + v['experiment_comment'] + ' ; ' + v['slice_comment'],
                    'thr' : np.float32(0),
                    'ptab' : v['pulses'].astype(np.int16),
                    'ltab' : np.transpose(v['lags']).astype(np.int16),
                    'pwr0' : lag_zero_power,
                    'slist' : np.array(list(range(0,this_main_acf.shape[0]))), # list from 0 to num_ranges
                    'acfd' : correlation_dict['main_acfs'],
                    'xcfd' : correlation_dict['xcfs']
                    # TODO: intf acfs or lag zero power?
                    })

        self._dmap_records = dmap_recs
