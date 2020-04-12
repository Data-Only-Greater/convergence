# -*- coding: utf-8 -*-

# Copyright 2017-2020 Mathew Topper
#
# This file is part of convergence.
#
#    convergence is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    convergence is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with convergence.  If not, see <https://www.gnu.org/licenses/>.

import os

import pytest

from convergence.interface import main, simple_read, Convergence

THIS_DIR_PATH = os.path.dirname(__file__)
DATA_DIR_PATH = os.path.join(THIS_DIR_PATH, "..", "data")


@pytest.fixture(scope="module")
def convergence():
    in_path = os.path.join(DATA_DIR_PATH, "prD.do")
    main_list = simple_read(in_path)
    convergence = Convergence()
    convergence.add_grids(main_list)
    return convergence


@pytest.fixture(scope="module")
def convergence_anal():
    in_path = os.path.join(DATA_DIR_PATH, "prD.do")
    main_list = simple_read(in_path)
    convergence = Convergence(f_anal=0.9713)
    convergence.add_grids(main_list)
    return convergence


def test_interface(tmpdir):
    
    in_path = os.path.join(DATA_DIR_PATH, "prD.do")
    out_path = str(tmpdir.join("test_main.txt"))
    
    assert not os.path.isfile(out_path)
    
    import subprocess
    subprocess.call(["grid-convergence",
                     "-o", out_path,
                     in_path])
    
    assert os.path.isfile(out_path)


def test_main(tmpdir):
    
    in_path = os.path.join(DATA_DIR_PATH, "prD.do")
    out_path = str(tmpdir.join("test_main.txt"))
    
    assert not os.path.isfile(out_path)
    
    main(in_path, out_path)
    
    assert os.path.isfile(out_path)


def test_convergence_str(convergence):
    
    expected_lines = (
'',
'Number of grids to be examined = 3 ',
'',
'     Grid Size     Quantity ',
'',
'     1.000000      0.970500 ',
'     2.000000      0.968540 ',
'     4.000000      0.961780 ',
'',
'',
'Discretisation errors for fine grids: ',
'',
'       Grids |     e_approx |     e_extrap |      f_exact |   gci_coarse | ',
' ========================================================================= ',
'       1 2 3 |     0.002020 |     0.000824 |     0.971300 |     0.003555 | ',
' ------------------------------------------------------------------------- ',
'',
'       Grids |     gci_fine |            p |          r21 |          r32 | ',
' ========================================================================= ',
'       1 2 3 |     0.001031 |     1.786170 |     2.000000 |     2.000000 | ',
' ------------------------------------------------------------------------- ',
'',
'',
'Discretisation errors for coarse grids: ',
'',
'       Grids |     e_approx |     e_extrap |      f_exact |   gci_coarse | ',
' ========================================================================= ',
'       1 2 3 |     0.006980 |     0.002842 |     0.971300 |     0.012287 | ',
' ------------------------------------------------------------------------- ',
'',
'       Grids |     gci_fine |            p |          r21 |          r32 | ',
' ========================================================================= ',
'       1 2 3 |     0.003562 |     1.786170 |     2.000000 |     2.000000 | ',
' ------------------------------------------------------------------------- ',
'',
'',
'Asymptotic ratio test: ',
'',
'           Grids | Asymptotic ratio | ',
' ==================================== ',
'           1 2 3 |         0.997980 | ',
' ------------------------------------ ',
'')
    
    for actual, expected in zip(str(convergence).split("\n"),
                                expected_lines):
        assert actual == expected


def test_convergence_anal_str(convergence_anal):
    
    expected_lines = (
'',
'Number of grids to be examined = 3 ',
'',
'     Grid Size     Quantity ',
'',
'     1.000000      0.970500 ',
'     2.000000      0.968540 ',
'     4.000000      0.961780 ',
'',
'',
'Discretisation errors for fine grids: ',
'',
'       Grids |   e_analytic |     e_approx |     e_extrap |   f_analytic | ',
' ========================================================================= ',
'       1 2 3 |     0.000824 |     0.002020 |     0.000824 |     0.971300 | ',
' ------------------------------------------------------------------------- ',
'',
'       Grids |      f_delta |      f_exact |   gci_coarse |     gci_fine | ',
' ========================================================================= ',
'       1 2 3 |    -0.000000 |     0.971300 |     0.003555 |     0.001031 | ',
' ------------------------------------------------------------------------- ',
'',
'       Grids |            p |          r21 |          r32 | ',
' ========================================================== ',
'       1 2 3 |     1.786170 |     2.000000 |     2.000000 | ',
' ---------------------------------------------------------- ',
'',
'',
'Discretisation errors for coarse grids: ',
'',
'       Grids |   e_analytic |     e_approx |     e_extrap |   f_analytic | ',
' ========================================================================= ',
'       1 2 3 |     0.002842 |     0.006980 |     0.002842 |     0.971300 | ',
' ------------------------------------------------------------------------- ',
'',
'       Grids |      f_delta |      f_exact |   gci_coarse |     gci_fine | ',
' ========================================================================= ',
'       1 2 3 |    -0.000000 |     0.971300 |     0.012287 |     0.003562 | ',
' ------------------------------------------------------------------------- ',
'',
'       Grids |            p |          r21 |          r32 | ',
' ========================================================== ',
'       1 2 3 |     1.786170 |     2.000000 |     2.000000 | ',
' ---------------------------------------------------------- ',
'',
'',
'Asymptotic ratio test: ',
'',
'           Grids | Asymptotic ratio | ',
' ==================================== ',
'           1 2 3 |         0.997980 | ',
' ------------------------------------ ',
'')
    
    for actual, expected in zip(str(convergence_anal).split("\n"),
                                expected_lines):
        assert actual == expected


@pytest.mark.parametrize("test_input,expected",
                         [(('asymptotic_ratio', None), 0.997980422462648),
                          (('grids', None), '1 2 3'),
                          (('sizes', None), [1.0, 2.0, 4.0]),
                          (('values', None), [0.9705, 0.96854, 0.96178]),
                          (('fine', 'e_approx'), 0.0020195775373519553),
                          (('fine', 'e_extrap'), 0.0008239813226325151),
                          (('fine', 'f_exact'), 0.9713003333333334),
                          (('fine', 'gci_coarse'), 0.0035552979563800613),
                          (('fine', 'gci_fine'), 0.0010308260346901172),
                          (('fine', 'p'), 1.7861695921669198),
                          (('fine', 'r21'), 2.0),
                          (('fine', 'r32'), 2.0),
                          (('coarse', 'e_approx'), 0.0069795775084147155),
                          (('coarse', 'e_extrap'), 0.002841894765814084),
                          (('coarse', 'f_exact'), 0.9713003333333334),
                          (('coarse', 'gci_coarse'), 0.012286964572105267),
                          (('coarse', 'gci_fine'), 0.0035624926865868733),
                          (('coarse', 'p'), 1.7861695921669198),
                          (('coarse', 'r21'), 2.0),
                          (('coarse', 'r32'), 2.0)])
def test_nspace(convergence, test_input, expected):
    
    nspace = convergence[0]
    first_level =  vars(nspace)[test_input[0]]
    
    if test_input[1] is None:
        test_value = first_level
    else:
        test_value = vars(first_level)[test_input[1]]
    
    assert test_value == expected


@pytest.mark.parametrize("test_input,expected",
                         [(('fine', 'e_analytic'), 0.000823638422732444),
                          (('fine', 'f_analytic'), 0.9713),
                          (('fine', 'f_delta'), -3.33333333379926e-07),
                          (('coarse', 'e_analytic'), 0.002841552558426949),
                          (('coarse', 'f_analytic'), 0.9713),
                          (('coarse', 'f_delta'), -3.33333333379926e-07)])
def test_nspace_anal(convergence_anal, test_input, expected):
    
    nspace = convergence_anal[0]
    first_level =  vars(nspace)[test_input[0]]
    
    if test_input[1] is None:
        test_value = first_level
    else:
        test_value = vars(first_level)[test_input[1]]
    
    assert test_value == expected


def test_convergence_len(convergence):
    assert len(convergence) == 1


def test_convergence_no_len():
    convergence = Convergence()
    assert len(convergence) == 0


def test_convergence_iter(convergence):
    
    for check in convergence:
        assert check.asymptotic_ratio == 0.997980422462648


def test_convergence_no_iter():
    convergence = Convergence()
    with pytest.raises(IndexError):
        convergence[0]


def test_convergence_iter_bad_key(convergence):
    with pytest.raises(TypeError):
        convergence["a"]
