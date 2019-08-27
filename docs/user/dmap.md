# Dmap Classes 

!!! Warning
    This module of pyDARN will be removed after the first release and will become its own package.

Please see for API documentation on [`DmapRead`](code/DmapRead.md) and [`DmapWrite`](code/DmapWrite.md). 

Data Map (DMap) Self-Describing Format was developed by Rob Barnes and is primary format used by SuperDARN. 
For more information on DMap please see [RST Documentation](https://radar-software-toolkit-rst.readthedocs.io/en/latest/). 

pyDARN provides two methods that reads and writes DMap formatted files. 

## DmapRead 

`DmapRead` reads Dmap format files and data streams. 
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

Write DMap file:
```python
import pydarn

array = pydarn.DmapArray('qflg', np.array([1, 0, 1]),
                          1, 'c', 1, [3])

scalar = pydarn.DmapScalar('channel', 0, 1, 'c')
dmap_write = pydarn.DmapWrite([{'qflg': array, 
                                'channel': scalar}])
dmap_file = dmap_write.write_dmap("example.dmap")

```
