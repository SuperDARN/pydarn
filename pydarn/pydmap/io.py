import os
import struct
import numpy as np
import logging
import collections

from pydarn import DmapRecord
from pydarn import DmapArray
from pydarn import Dmapscalar
from pydarn import pydmap_exceptions

# Keeping these global definitions for readbility purposes
# where do these values come from?
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

# ChainMap maybe of interest ... but not sure how to implement at this moment
DMAP_DATA_TYPES = {DMAP: ('', 0),
                   CHAR: ('c',1),
                   SHORT: ('h',2),
                   INT: ('i',4),
                   FLOAT: ('f',4)
                   DOUBLE: ('d',8),
                   STRING: ('s'),
                   LONG: ('q',8),
                   UCHAR: ('B',1),
                   USHORT: ('H',2),
                   UINT: ('I',4),
                   ULONG: ('Q',8)}


pydarn_logger = logging.getLogger('pydarn')

class DmapRead():
    """Contains members and methods relating to parsing files into raw Dmap objects.
        Takes in a buffer path to decode. Default is open a file, but can optionally
        use a stream such as from a real time socket connection
        :param dmap_file: is a file/stream to contains binary dmap records
    """
    DMAP_DATA_KEYS = [0, 1, 2, 3, 4, 8, 9, 10, 16, 17, 18, 19]

    def __init__(self, dmap_file, stream=False):
        self.dmap_cursor = 0 # offset of bytes
        self.dmap_end_bytes = 0 # units of bytes
        self.__dmap_records = []
        self.dmap_file = dmap_file

        # parses the whole file/stream into a byte object
        if stream is False:
            # check if the file is empty
            if os.path.getsize(self.dmap_file) == 0:
                raise EmptyFileError(self.dmap_file)

            # Read binary dmap file
            with open(self.dmap_file, 'rb') as f:
                self.dmap_bytearr = bytearray(f.read())
            pydarn_logger.info("DMAP Read file: {}".format(self.dmap_file))

        else:
            if len(dmap_file) == 0:
                raise EmptyFileError("data stream")

            self.dmap_bytearr = bytearray(self.dmap_file)
            self.dmap_file = "stream"
            pydarn_logger.info("DMAP Read file: Stream")
        self.dmap_end_bytes = len(self.dmap_bytearr)

    def read_records(self):
        """
            This method reads the records from the dmap file/stream passed
            into the class.
        """
        pydarn_logger.info("Sanity check first before reading records")
        # This may not be needed if there are checks through out the program
        #self.test_initial_data_integrity(self.dmap_bytearr)

        pydarn_logger.info("Reading dmap records...")
        # read bytes until end of byte array
        while self.dmap_cursor < self.dmap_end_bytes:
            # TODO: Maybe I need a debugger file for this kind of information?
            pydarn_logger.debug("TOP LEVEL LOOP: cursor {0}\n".format(self.cursor))
            new_record = self.read_record()
            self.__dmap_records.append(new_record)
            if (self.cursor > end_byte):
                message = "Bytes attempted {cursor} does not match the size of"\
                        " file {end_byte}".format(cursor=self.cursor,
                                                  end_byte=self.end_bytes)
                raise DmapDataError(self.dmap_file, message)
        return self.__dmap_records

    # TODO: Maybe break this method into smaller checks that could just be called
    #       In other methods. This method is useful for a script that just does
    #       file integrity but doesn't need to read the records.
    def test_initial_data_integrity(self):
        """
        Static method so that is detached to the potetial corruption of data and
        prevention of mutating and variables passed it. This also has a nice
        effect that users could use on other files if they just want to check
        the file.
         :pre: precondition is that the cursor is set to 0
         :exception CursorError: If the currsor is not set to an expected value.
         :exception DmapDateError: If the data is curropted by some byte offset.
        """
        pydarn_logger.info("Testing the integrity of the dmap file/stream")
        total_block_size = 0 # unit of bytes
        if self.cursor > 0:
            raise CursorError(self.cursor,0)

        while self.cursor < self.dmap_end_bytes:
            """
            DMAP files headers contain the following:
                - encoding identifier: is a unique 32-bit integer that indicates
                  how the block was constructed. It is used to differentiate
                  between the possible furture changes to the DataMap format.
                - block size: 32-bit integer that repersents the total size of
                  block including the header and the data.
                - Number of Scalars: number of scalar variables
                - Scalar data: the scalar data of the record.
                  Please see DMAPScalar for more information on scalars.
                - Number of arrays: number of array variables
                  Please see DMAPArray for more information on arrays.
            """
            # This is an unused variable but is need to move the cursor to the
            # next offset.
            encoding_identifier = self.read_data('i')
            if self.cursor > 4:
                raise CursorError(self.cursor,0)
            block_size = self.read_data('i')
            if block_size <= 0:
                message = "Error: Initial integrity check"\
                        " block size: {block_size} <= 0 or"\
                        " > end bytes: {end_bytes}\n Cursor: {cursor}."\
                        " Data is likely corrupted".format(cursor=self.cursor,
                                                           end_bytes=self.dmap_end_bytes,
                                                           block_size=block_size)
                raise DmapDataError(self.date_file, message)

            total_block_size += block_size

            if total_block_size > self.dmap_end_bytes:
                message = "Error: Initial integrity check shows record size"\
                        " mismatch. total block size: {total_size} >"\
                        " end bytes: {end_bytes}."\
                        " Data is likely corrupted".format(total_size=total_block_size,
                                                           end_bytes=self.dmap_end_bytes)
                raise DmapDataError(self.dmap_file, message)

            # why minus 2?
            self.cursor = self.cursor + block_size - 2 * DMAP_DATA_TYPE[INT][1]

        if total_block_size != self.dmap_end_bytes:
            message = "Error: Initial integrity check shows"\
                    " total block size: {total_size} < end bytes {end_bytes}."\
                    " Cursor: {cursor}."\
                    " Data is likely corrupted".format(total_size=total_block_size,
                                                       end_bytes=self.dmap_end_bytes,
                                                       cursor=self.cursor)
            raise DmapDataError(self.date_file, message)
        self.cursor = 0

    def zero_check(self, element, element_name):
        """
        Checks if the element <= 0 bytes. If true then raise a ZeroByteError.
        """
        if element <= 0:
            element_info = "{name} {size}".format(name=element_name,
                                                  size=element)
            raise pydmap_exceptions.ZeroByteError(self.dmap_file, element_info, self.cursor)

    def bytes_check(self, element, element_name, byte_check, byte_check_name)
        """
        check if the element > byte check. If true then raise a MismatchByteError.
        """
        if element > byte_check:
            element_info = "{name} {size} >"\
                    " {check_name} {check}".format(name=element_name,
                                                   size=element,
                                                   check_name=byte_check_name,
                                                   check=byte_check)
           raise pydmap_exceptions.MismatchByteError(self.dmap_file, element_info, self.cursor)

    def check_data_type(self, data_type, data_name):
        if data_type not in DMAP_DATA_TYPES.keys():
            raise pydmap_exceptions.DmapDataTypeError(self.dmap_file, data_name,
                                                     data_type, self.cursor)


    def read_record(self):
        """
        Parses a single dmap record from the buffer
        """
        # used in a cursor check.
        post_cursor = self.cursor

        encoding_identifier = self.read_data('i')
        block_size = self.read_data('i')

        pydarn_logger.info("Reading Record: encoding idetifier {code}"\
                           " block size {size}\n".format(code=encoding_identifier,
                                                         size=block_size))

        # adding 8 bytes because code+size are part of the record.
        remaining_bytes = self.dmap_end_bytes - self.cursor + 2 * DMAP_DATA_TYPE[INT][1] # why 2?
        bytes_check(block_size, "block size", remaining_bytes, "remaining bytes",
                    self.dmap_file, self.cursor)
        zero_check(block_size, "block size", self.dmap_file, self.cursor)

        num_scalars = self.read_data('i')
        num_arrays = self.read_data('i')

        pydarn_logger.info("Reading record: there are {scalars} scalars"\
                           " and {arrays} arrays\n"
                        .format(scalars=num_scaleas, arrays=num_arrays))
        zero_check(num_scalars, "number of scalars", self.dmap_file, self.cursor)
        zero_check(num_arrays, "number of arrays", self.dmap_file, self.cursor)
        bytes_check(num_scalars + num_arrays, "number of scalars + arrays",
                    block_size, "block size", self.dmap_file, self.cursor)


        pydarn_logger.info("Reading record: reading scalars\n")
        # TODO: Need to review how to rewrite this to fit new dmap record storage
        scalars = {}
        for i in range(0, num_scalars):
            scalar = self.read_scalar()
            # this will allow for faster access
            scalars[scalar.name] = scalar

        pydarn_logger.info("Reading record: reading arrays\n")
        arrays = {}
        for i in range(0, num_arrays):
            array = self.read_array(block_size)
            arrays[array.name] = array

        # check for a cursor error
        if (self.cursor - post_cursor) != block_size:
            raise pydmap_exceptions.CursorError(self.cursor, block_size)

        return DmapRecord(scalars, arrays)

    def read_scalars(self):
        """Parses a new dmap scaler from bytearray
        :returns: new RawDmapScaler with parsed data
        """

        mode = 6 # what does this mean?
        scalar_name = self.read_data('s')
        scalar_type = self.read_data('c')

        check_data_type(scalar_type, scalar_name, self.dmap_file, self.cursor)
        pydarn_logger.info("Read scalar: name {0} data type {1}\n"
                        .format(name, data_type))

        scalar_type_fmt = DMAP_DATA_TYPE.get(scalar_type, DMAP)

        if scalar_type_fmt != DMAP:
            scalar_data = self.read_data(scalar_type_fmt)
        else:
            scalar_data = self.read_record() # why do we read another record?

        return DmapScalar(scalar_name, scalar_type, scalar_type_fmt,
                          mode, scalar_data)

    def read_array(self, record_size):
        """Parses a new dmap array from bytearray
        :params record size: is the size of the record in bytes
        :returns: new RawDmapArray with parsed data
        """
        mode = 7 # again what does this mean?
        array_name = self.read_data('s')
        array_type = self.read_data('c')

        check_data_type(array_type, array_name, self.dmap_file, self.cursor)
        pydarn_logger.info("PARSE ARRAY: name {0} data_type {1}\n"
                           .format(array_name, array_type))

        array_type_fmt = DMAP_DATA_TYPE.get(array_type, (DMAP, None))[0]
        array_fmt_bytes = DMAP_DATA_TYPE.get(array_type,(DMAP, 0))[1]

        array_dimension = self.read_data('i')
        bytes_check(array_dimension, "array dimension",
                    record_size, "record size", self.dmap_file, self.cursor)
        zero_check(array_dimension, "array dimension", self.dmap_file, self.cursor)

        array_shape = [self.read_data('i') for i in range(0, array_dimension)]

        # if dimensions list is empty
        if array_shape > 0:
            message = "Error: Array shape {shape} could not be read."\
                    " cursor: {cursor}".format(shape=array_shape,
                                               cursor=self.cursor)
            raise DmapDataError(self.dmap_file, message)
        elif any(x <= 0 for x in array_dimensions) and name != "slist": # where does slist come from?
            message = "Error: Array shape {shape} contains dimension size <= 0."\
                    " Cursor: {cursor}".format(dim=array_shape,
                                               cursor=self.cursor)
            raise DmapDataError(self.filename, message)

        for i in range(len(array_shape)):
            if array_shape[i] >= record_size:
                message = "Error: Array {index}-dimension size {size}"\
                        " exceeds record size: {rec_size}.".format(index=i,
                                                               size=array_shape[i],
                                                               rec_size=record_size)
                raise pydmap_exceptions.DmapDataError(self.dmap_file, message)

        pydarn_logger.info("Read array: shape is {0}\n".format(array_dimensions))

        total_num_cells = np.prod(array_dimensions)
        byte_check(total_num_cells, "total number of cells", record_size,
                   "record size", self.dmap_file, self.cursor)

        total_num_cells_bytes = total_num_cells * array_fmt_bytes
        byte_check(total_num_cells_bytes, "total number of cells in bytes", record_size,
                   "record size", self.dmap_file, self.cursor)

        pydarn_logger.info("Read array: total elements {0} byte size {1}\n"
                        .format(total_elements, array_fmt_bytes))

        # parsing an array of strings requires a different method. Numpy can't
        # parse strings or dmaps into arrays the way it can for other
        # types because it doesnt
        # know the sizes. They have to be manually read the slow way.
        # Because chars
        # are encoded as hex literals, they have to be read one at a
        # time to make sense.

        # what is DMAP format? Can we get an example that has a list of Strings or DMAP?
        # Also why is char also included?
        if array_type_fmt == 's' or array_type_fmt == 'c' or array_type_fmt == DMAP:
            data_array = self.read_string_DMAP_array(array_shape, array_type_fmt)
        else:
            data_array = self.read_numerical_array(array_type_fmt,
                                                   dimensions,
                                                   total_elements)

        return RawDmapArray(name, data_type, array_type_fmt, mode,
                            array_dimension, dimensions, data_array)

    def read_string_DMAP_array(self, shape, array_type_fmt):
        """This is used to build a list of multiple dimensions without knowing
        them ahead of time. This method is used to manually parse arrays
        from a dmap

        :param shape: the shape of n-dimensional array containing
                      the size of each dimension
        :param data_type_fmt: string format identifier of the DMAP data type  <--- what about char?
        :returns: list of strings or DMAP data
        """
        data = []

        for dim_size in shape:
            for i in range(dim_size):
                data.append(self.read_data(data_type_fmt))
       # try to avoid using recursion, it is slow
       # if not dim:
       #     dim_data = [self.read_data(data_type_fmt)
       #                 for i in range(0, dimension)]
       # else:
       #     dim_data = [self.build_n_dimension_list(list(dim), data_type_fmt)
       #                 for i in range(0, dimension)]
        return np.array(data)

    def read_data(self, data_type):
        """Reads an individual data type from the buffer
        Given a format identifier, a number of bytes are read from the buffer
        and turned into the correct data type

        :param data_type: a string format identifier for the DMAP data type
        :returns: parsed data

        """
        pydarn_logger.info("read data: cursor {0} out of {1} bytes\n"
                        .format(self.cursor,
                                self.dmap_end_bytes))
        data_type_fmt = DMAP_DATA_TYPE.get(data_type, (DMAP, None))[0]
        data_fmt_bytes = DMAP_DATA_TYPE.get(data_type,(DMAP, 0))[1]

        if self.cursor >= self.dmap_end_bytes:
            message = "Error: Cursor {cursor} extends"\
                    " out of buffer {end_bytes}.".format(cursor=self.cursor,
                                                         end_bytes=self.dmap_end_bytes)
            raise pydmap_exceptions.CursorError(self.cursor, message=message)

        cursor_offset = self.dmap_end_bytes - self.cursor
        if cursor_offset < data_fmt_bytes:
            message = "Error: Byte offsets {offset} into buffer {fmt}"\
                    " are not aligned.".format(offset=cursor_offset,
                                               fmt=data_fmt_bytes)
            raise pydmap_exceptions.CursorError(self.cursor, message=message)

        # struct.upack is a python method the converts C struct as python bytes
        # to python values. See DEVELOPER_README.md for more information.
        # Still confused what DMAP means?
        if data_type_fmt is DMAP:
            return self.read_record()
        elif data_type_fmt == 'c':
            data = self.dmap_bytearr[self.cursor] # Not sure this always holds?
            self.cursor = self.cursor + data_fmt_bytes
            return data
        elif data_type_fmt == 's':
            byte_counter = 0
            while self.dmap_bytearr[self.cursor + byte_counter] != 0:
                # add 1 byte to byte_counter because a string is a list of chars.
                byte_counter = byte_counter + DMAP_DATA_TYPES[CHAR][1]
                if self.cursor + byte_counter >= self.dmap_end_bytes:
                    message = "Error: Cursor {cursor} + byte counter >="\
                            " {end_bytes} end number"\
                            " of bytes".format(cursor=self.cursor + byte_counter,
                                               end_bytes=self.dmap_end_bytes)
                    raise pydmap_exceptions.CursorError(self.cursor, message=message)

            # format byte counter to a string format for unpacking
            char_count = '{0}s'.format(byte_counter)
            data = struct.unpack_from(char_count,
                                      memoryview(self.dmap_bytearr),
                                      self.cursor)
            self.cursor = self.cursor + byte_counter + DMAP_DATA_TYPES[CHAR][1]
            return str(data[0],'utf-8')
        else:
            data = struct.unpack_from(data_type_fmt, memoryview(self.dmap_bytearr),
                                      self.cursor)
            self.cursor = self.cursor + data_fmt_bytes
            return data[0]

    def read_numerical_array(self, data_type, shape, total_number_cells):
        """Reads a numerical array from bytearray using numpy

        Instead of reading array elements one by one, this method uses numpy
        to read an
        entire section of the buffer into a numpy array and then reshapes
        it to the correct
        dimensions. This method is prefered due to massive performance increase

        :param data_type: a string format identifier for the DMAP data type
        :param dimensions: a list of each array dimension
        :param total_elements: total elements in the array
        :returns: parsed numpy array in the correct shape

        """

        data_type_fmt = DMAP_DATA_TYPE.get(data_type, (DMAP, None))[0]
        data_fmt_bytes = DMAP_DATA_TYPE.get(data_type,(DMAP, 0))[1]

        array_buffer_start = self.cursor
        array_buffer_end = self.cursor + total_number_cells * data_fmt_type
        self.byte_check(array_buffer_end, "array buffer end", self.dmap_end_bytes, "number of bytes in the file")

        array_buffer = self.dmap_bytearr[self.cursor:self.cursor + total_number_cells *
                                data_fmt_bytes]

        try:
            array = np.frombuffer(array_buffer, dtype=data_type_fmt)
        except ValueError as v:
            message = "Error: the following ValueError was raised {error}\n"\
                    "Array buffer {buf} is not a multiple"\
                    " of the data size {size}".format(error=v,
                                                      buf=array_buffer,
                                                      size=data_fmt_size)
            raise pydmap_exceptions.DmapDataError(self.dmap_file, message)

        if len(shape) > 1:
            # reshape the array from 1-d to n-d.
            # we need to reverse the shape order because it is read in reverse
            # from the file.
            array = array.reshape(tuple(shape[::-1]))

        self.cursor = self.cursor + total_number_cells * data_fmt_bytes

        pydarn_logger.info("Read numerical array: Successfully read array\n")
        return array


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
        element of the dictionary and creates a RawDmapArray or RawDmapScaler
        and adds them to a RawDmapRecord. Any python lists are converted to
        numpy arrays for fast and efficient convertion to bytes

        :param data_dict: a dictionary of data to encode

        """
        record = RawDmapRecord()
        for k, v in data_dict.items():

            if k in self.ud_types:
                data_type_fmt = self.ud_types[k]
            else:
                data_type_fmt = self.find_datatype_fmt(v)
                if data_type_fmt == '':
                    #TODO: handle recursive dmap writing
                    # recursive is slow so we should look at other options
                    pass

            if isinstance(v, (list, np.ndarray)):
                mode = 7
                if isinstance(v, list):
                    if data_type_fmt == 'c':
                        data = np.asarray([chr(x) for x in v], dtype='c')
                    elif data_type_fmt == 's':
                        data = np.asarray(v, dtype=object)
                    else:
                        data = np.asarray(v, dtype=data_type_fmt)
                if isinstance(v, np.ndarray):
                    if data_type_fmt == 'c' and v.dtype != 'S1':
                        data = np.asarray([chr(x) for x in v], dtype='c')
                    else:
                        data = np.asarray(v, dtype=data_type_fmt)

                dmap_type = self.convert_fmt_to_dmap_type(data_type_fmt)

                # dimensions need to be reversed to match what dmap expects
                arr_dimensions = data.shape[::-1]
                dimension = len(arr_dimensions)
                array = RawDmapArray(k, dmap_type, data_type_fmt, mode,
                                     dimension, arr_dimensions, data)
                record.add_array(array)

            else:
                dmap_type = self.convert_fmt_to_dmap_type(data_type_fmt)
                mode = 6
                scaler = RawDmapScaler(k, dmap_type, data_type_fmt, mode, v)
                record.add_scaler(scaler)

        self.records.append(record)

    def find_datatype_fmt(self, data):
        """Input could be an array of any dimensions so will recurse until
        fundamental type is found

        :param data: data for which to find its type format
        :returns: a string format identifier for the python data type

        """
        if isinstance(data, np.ndarray) or isinstance(data, list):
            return self.find_datatype_fmt(data[0])
        else:
            return self.type_to_fmt(data)

    def dmap_record_to_bytes(self, record):
        """This method converts a dmap record to the byte format that is written to file.

        Format is code,length of record,number of scalars,number of arrays, followed by
        the scalars and then the arrays

        :param record: a RawDmapRecord

        """
        scalars = record.get_scalars()
        arrays = record.get_arrays()

        code = 65537 # TODO: what is this value?
        num_scalars = record.get_num_scalars()
        num_arrays = record.get_num_arrays()

        byte_arr = bytearray()
        for sc in scalars:
            byte_arr.extend(self.dmap_scaler_to_bytes(sc))
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

    def dmap_scaler_to_bytes(self, scaler):
        """This method converts a RawDmapScaler to the byte format written out.

        The bytes are written as a name, then type, then data

        :param scaler: a RawDmapScaler
        :returns: total bytes the scaler will take up

        """

        name = "{0}\0".format(scaler.get_name())
        struct_fmt = '{0}s'.format(len(name))
        name_bytes = struct.pack(struct_fmt, name.encode('utf-8'))
        dmap_type_bytes = struct.pack('c', chr(scaler.get_type()).encode('utf-8'))

        data_type_fmt = scaler.get_datatype_fmt()

        if data_type_fmt == 's':
            data = "{0}\0".format(scaler.get_data())
            struct_fmt = '{0}s'.format(len(data))
            data_bytes = struct.pack(struct_fmt, data.encode('utf-8'))
        elif data_type_fmt == 'c':
            data_bytes = chr(scaler.get_data()).encode('utf-8')
        else:
            data_bytes = struct.pack(data_type_fmt, scaler.get_data())

        total_bytes = name_bytes + dmap_type_bytes + data_bytes

        return total_bytes

    def dmap_array_to_bytes(self, array):
        """This method converts a RawDmapArray to the byte format to be written
        out.

        The format is name,then type, number of dimensions, dimensions,
        array data.

        :param array: a RawDmapArray
        :returns: total bytes the array will take up

        """

        name = "{0}\0".format(array.get_name())
        struct_fmt = '{0}s'.format(len(name))
        name_bytes = struct.pack(struct_fmt, name.encode('utf-8'))

        dmap_type_bytes = struct.pack('c', chr(array.get_type()).encode('utf-8'))

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

#TODO: consider removing this function and get the user to call RawDmapWrite
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
                raise DmapDataError(file_path, message)

    for k, v in ud_types.items():
        if k not in dd:
            message = "DICTS_TO_FILE: Supplied dictionary is missing field {}"\
                    "".format(k)
            raise DmapDataError(file_path, message)
    RawDmapWrite(data_dicts, file_path, ud_types)


# TODO: Remove the unescessary functions
def parse_dmap_format_from_file(filepath, raw_dmap=False):
    """Creates a new dmap object from file and then formats the data results
     into a nice list of dictionaries

    :param filepath: file path to get DMAP data from
    :param raw_dmap: a flag signalling to return the RawDmapRead object
    instead of data dictionaries
    :returns: list of data dictionaries

    """

    dm = RawDmapRead(filepath)

    if raw_dmap is True:
        return dm
    else:
        records = dm.get_records()
        data_list = [dmap_rec_to_dict(rec) for rec in records]

        return data_list


def parse_dmap_format_from_stream(stream, raw_dmap=False):
    """Creates a new dmap object from a stream and then formats the data results
    into a nice list of dictionaries

    :param stream: buffer of raw bytes to convert
    :param raw_dmap: a flag signalling to return the RawDmapRead object
    instead of data dictionaries
    :returns: list of data dictionaries

    """

    dm = RawDmapRead(stream, stream=True)

    if raw_dmap is True:
        return dm
    else:
        records = dm.get_records()
        data_list = [dmap_rec_to_dict(rec) for rec in records]

        return data_list


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


if __name__ == '__main__':
    dm = RawDmapRead('20170410.1801.00.sas.rawacf')
    # records = parse_dmap_format_from_file('testfiles/20150831.0000.03.bks.rawacf')
    # print(records[5])
    # records = parse_dmap_format('20150831.0000.03.bks_corrupt.rawacf')
    # wr = RawDmapWrite(records,"testing.acf")

    # records = parse_dmap_format_from_file('testing.acf')

    # wr = RawDmapWrite(records,"testing.acf")
    # dicts_to_rawacf(records,'testing.acf')
    # records = parse_dmap_format_from_file('testing.acf')
    # print(records[0])

    # gc.collect()
    # records = parse_dmap_format_from_file('20131004.0401.00.rkn.fitacf')
    # print(records[0])
    # gc.collect()
    # print(len(gc.get_objects()))
    # while(True):
    # time.sleep(1)
    # records = parse_dmap_format_from_file('20150831.0000.03.bks.rawacf')
