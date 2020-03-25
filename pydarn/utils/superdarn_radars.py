# Copyright (C) 2020 SuperDARN Canada, University of Saskatchewan
# Authors: Marina Schmidt and Danno Peters

"""
This module contains SuperDARN radar information
"""
import os

from typing import NamedTuple
from enum import Enum
from datetime import datetime, timedelta
from pydarn import radar_exceptions


def read_hdw_file(abbrv, date: datetime = None):
    """
    Reads the hardware file for the associated abbreviation of the radar name.

    Parameters
    ----------
        abbrv : str
            Radars 3 letter assigned abbreviation
        date: datetime
            Datetime object of hardware information to obtain
            default: current date

    Return
    ------
    _HdwInfo object that contains all the field names in a hardware
        file

    Raises
    ------
    HardwareFileNotFoundError raised when there is no hardware file found for
    the given abbreviation
    """
    if date is None:
        date = datetime.now()

    hdw_path = os.path.dirname(__file__)+'/hdw/'
    hdw_file = "{path}/hdw.dat.{radar}".format(path=hdw_path, radar=abbrv)
    try:
        with open(hdw_file, 'r') as reader:
            for line in reader.readlines():
                if '#' not in line and len(line.split()) > 1:
                    hdw_data = line.split()
                    """
                    Hardware files give the year and seconds from the beginning
                    of that year. Thus to check the date if it corresponds we
                    need to convert to a datetime object and then compare.
                    """
                    hdw_line_date = datetime(year=int(hdw_data[1]), month=1,
                                             day=1) +\
                        timedelta(seconds=int(hdw_data[2]))
                    if hdw_line_date > date:
                        """
                        Hardware data array positions definitions:
                            0: station id - stid
                            1: last year that the parameter string is valid.
                            Note: currently updated line will
                            have a year of 2999
                            meaning it is currently still up to date.
                            2: last second of year that parameter
                            string is valid.
                            3: Geographic latitude of radar site
                            4: Geographic longitude of radar site
                            Note: southern lat and long are negative
                            5: Altitude of the radar site (meters)
                            6: Scanning boresight - direction of
                            the centre beam,
                            measured in degrees relative to geographic north.
                            Counter clockwise rotations are negative.
                            7: Beam separation (Angular seperation in degrees)
                            8: velocity sign - at radar level,
                            backscattered signal with
                            frequencies above the transmitted frequency
                            are assigned positive
                            Doppler velocities while backscattered signals
                            with frequencies
                            below the transmitted frequency are assigned
                            negative Doppler
                            velocity. Can be changed in receiver design.
                            9: Analog Rx attenuator step (dB)
                            10: Tdiff - propagation time from
                            interferometer array antenna
                            to phasing matrix input miunus propagation
                            time from main array
                            antenna through transmitter to phasing
                            matrix input.
                            (microseconds)
                            11: phase sign - to account for any cable errors
                            Interferometer offset - displacement of midpoint
                            interferometer array from midpoint main
                            array (meters).
                            12: x direction - along the line of antennas
                            with +X toward
                            higher antenna number
                            13: y direction - along the array normal
                            with +Y in the
                            direction of the array normal
                            14: z direction - is the altitude difference, +Z up
                            15: Analog Rx rise time (microseconds)
                            16: Analog Attenuation stages - gain control of
                            an analog
                            receiver or front-end
                            17: maximum range gates
                            18: maximum number of beams
                        """
                        return _HdwInfo(int(hdw_data[0]), abbrv,
                                        _Coord(float(hdw_data[3]),
                                               float(hdw_data[4]),
                                               float(hdw_data[5])),
                                        float(hdw_data[6]), float(hdw_data[7]),
                                        float(hdw_data[8]), float(hdw_data[9]),
                                        float(hdw_data[10]),
                                        float(hdw_data[11]),
                                        _InterferometerOffset(float(hdw_data[12]),
                                                              float(hdw_data[13]),
                                                              float(hdw_data[14])),
                                        float(hdw_data[15]),
                                        float(hdw_data[16]),
                                        int(hdw_data[17]), int(hdw_data[18]))
    except FileNotFoundError:
        raise radar_exceptions.HardwareFileNotFoundError(abbrv)


class Hemisphere(Enum):
    """
    Class used to denote which hemisphere a radar is located in

    Attributes
    ----------
    Hemisphere.North = 1
    Hemisphere.South = -1

    Notes
    -----
    This is based on the values assigned to the MAP file hemisphere
    field in RST>
    """
    North = 1
    South = -1


class _InterferometerOffset(NamedTuple):
    """
    Named tuple class to contain the interferometer offset
    Cartesian coordinates.

    Attributes
    ----------
    x : float
        direction along the line of antennas with +X toward
        higher antenna number
    y : float
        direction along the array normal with +Y in the
        direction of the array normal
    z : float
        direction is the altitude difference, +Z up
    """
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
    alt : float
        Altitude in meters
    """
    lat: float
    lon: float
    alt: float


class _HdwInfo(NamedTuple):
    """
    Class used to store relevant information about the SuperDARN Radars

    Attributes
    ----------
    stid : int
        station number
    abbrev : str
        three letter station abbreviation
    geographic : _Coord object
        Named Tuple containing geographic latitude longitude and altitude
    boresight : float
        boresight center beam in degrees
    beam_seperation : float
        angular separation between radar beams
    velocity_sign : float
        at radar level, backscattered signal with
        frequencies above the transmitted frequency are assigned positive
        Doppler velocities while backscattered signals with frequencies
        below the transmitted frequency are assigned negative Doppler
        velocity. Can be changed in receiver design.
    rx_attenuator : float
        Analog Rx attenuator step (dB)
    tdiff : float
        propagation time from interferometer array antenna
        to phasing matrix input minus propagation time from main array
        antenna through transmitter to phasing matrix input.
        (microseconds)
    phase_sign : float
        To account for flipped cable errors
    interferometer_offset : _InterferometerOffset
        displacement of midpoint
        interferometer array from midpoint main array in
        Cartesian coordinates(meters).
    rx_rise : float
        Analog Rx rise time (microseconds)
    attenuation_stages : float
        Analog Attenuation stages - gain control of an analog
        receiver or front-end
    gates :int
        number of range gates per beam
    beams : int
        number of possible beams

    See Also
    --------
    read_hdw_file : function for reading hardware files
    _Coord : object contain coordinate information
    """
    stid: int
    abbrev: str
    geographic: _Coord
    boresight: float
    beam_seperation: float
    velocity_sign: float
    rx_attenuator: float
    tdiff: float
    phase_sign: float
    interferometer_offset: _InterferometerOffset
    rx_rise_time: float
    attenuation_stages: float
    gates: int
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
    hemisphere: Hemisphere
        Hemisphere the radar belongs to
    hardware_info: _HdwInfo
        NamedTuple containing all hardware information from hardware files
    """
    name: str
    institution: str
    hemisphere: Hemisphere
    hardware_info: _HdwInfo


class SuperDARNRadars():
    """
    Class containing a dictionary of Nested Named Tuples with information
    about each radar in SuperDARN.

    Attributes
    ----------
        radars: dict
            dictionary of each SuperDARN radar with key being STID value and
            a _Radar object containing the name, institutional and hardware
            information of the radar

    See Also
    --------
        _Radar : radar object containing radar information
        read_hdw_file : function to read hardware information for a given radar
    """
    # Information obtained from
    # http://vt.superdarn.org/tiki-index.php?page=Radar+Overview
    radars = {209: _Radar('Adak Island East',
                          'University of Alaska Fairbanks', Hemisphere.North,
                          read_hdw_file('ade')),
              208: _Radar('Adak Island West', 'University of Alaska Fairbanks',
                          Hemisphere.North, read_hdw_file('adw')),
              33: _Radar('Blackstone', 'Virginia Tech', Hemisphere.North,
                         read_hdw_file('bks')),
              207: _Radar('Christmas Valley East', 'Dartmouth College',
                          Hemisphere.North, read_hdw_file('cve')),
              206: _Radar('Christmas Valley West', 'Dartmouth College',
                          Hemisphere.North, read_hdw_file('cvw')),
              66: _Radar('Clyde River', 'University of Saskatchewan',
                         Hemisphere.North, read_hdw_file('cly')),
              205: _Radar('Fort Hays East', 'Virginia Tech', Hemisphere.North,
                          read_hdw_file('fhe')),
              204: _Radar('Fort Hays West', 'Virginia Tech', Hemisphere.North,
                          read_hdw_file('fhw')),
              1: _Radar('Goose Bay', 'Virginia Tech', Hemisphere.North,
                        read_hdw_file('gbr')),
              10: _Radar('Hankasalmi', 'University of Leicester',
                         Hemisphere.North, read_hdw_file('han')),
              40: _Radar('Hokkaido East', 'Nagoya University',
                         Hemisphere.North, read_hdw_file('hok')),
              41: _Radar('Hokkaido West', 'Nagoya University',
                         Hemisphere.North, read_hdw_file('hkw')),
              64: _Radar('Inuvik', 'University of Saskatchewan',
                         Hemisphere.North, read_hdw_file('inv')),
              3: _Radar('Kapuskasing', 'Virginia Tech', Hemisphere.North,
                        read_hdw_file('kap')),
              16: _Radar('King Salmon',
                         'National Institute of Information and'
                         ' Communications Technology', Hemisphere.North,
                         read_hdw_file('ksr')),
              7: _Radar('Kodiak', 'University of Alaska Fairbanks',
                        Hemisphere.North, read_hdw_file('kod')),
              90: _Radar('Longyearbyen', 'University of Centre in Svalbard',
                         Hemisphere.North, read_hdw_file('lyr')),
              9: _Radar('Pykkvibaer', 'University of Leicester',
                        Hemisphere.North, read_hdw_file('pyk')),
              6: _Radar('Prince George', 'University of Saskatchewan',
                        Hemisphere.North, read_hdw_file('pgr')),
              65: _Radar('Rankin Inlet', 'University of Saskatchewan',
                         Hemisphere.North, read_hdw_file('rkn')),
              5: _Radar('Saskatoon', 'University of Saskatchewan',
                        Hemisphere.North, read_hdw_file('sas')),
              2: _Radar('Schefferville', 'CNRS/LPCE', Hemisphere.North,
                        read_hdw_file('sch')),
              8: _Radar('Stokkseyri', 'Lancaster University',
                        Hemisphere.North, read_hdw_file('sto')),
              32: _Radar('Wallops Island', 'JHU Applied Physics Laboratory',
                         Hemisphere.North, read_hdw_file('wal')),
              24: _Radar('Buckland Park', 'La Trobe University',
                         Hemisphere.South, read_hdw_file('bpk')),
              96: _Radar('Dome C',
                         'Institute for Space Astrophysics and Planetology',
                         Hemisphere.South, read_hdw_file('dce')),
              21: _Radar('Falkland Islands', 'British Antarctic Survey',
                         Hemisphere.South, read_hdw_file('fir')),
              4: _Radar('Halley', 'British Antarctic Survey',
                        Hemisphere.South, read_hdw_file('hal')),
              15: _Radar('Kerguelen', 'IRAP/CNRS/IPEV', Hemisphere.South,
                         read_hdw_file('ker')),
              20: _Radar('McMurdo', 'University of Alaska, Fairbanks',
                         Hemisphere.South, read_hdw_file('mcm')),
              11: _Radar('SANAE', 'South African National Space Agency',
                         Hemisphere.South, read_hdw_file('san')),
              22: _Radar('South Pole Station',
                         'University of Alaska, Fairbanks', Hemisphere.South,
                         read_hdw_file('sps')),
              13: _Radar('Syowa East', 'National Institute of Polar Research',
                         Hemisphere.South, read_hdw_file('sye')),
              12: _Radar('Syowa South', 'National Institute of Polar Research',
                         Hemisphere.South, read_hdw_file('sys')),
              14: _Radar('Tiger', 'La Trobe University', Hemisphere.South,
                         read_hdw_file('tig')),
              18: _Radar('Unwin', 'La Trobe University', Hemisphere.South,
                         read_hdw_file('unw')),
              19: _Radar('Zhongshan', 'Polar Research Institute of China',
                         Hemisphere.South, read_hdw_file('zho'))}
