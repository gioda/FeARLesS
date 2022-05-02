#!/usr/bin/env python
#
# @Author: Giovanni Dalmasso <gio>
# @Date:   20-Jan-2022
# @Email:  giovanni.dalmasso@embl.es
# @Project: FeARLesS
# @Filename: morphing.py
# @Last modified by:   gio
# @Last modified time: 02-May-2022
# @License: MIT
# @Copyright: Copyright © 2021 Giovanni Dalmasso


import numpy as np
from vedo import printc, ProgressBar, load, Points, write, interpolateToVolume
from utils import pathExists, forwardTransformation, samplePoints, inverseTransformations


#####################################
# PARAMETERS
sampleSize = 100
radiusDiscretisation = 50
N = 250
lmax = 50
expo = 1.0
deg_fit = 6

printc('\n sampleSize', sampleSize, '- radiusDiscretisation',
       radiusDiscretisation, '- N', N, '- lmax', lmax,
       c='green')


path = 'res/' \
    'allIntensities-sampleSize100-' + \
    'radiusDiscretisation-' + \
    str(radiusDiscretisation) + '-N-' + str(N) + '/'
path_resultsCLM = 'res/' \
    '/CLM/'\
    'morphing_sampleSize' + str(sampleSize) + \
    '-radDisc' + str(radiusDiscretisation) + '-N' + str(N) + '-degFit' + \
    str(deg_fit) + '-lmax'+str(lmax) + '/'
path_results = 'res/' \
    'morphing_sampleSize' \
    + str(sampleSize) + \
    '-radDisc' + str(radiusDiscretisation) + '-N' + str(N) + '-degFit' + \
    str(deg_fit) + '-lmax'+str(lmax) + '/'


pathExists(path_resultsCLM)
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


# matrix with all Clm of all limbs
allClmMatrix = np.zeros((totlimbs, radiusDiscretisation,
                        2, lmax, lmax), dtype=np.float32, order='C')

pb = ProgressBar(0, totlimbs, c=5)  # it should loop over totLimbs!!
printc('\n starting...', invert=1)
for j in pb.range():
    ##############################################
    # loading voxel intensities
    allIntensities = np.load(path + 'allIntensities_ReferenceShape_' +
                             str(limbs[j])[0:-1] + '_' + str(limbs[j])[-1] + '.npy')
    allIntensitiesShape = allIntensities.shape

    ##############################################
    # Forward Transformations (Splines and SPHARM)
    Clm = forwardTransformation(allIntensities, N, lmax)

    allClmMatrix[j, :, :, :, :] = Clm

    del Clm, allIntensities
    pb.print('Forward Transformations (splines and SPHARM) ...')

np.save(path_resultsCLM + 'allClmMatrix', allClmMatrix)
# np.save(pathOutClm + 'samplePointsCoord', samplePointsCoord)
# np.save(pathOutClm + 'allIntensities', allIntensities)
np.save(path_resultsCLM+'allIntensitiesShape', allIntensitiesShape)
printc('\n allIntensitiesShape.npy  \n', c='green')


##############################################
# splining
maxt = np.max(t)
mint = np.min(t)

xnew = np.linspace(mint, maxt, newTotLimbs)
allClmSpline = np.zeros(shape=(newTotLimbs, radiusDiscretisation,
                        2, allClmMatrix.shape[3], allClmMatrix.shape[4]))
# new clm from splines
range_m = np.linspace(
    0, newTotLimbs, num=allClmSpline.shape[0], endpoint=False).astype(int)


pb = ProgressBar(0, allClmMatrix.shape[1], c=5)
for f in pb.range():
    for ll in range(allClmMatrix.shape[2]):
        for k in range(allClmMatrix.shape[3]):
            for j in range(allClmMatrix.shape[4]):
                spl = np.poly1d(np.polyfit(np.array(t), np.array(
                    allClmMatrix[:, f, ll, k, j]), deg_fit))
                ynew = spl(xnew)

                for m in range(allClmSpline.shape[0]):
                    allClmSpline[m, f, ll, k, j] = ynew[range_m[m]]

    pb.print('splining ...')

print('allClmSpline.shape', allClmSpline.shape)


del allClmMatrix


np.save(path_resultsCLM + 'allClmSpline', allClmSpline)
printc('\n allClmSpline.npy \n', c='green')


##############################################
# vol parameters

pathTmp = 'res/TIF-signedDist_sampleSize' + str(sampleSize) + '/'


volTmp = load(pathTmp + 'ReferenceShape_290_2.vti')
pos = volTmp.center()
rmax = volTmp.diagonalSize()/2
volBounds = np.array(volTmp.GetBounds())
np.save(path_resultsCLM + 'volBounds', volBounds)
printc('\n volBounds.npy saved\n', c='green')

samplePoints = samplePoints(volTmp, expo, N, radiusDiscretisation)
del volTmp

##############################################
# inverse Transformations
pb = ProgressBar(0, allClmSpline.shape[0], c=5)
for t in pb.range():
    ##############################################
    # Inverse Transformations
    ##############################################
    inverse_Matrix = inverseTransformations(
        allClmSpline[t, :, :, :, :], allIntensitiesShape, N, lmax)

    intensitiesreshape = np.reshape(
        inverse_Matrix, inverse_Matrix.shape[0] * inverse_Matrix.shape[1])

    del inverse_Matrix

    # ##############################
    # #   interpolateToImageData
    voxBin = 100  # * radiusDiscretisation
    apts = Points(samplePoints).addPointArray(intensitiesreshape, 'scals')
    volume = interpolateToVolume(apts, kernel='shepard', radius=(
        rmax / 20), dims=(voxBin, voxBin, voxBin), bounds=volBounds)
    # printHistogram(volume, logscale=False, bins=25, c='g', minbin=3)
    del apts

    ##############################################
    # Reconstruction
    write(volume, path_results + 'Limb-rec_' +
          str(Treal[t]) + '.vti', binary=False)
    write(volume.isosurface(threshold=-0.01).smoothWSinc(),
          path_results + 'Limb-rec_' + str(Treal[t]) + '.vtk', binary=False)

    del volume

    pb.print('main reconstruction ... ')


##############################################
