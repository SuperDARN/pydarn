# Pydarn 

Is a SuperDARN data plotting and data visualization library. 

## Getting Started 

The following instructions will allow you to install and give some examples on how to use pydarn. 

### Prerequisites

Python Version: **python 3+**

### Installing 

1. Clone git repository:   
   `git clone https://github.com/SuperDARN/pydarn.git`

2. Install pydarn 
  1. **Recommended** Install in a [virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtualenv/):   
    This option allows the library to install needed version of libraries   
    without affecting system libraries. First install the environment:  
    `python3 -m pip install --user virtualenv`  
    `python3 -m virtualenv <environment name>`  
		`source <environment name>/bin/activate`  
		Now install pydarn:  
		navigate to where you cloned pydarn:  
		`python3 setup.py install`  
	2. Install in the system (root privileges required):  
		`sudo python3 setup.py install`

### Example 

#### Reading DMAP file 
DMAP files are SuperDARN's data file type. They are in binary format so not human readable unless 
read in and converted in software. 

```python
import pydarn
dmap_file = "./20180410.C0.sas.fitacf"
damp_reader = pydarn.DmapRead(dmap_file)
dmap_data = dmap_reader.read_records() 
```





