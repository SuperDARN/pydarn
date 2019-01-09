# Copyright 2018 SuperDARN
# Authors: Marina Schmidt and Keith Kotyk
"""
This file contains classes to reading and writing of DMAP file formats used by
SuperDARN.

Classes:
--------
DmapRead : Reads DMAP files
DmapWrite : writes DMAP Record structure into a DMAP file

Exceptions:
-----------
EmptyFileError
CursorError
DmapDataError
DmapDataTypeError
ZeroByteError
MismatchByteError
ValueError

Future work
-----------
logger improvement
    time performance can improve if we turn off the logger
DmapWrite cleanup
    updating and improving DmapWrite
Date stream reading/writing
    add the ability to read/write from data streams <-- this may be working but
                                                        not tested well
Organization
    rethink public and private methods? <--- discussion

Notes
-----
DmapRead and DmapWrite are updated and improved versions of
backscatter's pydmap:
git@github.com:SuperDARNCanada/backscatter.git
written by Keith Kotyk
"""

import os
import struct
import numpy as np
import logging
import collections

from pydarn import pydmap_exceptions

from pydarn import DmapArray
from pydarn import DmapScalar

# Keeping these global definitions for readability purposes
# Data types use in DMAP files
DMAP = 0
CHAR = 1
SHORT = 2
INT = 3
FLOAT = 4
DOUBLE = 8
STRING = 9
LONG = 10
UCHAR = 16
USHORT = 17
UINT = 18
ULONG = 19

# Dictionary of DMAP types (key) to quickly convert the format and byte size
# (value-tuple)
DMAP_DATA_TYPES = {DMAP: ('', 0),
                   CHAR: ('c', 1),
                   SHORT: ('h', 2),
                   INT: ('i', 4),
                   FLOAT: ('f', 4),
                   DOUBLE: ('d', 8),
                   STRING: ('s', 1),
                   LONG: ('q', 8),
                   UCHAR: ('B', 1),
                   USHORT: ('H', 2),
                   UINT: ('I', 4),
                   ULONG: ('Q', 8)}

pydarn_logger = logging.getLogger('pydarn')

class DmapRead():
    """
    Reading and testing the integrity of DMAP files/stream.
    ...

    Attributes
    ----------
    dmap_file : str
        DMAP file name or data stream (give data_stream=True)
    cursor : int
        Current position in the byte array
    dmap_end_bytes : int
        The length of the byte array

    Methods
    --------
    test_initial_data_integrity()
        Quickly reads the byte array for any errors
    read_records()
        Reads the byte array to obtain the DMAP records
    zero_negative_check(element, element_name)
        Checks if the element is equal to zero
    check_data_type(data_type, data_name)
        Checks if the data_type exists in DMAP_DATA_TYPE dictionary
    read_record()
        Reads a record from the byte array
    read_scalar()
        Reads a scalar from the byte array
    read_array(record_size)
        Reads an array from the byte array
    read_string_DMAP_array(Shape, array_type)
        Reads an array of strings/DMAP types into an array
    read_data()
        Reads the data type from the byte array
    read_numerical_array(data_type, shape, total_number_cells)
        Reads an array into a numpy array
    """

    def __init__(self, dmap_file: str, data_stream=False):
        """
        Reads the dmap file/stream into a byte array for further reading of the
        dmap records.

        Parameters
        ----------
        dmap_file : str
                    file name or data stream (given data_stream=True)
                    containing dmap data.
        data_stream : bool
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
        read_records : to obtain dmap_records
        """

        self.cursor = 0  # Current position in bytes
        self.dmap_end_bytes = 0  # total number of bytes in the dmap_file

        """
        Dmap records are stored in a deque data structure for
        memory efficiency and performance. Acts the same as a stack/list.
        See DEVELOPER_README.md for more information.
        """

        # __dmap_records are private to avoid tampering.
        self.__dmap_records = collections.deque()
        self.dmap_file = dmap_file

        # read the whole file/stream into a byte array
        if data_stream is False:
            # check if the file is empty
            if os.path.getsize(self.dmap_file) == 0:
                raise pydmap_exceptions.EmptyFileError(self.dmap_file)

            # Read binary dmap file
            with open(self.dmap_file, 'rb') as f:
                self.dmap_bytearr = bytearray(f.read())
            pydarn_logger.debug("DMAP Read file: {}".format(self.dmap_file))

        else:
            if len(dmap_file) == 0:
                raise pydmap_exceptions.EmptyFileError("data stream")

            self.dmap_bytearr = bytearray(self.dmap_file)
            self.dmap_file = "stream"
            pydarn_logger.debug("DMAP Read file: Stream")
        self.dmap_buffer = memoryview(self.dmap_bytearr)
        self.dmap_end_bytes = len(self.dmap_bytearr)
        if self.dmap_end_bytes == 0:
            raise pydmap_exceptions.EmptyFileError(self.dmap_file)

    def zero_negative_check(self, element: int, element_name: str):
        """
        Checks if the element <= 0 bytes. If true then raise a ZeroByteError.

        Parameter
        ---------
        element : int
            An element to check if it is zero
        element_name : str
            The element's name title for a more detailed exception message

        Raises
        ------
        ZeroByteError
            if element <= 0
        """

        if element == 0:
            element_info = "{name} {size}".format(name=element_name,
                                                  size=element)
            raise pydmap_exceptions.ZeroByteError(self.dmap_file, element_info,
                                                  self.cursor)
         elif element < 0:
            element_info = "{name} {size}".format(name=element_name,
                                                  size=element)
            raise pydmap_exceptions.NegativeByteError(self.dmap_file, element_info,
                                                  self.cursor)


    def bytes_check(self, element: int, element_name: str, byte_check: int,
                    byte_check_name: str):
        """
        Checks if the element greater than the value comparing against
        (byte_check).

        Parameter
        ---------
        element : int
            An element to check if it is greater than another value in bytes
        element_name : str
            Name of the element for a more detailed exception message
        byte_check : int
            The byte value for the element to compare against
        byte_check_name : str
            Name of the byte value to be compared too for a more detailed
            exception message

        Raises
        ------
        MismatchByteError
             if element > byte_check
        """
        if element > byte_check:
            element_info = "{name} {size} >"\
                    " {check_name} {check}".format(name=element_name,
                                                   size=element,
                                                   check_name=byte_check_name,
                                                   check=byte_check)
            raise pydmap_exceptions.MismatchByteError(self.dmap_file,
                                                      element_info,
                                                      self.cursor)

    def check_data_type(self, data_type: int, data_name: str):
        """
        Check if the data_type is a DMAP data type.

        Parameter
        ----------
        data_type : int
            Data_type read in by the byte array
        data_name : str
            Name of the data trying to read in

        Raises
        -------
        DmapDataTypeError
            if the data_type is not in the DMAP_DATA_TYPES dictionary
        """
        if data_type not in DMAP_DATA_TYPES.keys():
            raise pydmap_exceptions.DmapDataTypeError(self.dmap_file,
                                                      data_name,
                                                      data_type,
                                                      self.cursor)

    def test_initial_data_integrity(self):
        """
        Quick method for testing the integrity of the dmap data.

        Raises
        ------
        CursorError
            If the cursor is not set to an expected value.
        DmapDataError
            If the data is corrupted by some byte offset.

        See Also
        --------
        zero_check : raises ZeroByteError
        byte_check : raises MistmatchByteError
        """
        pydarn_logger.debug("Testing the integrity of the dmap file/stream")
        total_block_size = 0  # unit of bytes
        if self.cursor != 0:
            raise pydmap_exceptions.CursorError(self.cursor, 0)

        while self.cursor < self.dmap_end_bytes:
            """
            DMAP files headers contain the following:
                - encoding identifier: is a unique 32-bit integer that
                  indicates how the block was constructed.
                  It is used to differentiate between the possible future
                  changes to the DataMap format.
                - block size: 32-bit integer that represents the total size of
                  block including the header and the data.
                - Number of Scalars: number of scalar variables
                - Scalar data: the scalar data of the record.
                  Please see DmapScalar for more information on scalars.
                - Number of arrays: number of array variables
                  Please see DmapArray for more information on arrays.
            """
            # This is an unused variable but is need to move the cursor to the
            # next offset.
            # TODO: Possible check that uses the encoding identifier
            # encoding_identifier = self.read_data('i',4)
            self.cursor += 4
            block_size = self.read_data('i',4)
            self.zero_negative_check(block_size, "block size")

            total_block_size += block_size
            self.bytes_check(total_block_size, "total block size",
                             self.dmap_end_bytes, "total bytes in file")

            # 2 is to include the encoding_identifier and size of data which
            # are both int types.
            self.cursor = self.cursor + block_size - 2 * DMAP_DATA_TYPES[INT][1]

        if total_block_size != self.dmap_end_bytes:
            message = "Error: Initial integrity check shows"\
                    " total block size: {total_size} < end bytes {end_bytes}."\
                    " Cursor: {cursor}."\
                    " Data is likely corrupted"\
                    "".format(total_size=total_block_size,
                              end_bytes=self.dmap_end_bytes,
                              cursor=self.cursor)
            raise pydmap_exceptions.DmapDataError(self.date_file, message)
        self.cursor = 0

    def read_records(self) -> collections.deque:
        """
        This method reads the records from the dmap file/stream passed
        into the instance.


        Return
        -------
        __dmap_records : collections.Deque
                Deque list of DmapRecords (ordered dictionary)


        See Also
        --------
        DmapRecord : dmap record's data structure
        DmapScalar : dmap record's scalar data structure
        DmapArray  : dmap record's array data structure

        See DEVELOPER_README.md for more information DmapRecords data structure.
        """

        # read bytes until end of byte array
        pydarn_logger.debug("Reading DMAP records")
        while self.cursor < self.dmap_end_bytes:
            new_record = self.read_record()
            self.__dmap_records.append(new_record)

        self.bytes_check(self.cursor, "cursor",
                         self.dmap_end_bytes, "total bytes in the file")
        return self.__dmap_records

    def read_record(self) -> collections.OrderedDict:
        """
        Reads a single dmap record from the byte array.

        Return
        ------
        Ordered dict:
                Ordered dictionary containing DmapScalars and DmapArrays from
                a dmap array. The key is the name of the scalar/array and
                value is the DmapScalar/DmapArray data structure

        Raises
        ------
        CursorError
           if the beginning value of the cursor -
           the current position != block size

        See Also
        --------
        read_scalar : reads dmap scalars to be stored in the record
        read_array : reads dmap arrays to be stored in the record
        """
        # used in a cursor check.
        start_cursor_value = self.cursor

        # Need to get encoder for cursor movement though it is not moved.
        #encoding_identifier = self.read_data('i',4)
        # WARNING: normally would call encoding_identifier but since it is not
        # used the extra function call is point less so best just to move the
        # cursor for performance :)
        self.cursor += 4
        block_size = self.read_data('i',4)

        pydarn_logger.debug("Reading Record {record}"
                            .format(record=len(self.__dmap_records)))

        # adding 8 bytes because code+size are part of the record.
        # 4 is the number bytes for int format
        remaining_bytes = self.dmap_end_bytes - self.cursor + 2 * DMAP_DATA_TYPES[INT][1]
        self.bytes_check(block_size, "block size",
                         remaining_bytes, "remaining bytes")
        self.zero_negative_check(block_size, "block size")

        num_scalars = self.read_data('i', 4)
        num_arrays = self.read_data('i', 4)

        self.zero_negative_check(num_scalars, "number of scalars")
        self.zero_negative_check(num_arrays, "number of arrays")
        self.bytes_check(num_scalars + num_arrays,
                         "number of scalars + arrays",
                         block_size, "block size")

        pydarn_logger.debug("Reading record: reading scalars\n")
        # originally called DmapRecord but then was just returning the ordered dict
        # thus I am constructing it here instead for better speed performance.
        record = collections.OrderedDict()
        for i in range(num_scalars):
            scalar = self.read_scalar()
            record[scalar.name] = scalar

        pydarn_logger.debug("Reading record: reading arrays\n")
        for i in range(num_arrays):
            array = self.read_array(block_size)
            record[array.name] = array

        # check for a cursor error
        if (self.cursor - start_cursor_value) != block_size:
            raise pydmap_exceptions.CursorError(self.cursor, block_size)

        return record

    def read_scalar(self) -> DmapScalar:
        """
        Reads a scalar and stores the properties into a namedtuple DmapScalar.

        Return
        ------
        DmapScalar: namedtuple
            data structure that contains the data properties of
            the scalar read in

        Raises
        ------
        DmapDataError
            if the data type format is DMAP
            NOTE: In RST, this is allowed, if an example shows up where this is
            allowed DMAP files raise as an issue in the GitHub so the code can
            be re-accessed.

        See Also
        --------
        check_data_type : for other possible raised exceptions
        read_data : reads the data stored in the byte array
        """

        scalar_name = self.read_data('s', 1)
        scalar_type = self.read_data('c', 1)

        self.check_data_type(scalar_type, scalar_name)

        scalar_type_fmt = DMAP_DATA_TYPES[scalar_type][0]
        scalar_fmt_byte = DMAP_DATA_TYPES[scalar_type][1]

        if scalar_type_fmt != DMAP:
            scalar_value = self.read_data(scalar_type_fmt, scalar_fmt_byte)
        else:
            message = "Error: Trying to read DMAP data type for a scalar."\
                    " cursor at {}".format(self.cursor)
            # Not sure when this is used in a dmap file
            # so better to raise an error if used re-access the code.
            raise pydmap_exceptions.DmapDataError(self.dmap_file, message)

        return DmapScalar(scalar_name, scalar_value, scalar_type)

    def read_array(self, record_size) -> DmapArray:
        """
        Reads an array from a dmap record the byte arrays and
        stores the data properties in a DmapArray structure.

        Return
        ------
        DmapArray : namedtuple
             data structure that contains the data properties of
             the array read in.

        Raises
        -------
            DmapDataError
                if the array properties (like a dimension size == 0)
                are incorrect.

        See Also
        --------
        read_data : reads the data in the byte array
        read_numerical_array : reads in a numerical array from the byte array
        read_string_array: reads in a string/DMAP array
        """
        array_name = self.read_data('s', 1)
        array_type = self.read_data('c', 1)

        self.check_data_type(array_type, array_name)

        array_type_fmt = DMAP_DATA_TYPES[array_type][0]
        array_fmt_bytes = DMAP_DATA_TYPES[array_type][1]

        array_dimension = self.read_data('i', 4)
        self.bytes_check(array_dimension, "array dimension",
                         record_size, "record size")
        self.zero_negative_check(array_dimension, "array dimension")

        array_shape = [self.read_data('i', 4) for i in range(0, array_dimension)]
        array_shape.reverse()

        # if shape list is empty
        if len(array_shape) != array_dimension:
            message = "Error: Array shape {shape} could not be read."\
                    " cursor: {cursor}".format(shape=array_shape,
                                               cursor=self.cursor)
            raise pydmap_exceptions.DmapDataError(self.dmap_file, message)
        # TODO Explain where does slist come from?
        elif any(x <= 0 for x in array_shape) and array_name != "slist":
            message = "Error: Array shape {shape} contains "\
                    "dimension size <= 0."\
                    " Cursor: {cursor}".format(dim=array_shape,
                                               cursor=self.cursor)
            raise pydmap_exceptions.DmapDataError(self.filename, message)

        for i in range(array_dimension):
            if array_shape[i] >= record_size:
                message = "Error: Array {index}-dimension size {size}"\
                        " exceeds record size: {rec_size}."\
                        "".format(index=i,
                                  size=array_shape[i],
                                  rec_size=record_size)
                raise pydmap_exceptions.DmapDataError(self.dmap_file, message)

        # We could use np.prod(array_shape) but the for loop has a better
        # time performance. Note: cells can also be read as number of elements
        # depending on your background.
        total_num_cells = 1
        for i in array_shape:
            total_num_cells *= i
        self.bytes_check(total_num_cells, "total number of cells",
                         record_size, "record size")

        total_num_cells_bytes = total_num_cells * array_fmt_bytes
        self.bytes_check(total_num_cells_bytes,
                         "total number of cells in bytes",
                         record_size, "record size")

        # parsing an array of strings requires a different method. Numpy can't
        # parse strings or dmaps into arrays the way it can for other
        # types because it doesn't
        # know the sizes. They have to be manually read the slow way.
        # Because chars
        # are encoded as hex literals, they have to be read one at a
        # time to make sense.

        if array_type_fmt == 's' or array_type_fmt == 'c':
            array_value = self.read_string_array(array_shape,
                                                 array_type_fmt,
                                                 array_fmt_bytes)
        elif array_type == DMAP:
            message = "Error: Trying to read DMAP array data type."\
                    " cursor at {}".format(self.cursor)
            # Not sure when this is used in a dmap file
            # so better to raise an error if used re-access the code.
            raise pydmap_exceptions.DmapDataError(self.dmap_file, message)
        else:
            array_value = self.read_numerical_array(array_type_fmt,
                                                    total_num_cells,
                                                    array_fmt_bytes)

        return DmapArray(array_name, array_value, array_type,
                         array_dimension, array_shape)

    def read_data(self, data_type_fmt, data_fmt_bytes: int):
        """
        Reads in individual data type from the byte array
        Given a dmap data type.

        Parameter
        ---------
        data_type : int
            dmap data type numerical value for knowing how many bytes to read.

        Return
        ------
        data : data_type
            returns the data that was store in the byte array.
            Has the data type of the dmap data type passed in.

        Raises
        ------
        CursorError
            if cursor is not correctly aligned or at the correct position.
        DmapDataError
            if trying to read a DMAP data type

        See Also
        --------
        Struct.unpack : converts the bytes array values from a C structure to
        python objects

        See DEVELOPER_README.md for more information on DMAP data types and
        Struct.unpack.
        """
        if self.cursor >= self.dmap_end_bytes:
            message = "Error: Cursor {cursor} extends"\
                    " out of buffer {end_bytes}."\
                    "".format(cursor=self.cursor,
                              end_bytes=self.dmap_end_bytes)
            raise pydmap_exceptions.CursorError(self.cursor, message=message)

        cursor_offset = self.dmap_end_bytes - self.cursor
        if cursor_offset < data_fmt_bytes:
            message = "Error: Byte offsets {offset} into buffer {fmt}"\
                    " are not aligned.".format(offset=cursor_offset,
                                               fmt=data_fmt_bytes)
            raise pydmap_exceptions.CursorError(self.cursor, message=message)

        # struct.unpack is a python method the converts C struct as python bytes
        # to python values. See DEVELOPER_README.md for more information.
        # TODO: how to handle this gracefully? Return None and check later than
        #       continue in the loop?
        if data_type_fmt == 'c':
            data = self.dmap_bytearr[self.cursor]
            self.cursor += data_fmt_bytes
            return data
        elif data_type_fmt == 's':
            byte_counter = 0
            while self.dmap_bytearr[self.cursor + byte_counter] != 0 or self.cursor + byte_counter >= self.dmap_end_bytes:
                # add 1 byte to byte_counter because a string is a list of chars
                byte_counter += 1  # 1 is the number of bytes of a char
            self.bytes_check(self.cursor+byte_counter, 'cursor', self.dmap_end_bytes, 'Total number of Bytes')

            # format byte counter to a string format for unpacking
            # WARNING: not using format for performance purposes
            char_count = '%ss'%byte_counter
            data = struct.unpack_from(char_count,
                                      self.dmap_buffer,
                                      self.cursor)
            ## 1 is the number of bytes in a char
            self.cursor = self.cursor + byte_counter + 1
            return data[0].decode('utf-8')
        else:
            data = struct.unpack_from(data_type_fmt,
                                      self.dmap_buffer,
                                      self.cursor)
            self.cursor += data_fmt_bytes
            return data[0]

    def read_string_array(self, shape: list,
                          array_type_fmt: str,
                          array_fmt_bytes: int) -> np.ndarray:
        """
        Reads and builds a N-D array of string data types.

        Parameter
        ---------
        shape : list
            list of the arrays dimension size
        array_fmt_bytes : int
            String or char

        Return
        ------
        np.ndarray
            an numpy N-D array of string read in from the byte array
        """

        data = []
        # FIXME: still need to find a method for testing this... Or a file
        #        that contains a string/DMAP array
        for dim_size in shape:
            for i in range(dim_size):
                data.append(self.read_data(array_type_fmt, array_fmt_bytes))
        # try to avoid using recursion, it is slow
        # if not dim:
        #     dim_data = [self.read_data(data_type_fmt)
        #                 for i in range(0, dimension)]
        # else:
        #     dim_data = [self.build_n_dimension_list(list(dim), data_type_fmt)
        #                 for i in range(0, dimension)]
        return np.array(data)

    def read_numerical_array(self, data_type_fmt: str,
                             total_number_cells: int,
                             data_fmt_bytes: int) -> np.ndarray:
        """
        Reads in an array from the byte array into a N-D array.

        Parameter
        ---------
        shape : list
            A list of the array's dimension sizes
        data_type : int
            DMAP data type numeric value
        total_number_cells : int
            The number of cells in the N-D array being read in

        Return
        -------
        array : np.ndarray
            The numpy N-D array from the byte array

        Raises
        -------
        DmapDataError
            Mismatch on the data type and the size specified in the byte array.
        """
        array = np.frombuffer(self.dmap_buffer, data_type_fmt, total_number_cells, self.cursor)
        self.cursor += total_number_cells * data_fmt_bytes

        return array


# TODO: Clean up
class RawDmapWrite(object):
    """Contains members and methods relating to encoding dictionaries into a raw
    dmap buffer.

    The ud_types are use to override the default types for riding. Useful
    if you want to write a number as a char instead of an int for example

    """
    def __init__(self, data_dicts, file_path, ud_types={}):
        super(RawDmapWrite, self).__init__()
        self.data_dict = data_dicts
        self.records = []
        self.ud_types = ud_types
        self.dmap_bytearr = bytearray()

        for dd in data_dicts:
            self.data_dict_to_dmap_rec(dd)

        for rc in self.records:
            self.dmap_record_to_bytes(rc)

        with open(file_path, 'wb') as f:
            f.write(self.dmap_bytearr)

    def data_dict_to_dmap_rec(self, data_dict):
        """ This method converts a data dictionary to a dmap record.

        The user defined dictionary specifies if any default types are to be
        overridden with your own type. This functions runs through each key/val
        element of the dictionary and creates a DmapArray or DmapScalar
        and adds them to a RawDmapRecord. Any python lists are converted to
        numpy arrays for fast and efficient conversion to bytes

        :param data_dict: a dictionary of data to encode

        """
        record = DmapRecord()
        for name, value in data_dict.items():

            if name in self.ud_types:
                data_type_fmt = self.ud_types[name]
            else:
                data_type_fmt = self.find_datatype_fmt(value)
                if data_type_fmt == '':
                    # TODO: handle recursive dmap writing
                    # recursive is slow so we should look at other options
                    pass

            if isinstance(value, (list, np.ndarray)):
                if isinstance(value, list):
                    if data_type_fmt == 'c':
                        data = np.asarray([chr(x) for x in value], dtype='c')
                    elif data_type_fmt == 's':
                        data = np.asarray(value, dtype=object)
                    else:
                        data = np.asarray(value, dtype=data_type_fmt)
                if isinstance(value, np.ndarray):
                    if data_type_fmt == 'c' and value.dtype != 'S1':
                        data = np.asarray([chr(x) for x in value], dtype='c')
                    else:
                        data = np.asarray(value, dtype=data_type_fmt)

                dmap_type = self.convert_fmt_to_dmap_type(data_type_fmt)

                # dimensions need to be reversed to match what dmap expects
                shape = data.shape[::-1]
                dimension = len(shape)
                array = DmapArray(name, value, dmap_type,
                                  dimension, shape)
                record.add_array(array)

            else:
                dmap_type = self.convert_fmt_to_dmap_type(data_type_fmt)
                scalar = DmapScalar(name, value, dmap_type)
                record.add_scalar(scalar)

        self.records.append(record)

    def find_datatype_fmt(self, data):
        """Input could be an array of any dimensions so will recursive until
        fundamental type is found

        :param data: data for which to find its type format
        :returns: a string format identifier for the python data type

        """
        if isinstance(data, np.ndarray) or isinstance(data, list):
            return self.find_datatype_fmt(data[0])
        else:
            return self.type_to_fmt(data)

    def dmap_record_to_bytes(self, record):
        """This method converts a dmap record to the byte format
        that is written to file.

        Format is code,length of record,number of scalars,
        number of arrays, followed by
        the scalars and then the arrays

        :param record: a RawDmapRecord

        """
        scalars = record.get_scalars()
        arrays = record.get_arrays()

        code = 65537  # TODO: what is this value?
        num_scalars = record.get_num_scalars()
        num_arrays = record.get_num_arrays()

        byte_arr = bytearray()
        for sc in scalars:
            byte_arr.extend(self.dmap_scalar_to_bytes(sc))
        for ar in arrays:
            byte_arr.extend(self.dmap_array_to_bytes(ar))

        # + 16 for length,code,num scalars, and num arrays fields
        length = len(byte_arr) + 16

        code_bytes = struct.pack('i', code)
        length_bytes = struct.pack('i', length)
        num_scalars_bytes = struct.pack('i', num_scalars)
        num_arrays_bytes = struct.pack('i', num_arrays)
        self.dmap_bytearr.extend(code_bytes)
        self.dmap_bytearr.extend(length_bytes)
        self.dmap_bytearr.extend(num_scalars_bytes)
        self.dmap_bytearr.extend(num_arrays_bytes)
        self.dmap_bytearr.extend(byte_arr)

    def dmap_scalar_to_bytes(self, scalar):
        """This method converts a DmapScalar to the byte format written out.

        The bytes are written as a name, then type, then data

        :param scalar: a DmapScalar
        :returns: total bytes the scalar will take up

        """

        name = "{0}\0".format(scalar.get_name())
        struct_fmt = '{0}s'.format(len(name))
        name_bytes = struct.pack(struct_fmt, name.encode('utf-8'))
        dmap_type_bytes = struct.pack('c',
                                      chr(scalar.get_type()).encode('utf-8'))

        data_type_fmt = scalar.get_datatype_fmt()

        if data_type_fmt == 's':
            data = "{0}\0".format(scalar.get_data())
            struct_fmt = '{0}s'.format(len(data))
            data_bytes = struct.pack(struct_fmt, data.encode('utf-8'))
        elif data_type_fmt == 'c':
            data_bytes = chr(scalar.get_data()).encode('utf-8')
        else:
            data_bytes = struct.pack(data_type_fmt, scalar.get_data())

        total_bytes = name_bytes + dmap_type_bytes + data_bytes

        return total_bytes

    def dmap_array_to_bytes(self, array):
        """This method converts a DmapArray to the byte format to be written
        out.

        The format is name,then type, number of dimensions, dimensions,
        array data.

        :param array: a DmapArray
        :returns: total bytes the array will take up

        """

        name = "{0}\0".format(array.get_name())
        struct_fmt = '{0}s'.format(len(name))
        name_bytes = struct.pack(struct_fmt, name.encode('utf-8'))

        dmap_type_bytes = struct.pack('c',
                                      chr(array.get_type()).encode('utf-8'))

        dimension_bytes = struct.pack('i', array.get_dimension())
        arr_dimensions_bytes = bytes()
        for dim in array.get_arr_dimensions():
            arr_dimensions_bytes = arr_dimensions_bytes + struct.pack('i', dim)

        data_bytes = array.get_data().tostring()

        total_bytes = name_bytes + dmap_type_bytes + dimension_bytes +\
            arr_dimensions_bytes + data_bytes
        return total_bytes

    def type_to_fmt(self, data):
        """Finds data types and converts them to a format specifier for
        struct or numpy
        packing methods

        :param data: data for which to find type
        :returns: a string format identifier for the python data type

        """
        if isinstance(data, int):
            return 'i'
        elif isinstance(data, str):
            return 's'
        elif isinstance(data, float):
            return 'f'
        elif isinstance(data, np.float32):
            return 'f'
        elif isinstance(data, np.float64):
            return 'd'
        elif isinstance(data, np.char):
            return 'c'
        elif isinstance(data, np.int8):
            return 'c'
        elif isinstance(data, np.int16):
            return 'h'
        elif isinstance(data, np.int32):
            return 'i'
        elif isinstance(data, np.int64):
            return 'q'
        elif isinstance(data, np.uint8):
            return 'B'
        elif isinstance(data, np.uint16):
            return 'H'
        elif isinstance(data, np.uint32):
            return 'I'
        elif isinstance(data, np.uint64):
            return 'Q'
        else:
            return ''

    def convert_fmt_to_dmap_type(self, fmt):
        """Converts a format specifier to a dmap type to be written
        as part of buffer

        :param fmt: a string format identifier for the DMAP data type
        :returns: DMAP type

        """
        return {
                'c': CHAR,
                'h': SHORT,
                'i': INT,
                'f': FLOAT,
                'd': DOUBLE,
                's': STRING,
                'q': LONG,
                'B': UCHAR,
                'H': USHORT,
                'I': UINT,
                'Q': ULONG,
            }.get(fmt, None)


# TODO: consider removing this function and get the user to call RawDmapWrite
def dicts_to_file(data_dicts, file_path, file_type=''):
    """This function abstracts the type overrides for the main SuperDARN
    file types. These dictionaries write out the types to be compatible
    with C DMAP reading

    :param data_dicts: python dictionaries to write out
    :param file_path: path for which to write the data to file
    :param file_type: type of SuperDARN file with what the data is

    """
    # TODO: move to another file to make it shorter to search through
    # this will also clean up the file so it is nicer to look at
    rawacf_types = {
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
     'pwr0': 'f',
     'acfd': 'f',
     'xcfd': 'f',
    }

    mapfile_types = {
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
     'source': 's',
     'doping.level': 'h',
     'model.wt': 'h',
     'error.wt': 'h',
     'IMF.flag': 'h',
     'IMF.delay': 'h',
     'IMF.Bx': 'd',
     'IMF.By': 'd',
     'IMF.Bz': 'd',
     'model.angle': 's',
     'model.level': 's',
     'hemisphere': 'h',
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
     'N': 'd',
     'N+1': 'd',
     'N+2': 'd',
     'N+3': 'd',
     'model.mlat': 'f',
     'model.mlon': 'f',
     'model.kvect': 'f',
     'model.vel.median': 'f',
     'boundary.mlat': 'f',
     'boundary.mlon': 'f',
    }

    fitacf_types = {
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
     'fitacf.revision.major': 'i',
     'fitacf.revision.minor': 'i',
     'combf': 's',
     'noise.sky': 'f',
     'noise.lag0': 'f',
     'noise.vel': 'f',
     'ptab': 'h',
     'ltab': 'h',
     'pwr0': 'f',
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
     'sd_phi': 'f',
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
     'x_sd_phi': 'f',
    }

    iqdat_types = {
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

    ud_types = {
        'iqdat': iqdat_types,
        'fitacf': fitacf_types,
        'rawacf': rawacf_types,
        'map': mapfile_types
    }.get(file_type, None)

    if ud_types is None:
        raise ValueError("Incorrect or missing file type")

    for dd in data_dicts:
        for k, v in dd.items():
            if k not in ud_types:
                message = "DICTS_TO_FILE: A supplied dictionary contains"\
                        " extra field {}".format(k)
                raise pydmap_exceptions.DmapDataError(file_path, message)

    for k, v in ud_types.items():
        if k not in dd:
            message = "DICTS_TO_FILE: Supplied dictionary is missing field {}"\
                    "".format(k)
            raise pydmap_exceptions.DmapDataError(file_path, message)
    RawDmapWrite(data_dicts, file_path, ud_types)


def dmap_rec_to_dict(rec):
    """Converts the dmap record data to a easy to use dictionary

    :param rec: a RawDmapRecord
    :returns: a dictionary of all data contained in the record

    """
    scalars = rec.get_scalars()
    arrays = rec.get_arrays()

    merged_lists = scalars + arrays

    record_dict = {ml.get_name(): ml.get_data() for ml in merged_lists}
    return record_dict
