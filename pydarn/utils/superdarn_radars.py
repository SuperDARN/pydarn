# Copyright (C) SuperDARN Canada, University of Saskatchewan
# Authors: Marina Schmidt and Danno Peters

"""
This module contains SuperDARN radar information
"""
import os

from typing import NamedTuple
from enum import Enum
from datetime import datetime

class _Hemisphere(Enum):
    """
    Class used to denote which hemisphere a radar is located in

    Attributes
    ----------
    _Hemisphere.North = 1
    _Hemisphere.South = -1

    Notes
    -----
    This is based on the values assigned to the MAP file hemisphere
    field in RST>
    """
    North = 1
    South = -1

class _InterferometerOffset(NamedTuple):
    x: float
    y: float
    z: float

class _Coord(NamedTuple):
    """
    Class used to store Geo Coordinates (utilized for both Geographic
    and Geomagnetic) representing location and Boresite direction

    Attributes
    ----------
    lat : float
        Latitude in decimal format
    lon : float
        Longitude in decimal format
    bore : float
        Boresight in decimal format
    """
    lat: float
    lon: float
    alt: float

class _Radar(NamedTuple):
    """
    Class used to combine all Radar information
    Attributes
    ----------
    name: str
        Name of the Radar
    institute: str
        Institution of the Radar
    hemisphere: _Hemisphere
        Hemisphere the radar belongs to
    hardware_info: _HdwInfo
        NamedTuple containing all hardware information from hardware files
    """
    name: str
    institution: str
    hemisphere: _Hemisphere
    hardware_info: _HdwInfo

class _HdwInfo(NamedTuple):
    """
    Class used to store relevant information about the SuperDARN Radars

    Attributes
    ----------
    name : str
        full text of radar name
    stid : int
        station number
    abbrev : str
        three letter station abbreviation
    beams : int
        number of possible beams
    gates :int
        number of range gates per beam
    geographic : _Coord object
        Named Tuple containing geographic latitude longitude and Boresite
    geomagnetic : _Coord object
        Named Tuple containing geomagnetic latitude longitude and Boresite
    hemisphere : _Hemisphere enum
        Hemisphere the radar is associated with: North or South
    institute : str
        full text name of institution operating the radar site
    decommissioned : datetime object
        date radar was decommissioned (shut down)
    commissioned : datetime object
        sate radar was officially commissioned (data considered stable)
    beamSep : float
        angular separation between radar beams

    See Also
    --------
    _Hemisphere : enum for North and South hemisphere
    _Coord : object contain coordinate information
    """
    stid: int
    abbrev: str
    beams: int
    gates: int
    geographic: _Coord
    geomagnetic: _Coord
    hemisphere: _Hemisphere
    beamSep: float

class SuperDARNRadars():
    """
    Class containing a dictionary of Nested Named Tuples with information
    about each radar in SuperDARN.

    Attributes
    ----------
        radars: dict
            dictionary of each SuperDARN radar with key being STID value
    """
    # Information obtained from http://vt.superdarn.org/tiki-index.php?page=Radar+Overview
    radars = {209: _Radar('Adak Island East',
                          'University of Alaska Fairbanks', _Hemisphere.North,
                          self.read_hdw_file('ade')),
              208: _Radar('Adak Island West', 'University of Alaska Fairbanks',
                          _Hemisphere.North, self.read_hdw_file('adw')),
              33: _Radar('Blackstone', 'Virginia Tech', _Hemisphere.North,
                         self.read_hdw_file('bks')),
              207: _Radar('Christmas Valley East', 'Dartmouth College',
                          _Hemisphere.North, self.read_hdw_file('cve')),
              206: _Radar('Christmas Valley West', 'Dartmouth College',
                          _Hemisphere.North, self.read_hdw_file('cvw')),
              66: _Radar('Clyde River', 'University of Saskatchewan',
                         _Hemisphere.North, self.read_hdw_file('cly')),
              205: _Radar('Fort Hays East', 'Virginia Tech', _Hemisphere.North,
                          self.read_hdw_file('fhe')),
              204: _Radar('Fort Hays West', 'Virginia Tech', _Hemisphere.North,
                          self.read_hdw_file('fhw')),
              1: _Radar('Goose Bay', 'Virginia Tech', _Hemisphere.North,
                        self.read_hdw_file('gbr')),
              10: _Radar('Hankasalmi', 'University of Leicester',
                        _Hemisphere.North, self.read_hdw_file('han')),
              40: _Radar('Hokkaido East', 'Nagoya University',
                         _Hemisphere.North, self.read_hdw_file('hok')),
              41:
              64:
              3:
              15:
              16:
              7:
              90:
              20:
              6:
              9:
              65:
              11:
              5:
              2:
              22:
              8:
              13:
              12:
              14:
              18:
              32:
              19:
             }




    @staticmethod
    def read_hdw_file(abbrv, year: int = None):
        if year is None:
            today = datetime.now()
            year = today.year()

        hdw_path = os.path.abspath(__file__)+'/hdw/'
        hdw_file = "{path}/hdw.dat.{radar}".format(path=hdw_path, radar=abbrv)
        hdw_lines = []
        with open(hdw_file, 'r') as reader:
            for line in reader.readlines():
                if '#' not in line and year < line.split()[1]:
                    hdw_data = line.split()
                    return _HdwInfo(hdw_data[0], abbrv, _coord(hdw_data[3],
                                                               hdw_data[4],
                                                               hdw_data[5]),
                                    hdw_data[6], hdw_data[7], hdw_data[8],
                                    hdw_data[9], hdw_data[10], hdw_data[11],
                                    _interferometer_offset(hdw_data[12],
                                                           hdw_data[13],
                                                           hdw_data[14]),
                                    hdw_data[15], hdw_data[16], hdw_data[17],
                                    hdw_data[18])



