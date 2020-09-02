# Copyright (C) 2020 SuperDARN Canada, University of Saskatchewan
# Author: Daniel Billett, Marina Schmidt
"""
Fan plots, mapped to AACGM coordinates
"""

import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import os

from matplotlib import ticker, cm, colors
from typing import List

# third part libs
import aacgmv2

from pydarn import PyDARNColormaps

class Fan():
    # TODO: Add class documentation

	def __str__(self):
		return "This class is static class that provides"\
				" the following methods: \n"\
				"   - plot_fan()\n"\
				"   - return_beam_pos()\n"

	@classmethod
	def plot_fan(cls, dmap_data: List[dict], ax=None, scan_index: int = 0,
					   ranges: List = [0,75], boundary: bool = True,
					   parameter: str = 'v', lowlat: int = 50, cmap: str = None,
					   groundscatter: bool = False,
					   zmin: int = None, zmax: int = None,
					   colorbar: bool = True,
					   colorbar_label: str = ''):
		"""
        Plots a radar's Field Of View (FOV) fan plot for the given data and scan number

        Parameters
        -----------
            dmap_data: List[dict]
                Named list of dictionaries obtained from SDarn_read
            scan_index: int
                Scan number from beginning of first record in file
                Default: 0
            parameter: str
                Key name indicating which parameter to plot.
                Default: v (Velocity). Alternatives: 'p_l', 'w_l', 'elv'
            lowlat: int
                Lower AACGM latitude boundary for the polar plot
                Default: 50
            ranges: list
                Set to a two element list of the lower and upper ranges to plot
                Default: [0,75]
            boundary: bool    
                Set to false to not plot the outline of the FOV
                Default: True
            cmap: matplotlib.cm
                matplotlib colour map
                https://matplotlib.org/tutorials/colors/colormaps.html
                Default: Official pyDARN colour map for given parameter
            groundscatter : bool
                Set true to indicate if groundscatter should be plotted in grey
                Default: False
            zmin: int
                The minimum parameter value for coloring
                Default: {'p_l': [0], 'v': [-200], 'w_l': [0], 'elv': [0]}
            zmax: int
                The maximum parameter value for  coloring
                Default: {'p_l': [50], 'v': [200], 'w_l': [250], 'elv': [50]}
        	colorbar: bool
                Draw a colourbar if True
                Default: True
            colorbar_label: str
                the label that appears next to the colour bar. Requires colorbar to be true
                Default: ''
        """
		# TODO: put a function here to get the grid of the radar's FOV information
		my_path = os.path.abspath(os.path.dirname(__file__))
		base_path = os.path.join(my_path, '..')

		# Setup scans for easy locating
		# Makes a list of size (number of records), with the scan number for each
		scan_mark = [sub['scan'] for sub in dmap_data]
		no_scans = 0
		beam_scan = np.zeros((len(dmap_data)))
		for beam in range(len(dmap_data)):
			if abs(scan_mark[beam]) == 1:
				no_scans += 1
				beam_scan[beam] = no_scans
			if scan_mark[beam] == 0:
				beam_scan[beam] = no_scans
		no_scans += 1

		# Locate scan in loaded data
		plot_beams = np.where(beam_scan == scan_index)

		# Files holding radar beam/gate locations
		beam_lats = base_path+'/radar_fov_files/' + \
			dmap_data[0]['stid'].astype('str').zfill(3)+'_lats.txt'
		beam_lons = base_path+'/radar_fov_files/' + \
			dmap_data[0]['stid'].astype('str').zfill(3)+'_lons.txt'

		# Initialise arrays holding coordinates and MLT's
		beam_corners_lats = np.loadtxt(beam_lats)
		beam_corners_lons = np.loadtxt(beam_lons)

		fan_shape = beam_corners_lons.shape

		beam_corners_aacgm_lons = np.zeros((fan_shape[0], fan_shape[1]))
		beam_corners_aacgm_lats = np.zeros((fan_shape[0], fan_shape[1]))
		beam_corners_mlts = np.zeros((fan_shape[0], fan_shape[1]))

		# Time for coordinate conversion
		dtime = dt.datetime(dmap_data[plot_beams[0][0]]['time.yr'],
							dmap_data[plot_beams[0][0]]['time.mo'], dmap_data[plot_beams[0][0]]['time.dy'],
							dmap_data[plot_beams[0][0]]['time.hr'], dmap_data[plot_beams[0][0]]['time.mt'],
							dmap_data[plot_beams[0][0]]['time.sc'])
		for x in range(fan_shape[0]):
			for y in range(fan_shape[1]):
				# Convert to AACGM
				geomag = np.array(aacgmv2.
								  get_aacgm_coord(beam_corners_lats[x, y],
												  beam_corners_lons[x, y],
												  250, dtime))

				beam_corners_aacgm_lats[x, y] = geomag[0]
				beam_corners_aacgm_lons[x, y] = geomag[1]

		# Work out shift due in MLT
		mltshift = beam_corners_lons[x, y] - \
			(aacgmv2.convert_mlt(beam_corners_lons[x, y], dtime) * 15)
		beam_corners_mlts = beam_corners_aacgm_lons - mltshift

		# Hold the beam positions
		thetas = np.radians(beam_corners_mlts)
		rs = beam_corners_aacgm_lats

		# Get range-gate data and groundscatter array for given scan
		scan = np.zeros((fan_shape[0] - 1, fan_shape[1]-1))
		grndsct = np.zeros((fan_shape[0] - 1, fan_shape[1]-1)) #initialise arrays
		for i in np.nditer(plot_beams):
			try:
				slist = dmap_data[i.astype(int)]['slist'] #get a list of gates where there is data
				beam = dmap_data[i.astype(int)]['bmnum'] #get the beam number for the record
				scan[slist, beam] = dmap_data[i.astype(int)][parameter]
				grndsct[slist, beam] = dmap_data[i.astype(int)]['gflg']
			# if there is no slist field this means partial record
			except KeyError:
				continue

		# Colour table and max value selection depending on parameter plotted
		# Load defaults if none given
		# TODO: use cmaps as over writting cmap is bad practice...
		# did I do that in my code ... hmm
		if cmap is None:
			cmap = {'p_l': 'plasma', 'v': PyDARNColormaps.PYDARN_VELOCITY,
					'w_l': PyDARNColormaps.PYDARN_VIRIDIS,
					'elv': PyDARNColormaps.PYDARN}
			cmap = plt.cm.get_cmap(cmap[parameter])

		# Setting zmin and zmax
		defaultzminmax = {'p_l': [0, 50], 'v': [-200, 200],
						  'w_l': [0, 250], 'elv': [0, 50]}
		if zmin is None:
			zmin = defaultzminmax[parameter][0]
		if zmax is None:
			zmax = defaultzminmax[parameter][1]

        # Setup plot
        # TODO: eek! remeber there is an option to pass in a variable called ax
        # This may screw up references
		if ax is None:
			ax = plt.axes(polar=True)
		if beam_corners_aacgm_lats[0,0] > 0:
			ax.set_ylim(90, lowlat)
			ax.set_yticks(np.arange(lowlat, 90, 10))
		else:
			ax.set_ylim(-90, -lowlat)
			ax.set_yticks(np.arange(-lowlat, -90, -10))
		ax.set_xticklabels(['00', '', '06', '', '12', '', '18', ''])
		ax.set_theta_zero_location("S")

        # Begin plotting by iterating over ranges and beams
		for gates in range(ranges[0],ranges[1]-1):
			for beams in range(thetas.shape[1] - 2):
				# Index colour table correctly
				cmapindex = (scan[gates, beams] + abs(zmin)) /\
						(abs(zmin) + abs(zmax))
				if cmapindex < 0:
					cmapindex = 0

				if cmapindex > 1:
					cmapindex = 1
				colour_rgba = cmap(cmapindex)

				# Check for zero values (white) and groundscatter (gray)
				if scan[gates, beams] == 0:
					colour_rgba = 'w'

				if groundscatter and grndsct[gates, beams] == 1:
					colour_rgba = 'gray'

				#Angle for polar plotting
				theta = [thetas[gates, beams], thetas[gates + 1, beams],
						 thetas[gates + 1, beams + 1],
						 thetas[gates, beams + 1]]
				#Radius for polar plotting
				r = [rs[gates, beams], rs[gates + 1, beams],
					 rs[gates + 1, beams + 1], rs[gates, beams + 1]]
				im = ax.fill(theta, r, color=colour_rgba)

		# Plot FOV outline
		if boundary is True:
			plt.polar(thetas[0:ranges[1], 0], rs[0:ranges[1], 0], color='black',
					  linewidth=0.5)
			plt.polar(thetas[ranges[1] - 1, 0:thetas.shape[1] - 1],
					  rs[ranges[1] - 1, 0:thetas.shape[1] - 1], color='black',
					  linewidth=0.5)
			plt.polar(thetas[0:ranges[1], thetas.shape[1] - 2],
					  rs[0:ranges[1], thetas.shape[1] - 2],
					  color='black', linewidth=0.5)
			plt.polar(thetas[0, 0:thetas.shape[1] - 2],
					  rs[0, 0:thetas.shape[1] - 2], color='black',
					  linewidth=0.5)

		norm = colors.Normalize
		norm = norm(zmin, zmax)
		# Create color bar if True
		if colorbar is True:
			mappable = cm.ScalarMappable(norm=norm, cmap=cmap)
			locator = ticker.MaxNLocator(symmetric=True, min_n_ticks=3,
										 integer=True, nbins='auto')
			ticks = locator.tick_values(vmin=zmin, vmax=zmax)

			cb = ax.figure.colorbar(mappable, ax=ax, extend='both', ticks=ticks)

			if colorbar_label != '':
				cb.set_label(colorbar_label)

		return beam_corners_aacgm_lats, beam_corners_aacgm_lons, scan, grndsct