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

This tutorial will focus on reading in DMap structured files using Pydarn, including how to access common data fields.

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

## Accessing data fields
To see what you've loaded in, try:
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
where `cpcps` will be a 1D list of all the cross polar-cap potentials in the file.


