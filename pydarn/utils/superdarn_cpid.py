# Copyright (C) 2019 SuperDARN Canada, University Saskatchewan
# Author: Marina Schmidt
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
# Modification:
#
"""
This module contains SuperDARN radar modes classified by cpid number
Current documentation on modes:
    http://superdarn.thayer.dartmouth.edu/info/modes.html
"""
# TODO: find/create better radar mode/frequency bands documentation


class SuperDARNCpids():

    cpids = {26401: 'stereoscan',
             26009: 'stereoscan',
             26008: 'stereoscan',
             26007: 'stereoscan',
             26006: 'stereoscan',
             26005: 'stereoscan',
             26004: 'stereoscan',
             26003: 'stereoscan',
             26002: 'stereoscan',
             6401: 'stereoscan',
             150: 'normalscan slow',
             151: 'normalscan fast',
             152: 'stereoscan',
             153: 'stereoscan',
             155: 'normalsound slow',
             157: 'normalsound fast',
             200: 'rbspscan',
             3200: 'risrscan',
             3250: 'twotsg slow',
             3251: 'twotsg fast',
             3252: 'twotsg slow',
             3253: 'twotsg fast',
             3300: 'themisscan',
             3333: 'ddstest',
             3350: 'ulfscan',
             3370: 'epopsound',
             3375: 'longsound',
             3380: 'politescan',
             3400: 'fivepulse',
             3450: 'heatsound',
             3500: 'twofsound slow',
             3501: 'twofsound fast',
             3502: 'twofsound slow 7-8 pulses',
             3503: 'twofsound fast 7-8 pulses',
             3505: 'twofsound',
             3517: 'g10scan',
             3520: 'uafsound slow',
             3521: 'uafsound fast',
             3550: 'twofonebm',
             3560: 'multifonebm',
             3600: 'tauscan slow',
             3601: 'tauscan fast',
             8510: 'ltuseqscan slow',
             8511: 'ltuseqscan fast',
             9211: 'pcpscan',
             9151: 'pcodecamp'}
