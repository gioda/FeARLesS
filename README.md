<!-- PROJECT SHIELDS -->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![CI status][CI-shield]][CI-url]
<!-- [![LinkedIn][linkedin-shield]][linkedin-url] -->


<h1 align="center"> 4D reconstruction of developmental trajectories <br />
  using spherical harmonics </h1>
<p>
  <a href="https://twitter.com/giodalmasso" target="_blank">
    <img alt="Twitter: giodalmasso" src="https://img.shields.io/twitter/follow/giodalmasso.svg?style=social" />
  </a>
</p>


### 🏠 [Homepage](https://vedo.embl.es/fearless/#/home)

<br />

<p align="justify">
Computer based approach to recreate the continuous evolution in time and space of developmental stages from <b><i>3D volumetric images</i></b>. This method uses the mathematical approach of <b><i>spherical harmonics</i></b> to re-map discrete shape data into a space in which facilitates a smooth interpolation over time.

This aproach was tested on mouse limb buds (from E10 to E12.5) and embryonic hearts (from 10 to 29 somites). 

A key advantage of this method is that the resulting <b><i>4D trajectory</i></b> takes advantage of all the available data, while also being able to interpolate well through time intervals for which there is little or no data.

For more information --> https://doi.org/10.1101/2021.12.16.472948
</p>


<br />

![video](https://user-images.githubusercontent.com/29924733/146750585-d6c0b9cb-8b5c-49c7-86f9-92fba875b14d.mp4)


---
<p align="justify">

## Datasets


All the data can be dowloaded from --> https://www.ebi.ac.uk/biostudies/studies/S-BIAD441 (folders `/limbs-noFlank/` and `/limbs+flank/`).


## Pipeline

Follow the pipeline steps below to reproduce the analysis results.


#### `python pureSPharm.py`
- _Description:_ compute the spherical harmonics decomposition and reconstruction producing the 4D trajectory of the growing limb buds _without the flank_ (original data can be found in the folder `/limbs-noFlank/` of the archive). 
- _Usage:_ in the code, `DataPath` should be change to the location of the folder `/limbs-noFlank/` downloaded from the archive. Run the code with the command: `python pureSPharm.py lmax`, where `lmax` is the desired degree of shaprical harmonics expansion. 
- _Results:_ the results will be stored in a floder created automatically of the form `res/pure_spharm-lmax-N-deg_fit/` where `N` is the number of grid intervals on the sphere and `deg_fit` the degree of interpolation of the spherical harmonics coefficients. If the results folder already exists the code will ask if the user wants to delete it and continue or stop.

---

#### `python makeVoxel.py`
- _Description:_ convert a vtk mesh from the limb-data files into voxel data (original data can be found in the folder `/limbs+flank/` of the archive).
- _Usage:_ in the code, `DataPath` should be change to the location of the folder `/limbs+flank/` downloaded from the archive. Run the code with the command: `python makeVoxel.py`.
- _Results:_ ihe results will be stored in a floder created automatically of the form `res/TIF-signedDist_sampleSize100/`. Changing in the code the variable `sampleSize` will also change the name of the results folder. If the results folder already exists the code will ask if the user wants to delete it and continue or stop.

---

#### `python computeAllIntesities.py`
- _Description:_ compute the voxel intensities along the radii of a sphere of the voxel-limb-data obtained in the previous step.
- _Usage:_ in the code, `DataPath` should be change to the location of the folder `res/TIF-signedDist_sampleSize100/` obtained in the previous step. Run the code with the command: `python computeAllIntesities.py`.
- _Results:_ ihe results will be stored in a floder created automatically of the form `res/allIntensities-sampleSize100-radiusDiscretisation-N/` where `radiusDiscretisation` is the discretisation of the radii of the sphere and `N` is the number of grid intervals on the sphere. Changing in the code the variable `radiusDiscretisation` and `N` will also change the name of the results folder. If the results folder already exists the code will ask if the user wants to delete it and continue or stop. The results will be in the form of _numpy_ files, one for each limb.

---

#### `python morphing.py`
- _Description:_ produce the 4D trajectory of the growing limb buds _with the flank_ using the voxel intensities computed in the previous step.
- _Usage:_ in the code, `path` should be change to the location of the folder `res/allIntensities-sampleSize100-radiusDiscretisation-N/`obtained in the previous step. Run the code with the command: `python morphing.py`.
- _Results:_ two folder will be created automatically, `res/CLM/morphing_sampleSize-radDisc-N-degFit-lmax/` and `res/morphing_sampleSize-radDisc-N-degFit-lmax/` (where `sampleSize` is voxel dimension of the data, `radDisc` is the discretisation of the radii of the sphere and `N` is the number of grid intervals on the sphere, `degFit` is the degree of interpolation of the spherical harmonics coefficients and `lmax` is the desired degree of shaprical harmonics expansion). In the first one, a matrix containing the shperical harmonics coefficients will be stored (in the form of _numpy_ file) and in the second the volumes and isosurfaces of the limbs forming the 4D trajectory. If the results folders already exist the code will ask if the user wants to delete them and continue or stop.
  
---
  
### `python utils.py`
- _Description:_ contains some basic functions used.

</p>
  
---

## Authors

👤 **Giovanni Dalmasso**

* Website: https://tinyurl.com/yc6pbyb2
* Twitter: [@giodalmasso](https://twitter.com/giodalmasso)
* Github: [@gioda](https://github.com/gioda)
* LinkedIn: [@giovanni-dalmasso](https://linkedin.com/in/giovanni-dalmasso)

👤 **Marco Musy**

* Website: https://tinyurl.com/3zy9zmmy
* Github: [@marcomusy](https://github.com/marcomusy)


## 🤝 Contributing

Contributions, issues and feature requests are welcome!<br />Feel free to check [issues page](https://github.com/gioda/4D-reconstruction-of-developmental-trajectories-using-spherical-harmonics/issues). 

## Show your support

Give a ⭐️ if this project helped you!<br />
  <br />


[![vedo_powered](https://user-images.githubusercontent.com/32848391/94372929-13e0e400-0102-11eb-938c-bc0274d57108.png)](https://github.com/marcomusy/vedo)

![embl](https://user-images.githubusercontent.com/32848391/94371851-c3658880-00f9-11eb-9c2a-d418adb93d59.gif)

## 📝 License

Copyright © 2021 [Giovanni Dalmasso](https://github.com/gioda).<br />
This project is [MIT](https://github.com/gioda/4D-reconstruction-of-developmental-trajectories-using-spherical-harmonics/blob/main/LICENSE) licensed.  





<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/gioda/4D-reconstruction-of-developmental-trajectories-using-spherical-harmonics
[contributors-url]: https://github.com/gioda/4D-reconstruction-of-developmental-trajectories-using-spherical-harmonics/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/gioda/4D-reconstruction-of-developmental-trajectories-using-spherical-harmonics
[forks-url]: https://github.com/gioda/4D-reconstruction-of-developmental-trajectories-using-spherical-harmonics/network/members
[stars-shield]: https://img.shields.io/github/stars/gioda/4D-reconstruction-of-developmental-trajectories-using-spherical-harmonics
[stars-url]: https://github.com/gioda/4D-reconstruction-of-developmental-trajectories-using-spherical-harmonics/stargazers
[issues-shield]: https://img.shields.io/github/issues/gioda/4D-reconstruction-of-developmental-trajectories-using-spherical-harmonics
[issues-url]: https://github.com/gioda/4D-reconstruction-of-developmental-trajectories-using-spherical-harmonics/issues
[license-shield]: https://img.shields.io/github/license/gioda/4D-reconstruction-of-developmental-trajectories-using-spherical-harmonics
[license-url]: https://github.com/gioda/4D-reconstruction-of-developmental-trajectories-using-spherical-harmonics/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/giovanni-dalmasso
[product-screenshot]: images/screenshot.png
<!-- [product-screenshot]: images/screenshot.png -->
[CI-shield]: https://github.com/dguo/make-a-readme/workflows/CI/badge.svg
[CI-url]: https://github.com/gioda/4D-reconstruction-of-developmental-trajectories-using-spherical-harmonics/actions

