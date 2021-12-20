#!/usr/bin/env python
#
# @Author: Giovanni Dalmasso <gio>
# @Date:   15-Dec-2021
# @Email:  giovanni.dalmasso@embl.es
# @Project: FeARLesS
# @Filename: pureSPharm.py
# @Last modified by:   gio
# @Last modified time: 15-Dec-2021
# @License: MIT
# @Copyright: Copyright © 2021 Giovanni Dalmasso


from sys import argv, exit
from scipy.interpolate import griddata
import numpy as np

from vedo import printc, load, spher2cart, mag, ProgressBar,   Points, recoSurface, write
from utils import pathExists

import pyshtools
#############################################################


def computeCLM(mesh, rmax, N, x0):
    """Compute CLM."""
    # cast rays from the center and find intersections
    agrid, pts = [], []
    for th in np.linspace(0, np.pi, N, endpoint=False):
        lats = []
        for ph in np.linspace(0, 2*np.pi, N, endpoint=False):
            p = spher2cart(rmax, th, ph)
            intersections = mesh.intersectWithLine(x0, x0 + p)
            if len(intersections):
                value = mag(intersections[0]-x0)
                lats.append(value)
                pts.append(intersections[0])
            else:
                lats.append(rmax)
                # lats.append(0)
                pts.append(p)
        agrid.append(lats)
    agrid = np.array(agrid)

    grid = pyshtools.SHGrid.from_array(agrid)
    clm = grid.expand()
    # grid_reco = clm.expand(lmax=lmax)  # cut "high frequency" components

    return clm
#############################################################


#####################################
# PARAMETERS
parameters = argv
if len(parameters) != 2:
    printc('missing parameters!!!', c='r')
    exit()

#############################################################
# lmax = int(parameters[1])       # maximum degree of the spherical harm. expansion
lmax = 50
N = 500          # number of grid intervals on the unit sphere
rmax = 1400  # 2.0
x0 = [0, 0, 0]  # set object at this position
xLimb = [-200, 0, 200]
cutOrigin = [150, 0, 0]

deg_fit = 6


LimbsPath = '../data/Limbs_noFlank/'
path_results = 'res/' \
    'pure_spharm' + '-lmax' + str(lmax) + '-N' + \
    str(N) + '-deg_fit' + str(deg_fit) + '/'


pathExists(path_results)

printc('lmax =', lmax, 'N =', N, 'deg_fit =', deg_fit, c='y')

printc("loading limbs ...", c='y')
limbs = load(LimbsPath + '*.vtk')

totLimbs = len(limbs)
printc('tot # limbs --> ', totLimbs, c='y')


# CM = limbs[-1].centerOfMass()
# show(limbs[-1].pos(xLimb), Sphere(pos=x0, r=rmax, alpha=0.9),
#      Point(x0, r=20, c='b'), Point(CM, r=20, c='r'))

# exit()

################################
# finding time from limbs' file names
Tall = []
for j in range(totLimbs):
    # Tall.append(float(limbs[j].filename.split('/')[-1].split('_')[0]))
    Tall.append(float(limbs[j].filename.split('/')[-1].split('_')[1]))

Tall = np.array(Tall)
printc('Tall \n', Tall, c='y')

Treal = np.arange(Tall[0], Tall[-1]+1, dtype=int)

NumRecLimbs = len(Treal)


Mclm = []
pb = ProgressBar(0, totLimbs, c=2)
for j in pb.range():
    Mtmp = []
    clmAllTmp = []
    Mtmp.append(float(limbs[j].filename.split('/')[-1].split('_')[1]))

    clmTmp = computeCLM(limbs[j].pos(xLimb), rmax, N, x0)

    clmAllTmp.append(clmTmp.to_array())
    Mtmp.append(np.asarray(clmAllTmp))

    Mclm.append(Mtmp)

    pb.print('clm...')

CLM = sorted(Mclm, key=lambda tup: tup[0])

CLMtot = []
for j in range(len(CLM)):
    CLMtot.append(CLM[j][1])

CLMtot = np.asarray(CLMtot)
CLMtot = np.squeeze(CLMtot, axis=1)

filename = 'clm_N' + str(N) + '_lmax'+str(lmax) + '.npy'
printc('saving --> ', filename, c='g')
np.save(path_results + filename, CLMtot)


# CLMtot = np.load(path_results + 'clm_N500_lmax50.npy')

clmSpline = np.zeros(
    shape=(NumRecLimbs, CLMtot.shape[1], CLMtot.shape[2], CLMtot.shape[3]))
print('clmSpline.shape', clmSpline.shape)


maxt = np.max(Treal)
mint = np.min(Treal)
xnew = np.linspace(mint, maxt, NumRecLimbs)
range_m = np.linspace(
    0, NumRecLimbs, num=clmSpline.shape[0], endpoint=False).astype(int)


pb = ProgressBar(0, CLMtot.shape[1], c=2)
for ll in pb.range():
    for k in range(CLMtot.shape[2]):
        for j in range(CLMtot.shape[3]):

            spl = np.poly1d(np.polyfit(
                np.array(Tall), np.array(CLMtot[:,  ll, k, j]), deg_fit))
            ynew = spl(xnew)

            for m in range(clmSpline.shape[0]):
                clmSpline[m, ll, k, j] = ynew[range_m[m]]

    pb.print('splines...')


pb = ProgressBar(0, clmSpline.shape[0], c=2)
for t in pb.range():

    clmCoeffs = pyshtools.SHCoeffs.from_array(clmSpline[t])

    grid_reco = clmCoeffs.expand(lmax=lmax)
    # grid_reco.plot()

    ##############################################
    agrid_reco = grid_reco.to_array()

    ll = []
    for i, long in enumerate(np.linspace(0, 360, num=agrid_reco.shape[1], endpoint=True)):
        for j, lat in enumerate(np.linspace(90, -90, num=agrid_reco.shape[0], endpoint=True)):
            th = np.deg2rad(90 - lat)
            ph = np.deg2rad(long)
            p = spher2cart(agrid_reco[j][i], th, ph)
            ll.append((lat, long))

    radii = agrid_reco.T.ravel()
    n = 2*N * 1j
    lnmin, lnmax = np.array(ll).min(axis=0), np.array(ll).max(axis=0)
    grid = np.mgrid[lnmax[0]:lnmin[0]:n, lnmin[1]:lnmax[1]:n]
    grid_x, grid_y = grid
    agrid_reco_finer = griddata(ll, radii, (grid_x, grid_y), method='cubic')

    pts2 = []
    for i, long in enumerate(np.linspace(0, 360, num=agrid_reco_finer.shape[1], endpoint=False)):
        for j, lat in enumerate(np.linspace(90, -90, num=agrid_reco_finer.shape[0], endpoint=True)):
            th = np.deg2rad(90 - lat)
            ph = np.deg2rad(long)
            p = spher2cart(agrid_reco_finer[j][i], th, ph)
            pts2.append(p)

    mesh2 = Points(pts2, r=20, c="r", alpha=1)
    # .cutWithPlane(origin=[0, 0, 0])  # .scale(1/scalingF[t])
    mesh2.clean(0.005)

    surfTmp = recoSurface(mesh2.cutWithPlane(origin=[-30, 0, 0]),
                          dims=100
                          )

    surf = surfTmp.extractLargestRegion().clone()
    surf.smooth()

    # #Reconstruction
    # write(mesh2, path_results + 'Points_Limb-rec_' +
    #       str(Treal[t]) + '.vtk', binary=False)
    write(surf, path_results + 'Limb-rec_' +
          str(Treal[t]) + '.vtk', binary=False)

    pb.print('rec ...')
