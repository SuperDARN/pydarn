# Copyright 2018 SuperDARN Canada
# Author(s): Marina Schmidt
"""
This Module contains dmap data structure for pydarn.

Classes
-------
DmapScalar : named tuple for DMAP scalar data properties
DmapArray : named tuple for DMAP array data properties
DmapRecord : Ordered dictionary that stores Dmap scalars/arrays by their name
as the key and the data structure as the value.

Exceptions
----------
TypeError
    If something does not match the type setting

See Also
--------
namedtuple
OrderedDict
typing : for type setting in python3

Future Work
-----------
Relocation of module
        If cdmap is implemented this may need to live in high folder level for
        shared module and better organization.
Review DmapRecord and its structure
        Not sure if this structure is superfluous

See DEVELOPER_README.md on more information regarding the data structures
and their organization pertaining to DMAP records.
"""
from typing import NamedTuple, Type
from collections import OrderedDict, namedtuple
import numpy as np

"""
NamedTuple class that defines the structure of a DMAP scalar.
All fields can be accessed using the dot syntax. See DEVELOPER_README
for more information on NamedTuples.

Fields
-------
name : str
    the name of the scalar variable
value : data type
    the measure data value for the scalar
data_type : int
    the DMAP numerical value for the data_type
"""
class DmapScalar(NamedTuple):
    name: str
    value: Type[object]
    data_type: str

"""
NamedTuple class that defines the structure of a DMAP Array.
All fields can be accessed using the dot syntax. See DEVELOPER_README
for more information on NamedTuple.

Fields
-------
name : str
    the name of the scalar variable
value : data type
    the measure data value for the scalar
data_type : int
    the DMAP numerical value for the data_type
dimension : int
    The number of dimensions of the array, e.i., 1D, 2D, 3D
shape : list
    A list of dimension sizes of the array
"""
class DmapArray(NamedTuple):
    name: str
    value: np.ndarray
    data_type: str
    dimension: int
    shape: list


# TODO: May not be used anymore.
class DmapRecord():
    """
    DMAP Record class that store scalar data and array data into an ordered
    dictionary using the parameter name as the key, for quick O(1) lookup.

    This is a simple encapsulation class.

    Attributes
    ----------
    num_scalars : int
        the number of scalars in the record
    num_arrays : int
        the number of array in the record

    Methods
    --------
    record
        property getter to get the dmap record which is a private variable for
        security reasons.
    add_scalar
        Adds a DmapScalar or list of DmapScalars into the record
    add_array
        Adds a DmapArray or list of DmapArray into the record
    """
    def __init__(self, scalar_list=[], array_list=[]):
        """
        Setup the dmap record and adds a scalar list and/or array list into
        the record if provided.

        Parameter
        ---------
        scalar_list: list
            A list of namedtuples following the DmapScalar structure
        array_list: list
            A list of namedtuples following the DmapArray structure
        """
        self.__record = OrderedDict()  # private to avoid setting the record.
        self.num_scalars = 0  # may be useless attributes?
        self.num_arrays = 0

        # store scalars first into the
        self._add_scalar_list(scalar_list)

        # store arrays second into the record
        self._add_array_list(array_list)

    @property
    def record(self) -> OrderedDict():
        """
        A getter for the dmap record

        Return
        ------
        __record : OrderedDict
            returns the private dmap record attribute.
        """
        return self.__record

    # TODO If we find num_scalars and num_arrays unused then we
    # should look into encapsulating more of this.
    def _add_scalar_list(self, scalar_list=[]):
        """
        Private method to iterate over a DmapScalar list to add each
        DmapScalar namedtuple into the record using the name as the key.

        Parameter
        ---------
        scalar_list: list
            Is a list of DmapScalar namedtuples.
        """

        for scalar in scalar_list:
            self.record[scalar.name] = scalar
            self.num_scalars += 1

    def _add_array_list(self, array_list=[]):
        """
        Private method to iterate over a DmapArray list to add each
        DmapArray namedtuple into the record using the name as the key.

        Parameter
        ---------
        array_list: list
            Is a list of DmapArray namedtuples.
        """
        for array in array_list:
            self.record[array.name] = array
            self.num_arrays = 0

    def add_scalar(self, scalar):
        """
        Adds a DmapScalar or list of DmapScalars to the record.

        Parameter
        ---------
        scalar: DmapScalar/list
            A DmapScalar or a list of DmapScalars namedtuple that is added
            into the record.

        See Also
        --------
        DmapScalar : named tuple for dmap array variable
        """
        if isinstance(scalar, list):
            self._add_scalar_list(scalar)
        else:
            self.record[scalar.name] = scalar
            self.num_scalars += 1

    def add_array(self, array):
        """
        Adds a DmapArray or list of DmapArrays to the record.

        Parameter
        ---------
        scalar: DmapArray/list
            A DmapArray or a list of DmapArrays namedtuple that is added
            into the record.

        See Also
        ---------
        DmapArray : named tuple for dmap array variables
        """
        if isinstance(array, list):
            self._add_array_list(array)
        else:
            self.record[array.name] = array
            self.num_array += 1
