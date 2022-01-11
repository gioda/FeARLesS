#!/usr/bin/env python
#
# @Author: Giovanni Dalmasso <gio>
# @Date:   11-Jan-2022
# @Email:  giovanni.dalmasso@embl.es
# @Project: FeARLesS
# @Filename: computeAllIntesities.py
# @Last modified by:   gio
# @Last modified time: 11-Jan-2022
# @License: MIT
# @Copyright: Copyright © 2021 Giovanni Dalmasso


from sys import argv, exit
from vedo import printc, load

from utils import pathExists, voxelIntensity
import numpy as np

#####################################
# PARAMETERS
parameters = argv
if len(parameters) != 2:
    printc('missing parameters!!!', c='r')
    exit()

j = int(parameters[1])

radiusDiscretisation = 50
N = 250
FFTexpansion = radiusDiscretisation
expo = 1.0


LimbsPath = '../data/Limbs_Flank/'
path_results = 'res/' \
    'allIntensities-sampleSize100-' + \
    'radiusDiscretisation-' + \
    str(radiusDiscretisation) + '-N-' + str(N) + '-expo-' + str(expo)+'/'


pathExists(path_results)


limbs = [2490, 2500, 2510, 2540, 2570, 2571, 2573, 2574, 2590, 2600, 2601, 2610, 2620, 2631, 2640, 2642, 2650, 2651, 2652, 2653, 2654, 2655, 2660,
         2662, 2663, 2671, 2681, 2682, 2690, 2700, 2701, 2703, 2704, 2710, 2711, 2712, 2714, 2720, 2721, 2722, 2731, 2732, 2740, 2741, 2742, 2745,
         2746, 2750, 2751, 2752, 2754, 2755, 2760, 2761, 2762, 2771, 2772, 2780, 2790, 2831, 2840, 2850, 2870, 2880, 2881, 2882, 2890, 2901, 2902]
t = [249, 250, 251, 254, 257, 257, 257, 257, 259, 260, 260, 261, 262, 263, 264, 264, 265, 265, 265, 265, 265, 265, 266, 266, 266, 267,
     268, 268, 269, 270, 270, 270, 270, 271, 271, 271, 271, 272, 272, 272, 273, 273, 274, 274, 274, 274, 274, 275, 275, 275, 275, 275, 276, 276, 276,
     277, 277, 278, 279, 283, 284, 285, 287, 288, 288, 288, 289, 290, 290]

Treal = np.arange(t[0], t[-1]+1, dtype=int)
newTotLimbs = len(Treal)

totlimbs = len(limbs)
print(totlimbs, 'limbs!! \n')


##############################################
# loading files
vol = load(LimbsPath + 'ReferenceShape_' +
           str(limbs[j])[0:-1] + '_' + str(limbs[j])[-1] + '.vti')

##############################################
# computing voxel intensities
allIntensities = voxelIntensity(vol, expo, N, radiusDiscretisation)


name = 'allIntensities_' + 'ReferenceShape_' + \
    str(limbs[j])[0:-1] + '_' + str(limbs[j])[-1]
np.save(path_results + name, allIntensities)
printc('allIntensities', name, 'saved!', c='g')

if j == 0:
    allIntensitiesShape = allIntensities.shape
    np.save(path_results + 'allIntensitiesShape', allIntensitiesShape)
