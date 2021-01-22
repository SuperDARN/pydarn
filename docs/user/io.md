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

This tutorial will focus on reading in DMap structured files using Pydarn, including how to read compressed files and access common data fields.

## Reading with SuperDARNRead

The basic code to read in a DMap structured file is as follows:
```python
import pydarn

file = "path/to/file"
SDarn_read = pydarn.SuperDARNRead(file)
```
which puts the file contents into a Python class called `SDarn_read`.

Now you need to tell it what kind of file it is. For instance, if the file you were reading in is a FITACF file, you would write something like:
```python
fitacf_data = SDarn_read.read_fitacf()
```
where the named variable `fitacf_data` is a python dictionary list containing all the data in the file. If you were reading a different kind of file, you would need to use the methods `read_iqdat`, `read_rawacf`, `read_grid` or `read_map` for their respective filetypes.

## Reading a compressed file

To read a compressed file like **bz2** (commonly used for SuperDARN data products), you will need to use [bz2 library](https://docs.python.org/3/library/bz2.html). 
The `SuperDARNRead` class allows the user to provide the file data as a stream of data which is what the **bz2** returns when it reads a compressed file: 
```python
import bz2
import pydarn

fitacf_file = path/to/file.bz2
with bz2.open(fitacf_file) as fp:
      fitacf_stream = fp.read()

reader = pydarn.SuperDARNRead(fitacf_stream, True)
records = reader.read_fitacf()
```
## Generic SuperDARN File Reading
In the previous sections, you needed to tell the code which file you want to open, i.e. `read_fitacf` for a FITACF file. The following method will check to see which file type the file is and open it for you. 

```python
import pydarn
file = "path/to/file"
data = pydarn.SuperDARNRead().read_dmap(file)
```
Currently, this method will open FITACF, RAWACF and IQDAT format files. The method also unzips .bz2 files.

## Accessing data fields
To see the names of the variables you've loaded in and now have access to, try using the `keys()` method:
```python
print(fitacf_data[0].keys())
```
which will tell you all the variablies in the first [0th] record.

Let's say you loaded in a MAP file, and wanted to grab the cross polar-cap potentials for each record:
```python
file = "20150302.n.map"
SDarn_read = pydarn.SuperDARNRead(file)
map_data = SDarn_read.read_map()

cpcps=[i['pot.drop'] for i in map_data]
```
## Converting Borealis Files
Borealis data is often kept in RAWACF or BFIQ data formats. To be able to plot this data they must be converted into a SuperDARN data format.
In pyDARN, you can use the following example code to convert:

```python
import pydarn

borealis_file = "path/to/file"
sdarn_data = pydarn.SuperDARNRead().read_borealis(borealis_file)
```
You can then use the dictionary of data in sdarn_data for your plotting needs.  
In addition, you can select a specific *slice* to convert by assigning `slice_id = 0` in the options. This option is required for files produced before Borealis v0.5 was released.

!!! Warning 
    There may be some issues with using `hdf5` libraries on a Windows machine. pyDARNio will be looking into this bug. 

## Other Examples

Other examples of using pyDARN with file reading is for reading in multiple 2-hour files, sorting them, and concatenating the data together.
For example, you may do something like this, using the **glob** library:

```python
import bz2 
import pydarn 

from glob import glob

fitacf_files = glob('path/to/fitacf/files/<date><radar>.fitacf.bz2')

# assuming they are named via date and time
fitacf_files.sort()
print("Reading in fitacf files")
for fitacf_file in fitacf_files:
    with bz2.open(fitacf_file) as fp:
        fitacf_stream = fp.read()

    reader = pydarn.SuperDARNRead(fitacf_stream, True)
    records = reader.read_fitacf()
    data += records
print("Reading complete...")
``` 

!!! Note 
    If you have any other reading or writing data requirements, please see the io package [pyDARNio](https://pydarnio.readthedocs.io/en/latest/).
