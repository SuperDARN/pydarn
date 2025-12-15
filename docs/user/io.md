<!--Copyright (C) SuperDARN Canada, University of Saskatchewan 
Author(s): Marina Schmidt 
Modifications:
2020-09-01 Marina Schmidt removed pyDARN IO methods due to deprecation
2020-12-01 Carley Martin add new io method documenation

Disclaimer:
pyDARN is under the LGPL v3 license found in the root directory LICENSE.md 
Everyone is permitted to copy and distribute verbatim copies of this license 
document, but changing it is not allowed.

This version of the GNU Lesser General Public License incorporates the terms
and conditions of version 3 of the GNU General Public License, supplemented by
the additional permissions listed below.
-->


# Reading in DMap structured SuperDARN data files
---

Data Map (DMap) is a binary self-describing format that was developed by Rob Barnes. 
This format is currently the primary format used by SuperDARN. 
For more information on DMap please see [RST Documentation](https://radar-software-toolkit-rst.readthedocs.io/en/latest/).
Types of files used by SuperDARN which are usually accessed in DMap format are:
- IQDAT
- RAWACF
- FITACF
- GRID/GRD
- MAP
- SND

This tutorial will focus on reading in DMap structured files using pyDARN, including how to read compressed files and access common data fields.

## Reading in files

The basic code to read in a DMap structured file is as follows:
```python
import pydarn

file = "path/to/file"
data, corruption_start = pydarn.read_dmap(file)
```
which puts the file contents into a list of dictionaries, with each dictionary containing one DMap record. If the input file
is corrupted, the second return value will be the byte where the corrupted records start. If the file is not corrupted, it will
be `None`.

The function `read_dmap()` is able to read any DMap file type, but will not check to ensure that all fields for a given
DMap file type are there. There are specific I/O functions that will conduct these checks:
```python
iqdat_data, _ = pydarn.read_iqdat(iqdat_file)
rawacf_data, _ = pydarn.read_rawacf(rawacf_file)
fitacf_data, _ = pydarn.read_fitacf(fitacf_file)
grid_data, _ = pydarn.read_grid(grid_file)
map_data, _ = pydarn.read_map(map_file)
snd_data, _ = pydarn.read_snd(snd_file)
```
Note that if you pass a file of the incorrect type into one of these functions, it will raise an exception.
Another thing to note is that whether you read a file in using `read_dmap()` or one of the specific functions
like `read_rawacf()`, you will get the same data either way.

## Reading a compressed file

pyDARN can seamlessly read a compressed file like **bz2** (commonly used for SuperDARN data products). 
The I/O functions in the section above will detect `.bz2` compression, and handle decompression automatically. 
```python
import pydarn
fitacf_file = "path/to/file.bz2"
records, _ = pydarn.read_fitacf(fitacf_file)
```

## Accessing data fields
To see the names of the variables you've loaded in and now have access to, try using the `keys()` method:
```python
print(fitacf_data[0].keys())
```
which will tell you all the variables in the first [0th] record.

Let's say you loaded in a MAP file, and wanted to grab the cross polar-cap potentials for each record:
```python
file = "20150302.n.map"
map_data, _ = pydarn.read_map(file)

cpcps=[i['pot.drop'] for i in map_data]
```
## Converting Borealis Files
Borealis data is often kept in RAWACF or BFIQ data formats. To be able to plot this data they must be converted into a SuperDARN data format.
In pyDARN, you can use the following example code to convert:

```python
import pydarn

borealis_file = "path/to/file"
sdarn_data = pydarn.read_borealis(borealis_file)
```
You can then use the dictionary of data in sdarn_data for your plotting needs.  
In addition, you can select a specific *slice* to convert by assigning `slice_id = 0` in the options. This option is required for files produced before Borealis v0.5 was released.

!!! Warning 
    There may be some issues with using `hdf5` libraries on a Windows machine. pyDARNio will be looking into this bug. 

## Other Examples

Other examples of using pyDARN with file reading is for reading in multiple 2-hour files, sorting them, and concatenating the data together.
For example, you may do something like this, using the **glob** library:

```python
import pydarn 
from glob import glob

fitacf_files = glob('path/to/fitacf/files/<date><radar>.fitacf.bz2')
data = list()

# assuming they are named via date and time
fitacf_files.sort()
print("Reading in fitacf files")
for fitacf_file in fitacf_files:
    records, _ = pydarn.read_fitacf(fitacf_file)
    data += records
print("Reading complete...")
``` 

!!! Note 
    If you have any other reading or writing data requirements, please see the io package [pyDARNio](https://pydarnio.readthedocs.io/en/latest/).
