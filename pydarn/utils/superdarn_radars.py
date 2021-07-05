# Copyright (C) 2020 SuperDARN Canada, University of Saskatchewan
# Authors: Marina Schmidt and Danno Peters
#
# This file is part of the pyDARN Library.
#
# pyDARN is under the LGPL v3 license found in the root directory LICENSE.md
# Everyone is permitted to copy and distribute verbatim copies of this license
# document, but changing it is not allowed.
#
# This version of the GNU Lesser General Public License incorporates the terms
# and conditions of version 3 of the GNU Lesser General Public License,
# supplemented by the additional permissions listed below.
#
# Modifications:
#
"""
This module contains SuperDARN radar information
"""
import glob
import os
import pydarn
import shutil

from typing import NamedTuple
from enum import Enum
from datetime import datetime, timedelta
from subprocess import check_call


def get_hdw_files(force: bool = True, version: str = None):
    """
    downloads hardware files from the SuperDARN github page:
        https://github.com/SuperDARN/hdw

    Parameter
    ---------
    force: bool
        download hardware files even if they are in the
        directory
    version: str
        version number to download

    Note: version is not currently working as hardware files
    have yet to be versioned.
    """

    # Path should the path where pydarn is installed
    hdw_path = "{}/hdw/".format(os.path.dirname(pydarn.utils.__file__))

    # TODO: implement when DSWG starts versioning hardware files
    if version is not None:
        raise Exception("This feature is not implemented yet")

    # if there is no files in hdw folder or force is true
    # download the hdw files
    if len(os.listdir(hdw_path)) == 0 or force:
        # pycurl doesn't download a zip folder easily so
        # use the command line command
        check_call(['curl', '-L', '-o', hdw_path+'/master.zip',
                    'https://github.com/SuperDARN/hdw/archive/master.zip'])
        # use unzip command because zipfile on works with files and not folders
        # though this is possible with zipfile but this was easier for me to
        # get it working
        check_call(['unzip', '-d', hdw_path, hdw_path+'/master.zip'])
        dat_files = glob.glob(hdw_path+'/hdw-master/*')
        # shutil only moves specific files so we need to move
        # everything one at a time
        for hdw_file in dat_files:
            shutil.move(hdw_file, hdw_path+os.path.basename(hdw_file))
        # delete the empty folder
        os.removedirs(hdw_path+'/hdw-master/')


def read_hdw_file(abbrv, date: datetime = None, update: bool = False):
    """
    Reads the hardware file for the associated abbreviation of the radar name.

    Parameters
    ----------
        abbrv : str
            Radars 3 letter assigned abbreviation
        date: datetime
            Datetime object of hardware information to obtain
            default: current date
        update: bool
            If True this will update the hardware files again
            without re-installing pydarn
            default: False
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
    # if the file does not exist then try
    # and download it
    if os.path.exists(hdw_file) is False:
        get_hdw_files()
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
                            7: Beam separation (Angular separation in degrees)
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
        raise pydarn.radar_exceptions.HardwareFileNotFoundError(abbrv)


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
    beam_separation : float
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
    beam_separation: float
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
    range_gate_45: int
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
                          75, read_hdw_file('ade')),
              208: _Radar('Adak Island West', 'University of Alaska Fairbanks',
                          Hemisphere.North, 75, read_hdw_file('adw')),
              33: _Radar('Blackstone', 'Virginia Tech', Hemisphere.North,
                         100, read_hdw_file('bks')),
              207: _Radar('Christmas Valley East', 'Dartmouth College',
                          Hemisphere.North, 100, read_hdw_file('cve')),
              206: _Radar('Christmas Valley West', 'Dartmouth College',
                          Hemisphere.North, 100, read_hdw_file('cvw')),
              66: _Radar('Clyde River', 'University of Saskatchewan',
                         Hemisphere.North, 100, read_hdw_file('cly')),
              205: _Radar('Fort Hays East', 'Virginia Tech', Hemisphere.North,
                          100, read_hdw_file('fhe')),
              204: _Radar('Fort Hays West', 'Virginia Tech', Hemisphere.North,
                          100, read_hdw_file('fhw')),
              1: _Radar('Goose Bay', 'Virginia Tech', Hemisphere.North,
                        100, read_hdw_file('gbr')),
              10: _Radar('Hankasalmi', 'University of Leicester',
                         Hemisphere.North, 70, read_hdw_file('han')),
              40: _Radar('Hokkaido East', 'Nagoya University',
                         Hemisphere.North, 110, read_hdw_file('hok')),
              41: _Radar('Hokkaido West', 'Nagoya University',
                         Hemisphere.North, 110, read_hdw_file('hkw')),
              64: _Radar('Inuvik', 'University of Saskatchewan',
                         Hemisphere.North, 75, read_hdw_file('inv')),
              50: _Radar('Jiamusi East radar',
                         'National Space Science Center,'
                         'Chinese Academy of Sciences',
                         Hemisphere.North, 100, read_hdw_file('jme')),
              3: _Radar('Kapuskasing', 'Virginia Tech', Hemisphere.North,
                        75, read_hdw_file('kap')),
              16: _Radar('King Salmon',
                         'National Institute of Information and'
                         ' Communications Technology', Hemisphere.North,
                         75, read_hdw_file('ksr')),
              7: _Radar('Kodiak', 'University of Alaska Fairbanks',
                        Hemisphere.North, 110, read_hdw_file('kod')),
              90: _Radar('Longyearbyen', 'University of Centre in Svalbard',
                         Hemisphere.North, 70, read_hdw_file('lyr')),
              9: _Radar('Pykkvibaer', 'University of Leicester',
                        Hemisphere.North, 70, read_hdw_file('pyk')),
              6: _Radar('Prince George', 'University of Saskatchewan',
                        Hemisphere.North, 75, read_hdw_file('pgr')),
              65: _Radar('Rankin Inlet', 'University of Saskatchewan',
                         Hemisphere.North, 75, read_hdw_file('rkn')),
              5: _Radar('Saskatoon', 'University of Saskatchewan',
                        Hemisphere.North, 75, read_hdw_file('sas')),
              2: _Radar('Schefferville', 'CNRS/LPCE', Hemisphere.North,
                        75, read_hdw_file('sch')),
              8: _Radar('Stokkseyri', 'Lancaster University',
                        Hemisphere.North, 75, read_hdw_file('sto')),
              32: _Radar('Wallops Island', 'JHU Applied Physics Laboratory',
                         Hemisphere.North, 100, read_hdw_file('wal')),
              24: _Radar('Buckland Park', 'La Trobe University',
                         Hemisphere.South, 75, read_hdw_file('bpk')),
              96: _Radar('Dome C East',
                         'Institute for Space Astrophysics and Planetology',
                         Hemisphere.South, 75, read_hdw_file('dce')),
              97: _Radar('Dome C North',
                         'Institute for Space Astrophysics and Planetology',
                         Hemisphere.South, 75, read_hdw_file('dcn')),
              21: _Radar('Falkland Islands', 'British Antarctic Survey',
                         Hemisphere.South,  110, read_hdw_file('fir')),
              4: _Radar('Halley', 'British Antarctic Survey',
                        Hemisphere.South, 100, read_hdw_file('hal')),
              15: _Radar('Kerguelen', 'IRAP/CNRS/IPEV', Hemisphere.South,
                         75, read_hdw_file('ker')),
              20: _Radar('McMurdo', 'University of Alaska, Fairbanks',
                         Hemisphere.South, 75, read_hdw_file('mcm')),
              11: _Radar('SANAE', 'South African National Space Agency',
                         Hemisphere.South, 110, read_hdw_file('san')),
              22: _Radar('South Pole Station',
                         'University of Alaska, Fairbanks', Hemisphere.South,
                         75, read_hdw_file('sps')),
              13: _Radar('Syowa East', 'National Institute of Polar Research',
                         Hemisphere.South, 75, read_hdw_file('sye')),
              12: _Radar('Syowa South', 'National Institute of Polar Research',
                         Hemisphere.South, 80, read_hdw_file('sys')),
              14: _Radar('Tiger', 'La Trobe University', Hemisphere.South,
                         75, read_hdw_file('tig')),
              18: _Radar('Unwin', 'La Trobe University', Hemisphere.South,
                         75, read_hdw_file('unw')),
              19: _Radar('Zhongshan', 'Polar Research Institute of China',
                         Hemisphere.South, 70, read_hdw_file('zho'))}
