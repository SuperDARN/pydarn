# Copyright (C) SuperDARN Canada, University of Saskatchewan
# Authors: Marina Schmidt and Danno Peters

"""
This module contains SuperDARN radar information
"""
import os

from typing import NamedTuple
from enum import Enum
from datetime import datetime


def read_hdw_file(abbrv, year: int = None):
    if year is None:
        today = datetime.now()
        year = today.year

    hdw_path = os.path.dirname(__file__)+'/hdw/'
    hdw_file = "{path}/hdw.dat.{radar}".format(path=hdw_path, radar=abbrv)
    with open(hdw_file, 'r') as reader:
        for line in reader.readlines():
            if '#' not in line and len(line.split()) > 1 and year < int(line.split()[1]):
                hdw_data = line.split()
                """
                Hardware data array positions definitions:
                    0: station id - stid
                    1: last year that the parameter string is valid.
                    Note: currently updated line will have a year of 2999
                    meaning it is currently still up to date.
                    2: last second of year that parameter string is valid.
                    3: Geographic latitude of radar site
                    4: Geographic longitude of radar site
                    Note: southern lat and long are negative
                    5: Altitude of the radar site (meters)
                    6: Scanning boresight - direction of the centre beam,
                    measured in degrees relative to geographic north.
                    Counter clockwise rotations are negative.
                    7: Beam separation (Angular seperation in degrees)
                    8: velocity sign - at radar level, backscattered signal with
                    frequencies above the transmitted frequency are assigned positive
                    Doppler velocities while backscattered signals with frequencies
                    below the transmitted frequency are assigned negative Doppler
                    velocity. Can be changed in receiver design.
                    9: Analog Rx attenuator step (dB)
                    10: Tdiff
                """
                return _HdwInfo(int(hdw_data[0]), abbrv, _Coord(float(hdw_data[3]),
                                                                float(hdw_data[4]),
                                                                float(hdw_data[5])),
                                float(hdw_data[6]), float(hdw_data[7]), float(hdw_data[8]),
                                float(hdw_data[9]), float(hdw_data[10]), float(hdw_data[11]),
                                _InterferometerOffset(float(hdw_data[12]),
                                                      float(hdw_data[13]),
                                                      float(hdw_data[14])),
                                float(hdw_data[15]), float(hdw_data[16]), int(hdw_data[17]),
                                int(hdw_data[18]))


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
    geographic: _Coord
    boresight: float
    beamSep: float
    velocity_sign: float
    rx_attenuator: float
    tdiff: float
    phase_sign: float
    interferometer_offset: _InterferometerOffset
    rx_rise_time: float
    attenuation_stages: float
    max_range: int
    beams: int


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
                          read_hdw_file('ade')),
              208: _Radar('Adak Island West', 'University of Alaska Fairbanks',
                          _Hemisphere.North, read_hdw_file('adw')),
              33: _Radar('Blackstone', 'Virginia Tech', _Hemisphere.North,
                         read_hdw_file('bks')),
              207: _Radar('Christmas Valley East', 'Dartmouth College',
                          _Hemisphere.North, read_hdw_file('cve')),
              206: _Radar('Christmas Valley West', 'Dartmouth College',
                          _Hemisphere.North, read_hdw_file('cvw')),
              66: _Radar('Clyde River', 'University of Saskatchewan',
                         _Hemisphere.North, read_hdw_file('cly')),
              205: _Radar('Fort Hays East', 'Virginia Tech', _Hemisphere.North,
                          read_hdw_file('fhe')),
              204: _Radar('Fort Hays West', 'Virginia Tech', _Hemisphere.North,
                          read_hdw_file('fhw')),
              1: _Radar('Goose Bay', 'Virginia Tech', _Hemisphere.North,
                        read_hdw_file('gbr')),
              10: _Radar('Hankasalmi', 'University of Leicester',
                         _Hemisphere.North, read_hdw_file('han')),
              40: _Radar('Hokkaido East', 'Nagoya University',
                         _Hemisphere.North, read_hdw_file('hok')),
              41: _Radar('Hokkaido West', 'Nagoya University',
                         _Hemisphere.North, read_hdw_file('hkw')),
              64: _Radar('Inuvik', 'University of Saskatchewan',
                         _Hemisphere.North, read_hdw_file('inv')),
              3: _Radar('Kapuskasing', 'Virginia Tech', _Hemisphere.North,
                        read_hdw_file('kap')),
              16: _Radar('King Salmon',
                         'National Institute of Information and'
                         ' Communications Technology', _Hemisphere.North,
                         read_hdw_file('ksr')),
              7: _Radar('Kodiak', 'University of Alaska Fairbanks',
                        _Hemisphere.North, read_hdw_file('kod')),
              90: _Radar('Longyearbyen', 'University of Centre in Svalbard',
                         _Hemisphere.North, read_hdw_file('lyr')),
              9: _Radar('Pykkvibaer', 'University of Leicester',
                        _Hemisphere.North, read_hdw_file('pyk')),
              6: _Radar('Prince George', 'University of Saskatchewan',
                        _Hemisphere.North, read_hdw_file('pgr')),
              65: _Radar('Rankin Inlet', 'University of Saskatchewan',
                         _Hemisphere.North, read_hdw_file('rkn')),
              5: _Radar('Saskatoon', 'University of Saskatchewan',
                        _Hemisphere.North, read_hdw_file('sas')),
              2: _Radar('Schefferville', 'CNRS/LPCE', _Hemisphere.North,
                        read_hdw_file('sch')),
              8: _Radar('Stokkseyri', 'Lancaster University',
                        _Hemisphere.North, read_hdw_file('sto')),
              32: _Radar('Wallops Island', 'JHU Applied Physics Laboratory',
                         _Hemisphere.North, read_hdw_file('wal')),
              24: _Radar('Buckland Park', 'La Trobe University',
                         _Hemisphere.North, read_hdw_file('bpk')),
              96: _Radar('Dome C',
                         'Institute for Space Astrophysics and Planetology',
                         _Hemisphere.North, read_hdw_file('dce')),
              21: _Radar('Falkland Islands', 'British Antarctic Survey',
                         _Hemisphere.North, read_hdw_file('fir')),
              4: _Radar('Halley', 'British Antarctic Survey',
                        _Hemisphere.North, read_hdw_file('hal')),
              15: _Radar('Kerguelen', 'IRAP/CNRS/IPEV', _Hemisphere.North,
                         read_hdw_file('ker')),
              20: _Radar('McMurdo', 'University of Alaska, Fairbanks',
                         _Hemisphere.North, read_hdw_file('mcm')),
              11: _Radar('SANAE', 'South African National Space Agency',
                         _Hemisphere.North, read_hdw_file('san')),
              22: _Radar('South Pole Station',
                         'University of Alaska, Fairbanks', _Hemisphere.North,
                         read_hdw_file('sps')),
              13: _Radar('Syowa East', 'National Institute of Polar Research',
                         _Hemisphere.North, read_hdw_file('sye')),
              12: _Radar('Syowa South', 'National Institute of Polar Research',
                         _Hemisphere.North, read_hdw_file('sys')),
              14: _Radar('Tiger', 'La Trobe University', _Hemisphere.North,
                         read_hdw_file('tig')),
              18: _Radar('Unwin', 'La Trobe University', _Hemisphere.North,
                         read_hdw_file('unw')),
              19: _Radar('Zhongshan', 'Polar Research Institute of China',
                         _Hemisphere.North, read_hdw_file('zho'))}
