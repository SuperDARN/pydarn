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
Persistent real-time methods
    methods that can be called repetitively for reading and writing
    to a data stream that would be used in real-time feeds.
Organization
    rethink public and private methods? <--- discussion
Parallelization

Notes
-----
DmapRead and DmapWrite are inherited by DarnRead and DarnWrite
"""
from typing import Union, List
import logging

from pydarn import superdarn_exceptions, DmapRead, DmapWrite, superdarn_formats

pydarn_log = logging.getLogger('pydarn')


class DarnUtilities():
    """
    Utility class that contains static methods that does dictionary set
    calculations used for determining if there is any missing or extra
    fields in superDARN file types. Also, does data format type checks
    for SuperDARN file types.

    Static Methods
    ----------------
        dict_key_diff(dict1, dict2)
            Returns a set of the difference between dict1 and dict2 keys
        missing_field_check(file_struct_list, record, rec_num)
            Checks if there is any missing fields in the record from
            a list of possible file fields
        extra_field_check(file_struct_list, record, rec_num)
            Checks if there is any extra fields in the record from
            a list of possible file fields
        incorrect_types_check(file_struct_list, record)
            Checks if there is any incorrect types in the record from
            a list of possible file
            fields and their data type formats
        dict_list2set(dict_list)
            Converts a list of dictionaries to a set containing their keys

    Future Work:
        Add utilities for converting DMAP records to dictionaries containing
        only the values and dictionaries to DMAP records.

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
            diff_fields = \
                DarnUtilities.dict_key_diff(file_struct,
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
    def incorrect_types_check(file_struct_list: List[dict], record: dict,
                              rec_num: int):
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
            raise superdarn_exceptions.SuperDARNDataFormatTypeError(incorrect_types_check,
                                                                    rec_num)


class DarnRead(DmapRead):
    """
    Reading and testing the integrity of SuperDARN file/stream types.
    Currently support file types are:
        Iqdat
        Rawacf
        Fitacf
        Grid
        Map
    ...

    Attributes
    ----------
    filename : str
        DMAP file name or data stream (give data_stream=True)
    cursor : int
        Current position in the byte array
    dmap_end_bytes : int
        The length of the byte array
    rec_num : int
        The record number in the DMAP format, helps with better error messages

    Methods
    -------
    read_iqdat()
        reads and checks iqdat DMAP binary data
    read_rawacf()
        reads and checks rawacf DMAP binar data
    read_fitacf()
        reads and checks fitacf DMAP binary data
    read_grid()
        reads and checks grid DMAP binary data
    read_map()
        reads and checks map DMAP binary data

    See Also
    --------
    DmapRead
        Class it inherits from
    read_records()
        reads DMAP binary data
    """
    def __init__(self, filename: str, stream: bool = False):
        """
        Extension of DmapRead constructor that reads SuperDARN file/stream type
        into a byte array for reading methods.

        Parameters
        ----------
        filename : str or bytes
            file name or data stream (given data_stream=True)
            containing dmap data.
        stream : bool
            default to false, boolean that indicates if dmap_file is a
            data stream

        Raises
        ------
        EmptyFileError
            dmap_file is empty
        FileNotFoundError
            dmap_file path does not exist

        See Also
        --------
        DmapRead : for inheritance information
        """
        DmapRead.__init__(self, filename, stream)

    # helper function that could be used parallelization
    def _read_darn_record(self, format_fields: List[dict]):
        """
        Read SuperDARN DMAP records from the DMAP byte array. Several SuperDARN
        field checks are done to insure the integrity of the file.

        Parameters
        ----------
        format_fields : List[dict]
            Is a list of dictionaries for the fields that are possible in a
            SuperDARN file type

        Raises:
        -------
        SuperDARNFieldMissingError - when a field is missing from the SuperDARN
                                file/stream type
        SuperDARNExtraFieldError - when an extra field is present in the
                                SuperDARN file/stream type
        SuperDARNDataFormatTypeError - when a field has the incorrect
                                field type for the SuperDARN file/stream type

        See Also
        --------
        read_record() - inherited from DmapRead
        """
        record = self.read_record()
        DarnUtilities.missing_field_check(format_fields, record, self.rec_num)
        DarnUtilities.extra_field_check(format_fields, record, self.rec_num)
        DarnUtilities.incorrect_types_check(format_fields, record, self.rec_num)
        self._dmap_records.append(record)

    def _read_darn_records(self, format_fields: List[dict]):
        """
        loops over the bytes in the in the SuperDARN byte array and
        calls the helper method read the SuperDARN records from the file/stream

        Parameters
        ----------
        format_fields : List[dict]
            Is a list of dictionaries for the fields that are possible in a
            SuperDARN file type

        See Also
        --------
        _read_darn_record
        """
        self.rec_num = 0  # record number, for exception info
        while self.cursor < self.dmap_end_bytes:
            self._read_darn_record(format_fields)
            self.rec_num += 1

    def read_iqdat(self) -> List[dict]:
        """
        Reads iqdat DMAP file/stream

        Returns
        -------
        dmap_records : List[dict]
            DMAP record of the Iqdat data
        """
        pydarn_log.debug("Reading Iqdat file: {}".format(self.dmap_file))
        file_struct_list = [superdarn_formats.Iqdat.types]
        self._read_darn_records(file_struct_list)
        return self._dmap_records

    def read_rawacf(self) -> List[dict]:
        """
        Reads Rawacf DMAP file/stream

        Returns
        -------
        dmap_records : List[dict]
            DMAP record of the Rawacf data
        """
        pydarn_log.debug("Reading Rawacf file: {}".format(self.dmap_file))

        file_struct_list = [superdarn_formats.Rawacf.types]
        self._read_darn_records(file_struct_list)
        return self._dmap_records

    def read_fitacf(self) -> List[dict]:
        """
        Reads Fitacf DMAP file/stream

        Returns
        -------
        dmap_records : List[dict]
            DMAP record of the Fitacf data
        """
        pydarn_log.debug("Reading Fitacf file: {}".format(self.dmap_file))
        file_struct_list = [superdarn_formats.Fitacf.types,
                            superdarn_formats.Fitacf.fitted_fields]
        self._read_darn_records(file_struct_list)
        return self._dmap_records

    def read_grid(self) -> List[dict]:
        """
        Reads Grid DMAP file/stream

        Returns
        -------
        dmap_records : List[dict]
            DMAP record of the Grid data
        """
        pydarn_log.debug("Reading Grid file: {}".format(self.dmap_file))
        file_struct_list = [superdarn_formats.Grid.types,
                            superdarn_formats.Grid.fitted_fields,
                            superdarn_formats.Grid.extra_fields]
        self._read_darn_records(file_struct_list)
        return self._dmap_records

    def read_map(self) -> List[dict]:
        """
        Reads Map DMAP file/stream

        Returns
        -------
        dmap_records : List[dict]
            DMAP record of the Map data
        """
        pydarn_log.debug("Reading Map file: {}".format(self.dmap_file))
        file_struct_list = [superdarn_formats.Map.types,
                            superdarn_formats.Map.extra_fields,
                            superdarn_formats.Map.fit_fields,
                            superdarn_formats.Map.hmb_fields,
                            superdarn_formats.Map.model_fields]
        self._read_darn_records(file_struct_list)
        return self._dmap_records


class DarnWrite(DmapWrite):
    """
    Writes Dmap records to file or stream and writes SuperDARN file format.
    ...

    Attributes
    -----------
    dmap_records : List[dict]
        List of dmap records
    filename : str
        Name of the file the user wants to write to
    dmap_bytearr : bytearray
        Byte array representing the dmap records in bytes

    Methods
    -------
    write_iqdat(filename)
        Writes dmap records to SuperDARN IQDAT file structure
        with the given filename
    write_fitacf(filename)
        Write dmap records to SuperDARN RAWACF file structure
        with the given filename
    write_rawacf(filename)
        Writes dmap records to SuperDARN FITACF file structure
        with the given filename
    write_grid(filename)
        Writes dmap records to SuperDARN GRID file structure
        with the given filename
    write_map(filename)
        Writes dmap records to SuperDARN MAP file structure
        with the given filename
    SuperDARN_file_structure_to_bytes(file_struct_list)
        Converts dmap records to SuperDARN file structure bytes based
        on file_struct_list

    See Also
    --------
    DmapWrite
        class DarnWrite inherits from
    dmap_scalar_to_bytes(scalar)
        Converts a DmapScalar to bytes
    dmap_array_to_bytes(array)
        Converts a DmapArray to bytes
    """

    def __init__(self, dmap_records: List[dict] = [], filename: str = ""):
        """
        Inherits from DmapWrite class and checks the data record is not empty.
        This check will be taken out when real-time is implemented.

        Parameters
        ----------
        dmap_records : List[dict]
            List of dmap records
        filename : str
            Name of the file the user wants to write to
        """
        DmapWrite.__init__(self, dmap_records, filename)

        # WARNING: This check will be removed when real-time is implemented to
        # allow for constantly updating data from a processing data feed
        self._empty_record_check()

    def write_iqdat(self, filename: str = ""):
        """
        Writes SuperDARN file type IQDAT

        Parameters:
        -----------
        filename : str
            The name of the IQDAT file including path


        Raises:
        -------
        superDARNExtraFieldError - if there is an extra field
        SuperDARNFieldMissingError- if there is an missing field
        SuperDARNDataFormatTypeError - if there is a formatting error
                               like an incorrect data type format

        See Also:
        ---------
        extra_field_check
        missing_field_check
        superdarn_formats.Iqdat - module contain the data types
                                 in each SuperDARN files types
        """
        self._filename_check(filename)
        self._empty_record_check()
        pydarn_log.debug("Writing Iqdat file: {}".format(self.filename))

        file_struct_list = [superdarn_formats.Iqdat.types]
        self.superDARN_file_structure_to_bytes(file_struct_list)
        with open(self.filename, 'wb') as f:
            f.write(self.dmap_bytearr)

    def write_rawacf(self, filename: str = ""):
        """
        Writes SuperDARN file type RAWACF

        Parameters:
        -----------
        filename : str
            The name of the RAWACF file including path


        Raises:
        -------
        superDARNExtraFieldError - if there is an extra field
        SuperDARNFieldMissingError- if there is an missing field
        SuperDARNDataFormatTypeError - if there is a formatting error
                               like an incorrect data type format

        See Also:
        ---------
        extra_field_check
        missing_field_check
        superdarn_formats.Rawacf - module contain the data types
                                 in each SuperDARN files types
        """
        pydarn_log.debug("Writing Rawacf file: {}".format(self.filename))
        self._filename_check(filename)
        self._empty_record_check()
        file_struct_list = [superdarn_formats.Rawacf.types]
        self.superDARN_file_structure_to_bytes(file_struct_list)
        with open(self.filename, 'wb') as f:
            f.write(self.dmap_bytearr)

    def write_fitacf(self, filename: str = ""):
        """
        Writes SuperDARN file type FITACF

        Parameters:
        -----------
        filename : str
            The name of the FITACF file including path


        Raises:
        -------
        superDARNExtraFieldError - if there is an extra field
        SuperDARNFieldMissingError- if there is an missing field
        SuperDARNDataFormatTypeError - if there is a formatting error
                               like an incorrect data type format

        See Also:
        ---------
        extra_field_check
        missing_field_check
        superdarn_formats.Fitacf - module contain the data types
                                 in each SuperDARN files types
        """
        pydarn_log.debug("Writing Fitacf file: {}".format(self.filename))

        self._filename_check(filename)
        self._empty_record_check()
        file_struct_list = [superdarn_formats.Fitacf.types,
                            superdarn_formats.Fitacf.fitted_fields]
        self.superDARN_file_structure_to_bytes(file_struct_list)
        with open(self.filename, 'wb') as f:
            f.write(self.dmap_bytearr)

    def write_grid(self, filename: str = ""):
        """
        Writes SuperDARN file type GRID

        Parameters:
        -----------
        filename : str
            The name of the GRID file including path


        Raises:
        -------
        superDARNExtraFieldError - if there is an extra field
        SuperDARNFieldMissingError- if there is an missing field
        SuperDARNDataFormatTypeError - if there is a formatting error
                               like an incorrect data type format

        See Also:
        ---------
        extra_field_check
        missing_field_check
        superdarn_formats.Grid - module contain the data types
                                 in each SuperDARN files types
        """
        pydarn_log.debug("Writing Grid file: {}".format(self.filename))

        self._filename_check(filename)
        self._empty_record_check()
        # Grid files can have extra fields based on how they are processed.
        # If the command line option used in make_grid (See RST documentation)
        # uses the command line option -ext then power and
        # spectral width fields are included as well.
        file_struct_list = [superdarn_formats.Grid.types,
                            superdarn_formats.Grid.fitted_fields,
                            superdarn_formats.Grid.extra_fields]
        self.superDARN_file_structure_to_bytes(file_struct_list)
        with open(self.filename, 'wb') as f:
            f.write(self.dmap_bytearr)

    def write_map(self, filename: str = ""):
        """
        Writes SuperDARN file type MAP

        Parameters:
        -----------
        filename : str
            The name of the MAP file including path


        Raises:
        -------
        superDARNExtraFieldError - if there is an extra field
        SuperDARNFieldMissingError- if there is an missing field
        SuperDARNDataFormatTypeError - if there is a formatting error
                               like an incorrect data type format

        See Also:
        ---------
        extra_field_check
        missing_field_check
        superdarn_formats.Map - module contain the data types
                                 in each SuperDARN files types
        """
        pydarn_log.debug("Writing Map file: {}".format(self.filename))

        self._filename_check(filename)
        self._empty_record_check()
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

    def superDARN_file_structure_to_bytes(self, file_struct_list: List[dict]):
        """
        Checks the DMAP records are the correct structure of the file type and
        then uses the DmapWrite writing method to covert the record to bytes.

        Parameters
        ----------
        file_struct_list : List[dict]
        A list of possible fields for the given SuperDARN file type

        Raises
        ------
        SuperDARNFieldMissingError - Missing fields in the DMAP record that is
        required for the SuperDARN file type
        SuperDARNExtraFieldError - Extra fields in the DMAP record that are not
        allowed in the SuperDARN file type
        SuperDARNDataFormatTypeError - Wrong format data type error for the
        SuperDARN file type fields in the DMAP record
        """
        self.rec_num = 0
        pydarn_log.debug("Checking and converting SuperDARN data to bytes ")

        for self.rec_num in range(len(self.dmap_records)):
            record = self.dmap_records[self.rec_num]
            # field checks
            DarnUtilities.extra_field_check(file_struct_list, record,
                                            self.rec_num)
            DarnUtilities.missing_field_check(file_struct_list, record,
                                              self.rec_num)
            DarnUtilities.incorrect_types_check(file_struct_list, record,
                                                self.rec_num)
            # start converting
            self._dmap_record_to_bytes(record)
