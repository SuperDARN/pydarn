<!--Copyright (C) SuperDARN Canada, University of Saskatchewan 
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

# Publications used within pyDARN

If pyDARN contributes to a project that leads to a scientific publication, please acknowledge this fact by acknowledging the software and citing relevant publications used within the software. 
You can print the citations in command line by using the Citations class. 

```python
import pydarn

pydarn.Citations.print_citations()

```

```
If using pyDARN produced plots in publications please be aware of the following citations that may have been used to produce your plot:

 Ground Scatter Mapped Range:  Bristow, W. A. et al, 1994, 10.1029/93JA01470 
 AACGMv2 Wrapper:              Burrell, A. G. et al, 2023, 10.5281/zenodo.7621545 
 Chisham Virtual Height Model: Chisham, G. 2008, 10.5194/angeo-26-823-2008 
 pyDARN Software:              DVWG, 2023, 10.5281/zenodo.3727269 
 pyDARNio Software:            DVWG, 2023, 10.5281/zenodo.4009470 
 Cartopy:                      Met Office, 2010-2015, scitools.org.uk/cartopy 
 AACGMv2 article:              Shepherd, S. G., 2014, 10.1002/2014JA020264 
 Elevation Angle Calculations: Shepherd, S. G., 2017, 10.1002/2017RS006348 
 Ground Scatter Mapped Range:  Thomas, E. G. et al, 2022, 10.1029/2022RS007429

```

These citations refer to methods or codebases previously published that are used in the pyDARN software, cited below.

- Bristow, W. A., Greenwald, R. A., and Samson, J. C. (1994), Identification of high-latitude acoustic gravity wave sources using the Goose Bay HF Radar, J. Geophys. Res., 99( A1), 319– 331, doi:10.1029/93JA01470.
- Chisham, G., Yeoman, T. K., and Sofko, G. J.: Mapping ionospheric backscatter measured by the SuperDARN HF radars – Part 1: A new empirical virtual height model, Ann. Geophys., 26, 823–841, https://doi.org/10.5194/angeo-26-823-2008, 2008.
- Shepherd, S. G. (2014), Altitude-adjusted corrected geomagnetic coordinates: Definition and functional approximations, J. Geophys. Res. Space Physics, 119, 7501– 7521, doi:10.1002/2014JA020264.
- Shepherd, S. G. (2017), Elevation angle determination for SuperDARN HF radar layouts, Radio Sci., 52, 938– 950, doi:10.1002/2017RS006348.
- Thomas, E. G., & Shepherd, S. G. (2022). Virtual height characteristics of ionospheric and ground scatter observed by mid-latitude SuperDARN HF radars. Radio Science, 57, e2022RS007429. https://doi.org/10.1029/2022RS007429

# How to cite the SuperDARN Community

Super Dual Auroral Radar Network (SuperDARN) is a made up of 40+ radars and 20 institutions. 
To generally cite SuperDARN you can use: 

- Greenwald, R.A., Baker, K.B., Dudeney, J.R. et al. Space Sci Rev (1995) 71: 761. [doi:10.1007/BF00751350](https://doi.org/10.1007/BF00751350)

For the general achievements of the SuperDARN Network, you can read these papers: 

- Chisham, G., Lester, M., Milan, S.E. et al. A decade of the Super Dual Auroral Radar Network (SuperDARN): scientific achievements, new techniques and future directions. Surv Geophys 28, 33–109 (2007) [doi:10.1007/s10712-007-9017-8](https://link.springer.com/article/10.1007/s10712-007-9017-8)
- Nishitani, N., Ruohoniemi, J.M., Lester, M. et al. Review of the accomplishments of mid-latitude Super Dual Auroral Radar Network (SuperDARN) HF radars. Prog Earth Planet Sci 6, 27 (2019) [doi:10.1186/s40645-019-0270-5](https://progearthplanetsci.springeropen.com/articles/10.1186/s40645-019-0270-5)

During your study, if using data from individual radars only, please contact the Principal Investigator (PI) of that radar about potential co-authorship. 
A list of radars, institutions, and their PI's information can be found [here](https://superdarn.ca/radar-info).

Virginia Tech SuperDARN group has developed a data validation tool to help you include the correct citations and contact the correct PI's: [Data Validation Tool](http://vt.superdarn.org/data-usage)

## Acknowledgements

All publications that use SuperDARN Data must contain the following acknowledgement:

*The authors acknowledge the use of SuperDARN data. SuperDARN is a collection of radars funded by national scientific funding agencies of Australia, Canada, China, France, Italy, Japan, Norway, South Africa, United Kingdom and the United States of America.* 

This phrase can be accessed using the Citations class as shown below:


```python
import pydarn

pydarn.Citations.print_acknowledgements()

```

```
Acknowledgement required for SuperDARN data use:

The authors acknowledge the use of SuperDARN data. SuperDARN is a collection of radars funded by national scientific funding agencies of Australia, Canada, China, France, Italy, Japan, Norway, South Africa, United Kingdom and the United States of America. 

During your study, if using data from individual radars only, please contact the Principal Investigator (PI) of that radar about potential co-authorship or appropriate acknowledgments.

```

# Citing pyDARN

If pyDARN is used in a publication, we would like to be able to easily track this to show how widely used pyDARN is. 
Please either cite using the version DOI's below or acknowledge the use of the software in your acknowledgements section, giving the version or DOI of the software for reproducibility. 

## DOI's 

- Release 1.0 [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3727270.svg)](https://doi.org/10.5281/zenodo.3727270)
- Release 1.1.0 [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3978643.svg)](https://doi.org/10.5281/zenodo.3978643)
- Release 2.0 [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4549096.svg)](https://doi.org/10.5281/zenodo.4549096)
- Release 2.0.1 [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4558130.svg)](https://doi.org/10.5281/zenodo.4558130)
- Release 2.1 [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4958007.svg)](https://doi.org/10.5281/zenodo.4958007)
- Release 2.2 [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5605069.svg)](https://doi.org/10.5281/zenodo.5605069)
- Release 2.2.1 [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5762322.svg)](https://doi.org/10.5281/zenodo.5762322)
- Release 3.0 [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6473574.svg)](https://doi.org/10.5281/zenodo.6473574)
- Release 3.1 [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7468856.svg)](https://doi.org/10.5281/zenodo.7468856)
- Release 3.1.1 [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7767590.svg)](https://doi.org/10.5281/zenodo.7767590)
- Release 4.0 [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10452339.svg)](https://doi.org/10.5281/zenodo.10452339)
- Release 4.1 [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.13694617.svg)](https://doi.org/10.5281/zenodo.13694617)
- Release 4.1.1 [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14796490.svg)](https://doi.org/10.5281/zenodo.14796490)
- Release 4.1.2 [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15441879.svg)](https://doi.org/10.5281/zenodo.15441879)


## Python Library References 

#### Matplotlib
John D. Hunter. Matplotlib: A 2D Graphics Environment, Computing in Science & Engineering, 9, 90-95 (2007), [DOI:10.5281/zenodo.3264781](https://zenodo.org/record/3264781)

#### Numpy 
Stéfan van der Walt, S. Chris Colbert and Gaël Varoquaux. The NumPy Array: A Structure for Efficient Numerical Computation, Computing in Science & Engineering, 13, 22-30 (2011), [DOI:10.1109/MCSE.2011.37](https://ieeexplore.ieee.org/document/5725236)

#### pyDARNio

SuperDARN Data Visualization Working Group, Rohel et al. [Zenodo Link](https://doi.org/10.5281/zenodo.4009470)

#### AACGM

Angeline G. Burrell, Christer van der Meeren, Karl M. Laundal, & Hugo van Kemenade. [Zenodo Link](https://doi.org/10.5281/zenodo.1212694)

Shepherd, S. G. (2014), Altitude‐adjusted corrected geomagnetic coordinates: Definition and functional approximations, Journal of Geophysical Research: Space Physics, 119, 7501–7521, doi:10.1002/2014JA020264.
