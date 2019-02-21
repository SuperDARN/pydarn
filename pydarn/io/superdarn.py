# Copyright 2018 SuperDARN
# Author: Marina Schmidt
"""
This file contains classes for reading and writing of SuperDARN file types.
The file types that are supported:
    - Iqdat
    - Rawacf
    - Fitacf
    - Grid
    - Map

Classes:
--------
DarnUtilities: utilites class that contains static methods for
SuperDARN file type checking
DarnRead : Reads SuperDARN files types
DarnWrite : writes Dmap Record structure into a SuperDARN file type

Exceptions:
-----------
SuperDARNFieldMissingError
SuperDARNExtraFieldError
SuperDARNDataTypeError

Future work
-----------
Organization
    rethink public and private methods? <--- discussion

Notes
-----
DmapRead and DmapWrite are inherited by DarnRead and DarnWrite
"""
from typing import Union, List

from pydarn import superdarn_exceptions
from pydarn import DmapRead
from pydarn import DmapWrite
from pydarn import superdarn_formats


class DarnUtilities():
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

    # TODO: might be moved to utility class as a static method
    # Also, might not be needed if we do not use the data types
    # in the structure  dictionaries
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
        sets = [set(dic) for dic in dict_list]  # TODO: if data types don't matter in the structure format then they can become sets instead of dictionaries.
        # create a complete set list
        complete_set = set.union(*sets)
        return complete_set

    @staticmethod
    def missing_field_check(file_struct_list: List[dict],
                            record: dict, rec_num: int):
        """
        Checks if any fields are missing from the record compared to the file
        structure.

        Parameters:
        -----------
        file_struct_list : List[dict]
            List of dictionaries for the possible file structure fields
        record : dict
            Dictionary representing the dmap record
        rec_num : int
            Record number for better error message information

        Raises:
        -------
        SuperDARNFieldMissing
        """
        # Needed to get the intersection between the record and complete
        # file structure types
        complete_set = DarnUtilities.dict_list2set(file_struct_list)
        missing_fields = set()
        for file_struct in file_struct_list:
            # An intersection of a set returns what both sets have in common
            # then comparing the difference from the subset of types
            # you can determine what is missing.
            diff_fields = DarnUtilities.dict_key_diff(file_struct,
                                                      set(record).
                                                      intersection(complete_set))
            # For Grid and Map files this is needed because depending
            # on command line options to generate the grid and map files
            # some fields are added in.
            # If 0 nothing missing, if len(file_struct) then
            # that subset is missing only meaning that command option was
            # not used, not necessarily meaning that it is a record.
            if len(diff_fields) not in (0, len(file_struct)):
                missing_fields = missing_fields.union(diff_fields)

        if len(missing_fields) > 0:
            raise superdarn_exceptions.SuperDARNFieldMissingError(rec_num,
                                                             missing_fields)

    @staticmethod
    def extra_field_check(file_struct_list: List[dict],
                          record: dict, rec_num: int):
        """
        Check if there is an extra field in the file structure list and record.

        Parameters
        -----------
        file_struct_list : List[dict]
            List of dictionary representing the possible fields
            in file structure
        record : dict
            Dmap record
        rec_num : int
            Record number for better error message information

        Raises
        -------
        SuperDARNFieldExtra

        """
        file_struct = DarnUtilities.dict_list2set(file_struct_list)
        extra_fields = DarnUtilities.dict_key_diff(record, file_struct)

        if len(extra_fields) > 0:
            raise superdarn_exceptions.SuperDARNExtraFieldError(rec_num,
                                                           extra_fields)

    # TODO: Do we want to check this? If not, then change
    # SuperDARN_format_structure types to sets to get rid
    # of dict_list2set method.
    @staticmethod
    def incorrect_types_check(self, file_struct_list: List[dict],
                              record: dict, rec_num: int):
        """
        Checks if the file structure fields data type formats are correct
        in the record.

        Parameters
        ----------
        file_struct_list : List[dict]
            List of dictionaries representing the possible fields
            in a file structure
        record : dict
            Dmap record
        rec_num : int
            Record number for a better error message information

        Raises
        ------
        SuperDARNFileFormatError
        """
        complete_dict = {}
        for file_struct in file_struct_list:
            complete_dict.update(file_struct)
        incorrect_types_check = {param: complete_dict[param]
                                 for param in record.keys()
                                 if record[param].data_type_fmt
                                 != complete_dict[param]}
        if len(incorrect_types_check) > 0:
            raise superdarn_exceptions.SuperDARNDataFormatTypeError(incorrect_types_check, rec_num)


class DarnRead(DmapRead):
    def __init__(self, filename, stream=False):
        DmapRead.__init__(self, filename, stream)

    # helper function that could be used parallelization
    def _read_darn_record(self, rec_num: int, format_fields: List[dict]):
        record = self.read_record()
        DarnUtilities.missing_field_check(format_fields, record, rec_num)
        DarnUtilities.extra_field_check(format_fields, record, rec_num)
        DarnUtilities.incorrect_types_check(format_fields, record, rec_num)
        self.__dmap_records.append(record)

    def _read_darn_records(self, file_struct_list: List[dict]):
        rec_num = 0  # record number, for exception info
        while self.cursor < self.dmap_end_bytes:
            self._read_darn_record(rec_num, file_struct_list)
            rec_num += 1

    def read_iqdat(self):
        file_struct_list = [superdarn_formats.Iqdat.types]
        self._read_darn_records(file_struct_list)
        return self.__dmap_records

    def read_rawacf(self):
        file_struct_list = [superdarn_formats.Rawacf.types]
        self._read_darn_records(file_struct_list)
        return self.__dmap_records

    def read_fitacf(self):
        file_struct_list = [superdarn_formats.Fitacf.types]
        self._read_darn_records(file_struct_list)
        return self.__dmap_records

    def read_grid(self):
        file_struct_list = [superdarn_formats.Grid.types]
        self._read_darn_records(file_struct_list)
        return self.__dmap_records

    def read_map(self):
        file_struct_list = [superdarn_formats.Map.types]
        self._read_darn_records(file_struct_list)
        return self.__dmap_records


class DarnWrite(DmapWrite):
    def __init__(self, dmap_records: List[dict] = [], filename: str = ""):
        DmapWrite.__init__(dmap_records, filename)

    def write_iqdat(self, filename: str = ""):
        """
        Writes SuperDARN file type IQDAT

        Parameters:
        -----------
        filename : str
            The name of the IQDAT file including path


        Raises:
        -------
        superDARNFieldExtra - if there is an extra field
        SuperDARNFieldMissing - if there is an missing field
        SuperDARNFormatError - if there is a formatting error
                               like an incorrect data type format

        See Also:
        ---------
        extra_field_check
        missing_field_check
        superdarn_formats.Iqdat - module contain the data types
                                 in each SuperDARN files types
        """
        self.__filename_check(filename)
        self.__empty_record_check()
        file_struct_list = [superdarn_formats.Iqdat.types]
        self.superDARN_file_structure_to_bytes(file_struct_list)
        with open(self.filename, 'wb') as f:
            f.write(self.dmap_bytearr)

    def write_iqdat_stream(self, iqdat_data: List[dict] = []) -> bytearray:
        if iqdat_data != []:
            self.dmap_records = iqdat_data
        self.__empty_record_check()
        file_struct_list = [superdarn_formats.Iqdat.types]
        self.superDARN_file_structure_to_bytes(file_struct_list)
        return self.dmap_bytearr

    def write_rawacf(self, filename: str = ""):
        """
        Writes SuperDARN file type RAWACF

        Parameters:
        -----------
        filename : str
            The name of the RAWACF file including path


        Raises:
        -------
        superDARNFieldExtra - if there is an extra field
        SuperDARNFieldMissing - if there is an missing field
        SuperDARNFormatError - if there is a formatting error
                               like an incorrect data type format

        See Also:
        ---------
        extra_field_check
        missing_field_check
        superdarn_formats.Rawacf - module contain the data types
                                 in each SuperDARN files types
        """
        self.__filename_check(filename)
        self.__empty_record_check()
        file_struct_list = [superdarn_formats.Rawacf.types]
        self.superDARN_file_structure_to_bytes(file_struct_list)
        with open(self.filename, 'wb') as f:
            f.write(self.dmap_bytearr)

    def write_rawacf_stream(self, rawacf_data: List[dict] = []) -> bytearray:
        if rawacf_data != []:
            self.dmap_records = rawacf_data
        self.__empty_record_check()
        file_struct_list = [superdarn_formats.Rawacf.types]
        self.superDARN_file_structure_to_bytes(file_struct_list)
        return self.dmap_bytearr

    def write_fitacf(self, filename=""):
        """
        Writes SuperDARN file type FITACF

        Parameters:
        -----------
        filename : str
            The name of the FITACF file including path


        Raises:
        -------
        superDARNFieldExtra - if there is an extra field
        SuperDARNFieldMissing - if there is an missing field
        SuperDARNFormatError - if there is a formatting error
                               like an incorrect data type format

        See Also:
        ---------
        extra_field_check
        missing_field_check
        superdarn_formats.Fitacf - module contain the data types
                                 in each SuperDARN files types
        """
        self.__filename_check(filename)
        self.__empty_record_check()
        file_struct_list = [superdarn_formats.Fitacf.types]
        self.superDARN_file_structure_to_bytes(file_struct_list)
        with open(self.filename, 'wb') as f:
            f.write(self.dmap_bytearr)

    def write_fitacf_stream(self, fitacf_data: List[dict] = []) -> bytearray:
        if fitacf_data != []:
            self.dmap_records = fitacf_data
        self.__empty_record_check()
        file_struct_list = [superdarn_formats.Fitacf.types]
        self.superDARN_file_structure_to_bytes(file_struct_list)
        return self.dmap_bytearr

    def write_grid(self, filename=""):
        """
        Writes SuperDARN file type GRID

        Parameters:
        -----------
        filename : str
            The name of the GRID file including path


        Raises:
        -------
        superDARNFieldExtra - if there is an extra field
        SuperDARNFieldMissing - if there is an missing field
        SuperDARNFormatError - if there is a formatting error
                               like an incorrect data type format

        See Also:
        ---------
        extra_field_check
        missing_field_check
        superdarn_formats.Grid - module contain the data types
                                 in each SuperDARN files types
        """
        self.__filename_check(filename)
        self.__empty_record_check()
        # Grid files can have extra fields based on how they are processed.
        # If the command line option used in make_grid (See RST documentation)
        # uses the command line option -ext then power and
        # spectral width fields are included as well.
        file_struct_list = [superdarn_formats.Grid.types,
                            superdarn_formats.Grid.extra_fields]
        self.superDARN_file_structure_to_bytes(file_struct_list)
        with open(self.filename, 'wb') as f:
            f.write(self.dmap_bytearr)

    def write_grid_stream(self, grid_data: List[dict] = []) -> bytearray:
        if grid_data != []:
            self.dmap_records = grid_data
        self.__empty_record_check()
        # Grid files can have extra fields based on how they are processed.
        # If the command line option used in make_grid (See RST documentation)
        # uses the command line option -ext then power and
        # spectral width fields are included as well.
        file_struct_list = [superdarn_formats.Grid.types,
                            superdarn_formats.Grid.extra_fields]
        self.superDARN_file_structure_to_bytes(file_struct_list)
        return self.dmap_bytearr

    def write_map(self, filename=""):
        """
        Writes SuperDARN file type MAP

        Parameters:
        -----------
        filename : str
            The name of the MAP file including path


        Raises:
        -------
        superDARNFieldExtra - if there is an extra field
        SuperDARNFieldMissing - if there is an missing field
        SuperDARNFormatError - if there is a formatting error
                               like an incorrect data type format

        See Also:
        ---------
        extra_field_check
        missing_field_check
        superdarn_formats.Map - module contain the data types
                                 in each SuperDARN files types
        """
        self.__filename_check(filename)
        self.__empty_record_check()
        # Map files can have extra fields based on how they are processed.
        # If the command line option map_grid -ext (See RST documentation) is
        # used then power and spectral width is included into the fields.
        # Other fields are also included on which map_add<methods> are used on
        # the map file processing.
        file_struct_list = [superdarn_formats.Map.types,
                            superdarn_formats.Map.extra_fields,
                            superdarn_formats.Map.fit_fields,
                            superdarn_formats.Map.model_fields,
                            superdarn_formats.Map.hmb_fields]
        self.superDARN_file_structure_to_bytes(file_struct_list)
        with open(self.filename, 'wb') as f:
            f.write(self.dmap_bytearr)

    def write_map_stream(self, map_data: List[dict] = []) -> bytearray:
        if map_data != []:
            self.dmap_records = map_data
        self.__empty_record_check()
        # Map files can have extra fields based on how they are processed.
        # If the command line option map_grid -ext (See RST documentation) is
        # used then power and spectral width is included into the fields.
        # Other fields are also included on which map_add<methods> are used on
        # the map file processing.
        file_struct_list = [superdarn_formats.Map.types,
                            superdarn_formats.Map.extra_fields,
                            superdarn_formats.Map.fit_fields,
                            superdarn_formats.Map.model_fields,
                            superdarn_formats.Map.hmb_fields]
        self.superDARN_file_structure_to_bytes(file_struct_list)
        return self.dmap_bytearr

    def superDARN_file_structure_to_bytes(self, file_struct_list: List[dict]):
        # TODO: might make rec_num a field in the class as it may be
        # useful in error messages for both DmapRead and DmapWrite
        for rec_num in range(len(self.dmap_records)):
            record = self.dmap_records[rec_num]
            # field checks
            self.extra_field_check(file_struct_list, record, rec_num)
            self.missing_field_check(file_struct_list, record, rec_num)
            self.incorrect_types_check(file_struct_list, record, rec_num)
            # start converting
            self.__dmap_record_to_bytes(record)
