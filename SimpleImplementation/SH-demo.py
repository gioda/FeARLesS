'''
author: zyx
date: 2024-12-12
description: 
    Complete 3D Reconstruction Using Spherical Harmonics
'''

import numpy as np
import os
from scipy.spatial.transform import Rotation as R
from scipy.interpolate import griddata
import pyshtools as shtools
import trimesh
from tqdm import tqdm
import pyvista as pv

# Parameters
lmax = 50       # Maximum degree of spherical harmonics
N = 500         # Number of grid points
rmax = 1400     # Maximum radius for reconstruction
## Data download from https://www.ebi.ac.uk/biostudies/bioimages/studies/S-BIAD441
input_path = "/home/zhangy8@hhmi.org/data3/Spherical_Harmonics/zyx/TestData"
output_path = "/home/zhangy8@hhmi.org/data3/Spherical_Harmonics/zyx/output/reconstructed_shapes/"
intensity_path = "/home/zhangy8@hhmi.org/data3/Spherical_Harmonics/zyx/output/voxel_intensities/"
os.makedirs(output_path, exist_ok=True)
os.makedirs(intensity_path, exist_ok=True)

def pathExists(path):
    if not os.path.exists(path):
        os.makedirs(path)

def voxelIntensity(vol, expo, N, radiusDiscretisation):
    '''
    Compute voxel intensities for a volume.
    '''
    grid_x = np.linspace(-1, 1, N) * radiusDiscretisation
    grid_y = np.linspace(-1, 1, N) * radiusDiscretisation
    grid_z = np.linspace(-1, 1, N) * radiusDiscretisation
    grid_x, grid_y, grid_z = np.meshgrid(grid_x, grid_y, grid_z, indexing="ij")

    # Compute intensities using the given volume data
    intensities = expo * vol.sample((grid_x, grid_y, grid_z))
    return intensities

def process_volumes(input_path, intensity_path, N, radiusDiscretisation, expo):
    '''
    Compute and save voxel intensities for volumetric datasets.
    '''
    volume_files = [f for f in os.listdir(input_path) if f.endswith('.vti')]

    for volume_file in tqdm(volume_files, desc="Processing volumes"):
        vol_path = os.path.join(input_path, volume_file)
        vol = pv.read(vol_path)

        allIntensities = voxelIntensity(vol, expo, N, radiusDiscretisation)

        name = f"intensities_{os.path.splitext(volume_file)[0]}.npy"
        np.save(os.path.join(intensity_path, name), allIntensities)
        print(f"Voxel intensities saved: {name}")

        shape_file = f"shape_{os.path.splitext(volume_file)[0]}.npy"
        np.save(os.path.join(intensity_path, shape_file), allIntensities.shape)
        print(f"Voxel intensity shape saved: {shape_file}")

# Forward transformation (spherical harmonics fitting)
def forwardTransformation(points, values, N, lmax):
    theta = np.arccos(points[:, 2] / np.linalg.norm(points, axis=1))
    phi = np.arctan2(points[:, 1], points[:, 0])

    grid = np.zeros((N, N))
    for t, p, v in zip(theta, phi, values):
        grid[int(t / np.pi * N), int(p / (2 * np.pi) * N)] = v

    sh_grid = shtools.SHGrid.from_array(grid)
    return sh_grid.expand(lmax=lmax)

# Inverse transformation (reconstruction)
def inverseTransformations(clm, shape, N, lmax):
    sh_grid = clm.expand(lmax=lmax)
    grid = sh_grid.to_array()
    x = np.linspace(-1, 1, shape[0])
    y = np.linspace(-1, 1, shape[1])
    z = np.linspace(-1, 1, shape[2])
    values = griddata((x, y, z), grid.flatten(), (x, y, z), method='linear')
    return values

# Function to compute spherical harmonic coefficients
def compute_spherical_harmonics(mesh, rmax, N, center):
    theta = np.linspace(0, np.pi, N, endpoint=False)
    phi = np.linspace(0, 2 * np.pi, N, endpoint=False)
    grid_theta, grid_phi = np.meshgrid(theta, phi, indexing='ij')

    radii = np.full(grid_theta.shape, rmax)
    for i in range(grid_theta.shape[0]):
        for j in range(grid_theta.shape[1]):
            direction = R.from_euler('zy', [grid_phi[i, j], grid_theta[i, j]]).apply([1, 0, 0])
            ray_origin = center
            locations = mesh.ray.intersects_location(
                ray_origins=[ray_origin], ray_directions=[direction]
            )
            if len(locations) > 0:
                radii[i, j] = np.linalg.norm(locations[0] - center)

    grid = shtools.SHGrid.from_array(radii)
    return grid.expand()

def reconstruct_shape(coeffs, lmax, rmax):
    # Directly use the SHRealCoeffs object to expand into a grid
    grid = coeffs.expand(lmax=lmax).to_array()

    # Convert spherical grid to Cartesian coordinates
    theta = np.linspace(0, np.pi, grid.shape[0], endpoint=True)
    phi = np.linspace(0, 2 * np.pi, grid.shape[1], endpoint=True)
    points = []
    for i, t in enumerate(theta):
        for j, p in enumerate(phi):
            r = grid[i, j]
            x = r * np.sin(t) * np.cos(p)
            y = r * np.sin(t) * np.sin(p)
            z = r * np.cos(t)
            points.append([x, y, z])

    return trimesh.points.PointCloud(np.array(points))


def process_all_meshes(input_path, output_path, lmax, rmax, N):
    mesh_files = [f for f in os.listdir(input_path) if f.endswith('.obj') or f.endswith('.stl') or f.endswith('.vtk')]

    for mesh_file in tqdm(mesh_files, desc="Processing meshes"):
        mesh_path = os.path.join(input_path, mesh_file)
        if mesh_file.endswith('.vtk'):
            # Convert VTK to trimesh-compatible format using pyvista
            pv_mesh = pv.read(mesh_path)
            vertices = np.array(pv_mesh.points)
            faces = np.array(pv_mesh.faces).reshape(-1, 4)[:, 1:]
            mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
        else:
            mesh = trimesh.load_mesh(mesh_path)

        center = mesh.centroid

        coeffs = compute_spherical_harmonics(mesh, rmax, N, center)

        coeffs_file = os.path.join(output_path, mesh_file.replace('.obj', '.npy').replace('.stl', '.npy').replace('.vtk', '.npy'))
        np.save(coeffs_file, coeffs.to_array())

        reconstructed_mesh = reconstruct_shape(coeffs, lmax, rmax)
        output_file = os.path.join(output_path, mesh_file.replace('.obj', '_reconstructed.ply').replace('.stl', '_reconstructed.ply').replace('.vtk', '_reconstructed.ply'))
        reconstructed_mesh.export(output_file)

if __name__ == "__main__":
    process_volumes(input_path, intensity_path, N, rmax, 1.0)
    process_all_meshes(input_path, output_path, lmax, rmax, N)
