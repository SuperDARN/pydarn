# (C) Copyright SuperDARN Canada, University of Saskatchewan
# Author: Carley Martin
#
# Disclaimer:
# pyDARN is under the LGPL v3 license found in the root directory LICENSE.md
# Everyone is permitted to copy and distribute verbatim copies of this license
# document, but changing it is not allowed.
#
# This version of the GNU Lesser General Public License incorporates the terms
# and conditions of version 3 of the GNU General Public License,
# supplemented by the additional permissions listed below.
#
# Modifications:
#


class Citations():
    '''
    A class to contain the different citations for pyDARN use
    
    Parameters
    ----------
    citations with format authorYYYY = str
    '''
    # Groundscatter equation
    bristow1994 = 'Bristow, W. A. et al, 1994, 10.1029/93JA01470 \n'
    # AACGMv3 Wrapper:
    burrell2023 = 'Burrell, A. G. et al, 2023, 10.5281/zenodo.7621545 \n'
    # Cartopy:
    cartopy2015 = 'Met Office, 2010-2015, scitools.org.uk/cartopy \n'
    # Chisham model/ Standard model:
    chisham2008 = 'Chisham, G. 2008, 10.5194/angeo-26-823-2008 \n'
    #pydarn citation:
    pydarn2023 = 'DVWG, 2023, 10.5281/zenodo.3727269 \n'
    #pydarnio citation:
    pydarnio2023 = 'DVWG, 2023, 10.5281/zenodo.4009470 \n'
    # AACGMv2 Paper:
    shepherd2014 = 'Shepherd, S. G., 2014, 10.1002/2014JA020264 \n'
    # elevation angle claculations:
    shepherd2017 = 'Shepherd, S. G., 2017, 10.1002/2017RS006348 \n'
    # GSMR Options:
    thomas2022 = 'Thomas, E. G. et al, 2022, 10.1029/2022RS007429 \n'


    @classmethod
    def print_citations(self):
        print("\nIf using pyDARN produced plots in publications please be "
              "aware of the following citations that may have been used to"
              " produce your plot and should be included in your publication:"
              "\n\n",
              "Ground Scatter Mapped Range: ", self.bristow1994,
              "AACGMv2 Wrapper:             ", self.burrell2023,
              "Chisham Virtual Height Model:", self.chisham2008,
              "pyDARN Software:             ", self.pydarn2023,
              "pyDARNio Software:           ", self.pydarnio2023,
              "Cartopy:                     ", self.cartopy2015,
              "AACGMv2 article:             ", self.shepherd2014,
              "Elevation Angle Calculations:", self.shepherd2017,
              "Ground Scatter Mapped Range: ", self.thomas2022,
              "\nFurther information can be found at"
              " https://pydarn.readthedocs.io/en/main/user/citing/\n")


    @classmethod
    def print_acknowledgements(self):
        print("\nAcknowledgement required for SuperDARN data use:\n\n"
              "\x1B[3m"
              "The authors acknowledge the use of SuperDARN data. "
              "SuperDARN is a collection of radars funded by "
              "national scientific funding agencies of Australia, "
              "Canada, China, France, Italy, Japan, Norway, South "
              "Africa, United Kingdom and the United States of "
              "America."
              "\x1B[0m \n\n"
              "During your study, if using data from individual "
              "radars only, please contact the Principal Investigator "
              "(PI) of that radar about potential co-authorship or "
              "appropriate acknowledgments."
              "\n")
