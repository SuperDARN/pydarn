# Converting Borealis HDF5 to DMap SuperDARN Standard

!!! Warning
    These methods will be removed from pyDARN in the next release. Please use [pyDARNio](https://github.com/SuperDARN/pyDARNio)


The conversions available from Borealis HDF5 to SuperDARN DMap (SDARN) standards
are currently:

| Borealis  | SDarn      |
|-----------|------------|
| rawacf    | rawacf     |
| bfiq      | iqdat      |

If the Borealis file is not provided as one of the required Borealis filetypes,
the conversion will fail with `BorealisConversionTypesError`.

Note that the complexity of the data stored in the Borealis-created file may
mean that conversion is not possible. If this is the case, the code will
throw an error such as `BorealisConvert2IqdatError` or
`BorealisConvert2RawacfError`.

The BorealisConvert class is built off of BorealisRead. It takes the following
parameters:

- `borealis_filename` (to read from),
- `borealis_filetype`,
- `sdarn_filename` (to write to),
- `borealis_slice_id`, and
- `borealis_file_structure` (optional but recommended).

The following will convert a Borealis file (`my_borealis_array_file`) and write
to an SDarn filename (`sdarn_file`):

```python
import pydarn
my_borealis_array_file = "path/to/file"
sdarn_file = "path/to/write/to"

converter = pydarn.BorealisConvert(my_borealis_file, "rawacf",
    sdarn_file, 0, borealis_file_structure='array')
```

Similarly to read and write functions, if the structure is not provided, array
structure is attempted first.

Other information can be gathered from the converter if desired, for example:

```python
borealis_array_data = converter.arrays

sdarn_dictionary = converter.sdarn_dict # python dictionary of the SDarn standard fields.

dmap_records = converter.sdarn_dmap_records
```
