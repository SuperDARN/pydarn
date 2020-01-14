<!--Copyright (C) SuerDARN Canada, University of Saskatchewan 
Author(s): Marina Schmidt -->
# Hardware Files

SuperDARN Radar hardware information is stored in hardware files located [here](https://github.com/vtsuperdarn/hdw.dat). 
pyDarn pulls down the hardware files from the `master` branch on the [repository](https://github.com/vtsuperdarn/hdw.dat) to obtain geological and hardware information. 

Users can also access and read these hardware files using the function `read_hdw_file`.
``` python 
import pydarn

# Read Saskatoon's hardware file
hdw_data = pydarn.read_hdw_file('sas')
print(hdw_data.geological))
```
expected output: 
``` python 

```


