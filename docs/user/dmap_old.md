# Reading and Writing DMap format files
Please see API documentation on [`DmapRead`](code/DmapRead.md) and [`DmapWrite`](code/DmapWrite.md) for information on class methods and attributes. 

Data Map (DMap) is a binary self-describing format that was developed by Rob Barnes. 
This format is currently the primary format used by SuperDARN. 
For more information on DMap please see [RST Documentation](https://radar-software-toolkit-rst.readthedocs.io/en/latest/). 

pyDARN provides two classes to read (*DmapRead*) and write (DmapWrite) DMap formated files. 

!!! Note
    After pyDARN release 1.0, these modules will be moved to it's own python library. 

## DmapRead 

*DmapRead* reads DMap format files and data streams. 
Here are some examples on how to use the class:

### Read from a file

```python
import pydarn

dmap_file = "20180220.C0.rkn.fitacf"
dmap_read = pydarn.DmapRead(fitacf_file)
dmap_data = dmap_read.read_records()
```

Accessing data from pyDARN Dmap structure:
```python
# loop over every record in the dmap structure
for dmap_rec in dmap_data:
  # check if the beam number is 7  
  if dmap_rec['bmnum'].value == 7:
    # print the channel number for that record 
    # corresponding to beam number 7 
    print(dmap_rec['channel'].value)
```

To convert to python dictionary:
```python
dmap_dict = pydarn.dmap2dict(dmap_data)
```

Accessing data from a python dictionary:
```python
# loop over every record in the dmap structure
for dmap_rec in dmap_data:
  # check if the beam number is 7  
  if dmap_rec['bmnum'] == 7:
    # print the channel number for that record 
    # corresponding to beam number 7 
    print(dmap_rec['channel'])
```

### Read from a compressed file 

Reading from a `bzip2` compressed file (extension of the file would be *bz2*):
```python
import pydarn
import bz2

dmap_file = ""20170410.1801.00.sas.stream.rawacf.bz2

# does not unzip the actual file but uncompresses it in memory
with bz2.open(rawacf_stream) as fp:
    dmap_stream = fp.read()

# compressed data is stored as a data stream, so stream = True
dmap = pydarn.DmapRead(dmap_stream, True)
dmap_data = dmap.read_records()

```

### Reading multiple files

Reading multiple DMap formatted files via list:
```python
import pydarn 
import glob 

# Initialize empty DMap data list 
dmap_list = []

# list of files 
dmap_files = [""]

# loop over the list of files and read them in
for dmap_file in dmap_files:
  dmap = pydarn.DmapRead(dmap_file)
  dmap_list.append(dmap.read_records())
```


Reading multiple DMap formatted file via [`glob`](https://docs.python.org/3/library/glob.html):
```python
import pydarn 
import glob 

# Initialize empty DMap data list 
dmap_list = []

# obtain a list of files with the file extension of fitacf
dmap_files = glob.glob('*.rawacf')

# loop over the list of files and read them in
for dmap_file in dmap_files:
  dmap = pydarn.DmapRead(dmap_file)
  dmap_list.append(dmap.read_records())
```

## DmapWrite

Writes a file in DMap format.
The data types that are supported in DMap format are:

| Data type name | binary character representation | DMap number representation | python representation |
|----------------|----                      |---                  |---                    |
| char      | c                      | 1                   | `numpy.int8`          |
| short | h | 2 | `numpy.int16` |
| integer | i | 3 | `numpy.int32`, `int` |
| float | f | 4 | `numpy.float32`, `float` | 
| double | d | 8 | `numpy.float64`, `double` | 
| string | s | 9 | `str`, `numpy._str`, `numpy.str` | 
| long | q | 10 | `numpy.int64` | 
| unsigned char | B | 16 | `numpy.uint8` |
| unsigned short | H | 17 | `numpy.uint16` | 
| unsigned int | I | 18 | `numpy.unint32` | 
| unsigned long | Q | 19 | `numpy.unint64`|


### DMap Writing limitations

Currently DMap does not support:
- *C-type* characters which is a single letter, instead you will need to define it as a *string* type.
- string arrays, due to how DMap implements strings in binary

### Simple writing example with DmapArray and DmapScalar objects

pyDARN uses *DmapArray* and *DmapScalar* objects to represent the DMap array and scalar binary structures. 

```python
import pydarn

array = pydarn.DmapArray('qflg', np.array([1, 0, 1]),
                          1, 'c', 1, [3])

scalar = pydarn.DmapScalar('channel', 0, 1, 'c')
dmap_write = pydarn.DmapWrite([{'qflg': array, 
                                'channel': scalar}])
dmap_file = dmap_write.write_dmap("example.dmap")

```
However, this is inconvenient to users who are not as familiar with the DMap structure. 
Thus, with the function *dict2dmap* the user can convert a python dictionary to a DMap array or scalar structure. 

When using a python `dict` to DMap structure it is **highly** adviced to cast python representation types (see table abobe) and for arrays make sure to use `numpy.array` to set the  *dtype* attribute.  

```python
# import numpy library to define DmapArray types
import numpy 
import pydarn

# dictionary of fields
data_dict = {'channel': numpy.int8(0), # defining a character field called channel with 0 as its value 
             'bmnum': numpy.int16(16), # beam number field with a value of 16 as a short type
             'qflg': numpy.array([1, 0, 1], dtype=numpy.int8)} # create an array called qflg with DMap char types
dmap_data = pydarn.dict2dmap(data_dict)
dmap_write = pydarn.DmapWrite(dmap_data)
dmap_file = dmap_write.write_dmap("example_dict.dmap")
```
[Next Tutorial](user/darn.md)

## See Also:

- [DarnRead/DarnWrite](user/darn.md): Turorial on read SuperDARN standard structure files
- [dict2dmap and dmap2dict](code/ioutilities.md): API documentation on the IO utility functions *dict2dmap* and *dmap2dict*
- [DmapArray](code/DmapArray.md): API documentation on *DmapArray* array structure for DMap array types 
- [DmapScalar](code/DmapScalar): API documentation on *DmapScalar* scalar structure for DMap  scalar '' 
- [DarnRead](code/DarnRead.md): API documentation on *DarnRead*
- [DarnWrite](code/DarnWrite.md): API documentation on *DarnWrite*

    
