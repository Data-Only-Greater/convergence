# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 13:33:39 2020

@author: Work
"""

import pytest


from convergence.functions import (order_of_convergence,
                                   required_resolution)


def test_order_of_convergence_runtimeerror():
    
    with pytest.raises(RuntimeError):
        order_of_convergence (0.9705, 0.96854, 0.96178, 2.0, 2.0,
                              tol=-1, max_iter=10)


def test_required_resolution():
    
    gci = 0.1
    gci12 = 0.4
    p = 2
    h1 = 4
    
    test = required_resolution(gci, gci12, p, h1)
    expected = 2
    
    assert abs(test - expected) < 1e-10
