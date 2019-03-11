# Copyright (C) 2019 SuperDARN
# Author: Marina Schmidt

"""
This module contains SuperDARN radar information
"""
from typing import NamedTuple
from enum import Enum


class _Hemisphere(Enum):
    North = 0
    South = 1


class _Radar(NamedTuple):
    name: str
    stid: int
    acronym: str
    hemisphere: _Hemisphere
    institute: str


class SuperDARNRadars():
    # Information obtained from http://vt.superdarn.org/tiki-index.php?page=Radar+Overview
    # North Radars
    radars = {209: _Radar('Adak Island East', 209, 'ade',
                          _Hemisphere.North, 'University of Alaska'),
              208: _Radar('Adak Island West', 208, 'adw',
                          _Hemisphere.North, 'University of Alaska'),
              33: _Radar('Blackstone', 33, 'bks', _Hemisphere.North,
                         'Virginia Tech'),
              207: _Radar('Christmas Valley East', 207, 'cve',
                          _Hemisphere.North, 'Dartmouth College'),
              206: _Radar('Christmas Valley West', 206, 'cvw',
                          _Hemisphere.North, 'Dartmouth College'),
              66: _Radar('Clyde River', 66, 'cly', _Hemisphere.North,
                         'University of Saskatchewan'),
              205: _Radar('Fort Hays East', 205, 'fhe', _Hemisphere.North,
                          'Virginia Tech'),
              204: _Radar('Fort Hays West', 204, 'fhw', _Hemisphere.North,
                          'Virginia Tech'),
              1: _Radar('Goose Bay', 1, 'gbr', _Hemisphere.North,
                       'Virginia Tech'),
              10: _Rdara('Hankasalmi', 10, 'han', _Hemisphere.North,
                         'University of Leicester'),
              40: _Radar('Hokkaido East', 40, 'hok', _Hemisphere.North,
                         'Nagoya University'),
              41: _Radar('Hokkaido West', 41, 'hkw', _Hemisphere.North,
                         'Nagoya University'),
              64: _Radar('Inuvik', 64, 'inv', _Hemisphere.North,
                         'University of Saskatchewan'),
              3: _Radar('Kapuskasing', 3, 'kap', _Hemisphere.North,
                        'Virginia Tech'),
              16: _Radar('King Salmon', 16, 'ksr', _Hemisphere.North,
                         'National Institute of Information and Communication'),
              7: _Radar('Kodiak', 7, 'kod', _Hemisphere.North,
                        'University of Alaska'),
              90: _Radar('Longyearbyen', 90, 'lyr', _Hemisphere.North,
                         'University Centre in Svalbard'),
              9: _Radar('Pykkvibaer', 9, 'pyk', _Hemisphere.North,
                        'University of Leicester'),
              6: _Radar('Prince George', 6, 'pgr', _Hemisphere.North,
                        'University of Saskatchewan'),
              65: _Radar('Rankin Inlet', 65, 'rkn', _Hemisphere.North,
                         'University of Saskatchewan'),
              5: _Radar('Saskatoon', 5, 'sas', _Hemisphere.North,
                        'University of Saskatchewan'),
              2: _Radar('Schefferville', 2, 'sch', _Hemisphere.North,
                        'CNRS/LPCE'),
              8: _Radar('Stokkseyri', 8, 'sto', _Hemisphere.North,
                        'Lancaster University'),
              32: _Radar('Wallops Island', 32, 'wal', _Hemisphere.North,
                         'JHU Applied Physics Laboratory'),
              24: _Radar('Buckland Park', 24, 'bpk', _Hemisphere.South,
                         'La Trobe University'),
              96: _Radar('Dome C', 96, 'dce', _Hemisphere.South,
                         'Institute for Space Astrophysics and Planetology'),
              21: _Radar('Falkland Islands', 21, 'fir', _Hemisphere.South,
                         'British Antarctic Survey'),
              4: _Radar('Halley', 4, 'hal', _Hemisphere.South,
                        'British Antarctic Survey'),
              15: _Radar('Kergueien', 15, 'ker', _Hemisphere.South,
                         'IRAP/CNRS/IPEV'),
              20: _Radar('McMurdo', 20, 'mcm', _Hemisphere.South,
                         'University of Alaska, Fairbanks'),
              11: _Radar('SANAE', 11, 'san', _Hemisphere.South,
                         'South Africa National Space Agency'),
              22: _Radar('South Pole Station', 22, 'sps', _Hemisphere.South,
                         'University of Alaska, Fairbanks'),
              13: _Radar('Syowa East', 13, 'sye', _Hemisphere.South,
                         'National Institute of Polar Research'),
              12: _Radar('Syowa South', 12, 'sys', _Hemisphere.South,
                         'National Institute of Polar Research'),
              14: _Radar('Tiger', 14, 'tig', _Hemisphere.South,
                         'La Trobe University'),
              18: _Radar('Unwin', 18, 'unw', _Hemisphere.South,
                         'La Trobe University'),
              19: _Radar('Zhongshan', 19, 'zho', _Hemisphere.South,
                         'Polar Research Institute of China')}
