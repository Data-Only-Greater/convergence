# -*- coding: utf-8 -*-
"""
Created on Sun Oct 08 09:10:28 2017

@author: mtopper
"""

import os

from verify import Verify, simple_read

this_dir_path = os.path.dirname(__file__)
data_dir_path = os.path.join(this_dir_path, "..", "data")


def test_main(tmpdir):
    
    in_path = os.path.join(data_dir_path, "prD.do")
    out_path = str(tmpdir.join("test_main.txt"))
    
    assert not os.path.isfile(out_path)
    
    # Read in the file
    main_list = simple_read(in_path)
    
    # Run verify
    mainver = Verify(main_list)
        
    # Write the report
    mainver.add_file(out_path, write_mode='w')
    mainver(coarse=True, ratios=True)
    
    assert os.path.isfile(out_path)
