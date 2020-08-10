# Reading in Borealis HDF5 structured SuperDARN data files
---

!!! Warning
    These methods will be removed from pyDARN in the next release. Please use [pyDARNio](https://github.com/SuperDARN/pyDARNio)

HDF5 (Hierarchical Data Format v5) is a user-friendly data format that supports
heterogeneous data, allows for easy sharing, is cross platform, has fast I/O
with storage space optimizations, has no limit on dataset size inside the file,
and supports keeping metadata with the data in the file. For more on
HDF5, see the website of the [HDF Group](www.hdfgroup.org).

The Borealis software writes data files in HDF5 format. The files written on
site are written record-by-record, in a similar style to the SuperDARN standard
dmap format. These files are named with a .site extension and are said to be
`'site'` structured.

After recording, the files are array restructured using pyDARN, for distribution.
The restructuring is done to make the files more human-readable, and it also
reduces the file size. After restructuring the files are said to be `'array'`
structured.

Restructuring reduces repetition by writing file-wide parameters only once,
and writing integration-specific parameters in arrays where the first
dimension is the record index.

The restructuring process is fully built into the IO so that if you would like to see
the record-by-record data, you can simply return the record's attribute of the
IO class for any Borealis file. Similarly, if you would like to see the data in
the arrays format, return the arrays attribute. This works regardless of how
the original file was structured.

In addition to file structure, there are various types of datasets (filetypes)
that can be produced by Borealis. The filetypes that can be produced are:


- `'rawrf'`
This is the raw samples at the receive bandwidth rate. This is rarely
produced and only would be done by request.


- `'antennas_iq'`
Decimated and filtered data from individual antennas, i and q samples.


- `'bfiq'`
Beamformed i and q samples. Typically two array data sets are included,
for main array and interferometer array.


- `'rawacf'`
The correlated data given as lags x ranges, for the two arrays.

Borealis files can also be converted to the standard SuperDARN DMap formats
using pyDARN.

## Reading with BorealisRead

BorealisRead class takes 3 parameters:

- `filename`,
- `borealis_filetype`, and
- `borealis_file_structure` (optional but recommended).

The BorealisRead class can return either array or site structured data,
regardless of the file's structure. Note that if you are returning the structure
that the file was not stored in, it will require some processing time.

Here's an example:

```python
import pydarn

bfiq_site_filename = "path/to/bfiq_site_file"
borealis_reader = pydarn.BorealisRead(bfiq_site_filename, 'bfiq', 'site')

# We can return the original data from the site file. This will be a dictionary
# of dictionaries.
record_data = borealis_reader.records

# For site structured data, it is often helpful to have the record names alone
# in order to retrieve the data from the fields within the record.
record_names = borealis_reader.record_names

# We can also get the data in array structured format. Beware that this
# will require some processing. This will be a dictionary.
array_data = borealis_reader.arrays
```

If you don't supply the borealis_file_structure parameter, the reader will
attempt to read the file as array structured first (as this should be the most
common structure available to the user), and following failure will attempt to
read as site structured.

```python
import pydarn

rawacf_array_filename = "path/to/rawacf_array_file"
borealis_reader = pydarn.BorealisRead(rawacf_array_filename, 'rawacf')

print(borealis_reader.borealis_file_structure) # confirm it was array structured

# We can return the original data from the array file
array_data = borealis_reader.arrays

# We can also get the data in the site structured format. Again, beware that
# this will require some processing.
record_data = borealis_reader.records
```

## Accessing Data Fields in a Borealis Dataset

The method of accessing data fields will vary depending on if you have loaded
site data or array data. In both cases, you can use the `keys()` method.

For site files, to see all the data fields in the first record:
```python
record_names = borealis_reader.record_names
first_record_name = record_names[0]
print(record_data[first_record_name].keys())
```

For array files, to see all the data fields available for all the records:
```python
print(array_data.keys())
```

For more information on the data fields available in both array structured
and site structured files (they vary slightly), see the Borealis documentation
[here](https://borealis.readthedocs.io/en/latest/borealis_data.html).

## Writing with BorealisWrite

The BorealisWrite class takes 4 parameters:

- `filename`,
- `borealis_data`,
- `borealis_filetype`, and
- `borealis_file_structure` (optional but recommended).

Here's an example that will write `my_rawacf_data` to `my_file`:

```python
import pydarn

my_rawacf_data = borealis_reader.arrays

my_file = "path/to/file"
writer = pydarn.BorealisWrite(my_file, my_rawacf_data, 'rawacf', 'array')
```

Similar to reading files, if you don't supply the borealis_file_structure
parameter, the writer will attempt to write the file as array structured first,
and following failure will attempt to write as site structured.

```python
import pydarn

my_rawacf_data = borealis_reader.arrays

my_file = "path/to/file"
writer = pydarn.BorealisWrite(my_file, my_rawacf_data, 'rawacf')

print(writer.borealis_file_structure)  # to check the file structure written
```
