# convergence

A Python program to Perform Calculations Associated with a Grid Convergence
Study.

******

[![](https://img.shields.io/badge/python-2.7-blue.svg)](https://www.python.org/download/releases/2.7.0/) 
[![](https://img.shields.io/badge/python-3.5-blue.svg)](https://www.python.org/download/releases/3.5.0/) 
[![](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/download/releases/3.6.0/) 
[![](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/download/releases/3.7.0/) 
[![](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/download/releases/3.8.0/) 

![](https://img.shields.io/badge/platform-linux-lightgrey.svg)
[![](https://img.shields.io/travis/Data-Only-Greater/convergence)](https://travis-ci.com/github/Data-Only-Greater/convergence)

![](https://img.shields.io/badge/platform-windows-lightgrey.svg)
[![](https://img.shields.io/appveyor/build/Data-Only-Greater/convergence)](https://ci.appveyor.com/project/DataOnlyGreater/convergence)

[![](https://img.shields.io/codecov/c/github/Data-Only-Greater/convergence)](https://codecov.io/gh/Data-Only-Greater/convergence)

## Introduction

This is a port of verify.f90, a program provided as part of the NASA Examining
Spatial (Grid) Convergence tutorial.

http://www.grc.nasa.gov/WWW/wind/valid/tutorial/spatconv.html

Additional changes have been made to reflect the recommendations in:

Celik, I. B., Ghia, U., & Roache, P. J. (2008). Procedure for estimation and
reporting of uncertainty due to discretization in CFD applications. Journal of
fluids Engineering-Transactions of the ASME, 130(7).

This code was written by Mathew Topper between 2009 and 2011 as part of the
Supergen Marine Research Consortium project. I was younger then and would
do many things differently now. I am working on updating this code to make
the main class and functions more easy to use and also integrate into other
projects. Watch this space.

## Installation

The package requires no dependencies and is currently available for Pythons 
2.7, 3.5, 3.6, 3.7 and 3.8.

The package can be installed by downloading the source code, and using a
terminal or command prompt as follows:

```
cd /path/to/convergence
python setup.py install
```

The package can also be downloaded from PyPI, again using a
terminal or command prompt:

```
pip install convergence
```

## Basic Usage

The package provides a command line interface which is the main (and currently 
only sensible) way to use the package. The input data must be a space delimeted 
text file with the first column being the grid spacing and the second column 
being the metric of interest. An example can be found in the _data_ folder of 
the source code.

The program can then be executed as follows: 

```
grid-convergence /path/to/data/file
```

By default, the results of the program are written to a file called 
_verify_report.txt_ in the calling directory. The file name can be changed
using the _-o_ or _--out_ command line options. The format of the file
is as follows:

    --- VERIFY: Performs verification calculations --- 

    Number of grids to be examined = 3 

         Grid Size     Quantity 

         1.000000      0.970500 
         2.000000      0.968540 
         4.000000      0.961780 


    Discretisation errors for fine grids:

           Grids |     e_approx |     e_extrap |      f_exact |   gci_coarse | 
     =========================================================================
           1 2 3 |     0.002020 |     0.000824 |     0.971300 |     0.003555 | 
     -------------------------------------------------------------------------

           Grids |     gci_fine |            p |          r21 |          r32 | 
     =========================================================================
           1 2 3 |     0.001031 |     1.786170 |     2.000000 |     2.000000 | 
     -------------------------------------------------------------------------


    Discretisation errors for coarse grids:

           Grids |     e_approx |     e_extrap |      f_exact |   gci_coarse | 
     =========================================================================
           1 2 3 |     0.006980 |     0.002842 |     0.971300 |     0.012287 | 
     -------------------------------------------------------------------------

           Grids |     gci_fine |            p |          r21 |          r32 | 
     =========================================================================
           1 2 3 |     0.003562 |     1.786170 |     2.000000 |     2.000000 | 
     -------------------------------------------------------------------------


    Asympototic ratio test:

               Grids | Asymptotic ratio | 
     ====================================
               1 2 3 |         0.997980 | 
     ------------------------------------


    --- End of VERIFY --- 

In the first table the input data is displayed. The second table shows the
fine analysis results for each trio of grids and the second table shows the
coarse analysis results for each trio. The final table shows the asymptotic
ratio.

The headers of the tables have the following meanings:

+ **Grids**: the trio of grids being analysed
+ **e_approx**: approximate relative error
+ **e_extrap**: extrapolated relative error
+ **f_exact**: the estimated the zero grid spacing value
+ **gci_coarse**: coarse grid convergence index
+ **gci_fine** fine grid convergence index
+ **p**: order of convergence
+ **r21**: ratio of the middle to fine grid spacing
+ **r32**: ratio of the coarse to middle grid spacing

## Known Analytical Result

If there is a known zero spacing value for the convergence study this value
can be added to the analysis using the _-a_ or _--analytical_ command line
option. To illustrate, the basic example would now become:

```
grid-convergence /path/to/data/file -a 0.12345
```

Additional headers now appear in the fine and coarse analysis tables with the
following meanings:

+ **e_analytic**: analytical relative error
+ **f_analytic**: the analytical the zero grid spacing value
+ **f_delta**: the different between the analytical and estimated zero grid
               spacing value

## License

This program is free software: you can redistribute it and/or modify it under 
the terms of the GNU General Public License as published by the Free Software 
Foundation, either version 3 of the License, or (at your option) any later 
version. 

This program is distributed in the hope that it will be useful, but WITHOUT ANY 
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A 
PARTICULAR PURPOSE. See the GNU General Public License for more details. 

You should have received a copy of the GNU General Public License along with 
this program. If not, see <https://www.gnu.org/licenses/>. 
