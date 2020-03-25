# Copyright 2018 SuperDARN Canada
# Author(s): Marina Schmidt
"""
This Module contains dmap data structure for pyDARN.

Classes
-------
DmapScalar : named tuple for DMAP scalar data properties
DmapArray : named tuple for DMAP array data properties

See Also
--------
namedtuple
typing : for type setting in python3

Future Work
-----------
Relocation of module
        If cdmap is implemented this may need to live in high folder level for
        shared module and better organization.
"""
from typing import NamedTuple, Type
import numpy as np


class DmapScalar(NamedTuple):
    """
    NamedTuple DmapScalar class that defines the structure of a DMAP scalar.
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
    name: str
    value: Type[object]
    data_type: chr
    data_type_fmt: str


class DmapArray(NamedTuple):
    """
    NamedTuple DmapArray class that defines the structure of a DMAP Array.
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
    name: str
    value: np.ndarray
    data_type: chr
    data_type_fmt: str
    dimension: int
    shape: list
