# SuperDARN DMap structured data files 

!!! Warning
    This module will be deprecated from pyDARN after release 1.0 and moved to another python library.

SuperDARN currently supports the following data file types in DMap format:
- IQDAT
- RAWACF
- FITACF
- GRID/GRD
- MAP

pyDARN does not support legacy file types  FIT, and dat 

please see [Borealis IO](user/borealis.md) for new data file types and hdf5 support for some of the above files. 

!!! Note
    If the format is DMap but not listed above then use [DmapRead](user/dmap.md) to read in the file. 

The `DarnRead` and `DarnWrite` classes inherit from `DmapRead` and `DmapWrite` to read the above file types that 
are in DMap format. `DarnRead` and `DarnWrite` also does an additional checks on the files structure to ensure the correct fields are present and erronous fields are not present. 

## DarnRead

See [DarnRead](code/darnread.md) for API documentation, 

### Example of reading in the above file types 

```python
import pydarn
import glob

```

### Example of reading in compressed RAWACF file

## DarnWrite



### Example of trimming SuperDARN files 

```python
import pydarn

fitacf_file = "20180220.C0.rkn.fitacf"
darn = pydarn.DarnRead(fitacf_file)
fitacf_data = darn.read_fitacf()

trimmed_data = []

for record in fitacf_data:
    if record['time.hr'].value < 3: 
        timmed_data.append(record)
    else 
        break

darn = pydarn.DarnWrite(trimmed_data)
darn.write_fitacf("timmed_20180220.00-03.rkn.fitacf")
```

## See Also 

- [DmapRead/DmapWrite](user/dmap.md): Turorial on read SuperDARN standard structure files
- [dict2dmap and dmap2dict](code/ioutilities.md): API documentation on the IO utility functions *dict2dmap* and *dmap2dict*
- [Range-Time Plots](user/range-time.md): example of using `DarnRead` to produce a range-time parameter plot 
- [Time-Series Plots](user/time-series.md): example of using `DarnRead` to produce a time-series plot
- [Summary Plots](user/summary.md): example of using `DarnRead` to produce a summary plot
