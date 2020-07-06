# Copyright 2018 SuperDARN Canada, University of Saskatchewan
# Authors: Marina Schmidt and Keith Kotyk
"""
This file contains classes to reading and writing of  formats used by
SuperDARN.

Classes:
--------
DmapRead : Reads s
DmapWrite : writes DMap record structure into a

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
Organization
    rethink public and private methods? <--- discussion

Notes
-----
DmapRead and DmapWrite are updated and improved versions of
backscatter's pydmap:
git@github.com:SuperDARNCanada/backscatter.git
written by Keith Kotyk
"""

import collections
import logging
import numpy as np
import os
import struct
import warnings

from typing import List, Union

from pydarn import dmap_exceptions, DmapArray, DmapScalar, dmap2dict, dict2dmap

# Keeping these global definitions for readability purposes
# Data types use in s
DMAP = 0
# CHAR is defined as an int8 in RST rtypes.h https://github.com/SuperDARN/rst
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

# Dictionary of DMap types (key) to quickly convert the format and byte size
# (value-tuple)
# DMap stands for DataMap documented in:
# https://superdarn.github.io/rst/superdarn/src.doc/rfc/0006.html
# https://radar-software-toolkit-rst.readthedocs.io/en/latest/
DMAP_DATA_TYPES = {DMAP: ('', 0),
                   CHAR: ('c', 1),  # CHAR is defined as an int8 in RST
                   SHORT: ('h', 2),  # defined as int16
                   INT: ('i', 4),  # defined as int32
                   FLOAT: ('f', 4),  # defined as float32
                   DOUBLE: ('d', 8),  # equavalece to float64
                   STRING: ('s', 1),  # strings - array of 1 byte characters
                   LONG: ('q', 8),  # defined as int64
                   UCHAR: ('B', 1),  # unsigned int8
                   USHORT: ('H', 2),  # unsigned int16
                   UINT: ('I', 4),  # unsigned int32
                   ULONG: ('Q', 8)}  # unsigned int64
# unsigned refers to how the integer is stored in the byte string, meaning
# the first bit is part of the number and not referring
# to the sign of the integer

pydarn_log = logging.getLogger('pydarn')


class DmapRead():
    """
    Reading and testing the integrity of s/stream.
    DMap is describe in the RST documentation:
    - https://superdarn.github.io/rst/superdarn/src.doc/rfc/0006.html
    - https://radar-software-toolkit-rst.readthedocs.io/en/latest/
    ...

    Attributes
    ----------
    dmap_file : str
         name or data stream (give data_stream=True)
    cursor : int
        Current position in the byte array
    dmap_end_bytes : int
        The length of the byte array

    Methods
    --------
    test_initial_data_integrity()
        Quickly reads the byte array for any errors
    read_records()
        Reads the byte array to obtain the DMap records
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
        Reads an array of strings/DMap types into an array
    read_data()
        Reads the data type from the byte array
    read_numerical_array(data_type, shape, total_number_cells)
        Reads an array into a numpy array
    """

    def __init__(self, dmap_file: Union[str, bytes], data_stream=False):
        """
        Reads the /stream into a byte array for further reading of the
        DMap records.

        Parameters
        ----------
        dmap_file : str or bytes
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
        warnings.warn("DmapRead method will be removed from pyDARN v 1.2,"
                      " please use pyDARNio:"
                      " https://github.com/SuperDARN/pyDARNio",
                      PendingDeprecationWarning)
        self.rec_num = 0
        self.cursor = 0  # Current position in bytes
        self.dmap_end_bytes = 0  # total number of bytes in the dmap_file

        """
        DMap records are stored in a deque data structure for
        memory efficiency and performance. Acts the same as a stack/list.
        See DEVELOPER_README.md for more information.
        """

        # _dmap_records are private to avoid tampering.
        self._dmap_records = collections.deque()
        self._records = collections.deque()
        self.dmap_file = dmap_file

        # read the whole file/stream into a byte array
        if data_stream is False:
            # check if the file is empty
            if os.path.getsize(self.dmap_file) == 0:
                raise dmap_exceptions.EmptyFileError(self.dmap_file)

            # Read binary
            with open(self.dmap_file, 'rb') as f:
                self.dmap_bytearr = bytearray(f.read())
            pydarn_log.info("DMap Read file: {}".format(self.dmap_file))

        else:
            if len(dmap_file) == 0:
                raise dmap_exceptions.EmptyFileError("data stream")

            self.dmap_bytearr = bytearray(self.dmap_file)
            self.dmap_file = "stream"
            pydarn_log.debug("DMap Read file: Stream")
        self.dmap_buffer = memoryview(self.dmap_bytearr)
        self.dmap_end_bytes = len(self.dmap_bytearr)
        if self.dmap_end_bytes == 0:
            raise dmap_exceptions.EmptyFileError(self.dmap_file)

    def __repr__(self):
        """ for representation of the class object"""
        # __class__.__name__ allows to grab the class name such that
        # when a class inherits this one, the class name will be the child
        # class and not the parent class (dmap classes)
        return "{class_name}({filename}, {cursor}, {rec_num}, {total})"\
               "".format(class_name=self.__class__.__name__,
                         filename=self.dmap_file,
                         cursor=self.cursor,
                         total=self.dmap_end_bytes,
                         rec_num=self.rec_num)

    def __str__(self):
        """ for printing of the class object"""
        # __class__.__name__ allows to grab the class name such that
        # when a class inherits this one, the class name will be the child
        # class and not the parent class (dmap classes)
        return "Reading from {filename} at cursor: {cursor} "\
               "record number: {rec_num} with"\
               " a total number of bytes: {total_bytes}"\
               "".format(filename=self.dmap_file,
                         cursor=self.cursor,
                         rec_num=self.rec_num,
                         total_bytes=self.dmap_end_bytes)

    @property
    def get_dmap_records(self):
        """
        Returns the DMap structured records
        """
        return self._dmap_records

    @property
    def get_records(self):
        """
        Returns records of fields in a dictionary format
        """
        return self._records

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
            raise dmap_exceptions.ZeroByteError(self.dmap_file, element_info,
                                                self.rec_num)
        elif element < 0:
            element_info = "{name} {size}".format(name=element_name,
                                                  size=element)
            raise dmap_exceptions.NegativeByteError(self.dmap_file,
                                                    element_info,
                                                    self.rec_num)

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
            raise dmap_exceptions.MismatchByteError(self.dmap_file,
                                                    element_info,
                                                    self.rec_num)

    def check_data_type(self, data_type: int, data_name: str):
        """
        Check if the data_type is a DMap data type.

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
            raise dmap_exceptions.DmapDataTypeError(self.dmap_file,
                                                    data_name,
                                                    data_type,
                                                    self.rec_num)

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
        pydarn_log.info("Testing the integrity of the /stream")
        total_block_size = 0  # unit of bytes
        if self.cursor != 0:
            raise dmap_exceptions.CursorError(self.cursor, 0, self.rec_num)

        while self.cursor < self.dmap_end_bytes:
            """
            s headers contain the following:
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
            block_size = self.read_data('i', 4)
            self.zero_negative_check(block_size, "block size")

            total_block_size += block_size
            self.bytes_check(total_block_size, "total block size",
                             self.dmap_end_bytes, "total bytes in file")

            # 2 is to include the encoding_identifier and size of data which
            # are both int types.
            self.cursor = self.cursor + block_size - 2 *\
                DMAP_DATA_TYPES[INT][1]

        if total_block_size != self.dmap_end_bytes:
            message = "Error: Initial integrity check shows"\
                " total block size: {total_size} < end bytes {end_bytes}."\
                " Failed at record {rec}."\
                "".format(total_size=total_block_size,
                          end_bytes=self.dmap_end_bytes,
                          rec=self.rec_num)
            raise dmap_exceptions.DmapDataError(self.data_file, message)
        self.cursor = 0

    def read_records(self) -> collections.deque:
        """
        This method reads the records from the /stream passed
        into the instance.


        Return
        -------
        _dmap_records : collections.Deque
                Deque list of DmapRecords (ordered dictionary)


        See Also
        --------
        DmapScalar : DMap record's scalar data structure
        DmapArray  : DMap record's array data structure

        See DEVELOPER_README.md for more information on
        Dmap data structure.
        """

        # read bytes until end of byte array
        pydarn_log.debug("Reading DMap records")
        while self.cursor < self.dmap_end_bytes:
            new_record = self.read_record()
            self._dmap_records.append(new_record)
            self.rec_num += 1

        self.bytes_check(self.cursor, "cursor",
                         self.dmap_end_bytes, "total bytes in the file")

        self._records = dmap2dict(self._dmap_records)
        return self._records

    def read_record(self) -> collections.OrderedDict:
        """
        Reads a single DMap record from the byte array.

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
        # encoding_identifier = self.read_data('i',4)
        # WARNING: normally would call encoding_identifier but since it is not
        # used the extra function call is point less so best just to move the
        # cursor for performance :)
        self.cursor += 4
        block_size = self.read_data('i', 4)

        pydarn_log.debug("Reading Record {record}"
                         .format(record=len(self._dmap_records)))

        # adding 8 bytes because code+size are part of the record.
        # 4 is the number bytes for int format
        remaining_bytes = self.dmap_end_bytes - self.cursor + 2 *\
            DMAP_DATA_TYPES[INT][1]
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

        pydarn_log.debug("Reading record: reading scalars\n")
        record = collections.OrderedDict()
        for i in range(num_scalars):
            scalar = self.read_scalar()
            record[scalar.name] = scalar

        pydarn_log.debug("Reading record: reading arrays\n")
        for i in range(num_arrays):
            array = self.read_array(block_size)
            record[array.name] = array

        # check for a cursor error
        if (self.cursor - start_cursor_value) != block_size:
            raise dmap_exceptions.CursorError(self.cursor, block_size,
                                              self.rec_num)

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
            if the data type format is DMap
            NOTE: In RST, this is allowed, if an example shows up where this is
            allowed s raise as an issue in the GitHub so the code can
            be re-accessed.

        See Also
        --------
        check_data_type : for other possible raised exceptions
        read_data : reads the data stored in the byte array
        """

        # String and char have a byte size of 1
        scalar_name = self.read_data('s', 1)
        scalar_type = self.read_data('c', 1)

        self.check_data_type(scalar_type, scalar_name)

        scalar_type_fmt = DMAP_DATA_TYPES[scalar_type][0]
        scalar_fmt_byte = DMAP_DATA_TYPES[scalar_type][1]

        if scalar_type_fmt != DMAP:
            scalar_value = self.read_data(scalar_type_fmt, scalar_fmt_byte)
        else:
            message = "Error: Trying to read DMap data type for a scalar."\
                " Failed at record {}".format(self.rec_num)
            # Not sure when this is used in a
            # so better to raise an error if used re-access the code.
            raise dmap_exceptions.DmapDataError(self.dmap_file, message)

        return DmapScalar(scalar_name, scalar_value,
                          scalar_type, scalar_type_fmt)

    def read_array(self, record_size) -> DmapArray:
        """
        Reads an array from a DMap record the byte arrays and
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
        read_string_array: reads in a string/DMap array
        """
        array_name = self.read_data('s', 1)
        array_type = self.read_data('c', 1)

        self.check_data_type(array_type, array_name)

        array_type_fmt = DMAP_DATA_TYPES[array_type][0]
        array_fmt_bytes = DMAP_DATA_TYPES[array_type][1]

        array_dimension = self.read_data('i', 4)
        self.bytes_check(array_dimension, "array dimension",
                         record_size, "record size")
        self.zero_negative_check(array_dimension,
                                 "{name} array dimension"
                                 "".format(name=array_name))

        array_shape = [self.read_data('i', 4)
                       for i in range(0, array_dimension)]
        if array_dimension > 1:
            array_shape.reverse()

        # slist is the array that holds the range gates that have valid data
        # when qflg is 1
        if any(x <= 0 for x in array_shape) and array_name != "slist":
            message = "Error: Array shape {shape} contains "\
                "dimension size <= 0."\
                " Failed at record {rec}".format(shape=array_shape,
                                                 rec=self.rec_num)
            raise dmap_exceptions.DmapDataError(self.dmap_file, message)

        for i in range(array_dimension):
            if array_shape[i] >= record_size:
                message = "Error: Array {index}-dimension size {size}"\
                    " exceeds record size: {rec_size}. "\
                    "Failed at record {rec}"\
                    "".format(index=i,
                              size=array_shape[i],
                              rec_size=record_size,
                              rec=self.rec_num)
                raise dmap_exceptions.DmapDataError(self.dmap_file, message)

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

        if array_type_fmt == 's':
            message = "Error: Trying to read array of strings."\
                " Currently not implemented."\
                " Failed at record {}".format(self.rec_num)
            # Not sure when this is used in a
            # so better to raise an error if used re-access the code.
            raise dmap_exceptions.DmapDataError(self.dmap_file, message)
            # FIXME: Not working
            # array_value = self.read_string_array(array_shape,
            #                                     array_type_fmt,
            #                                     array_fmt_bytes)
        elif array_type == DMAP:
            message = "Trying to read DMap array data type."\
                " Failed at record {}".format(self.rec_num)
            # Not sure when this is used in a
            # so better to raise an error if used re-access the code.
            raise dmap_exceptions.DmapDataError(self.dmap_file, message)
        else:
            array_value = self.read_numerical_array(array_shape,
                                                    array_type_fmt,
                                                    total_num_cells,
                                                    array_fmt_bytes)

        return DmapArray(array_name, array_value, array_type, array_type_fmt,
                         array_dimension, array_shape)

    def read_data(self, data_type_fmt: str, data_fmt_bytes: int):
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
            if trying to read a DMap data type

        See Also
        --------
        Struct.unpack : converts the bytes array values from a C structure to
        python objects

        See DEVELOPER_README.md for more information on DMap data types and
        Struct.unpack.
        """
        if self.cursor >= self.dmap_end_bytes:
            message = "Error: Cursor {cursor} extends"\
                " out of buffer {end_bytes}. "\
                "Fails at record {rec}"\
                "".format(cursor=self.cursor,
                          end_bytes=self.dmap_end_bytes,
                          rec=self.rec_num)
            raise dmap_exceptions.CursorError(self.cursor, message=message)

        cursor_offset = self.dmap_end_bytes - self.cursor
        if cursor_offset < data_fmt_bytes:
            message = "Error: Byte offsets {offset} into buffer {fmt}"\
                " are not aligned. Failed at record "\
                "{rec}".format(offset=cursor_offset,
                               fmt=data_fmt_bytes,
                               rec=self.rec_num)
            raise dmap_exceptions.CursorError(self.cursor, message=message)

        # struct.unpack is a python method the converts C struct
        # as python bytes to python values. See DEVELOPER_README.md
        # for more information.
        # TODO: how to handle this gracefully? Return None and check later than
        #       continue in the loop?
        if data_type_fmt == 'c':
            # This casting is needed to keep the correct instance otherwise
            # python will default it to int which later could have some
            # consequences if you try to rewrite the file
            data = self.dmap_bytearr[self.cursor]
            self.cursor += data_fmt_bytes
            return data
        elif data_type_fmt == 's':
            byte_counter = 0
            while self.dmap_bytearr[self.cursor + byte_counter] != 0 or \
                    self.cursor + byte_counter >= self.dmap_end_bytes:
                # add 1 byte to byte_counter because
                # a string is a list of chars
                byte_counter += 1  # 1 is the number of bytes of a char

            self.bytes_check(self.cursor + byte_counter, 'cursor',
                             self.dmap_end_bytes, 'Total number of Bytes')

            # format byte counter to a string format for unpacking
            # WARNING: not using format for performance purposes
            char_count = '%ss' % byte_counter
            data = struct.unpack_from(char_count,
                                      self.dmap_buffer,
                                      self.cursor)
            # 1 is the number of bytes in a char
            self.cursor = self.cursor + byte_counter + 1
            return data[0].decode('utf-8')
        else:
            data = struct.unpack_from(data_type_fmt,
                                      self.dmap_buffer,
                                      self.cursor)
            self.cursor += data_fmt_bytes
            return data[0]

    # FIXME: Currently this method is not working, thus there is no support
    # for array[str], but may not be important. ¯\_(ツ)_/¯
    # The problem is the padding between various string encodings:
    # UTF-8 -> 4 bytes and ASCII -> 1 byte
    # so either DMap would have to incorporate that information plus
    # string length would be a god send... If not one possible solution
    # you would record the length of the record size and subtract the byte
    # (or start at cursor point and increment to the end of the record size)
    # information: encoding, data type, dimension, shape, name, then you
    # should have the length of the array. Then by trial and error (unless we
    # store the encoding information) determine the encoding size, if there is
    # padding you will get "\x00", from there you can jump over the byte size
    # and when a comma occurs then that is the end of your string and append to
    # the array and continue until you reach the end of the record size.
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

        dim_data = []
        dim = shape
        dimension = dim.pop()
        # FIXME: still need to find a method for testing this... Or a file
        #        that contains a string/DMap array
        # for dim_size in shape:
        #    for i in range(dim_size):
        #        result = self.read_data(array_type_fmt, array_fmt_bytes)
        #        data.append(result)
        # try to avoid using recursion, it is slow
        if not dim:
            dim_data = [self.read_data(array_type_fmt, array_fmt_bytes)
                        for i in range(0, dimension)]
        else:
            dim_data = [self.build_n_dimension_list(list(dim), array_type_fmt)
                        for i in range(0, dimension)]
        return np.array(dim_data)

    def read_numerical_array(self, shape: list, data_type_fmt: str,
                             total_number_cells: int,
                             data_fmt_bytes: int) -> np.ndarray:
        """
        Reads in an array from the byte array into a N-D array.

        Parameter
        ---------
        shape : list
            A list of the array's dimension sizes
        data_type : int
            DMap data type numeric value
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
        if data_type_fmt == 'c':
            # In RST rtypes.h file, chars are defined as int8
            # allowing this assumption to be allowed for now
            array = np.frombuffer(self.dmap_buffer, np.int8,
                                  total_number_cells, self.cursor)
        else:
            array = np.frombuffer(self.dmap_buffer, data_type_fmt,
                                  total_number_cells, self.cursor)
        self.cursor += total_number_cells * data_fmt_bytes
        array = np.reshape(array, shape, order='C')
        return array


class DmapWrite(object):
    """
    Writes DMap records to file or stream and writes SuperDARN file format.
    ...

    Attributes
    -----------
    dmap_records : List[dict]
        List of DMap records
    filename : str
        Name of the file the user wants to write to
    dmap_bytearr : bytearray
        Byte array representing the DMap records in bytes

    Methods
    -------
    write_dmap(filename)
        Writes DMap records to DMap format with the given filename
    write_dmap_stream(dmap_records)
        Writes DMap records to DMap format byte stream
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
    SuperDARN_file_structure_to_bytes(file_struct_list)
        Converts DMap records to SuperDARN file structure bytes based
        on file_struct_list
    dmap_records_to_bytes()
        Converts DMap records to byte array stored in dmap_bytearr
    dmap_scalar_to_bytes(scalar)
        Converts a DmapScalar to bytes
    dmap_array_to_bytes(array)
        Converts a DmapArray to bytes
    """
    def __init__(self, dmap_records: List[dict] = [], filename: str = ""):
        """
        Writes DMap records to a given filename of byte array in DMap format,
        this includes the following SuperDARN file types:
                                                      - Iqdat
                                                      - Rawacf
                                                      - Fitacf
                                                      - Grid
                                                      - Map

        Parameters
        ----------
        dmap_records : List[dict]
            list of dictionaries representing a list of DMap records containing
            DmapScalar and DmapArrays
        filename : str
            The path and name of the file the user wants to write to
        dmap_file_fmt : str
             types, the following are supported:
                                     - 'iqdat' : SuperDARN file type
                                     - 'rawacf' : SuperDARN file type
                                     - 'fitacf' : SuperDARN file type
                                     - 'grid' : SuperDARN file type
                                     - 'map' : SuperDARN file type
                                     - 'dmap' : writes a file in DMap format
                                     - 'stream' : writing to dmap data stream

        Raises
        ------
        DmapTypeError
        FilenameRequiredError
        """
        warnings.warn("DmapWrite method will be removed from pyDARN v 1.2,"
                      " please use pyDARNio:"
                      " https://github.com/SuperDARN/pyDARNio",
                      PendingDeprecationWarning)

        self.filename = filename
        self.rec_num = 0

        self.dmap_records = self.__check_dmap_dict(dmap_records)

        self.dmap_bytearr = bytearray()
        pydarn_log.info("Initiating DmapWrite")

    def __repr__(self):
        """ for representation of the class object"""
        # __class__.__name__ allows to grab the class name such that
        # when a class inherits this one, the class name will be the child
        # class and not the parent class (dmap classes)
        return "{class_name}({filename}, {rec_num})"\
               "".format(class_name=self.__class__.__name__,
                         filename=self.filename,
                         rec_num=self.rec_num)

    def __str__(self):
        """ for printing of the class object"""
        # __class__.__name__ allows to grab the class name such that
        # when a class inherits this one, the class name will be the child
        # class and not the parent class (dmap classes)
        return "Writing to filename: {filename} at record number: {rec_num}"\
               "".format(filename=self.filename,
                         rec_num=self.rec_num)

    def __check_dmap_dict(self, dmap_records):
        """
        Checks if the dmap data is a dict, if so, converts to a dmap_structure

        Parameter:
            dmap_data : List[dict]
                dmap_data structure to test if it is a dict of value or dmap
                structure
        Returns:
            dmap_structure : List[dict]
                returns the dmap structure of dmap_data
        """
        try:
            first_value = list(dmap_records[0].values())[0]
            if isinstance(first_value, DmapScalar) or isinstance(first_value,
                                                                 DmapArray):
                return dmap_records
            else:
                return dict2dmap(dmap_records)
        except IndexError:
            return dmap_records

    # HONEY BADGER method: Because dmap just don't care -
    # will write anything into DMap format with out any file
    # structure checks. See supedarn.py for methods that do checks
    # for superDARN file structures.
    def write_dmap(self, filename: str = ""):
        """
        Writes DMap record to  format.

        Parameters:
        -----------
        filename : str
            The name of the DMap file including the path

        WARNING:
        --------
        No checks are done, this up to the user to ensure their fields are
        correct.
        """
        self._filename_check(filename)
        pydarn_log.info("Writing : {}".format(self.filename))
        self.write_dmap_stream()
        with open(self.filename, 'wb') as f:
            f.write(self.dmap_bytearr)

    def write_dmap_stream(self, dmap_records: List[dict] = []) -> bytearray:
        """
        Writes DMap record to  format.

        Return
        ------
        dmap_bytearr : bytearray
            Bytearray of the DMap records

        WARNING:
        --------
        No checks are done, this up to the user to ensure their fields are
        correct.
        """
        if self.dmap_records == []:
            self.dmap_records = self.__check_dmap_dict(dmap_records)
        self._empty_record_check()
        pydarn_log.info("Writing to dmap stream")
        self.dmap_records_to_bytes()
        return self.dmap_bytearr

    def _empty_record_check(self):
        if self.dmap_records == []:
            raise dmap_exceptions.DmapDataError(self.filename,
                                                "DMap record is empty "
                                                "there is nothing to write.")

    def _filename_check(self, filename: str = ""):
        """
        Checks if a filename is given and overrides the current
        filename with the new one.

        Parameter:
        ----------
        filename : str
            Name of the file to write to

        Raises:
        ------
        FilenameRequireError - raised if no filename is given
        """
        if self.filename == "" and filename == "":
            raise dmap_exceptions.FilenameRequiredError()
        elif filename != "":
            self.filename = filename

    def dmap_records_to_bytes(self):
        """
        Loops through the DMap records and calls dmap_record_to_bytes
        to convert the DMap records to a byte array.

        Future use of this function is for parallelization.
        """
        # For performance increase len of the records can be
        # attribute value initialized in the class
        pydarn_log.debug("Converting DMap records to bytes")
        for self.rec_num in range(len(self.dmap_records)):
            record = self.dmap_records[self.rec_num]
            self._dmap_record_to_bytes(record)

    def _dmap_record_to_bytes(self, record: dict):
        """
        Converts DMap record to byte stream and stores in the
        dmap byte array

        Parameter
        ---------
        record : dict
            DMap record

        Notes
        -----
        Might be useful to return bytes of records for potential
        writing into a data stream or real-time stream
        """
        # DaVitpy reference, still unclear of meaning of the numeber
        encoding_identifier = 65537
        num_scalars = 0
        num_arrays = 0
        data_bytearray = bytearray()
        for name, data_info in record.items():
            if isinstance(data_info, DmapScalar):
                data_bytearray.extend(self.dmap_scalar_to_bytes(data_info))
                num_scalars += 1
            elif isinstance(data_info, DmapArray):
                data_bytearray.extend(self.dmap_array_to_bytes(data_info))
                num_arrays += 1
            else:
                raise dmap_exceptions.DmapTypeError(self.filename,
                                                    type(data_info),
                                                    self.rec_num)

        # 16 = encoding_identifier (int - 4 bytes) + num_scalars (int - 4) +
        #      num_arrays (int - 4) + size of the block (int - 4)
        block_size = len(data_bytearray) + 16

        # TODO: potential performance increase by saving the extend object
        self.dmap_bytearr.extend(struct.pack('i', encoding_identifier))
        self.dmap_bytearr.extend(struct.pack('i', block_size))
        self.dmap_bytearr.extend(struct.pack('i', num_scalars))
        self.dmap_bytearr.extend(struct.pack('i', num_arrays))
        self.dmap_bytearr.extend(data_bytearray)

    def dmap_scalar_to_bytes(self, scalar: DmapScalar) -> bytes:
        """
        Converts a DmapScalar to byte format.
        Byte format: name, data type, data

        Parameter
        ---------
        scalar : DmapScalar
            Dmap scalar to be convert into byte format

        Return
        ------
        scalar_total_bytes : bytes
            Bytes of the scalar
        """

        scalar_name = "{0}\0".format(scalar.name)
        scalar_name_format = '{0}s'.format(len(scalar_name))
        scalar_name_bytes = struct.pack(scalar_name_format,
                                        scalar_name.encode('utf-8'))

        scalar_type_bytes = struct.pack('c',
                                        chr(scalar.data_type).encode('utf-8'))

        if scalar.data_type_fmt == 's':
            scalar_data = "{0}\0".format(scalar.value)
            scalar_data_format = '{0}s'.format(len(scalar_data))
            scalar_data_bytes = struct.pack(scalar_data_format,
                                            scalar_data.encode('utf-8'))
        elif scalar.data_type_fmt == 'c':
            # char is defined as int8 by RST
            if isinstance(scalar.value, str):
                raise dmap_exceptions.DmapCharError(scalar.name, self.rec_num)
            # scalar_data_bytes = scalar.value
            scalar_data_bytes = chr(scalar.value).encode('utf-8')
        elif scalar.data_type_fmt == 'f':
            scalar_data_value = np.float32(scalar.value)
            scalar_data_bytes = struct.pack(scalar.data_type_fmt,
                                            scalar_data_value)
        else:
            scalar_data_bytes = struct.pack(scalar.data_type_fmt, scalar.value)

        scalar_total_bytes = scalar_name_bytes + scalar_type_bytes +\
            scalar_data_bytes

        return scalar_total_bytes

    def dmap_array_to_bytes(self, array: DmapArray) -> bytes:
        """
        Converts a DmapArray to the byte format.

        Byte format: name, data type, dimension, shape, data

        Parameter
        ---------
        array : DmapArray
            Dmap array to be converted to bytes

        Return
        -------
        array_total_bytes : bytes
            Total bytes of the array
        """
        # need to ensure the array is flattened
        if array.data_type_fmt == 'c' and isinstance(array.value[0], str):
            raise dmap_exceptions.DmapCharError(array.name, self.rec_num)
        elif array.data_type_fmt == 's':
            message = "Error: Trying to read array of strings."\
                " Currently not implemented."\
                " Failed at record {}".format(self.rec_num)
            raise dmap_exceptions.DmapDataError(self.filename, message)

        array_value = array.value.flatten()
        array_name = "{0}\0".format(array.name)
        array_name_format = '{0}s'.format(len(array_name))
        array_name_bytes = struct.pack(array_name_format,
                                       array_name.encode('utf-8'))

        array_type_bytes = struct.pack('c',
                                       chr(array.data_type).encode('utf-8'))

        array_dim_bytes = struct.pack('i', array.dimension)
        array_shape_bytes = bytes()
        if array.dimension > 1:
            array.shape.reverse()
        for size in array.shape:
            array_shape_bytes += struct.pack('i', size)

        array_data_bytes = array_value.tostring()

        array_total_bytes = array_name_bytes + array_type_bytes + \
            array_dim_bytes + array_shape_bytes + array_data_bytes

        return array_total_bytes
