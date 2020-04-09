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

from convergence import Convergence, simple_read

this_dir_path = os.path.dirname(__file__)
data_dir_path = os.path.join(this_dir_path, "..", "data")


def test_main(tmpdir):
    
    in_path = os.path.join(data_dir_path, "prD.do")
    out_path = str(tmpdir.join("test_main.txt"))
    
    assert not os.path.isfile(out_path)
    
    # Read in the file
    main_list = simple_read(in_path)
    
    # Run convergence study
    mainver = Convergence(main_list)
        
    # Write the report
    mainver.add_file(out_path, write_mode='w')
    mainver(coarse=True, ratios=True)
    
    assert os.path.isfile(out_path)
