# Reading in Borealis HDF5 structured SuperDARN data files
---

HDF5 (Hierarchical Data Format v5) is a user-friendly data format that supports
heterogeneous data, allows for easy sharing, is cross platform, has fast I/O
with storage space optimizations, has no limit on dataset size inside the file,
and supports keeping metadata with the data in the file. For more on
HDF5, see the website of the [HDF Group](www.hdfgroup.org).

The Borealis software writes data files in HDF5 format. The files written on
site are written record-by-record, in a similar style to the SuperDARN standard
dmap format. These files are named with a .site extension. The types of files
that can be produced are:
- RAWRF
    This is the raw samples at the receive bandwidth rate. This is rarely
    produced and only would be done by request.
- ANTENNAS_IQ
    Decimated and filtered data from individual antennas, i and q samples.
- BFIQ
    Beamformed i and q samples. Typically two array datasets are included,
    for main array and interferometer array.
- RAWACF
    The correlated data given as lags x ranges, for the two arrays.


After recording, the files are array restructured using pyDARN for distribution.
The restructuring process is built into the IO so that if you would like to see
the record-by-record data, you can simply return the records attribute of the
IO class. Similarly, if you would like to see the data in the arrays format,
return the arrays attribute.

Borealis files can also be converted to the standard SuperDARN DMap formats
using pyDARN. Examples of this will be shown below.

## Reading with BorealisRead

## Restructuring with BorealisRead, BorealisWrite

## Converting to DMap SuperDARN Standard

The basic code to read in a Borealis HDF5 structured file is as follows:

```python
import pydarn

file = "path/to/file"
Borealis_read = pydarn.BorealisRead(file)
```
which puts the file contents into a Python class called `SDarn_read`.

Now you need to tell it what kind of file it is. For instance, if the file you were reading in is a FITACF file, you would write something like:
```python
fitacf_data = SDarn_read.read_fitacf()
```
where the named variable `fitacf_data` is a python dictionary list containing all the data in the file. If you were reading a different kind of file, you would need to use the methods `read_iqdat`, `read_rawacf`, `read_grid` or `read_map` for their respective filetypes.

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