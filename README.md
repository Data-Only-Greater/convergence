# convergence

A Python program to Perform Calculations Associated with a Grid Convergence
Study.

******

[![python](https://img.shields.io/badge/dynamic/yaml?label=python&query=%24.jobs.pytest.strategy.matrix[%27python-version%27][:]&url=https%3A%2F%2Fraw.githubusercontent.com%2FData-Only-Greater%2Fconvergence%2Fmaster%2F.github%2Fworkflows%2Funit_tests.yml)](https://www.python.org/)
[![platform](https://img.shields.io/badge/dynamic/yaml?label=os&query=%24.jobs.pytest.strategy.matrix.os[:]&url=https%3A%2F%2Fraw.githubusercontent.com%2FData-Only-Greater%2Fconvergence%2Fmaster%2F.github%2Fworkflows%2Funit_tests.yml)](https://en.wikipedia.org/wiki/Usage_share_of_operating_systems#Desktop_and_laptop_computers)

[![unit tests](https://github.com/Data-Only-Greater/convergence/actions/workflows/unit_tests.yml/badge.svg)](https://github.com/Data-Only-Greater/convergence/actions/workflows/unit_tests.yml)
[![documentation](https://github.com/Data-Only-Greater/convergence/actions/workflows/docs.yml/badge.svg)](https://github.com/Data-Only-Greater/convergence/actions/workflows/docs.yml)

[![](https://img.shields.io/codecov/c/github/Data-Only-Greater/convergence)](https://codecov.io/gh/Data-Only-Greater/convergence)
[![](https://img.shields.io/pypi/v/convergence)](https://pypi.org/project/convergence/)

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
2.7, 3.6, 3.7, 3.8 and 3.9.

The latest stable version of the package can be downloaded from PyPI using 
[pip](https://packaging.python.org/tutorials/installing-packages/):

```
pip install convergence
```

The development version of the package can be installed by cloning or 
downloading the source code, and using the command prompt as follows: 

```
cd /path/to/convergence
python setup.py install
```

Note that the stable version may not contain all of the features found in the
development version but it should be more reliable.

## Basic Usage

The most straightforward method of using convergence is to generate a report
which details the grid convergence metrics for a given set of grids.

### Command Line

The package provides a command line interface. The input data must be a space 
delimited text file with the first column being the grid spacing and the second 
column being the metric of interest. An example can be found in the _data_ 
folder of the source code. The program can then be executed as follows: 

```
grid-convergence /path/to/data/file
```

By default, the results of the program are written to a file called 
_verify_report.txt_ in the calling directory. The file name can be changed
using the _-o_ or _--out_ command line options.

### Scripting

The package can also be used from within a script. Grids are provided in a 
list of pairs, i.e `[(size1, value1), (size2, value2), ...]`. Example usage
is:

```python
>>> from __future__ import print_function
>>> from convergence import Convergence
>>> grids = [(1.000000, 0.970500),
...          (2.000000, 0.968540),
...          (4.000000, 0.961780)]
>>> convergence = Convergence()
>>> convergence.add_grids(grids)
>>> print(convergence) # doctest:+ELLIPSIS
<BLANKLINE>
Number of grids to be examined = 3 ...

```

### Expected Output

The result, contained in the output file when using the command line interface 
or when printing a `Convergence` object, will resemble the following: 

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


    Asymptotic ratio test:

               Grids | Asymptotic ratio | 
     ====================================
               1 2 3 |         0.997980 | 
     ------------------------------------

In the first table the input data is displayed. The second table shows the
fine analysis results for each trio of grids and the second table shows the
coarse analysis results for each trio. The final table shows the asymptotic
ratio.

The headers of the tables have the following meanings:

+ **Grids**: the trio of grids being analysed
+ **e_approx**: approximate relative error
+ **e_extrap**: extrapolated relative error
+ **f_exact**: the estimated value at zero grid spacing 
+ **gci_coarse**: coarse grid convergence index
+ **gci_fine** fine grid convergence index
+ **p**: order of convergence
+ **r21**: ratio of the middle to fine grid spacing
+ **r32**: ratio of the coarse to middle grid spacing

## Advanced Usage

### Known Analytical Result

If there is a known zero spacing value for the convergence study this value
can be added to the analysis using the _-a_ or _--analytical_ command line
option. To illustrate, the basic example would now become:

```
grid-convergence /path/to/data/file -a 0.12345
```

Alternatively, when using the `Convergence` class, add the analytical value
when instantiating the object, using the `f_anal` argument:

```python
>>> convergence = Convergence(f_anal=0.9713)
>>> convergence.add_grids(grids)
>>> print(convergence) # doctest:+SKIP
```

Additional headers now appear in the fine and coarse analysis tables with the
following meanings:

+ **e_analytic**: analytical relative error
+ **f_analytic**: the analytical value at zero grid spacing
+ **f_delta**: the different between the analytical and estimated zero grid
               spacing values

### Report Attribute Access

Values for the report attributes can be accessed through the `Convergence`
class. A namespace containing the values for each triplet of grids is stored in 
the items of a `Convergence` object, ordered from finest to coarsest. For 
example:

```python
>>> len(convergence)
1
>>> convergence[0] # doctest:+ELLIPSIS
Namespace(...

```

Values associated the both the fine and coarse grids are available at the
first level of the namespace. For example, to get the asymptotic ratio of the
finest triplet of grids:

```python
>>> convergence[0].asymptotic_ratio
0.997980422462648

```

Values associated to either the fine of coarse analysis, are stored under the
`fine` and `coarse` keys. For example, to examine the extrapolated relative 
errors:

```python
>>> convergence[0].fine.e_extrap
0.0008239813226325151
>>> convergence[0].coarse.e_extrap
0.002841894765814084

```

### Required Grid Resolution

To determine the required grid resolution for a given GCI value the
`get_resolution` method can be used. For example:

```python
>>> convergence.get_resolution(0.001)
0.9831461212423797

```

By default the GCI for the fine grid is used. To use the coarse grid estimate
pass `"coarse"` as the second optional argument:

```python
>>> convergence.get_resolution(0.001, "coarse")
0.49157306062118994

```

Note that the equation in the NASA tutorial is incorrect. If 
<img src="https://render.githubusercontent.com/render/math?math=\text{GCI}*">
is the desired accuracy and <img src="https://render.githubusercontent.com/render/math?math=h*">
is the required resolution, then:

<p align="center">
<img src="https://render.githubusercontent.com/render/math?math=\displaystyle r = \left( \frac{\text{GCI}_{12}}{\text{GCI}*} \right)^{p^{-1}}">
</br></br>
<img src="https://render.githubusercontent.com/render/math?math=\displaystyle h* = \frac{h_1}{r}">
</p>

## License

Copyright 2011 SuperGen Marine Energy Research Consortium  
Copyright 2013 SuperGen UK Centre for Marine Energy Research  
Copyright 2017-2020 Mathew Topper

This program is free software: you can redistribute it and/or modify it under 
the terms of the GNU General Public License as published by the Free Software 
Foundation, either version 3 of the License, or (at your option) any later 
version. 

This program is distributed in the hope that it will be useful, but WITHOUT ANY 
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A 
PARTICULAR PURPOSE. See the GNU General Public License for more details. 

You should have received a copy of the GNU General Public License along with 
this program. If not, see <https://www.gnu.org/licenses/>. 
