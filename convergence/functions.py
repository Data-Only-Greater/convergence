#!/usr/bin/env python

"""
 -- convergence package  -------------------------------------------------------
 
   Performs several verification calculations given a file of grid spacings 
   and some observed quantity corresponding to each grid spacing.
 
   Computes:
   - order of convergence
   - Richardson extrapolation to zero grid spacing
   - grid convergence indices (GCI)
 
 --------------------------------------------------------------------------
 
Adapted from:
    
    NPARC Alliance CFD Verification and Validation Web Site
    Examining Spatial (Grid) Convergence
    verify.f90

    URL: http://www.grc.nasa.gov/WWW/wind/valid/tutorial/spatconv.html
    
    Nov '11: Updated to reflect Celik et al 2008.
"""

__author__ = "Mathew Topper"
__copyright__ = "Copyright 2013, SuperGen Marine"
__licence__ = "GPL"
__version__ = "trunk"
__maintainer__ = "Mathew Topper"
__email__ = "mathew.topper@ed.ac.uk"
__status__ = "Development"

# Import built-in modules
from math import log

        
def order_of_convergence (value_1, value_2, value_3, ratio_21, ratio_32, 
                          omega=0.5, tol=1.E-4): #, start_p=1.):
                              
    """ Calculate the order of convergence values generated with three
    grids of reducing resolution (ie grid_1 is finest). The values of the grids
    are needed along with the ratios between them.
    
    An iterative method with under-relaxation is used to calculate the order
    of convergence as the refinement ratio is not necessarily constant.
    
    This has been modified to the method of Celik (2008).
    """
    
    # Set a maximum residual and number of iterations
    max_res = 1.E6

    # calculate the epsilons.
    epsilon32 = float(value_3 - value_2)
    epsilon21 = float(value_2 - value_1)

    # Calculate the fraction
    epfrac = epsilon32 / epsilon21
    
    # Get the signed unit, s
    s = epfrac / abs(epfrac)
    
    # Initial guess at order of convergence, p
    p1 = (1. / log(ratio_21)) * abs(log(abs(epfrac))) # start_p
    
    # Initialise the residual and number of iterations
    residual = 1.
    iterations = 0
    
    while abs(residual) > tol:
    
        # Break if it's all gone bad
        if float(iterations) > max_res or residual > max_res:
            ValueError('Residual out of range or too many iterations')
        
        # Get the last value
        p0 = p1
        
        # Calculate q
        q = log((ratio_21 ** p0 - s) / (ratio_32 ** p0 - s))
        
        # Calculate the p iteration
        pnew = (1. / log(ratio_21)) * abs(log(abs(epfrac)) + q)
        
        # Calculate the relaxation step.
        p1 = (1. - omega) * p0 + omega * pnew
        
        residual = p1 - p0
        
        iterations += 1
        
    return p1


def richardson_extrapolate(value_1, value_2, ratio_21, p):
    
    """ Estimate the zero grid spacing value using richardsons extrapolation and
    two grids of reducing resolution (ie grid_1 is finest). The refinement ratio
    is needed. The order of convergence, p, is also required.
    """
    
    f_exact = ( ratio_21**p * value_1 - value_2 ) / ( ratio_21**p - 1.0 )
    
    return f_exact


def error_estimates(value_1, value_2, f_exact):
    
    """ This routine returns the relative error and extrapolated 
    relative error. The values of the grids and needed along 
    with the extrapolated value.
    """

    # Get the approximate relative error
    e21a =  abs( (value_1 - value_2) / value_1 )
    
    # Get the extrapolated relative error
    e21ext = abs( ( f_exact - value_1 ) / f_exact )
    
    return e21a, e21ext


def gci(ratio_21, e21_approx, p):
    
    """ Calculate the fine and coarse grid convergence index for two grids of 
    reducing resolution (ie grid_1 is finest). The refinement ration between the 
    grids is required along with the approximate relative error (e21_approx) and 
    the order of convergence, p.
    """
    
    # Using a fixed safety factor as per Celik (2008)
    safety_factor = 1.25
    
    # Calculate the gci
    gci_fine = safety_factor * e21_approx / (ratio_21**p - 1.0)

    gci_coarse = ratio_21**p * gci_fine
    
    return gci_fine, gci_coarse


def asymptotic_ratio(gci_fine_21, gci_fine_32, ratio_21, p):
    
    """ Calculate the ratio in succesive Eps as defined at the bottom of page
    129 in Roache. If the ration is close to one then the asymptotic range has
    been reached.
    """
    
    ratio = ratio_21**p * ( gci_fine_21 / gci_fine_32)
    
    return ratio
