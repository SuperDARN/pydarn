<!--Copyright (C) SuperDARN Canada, University of Saskatchewan 
Author(s): Marina Schmidt 
Modifications:

Disclaimer:
pyDARN is under the LGPL v3 license found in the root directory LICENSE.md 
Everyone is permitted to copy and distribute verbatim copies of this license 
document, but changing it is not allowed.

This version of the GNU Lesser General Public License incorporates the terms
and conditions of version 3 of the GNU General Public License, supplemented by
the additional permissions listed below.
-->
# Getting SuperDARN Data 

pyDARN does not provide an interface for downloading data. However, there are other means of getting access to the data. 

The [Data Distribution Working Group (DDWG)](https://github.com/SuperDARN/DDWG) manages the checking and distribution of data. If you have any inquiries, please contact the chair or submit an [issue on DDWG repo](https://github.com/SuperDARN/DDWG/issues)

!!! Note
    If you would like to see a data downloading interface, speak to your local PI and let them know so we can develop it in the future!


## Data Mirrors
To get access to rawacf, fitacf and sometimes higher lever data, there are three possible data servers: one utilizes *Globus*, others use `rsync`, `sftp` and `scp`:

  - [SuperDARN Canada](https://superdarn.ca/): uses [Globus](https://github.com/SuperDARNCanada/globus) to allow access to the SuperDARN data. Contact [superdarn@usask.ca](mailto:superdarn@usask.ca) for access.
  - [BAS](https://www.bas.ac.uk/project/superdarn/#about): information on data access can be found [here](https://www.bas.ac.uk/project/superdarn/#data)
  - [NSSC](https://www.nssdc.ac.cn/nssdc_en/html/task/sdarn.html): please contact NSSC for access.


## RAWACF Data
Raw data with DOI's can be accessed on [FRDR](https://www.frdr-dfdr.ca/repo/collection/superdarn).
These data are published once all gaps are checked and PIs are happy with the collection for each year and no data is under embargo. This process can take up to two years, recent rawacf data can be supplied by the mirrors above. 