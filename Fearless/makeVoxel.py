#!/usr/bin/env python
#
# @Author: Giovanni Dalmasso <gio>
# @Date:   13-Jan-2022
# @Email:  giovanni.dalmasso@embl.es
# @Project: FeARLesS
# @Filename: makeVoxel.py
# @Last modified by:   gio
# @Last modified time: 02-May-2022
# @License: MIT
# @Copyright: Copyright © 2021 Giovanni Dalmasso


from utils import pathExists
from vedo import ProgressBar, load, printc, volumeFromMesh, write
import numpy as np


"""Convert a vtk mesh from the limb-data files into voxel data."""


DataPath = 'limbs+flank/'


limbs = load(DataPath + '*.vtk')
totLimbs = len(limbs)
printc("limbs # ", totLimbs, invert=1)


sampleSize = (100, 100, 100)

path_results = 'res/TIF-signedDist_sampleSize' + \
    str(sampleSize[0]) + '/'

pathExists(path_results)

# needed to have all the normals pointing in the same direction
noMirror = [4, 5, 6, 8, 9, 13, 14, 16, 17, 18, 19, 20, 22, 23, 25, 26, 27, 29, 30, 31, 33, 34,
            35, 37, 38, 40, 41, 42, 43, 44, 45, 47, 48, 49, 50, 52, 53, 55, 56, 59, 63, 64, 67, 68]

# collecting imgBounds of all limbs
allBounds = np.empty(shape=(6, totLimbs))
pb = ProgressBar(0, totLimbs, c=1)
for j in pb.range():
    allBounds[:, j] = limbs[j].GetBounds()
    pb.print('all bounds ...')

# finding max imgBounds
allBoundsTmp = []
pb = ProgressBar(0, allBounds.shape[0], c=1)
for j in pb.range():
    if allBounds[j, 0] > 0:
        allBoundsTmp.append(np.max(allBounds[j, :]))
    else:
        allBoundsTmp.append(np.min(allBounds[j, :]))
    pb.print('allBoundsTmp ... ')

# making imgBounds a bit bigger, just in case
imgBOunds = [x * 1.2 for x in allBoundsTmp]


pb = ProgressBar(0, totLimbs, c=1)
for j in pb.range():

    time = limbs[j].filename.split('.')[0].split('/')[-1].split('_')[1]

    if limbs[j].filename.split('.')[0].split('/')[-1].split('_')[-1] == 'clean-newAlignement':
        outputName = path_results + 'ReferenceShape_' + time + '_0.vti'
    else:
        outputName = path_results + 'ReferenceShape_' + time + '_' + \
            limbs[j].filename.split('.')[0].split(
                '/')[-1].split('_')[-1] + '.vti'

    if j in noMirror:
        vol = volumeFromMesh(limbs[j],
                             dims=sampleSize,
                             bounds=imgBOunds,
                             signed=True,
                             negate=True,  # invert sign
                             )
        write(vol, outputName)
    else:
        vol = volumeFromMesh(limbs[j],
                             dims=sampleSize,
                             bounds=imgBOunds,
                             signed=True,
                             negate=False,  # invert sign
                             )
        write(vol, outputName)

    pb.print('making voxel data ...')
