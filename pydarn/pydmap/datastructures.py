""" Copyright 2018 SuperDARN Canada

Author(s): Marina Schmidt

"""
from typing import NamedTuple
from typing import Type
from collections import OrderedDict
import numpy as np


class DmapScalar(NamedTuple):
    """
    NamedTuple class that defines the structure of a DMAP scalar.
    All fields can be accessed using the dot syntx. See DEVELOPER_README
    for more information on NamedTuples.
    """
    name: str
    value: Type[object]  # This allows for any type to be passed in
    data_type: int


class DmapArray(NamedTuple):
    """
    NamedTuple class that defines the structure of a DMAP Array.
    All fields can be accessed using the dot syntax. See DEVELOPER_README
    for more information on NamedTuple.
    """
    name: str
    value: np.array
    data_type: int
    dimension: int
    shape: list


class DmapRecord():
    """
    DMAP Record class that store scalar data and array data into an ordered
    dictionary using the parameter name as the key, for quick O(1) lookup.

    This is a simple encapsulation class.
    """
    def __init__(self, scalar_list=[], array_list=[]):
        """
        :params scalar_list: a list of namedtuples following the DmapScalar
                             structure
        :params array_list: a list of numedtuples following the DmapArray
                            structure
        """
        self.__record = OrderedDict()  # private to avoid setting the record.
        self.num_scalars = 0  # may be useless attributes?
        self.num_arrays = 0

        # store scalars first into the
        self._add_scalar_list(scalar_list)

        # store arrays second into the record
        self._add_array_list(array_list)

    @property
    def record(self):
        """
        A getter for a record.
        """
        return self.__record

    # if we find num_scalars and num_arrays unused then we
    # should look into encapsulating more of this.
    def _add_scalar_list(self, scalar_list=[]):
        """
        Iterate over a scalar list to add each DmapScalar namedtuple into the
        record using the name as the key.

        :param scalar_list: is a list of DmapScalar namedtuples.
        """
        for scalar in scalar_list:
            self.record[scalar.name] = scalar
            self.num_scalars += 1

    def _add_array_list(self, array_list=[]):
        for array in array_list:
            self.record[array.name] = array
            self.num_arrays = 0

    def add_scalar(self, scalar):
        """
        Adds a scalar(s) to the record.

        :param scalar: can be a list or DmapScalar namedtuple that is added
                       into the record.
        """
        if isinstance(scalar, list):
            self._add_scalar_list(scalar)
        else:
            self.record[scalar.name] = scalar
            self.num_scalars += 1

    def add_array(self, array):
        """
        Adds a array(s) to the record.

        :param array: can be a list or DmapArray namedtuple that is added
                       into the record.
        """
        if isinstance(array, list):
            self._add_array_list(array)
        else:
            self.record[array.name] = array
            self.num_array += 1
