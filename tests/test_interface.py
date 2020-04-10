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

from convergence.interface import main, simple_read, Convergence

this_dir_path = os.path.dirname(__file__)
data_dir_path = os.path.join(this_dir_path, "..", "data")


def test_interface(tmpdir):
    
    in_path = os.path.join(data_dir_path, "prD.do")
    out_path = str(tmpdir.join("test_main.txt"))
    
    assert not os.path.isfile(out_path)
    
    import subprocess
    subprocess.call(["grid-convergence",
                     "-o", out_path,
                     in_path])
    
    assert os.path.isfile(out_path)


def test_main(tmpdir):
    
    in_path = os.path.join(data_dir_path, "prD.do")
    out_path = str(tmpdir.join("test_main.txt"))
    
    assert not os.path.isfile(out_path)
    
    main(in_path, out_path)
    
    assert os.path.isfile(out_path)


def test_Convergence_str():
    
    in_path = os.path.join(data_dir_path, "prD.do")
    main_list = simple_read(in_path)
    convergence = Convergence()
    convergence.add_grids(main_list)
    
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
    
    expected = "\n".join(expected_lines)
    
    assert str(convergence) == expected
