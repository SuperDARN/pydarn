# Reading in DMap structured SuperDARN data files
---

!!! Warning
    These methods will be removed from pyDARN in the next release. Please use [pyDARNio](https://github.com/SuperDARN/pyDARNio)


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

## Reading with SDarnRead

The basic code to read in a DMap structured file is as follows:
```python
import pydarn

file = "path/to/file"
SDarn_read = pydarn.SDarnRead(file)
```
which puts the file contents into a Python class called `SDarn_read`. 

Now you need to tell it what kind of file it is. For instance, if the file you were reading in is a FITACF file, you would write something like:
```python
fitacf_data = SDarn_read.read_fitacf()
```
where the named variable `fitacf_data` is a python dictionary list containing all the data in the file. If you were reading a different kind of file, you would need to use the methods `read_iqdat`, `read_rawacf`, `read_grid` or `read_map` for their respective filetypes.

## Reading a compressed file

To read a compressed file like **bz2** (commonly used for SuperDARN data products), you will need to use [bz2 library](https://docs.python.org/3/library/bz2.html). 
The `SDarnRead` class allows the user to provide the file data as a stream of data which is what the **bz2** returns when it reads a compressed file: 
```python
import bz2
import pydarn

fitacf_file = path/to/file.bz2
with bz2.open(fitacf_file) as fp:
      fitacf_stream = fp.read()

reader = pydarn.SDarnRead(fitacf_stream, True)
records = reader.read_fitacf()
```

## Accessing data fields
To see the names of the variables you've loaded in and now have access to, try using the `keys()` method:
```python
print(fitacf_data[0].keys())
```
which will tell you all the variablies in the first [0th] record.

Let's say you loaded in a MAP file, and wanted to grab the cross polar-cap potentials for each record:
```python
file = "20150302.n.map"
SDarn_read = pydarn.SDarnRead(file)
map_data = SDarn_read.read_map()

cpcps=[i['pot.drop'] for i in map_data]
```
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

    reader = pydarn.SDarnRead(fitacf_stream, True)
    records = reader.read_fitacf()
    data += records
print("Reading complete...")
```

## DMapRead

In pyDARN, there also exists a class called `DMapRead`, which you can use in place of SDarnRead to read in any generic DMap structured file. However, Pydarn won't test its integrety as it doesn't know what file it's supposed to be. If you're reading a SuperDARN file from one of the official data mirrors, then it is best to use SDarnRead in general.
