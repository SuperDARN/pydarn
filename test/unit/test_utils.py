# Copyright (C) SuperDARN Canada, University of Saskatchewan
# Author(s): Marina Schmidt
import logging
import unittest

import pydarn

from datetime import datetime

pydarn_logger = logging.getLogger('pydarn')


class TestSuperDarnRadars(unittest.TestCase):
    """
    This class tests the superdarn_radars module
    """
    def test_read_hdw_file(self):
        """
        test if read_hdw_file can read Saskatoon's
        most current hardware information
        """
        hdw_data = pydarn.read_hdw_file('sas')
        self.assertEqual(hdw_data.abbrev, 'sas')
        self.assertEqual(hdw_data.stid, 5)
        self.assertEqual(hdw_data.geographic.lat, 52.160)
        self.assertEqual(hdw_data.geographic.lon, -106.530)
        self.assertEqual(hdw_data.geographic.alt, 494.0)
        self.assertEqual(hdw_data.boresight, 23.1)
        self.assertEqual(hdw_data.beam_seperation, 3.24)
        self.assertEqual(hdw_data.velocity_sign, 1)
        self.assertEqual(hdw_data.rx_attenuator, 10)
        self.assertEqual(hdw_data.tdiff, 0.000)
        self.assertEqual(hdw_data.phase_sign, 1)
        self.assertEqual(hdw_data.interferometer_offset.x, 0.0)
        self.assertEqual(hdw_data.interferometer_offset.y, -100.0)
        self.assertEqual(hdw_data.interferometer_offset.z, 0.0)
        self.assertEqual(hdw_data.rx_rise_time, 0.0)
        self.assertEqual(hdw_data.attenuation_stages, 0)
        self.assertEqual(hdw_data.gates, 225)
        self.assertEqual(hdw_data.beams, 16)

    def test_read_hdw_file_old_year(self):
        """
        test if read_hdw_file can read McMurdo's older
        hardware file information
        """
        hdw_data = pydarn.read_hdw_file('mcm', datetime(year=2016, month=1,
                                                        day=1))
        self.assertEqual(hdw_data.abbrev, 'mcm')
        self.assertEqual(hdw_data.stid, 20)
        self.assertEqual(hdw_data.geographic.lat, -77.880)
        self.assertEqual(hdw_data.geographic.lon, 166.730)
        self.assertEqual(hdw_data.geographic.alt, 300.0)
        self.assertEqual(hdw_data.boresight, 263.4)
        self.assertEqual(hdw_data.beam_seperation, 3.24)
        self.assertEqual(hdw_data.velocity_sign, 1)
        self.assertEqual(hdw_data.rx_attenuator, 10)
        self.assertEqual(hdw_data.tdiff, 0.0)
        self.assertEqual(hdw_data.phase_sign, 1)
        self.assertEqual(hdw_data.interferometer_offset.x, 0.0)
        self.assertEqual(hdw_data.interferometer_offset.y, 70.1)
        self.assertEqual(hdw_data.interferometer_offset.z, -4.1)
        self.assertEqual(hdw_data.rx_rise_time, 0.0)
        self.assertEqual(hdw_data.attenuation_stages, 2)
        self.assertEqual(hdw_data.gates, 75)
        self.assertEqual(hdw_data.beams, 16)

    def test_hardware_file_not_found(self):
        """
        Test if it raises an error for an non-existing
        hardware file
        """
        with self.assertRaises(pydarn.radar_exceptions.HardwareFileNotFoundError):
            pydarn.read_hdw_file('dog')

    def test_SuperDarn_class_dict(self):
        """
        test if the superdarn class dict returns
        Goose Bay's radars information
        """
        radar_data = pydarn.SuperDARNRadars.radars[1]
        self.assertEqual(radar_data.institution, 'Virginia Tech')
        self.assertEqual(radar_data.name, 'Goose Bay')
        self.assertEqual(radar_data.hemisphere, pydarn.Hemisphere.North)

    def test_SuperDARN_class_south_radar(self):
        """
        test if SuperDARN radars returns a southern
        hemisphere radar information correctly
        """
        radar_data = pydarn.SuperDARNRadars.radars[24]
        self.assertEqual(radar_data.institution, 'La Trobe University')
        self.assertEqual(radar_data.name, 'Buckland Park')
        self.assertEqual(radar_data.hemisphere, pydarn.Hemisphere.South)

    def test_SuperDarn_class_stid_not_found(self):
        """
        Test if it raises an error for a radar stid
        that does not exist
        """
        with self.assertRaises(KeyError):
            pydarn.SuperDARNRadars.radars[100]

if __name__ == '__main__':

    pydarn_logger.info('Starting Utils Testing')
    unittest.main()
