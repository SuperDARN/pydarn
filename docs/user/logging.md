<!--Copyright (C) SuerDARN Canada, University of Saskatchewan 
Author(s): Marina Schmidt 
Modifications:
2020-12-01 Carley Martin updated documentation

Disclaimer:
pyDARN is under the LGPL v3 license found in the root directory LICENSE.md 
Everyone is permitted to copy and distribute verbatim copies of this license 
document, but changing it is not allowed.

This version of the GNU Lesser General Public License incorporates the terms
and conditions of version 3 of the GNU General Public License, supplemented by
the additional permissions listed below.
-->


# Logging

pyDARN supports python [logging library](https://docs.python.org/3/library/logging.html) and can be used in debugging or checking on the status of the library. 

## How to use

Use `logging.basicConfig()` to set various configurations include logging levels. 
pyDARN supports various levels of logging:

- `INFO`: provided info and status of where the pyDARN are at in functionality 
- `DEBUG`: provides extra information useful for debugging 
- `ERROR`: provides exceptions error information 

*Example*

```python
import pydarn
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
#Load in dmap file
file = "20170410.1801.00.sas.fitacf_30"
SDarn_read = pydarn.SuperDARNRead(file)
fitacf_data = SDarn_read.read_fitacf()
```

Will yield the output:
```bash
python3 test_read.py 
INFO:pydarn:DMap Read file: 20170410.1801.00.sas.fitacf_30
INFO:pydarn:Reading Fitacf file: 20170410.1801.00.sas.fitacf_30
```

If you set the `logging.basicConfig(level=logging.DEBUG)`, you will get the following output:

```bash
INFO:pydarn:DMap Read file: 20170410.1801.00.sas.fitacf_30
INFO:pydarn:Reading Fitacf file: 20170410.1801.00.sas.fitacf_30
DEBUG:pydarn:Reading Record 0
DEBUG:pydarn:Reading record: reading scalars

DEBUG:pydarn:Reading record: reading arrays

DEBUG:pydarn:Reading Record 1
DEBUG:pydarn:Reading record: reading scalars

DEBUG:pydarn:Reading record: reading arrays

DEBUG:pydarn:Reading Record 2
DEBUG:pydarn:Reading record: reading scalars

DEBUG:pydarn:Reading record: reading arrays

DEBUG:pydarn:Reading Record 3
DEBUG:pydarn:Reading record: reading scalars

DEBUG:pydarn:Reading record: reading arrays

DEBUG:pydarn:Reading Record 4
DEBUG:pydarn:Reading record: reading scalars

DEBUG:pydarn:Reading record: reading arrays
```
