""" Copyright 2018 SuperDARN Canada

Author(s): Keith Kotyk and Marina Schmidt

"""
import collections

from pydarn import EmptyFileError, DmapDataError


class Dmapscalar(object):
    """
        Scalar object containing the dmap scalar parameters.
    """
    # 3 means INT idicated in io.py
    def __init__(self, name, mode, data, scalar_type=3, scalar_type_fmt='i'):
        self.scalar_type = scalar_type
        self.name = name # parameter?
        self.mode = mode # is this ther cpid?
        self.data = data # paramater values?
        self.scalar_type_fmt = scalar_type_fmt # what is the difference between scalar type?

    # decorator syntax for property, makes things pythonic
    # read DEVELOPER_README for more information.
    @property
    def scalar_type(self):
        """
        Getter for DMAP scalar type
            :returns: scalar_type
        """
        return self.scalar_type

    @scalar_type.setter
    def scalar_type(self, scalar_type):
        """
        Setter for DMAP scalar type
            :param: scalar_type
        """
        self.scalar_type = scalar_type

    @property
    def name(self):
        """
        Getter the name of the scalar
        :returns: name
        """
        return self.name

    @property
    def mode(self):
        """
        Getter for mode of the scalar
            :returns: mode
        """
        return self.mode

    @property
    def data(self):
        """Returns the scalar data
        :returns: data
        """
        return self.data

    # TODO: might be a simplier way of doing this than storing a
    # string of the data type itself.
    @property
    def datatype_fmt(self):
        """
        Returns the string format identifier of the scalar that
        corresponds to the DMAP type
            :returns: data_type_fmt
        """
        return self.data_type_fmt

    @name.setter
    def name(self, name):
        """Sets the name of the scalar
        :param name: scalar name
        """
        self.name = name

    @mode.setter
    def mode(self, mode):
        """Sets the mode of the scalar
        :param mode: scalar mode
        """
        self.mode = mode

    @data.setter
    def data(self, data):
        """Sets the data of the scalar
        :param data: data for the scalar to contain
        """
        self.data = data

    @datatype_fmt.seeter
    def set_datatype_fmt(self, fmt):
        """Sets the string format identifier of the scalar that
        corresponds to the DMAP type of the scalar
        :param fmt: DMAP type string format of the scalar
        """
        self.data_type_fmt = fmt


class DmapArray(object):
    """
    Holds all the same data that the original C dmap array struct holds +
    some additional type information
    """
    # TODO: review depending on the arrays python type we could probably get the
    # deminsion and lengths another instead of getting the user to enter it.
    def __init__(self, name, data, array_type='i', mode=None, dimention=1, lengths=0, data_type_fmt='i'):
        self.array_type = dmap_type
        self.name = name # parameter?
        self.mode = mode # what is this?
        self.dimension = dimension # how so?
        self.lengths = arr_dimensions
        self.data = data
        self.data_type_fmt = data_type_fmt

    @property
    def array_type(self):
        """Returns the DMAP type of the array
        :returns: dmap_type
        """
        return self.dmap_type

    @property
    def name(self):
        """Returns the name of the array
        :returns: name
        """
        return self.name

    @property
    def mode(self):
        """Returns the mode of the array
        :returns: mode
        """
        return self.mode

    @property
    def dimension(self):
        """Returns the number of dimensions in the array
        :returns: dimension
        """
        return self.dimension

    @property
    def lengths(self):
        """Returns a list of array dimensions
        :returns: arr_dimensions
        """
        return self.arr_dimensions

    @property
    def data(self):
        """Returns the array data
        :returns: data
        """
        return self.data

    @property
    def datatype_fmt(self):
        """Returns the string format identifier of the scalar that
        corresponds to the DMAP type
        :returns: data_type_fmt
        """
        return self.data_type_fmt

    @array_type.setter
    def array_type(self, data_type):
        """Sets the DMAP type of the array
        :param data_type: DMAP type of the array
        """
        self.type = data_type

    @name.setter
    def name(self, name):
        """Sets the name of the array
        :param name: name of the array
        """
        self.name = name

    @mode.setter
    def mode(self, mode):
        """Sets the mode of the array
        :param mode: the mode of the array
        """
        self.mode = mode

    @dimensions
    def dimension(self, dimension):
        """Sets the number of array dimensions
        :param dimension: total array dimensions
        """
        self.dimension = dimension

    @lengths.setter
    def lengths(self, arr_dimensions):
        """Sets the list of dimensions for the array

        :param arr_dimensions: list of dimensions for the array

        """
        self.arr_dimensions = arr_dimensions

    @data.setter
    def data(self, data):
        """Sets the array data
        :param data: the data associated with the array
        """
        self.data = data

    @datatype_fmt.setter
    def datatype_fmt(self, fmt):
        """Sets the DMAP type string format identifier of the array
        :param fmt: the string format identifier
        """
        self.data_type_fmt = fmt


class DmapRecord():
    """
    Contains the arrays and scalars associated with a dmap record.
        :param scalars: A dictionary of scalars in dmap file record.
        :param arrays: A dictionary of the arrays in dmap files record.
    """
    # ChainMaps are a layered lis-dictionarys, very useful in command line arguements as
    # they can layer bases onf priority. They also have some advantages in terms of performance.
    # Please read the DEVELOPER_README for more information on these data structures.

    # scalars and arrays are dictionary for easy O(1) access on the names of the variables
    # needed for future plotting/processing. List will cost O(n) traversing where n is the number of elements.
    def __init__(self, scalars={}, arrays={}):
        # We do not want users to access the data structure in a record, to help
        # avoid any side effects of mutation in the code.
        # maybe this will become public if resetting scalars is really necessary.
        self.__data = collections.ChainMap(scalars, arrays)

    def num_scalars(self):
        """Returns the number of scalars in the DMAP record
        :returns: num_scalars
        """
        return len(self.__data.maps[0])

    def num_arrays(self):
        """Returns the number of arrays in the DMAP record
        :returns: num_arrays
        """
        return len(self.__data.maps[1])

    @property
    def scalars(self):
        """Returns the dictionary of scalars in the DMAP record
        :returns: scalars
        """
        return self.__data.maps[0]

    @property
    def arrays(self):
        """Returns the dictionary of arrays in the DMAP record
        :returns: arrays
        """
        return self.__data.maps[1]

    def add_scalar(self, new_scalar):
        """Adds a new scalar to the DMAP record
        :param new_scalar: new RawDmapscalar to added in dictionary
                           format with name as the key.
                           This allows O(1) lookup in future work.
        """
        self.__data.maps[0].update(new_scalar)

    # TODO: is this needed? or can I delete?
    @scalars.setter
    def scalars(self, scalars):
        """Sets the DMAP scalar list to a new list
        :param scalars: new dictionaty of scalars
        """
        self.__data.maps[0] = scalars

    def add_array(self, new_array):
        """Adds a new array to the DMAP record
        :param new_array: new RawDmapscalar to added in dictionary
                          format with name as the key.
                          This allows O(1) lookup in future work.
        """
        self.__data.maps[1].update(new_scalar)

    @array.setter
    def set_arrays(self, arrays):
        """Sets the DMAP array list to a new list
        :param arrays: new dictioary of arrays
        """
        self.__data.maps[1] = arrays

