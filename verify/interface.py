#!/usr/bin/env python

"""
 -- verify package  -------------------------------------------------------
 
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
import argparse

## Get the main functions, reporting structure and triplet iterator
from .functions import (order_of_convergence,
                        richardson_extrapolate,
                        error_estimates,
                        gci,
                        asymptotic_ratio)
from .tables import Record, Table


class Verify(object):
    """ Calculate convergence for a set of grids (each grid being of the
    form [grid spacing, value]) examining the order of convergence, richardson
    extrapolated value to zero, GCI, and test whether the grids are in the
    asmptotic range. It will also calculate errors with an analytical value.
    Each of these tests can be carried out independantly and written to a file.
    The outputs are stored in dictionaries for easy access by parameter.
    """
    
    def __init__(self, grid_list, met_name=None, f_anal=None, zero_tol=1E-4):
    
        self.grid_list = grid_list
        self.met_name = met_name
        self.f_anal = None
        self.grid_trips = None
        self.grid_shared = None
        self.grid_fine = None
        self.grid_coarse = None
        self.grid_ratios = None
        self.file_name = None
        self.write_mode = None
        self._file_handle = None
        self.zero_tol = zero_tol

        # Set a log
#        self._log = logging.getLogger("fifthwave.verify.Verify")
        
        # Sort the given grid list at this stage
        self._sort_list(grid_list)

        # Collect the shared information for the given grid list.
        self._get_shared()
        
        # Get the analytical value if it's given
        if f_anal is not None: self.f_anal = float(f_anal)

    def add_file(self, file_name, write_mode='append'):
        
        self.file_name = file_name
        self.write_mode = write_mode

    def get_fine_values(self):
        
        """ Get the fine values (for grids 1 and 2 of the triplet) of the 
        extrapolated value, relative and extrapolated relative error and GCI 
        fine and coarse.
        """

        # Initialise the fine grid results list
        self.grid_fine = []
        
        for trip in self.grid_trips:
            
            tripdex = self.grid_trips.index(trip)

            ratio_21 = self.grid_shared[tripdex]['ratio_21']
            p = self.grid_shared[tripdex]['p']
            
            # if p is None then nothing can be done
            if p is None:
                self.grid_fine.append(None)
                continue
            
            # Get the values for the fine grids
            f_exact, e21a, e21ext, gci_f, gci_c = self._get_values(trip[0],
                                                                   trip[1],
                                                                   ratio_21,
                                                                   p)
            
            # Make a dictionary
            fine_dict = {'f_exact' : f_exact, 'e_a' : e21a, 'e_ext' : e21ext,
                         'gci_f' : gci_f, 'gci_c' : gci_c}
                         
            # If there is an anlytical value than do more work
            if self.f_anal is not None:
                
                f_delta = self.f_anal - f_exact
                e21dummy, e21_anal = error_estimates(trip[0][2], trip[1][2],
                                                     self.f_anal)
                                            
                # Add these to the dictionary
                anal_dict = {'f_anal': self.f_anal, 'f_delta' : f_delta, 
                             'e_anal' : e21_anal}
                             
                fine_dict.update(anal_dict)
            
            # Write the results to the list.
            self.grid_fine.append(fine_dict)
            
    def get_coarse_values(self):
        
        """ Get the coarse values (for grids 2 and 3 of the triplet) of the 
        extrapolated value, relative and extrapolated relative error and GCI 
        fine and coarse.
        """

        # Initialise the coarse grid results list
        self.grid_coarse = []
        
        for trip in self.grid_trips:
            
            tripdex = self.grid_trips.index(trip)

            ratio_32 = self.grid_shared[tripdex]['ratio_32']
            p = self.grid_shared[tripdex]['p']

            # if p is None then nothing can be done
            if p is None:
                self.grid_coarse.append(None)
                continue
            
            # Get the values for the coarse grids
            f_exact, e32a, e32ext, gci_f, gci_c = self._get_values(trip[1],
                                                                   trip[2],
                                                                   ratio_32,
                                                                   p)
                                                                   
            # Make a dictionary
            coarse_dict = {'f_exact' : f_exact, 'e_a' : e32a,
                           'e_ext' : e32ext, 'gci_f' : gci_f, 'gci_c' : gci_c}
                           
            # If there is an anlytical value than do more work
            if self.f_anal is not None:
                
                f_delta = self.f_anal - f_exact
                e21dummy, e23_anal = error_estimates(trip[1][2], trip[2][2],
                                                     self.f_anal)
                                            
                # Add these to the dictionary
                anal_dict = {'f_anal': self.f_anal, 'f_delta' : f_delta, 
                             'e_anal' : e23_anal}
                             
                coarse_dict.update(anal_dict)
            
            # Write the results to the list.
            self.grid_coarse.append(coarse_dict)
     
    def get_ratios(self):
        
        """ Get the asymptotic ratios for the triplets to check to see if the
        simulations are in the asymptotic range."""
        
        # If the fine are coarse values are not calculated then they need to be.
        if self.grid_fine is None: self.get_fine_values()
        if self.grid_coarse is None: self.get_coarse_values()
        
        # Initialise the ratios list
        self.grid_ratios = []
        
        for shared, fine, coarse in zip(self.grid_shared,
                                        self.grid_fine,
                                        self.grid_coarse):
            
            # Set a default ratio
            ratio = None
            
            # By this point there might be loads of issues. Check for Nones.
            none_check = (fine and coarse and shared['ratio_21']
                          and fine['gci_f'] and coarse['gci_f'])
            
            if none_check is not None:

                ratio_21 = shared['ratio_21']
                p = shared['p']

                gci_fine_21 = fine['gci_f']
                gci_fine_32 = coarse['gci_f']
                
                try:
                
                    ratio = asymptotic_ratio(gci_fine_21, gci_fine_32,
                                             ratio_21, p)
            
                except ArithmeticError, e:
                
                    # log the error
                    self._log.warning(e)
                    
            else:
                
                # log the error
                self._log.warning('get_ratios: failed none_check')
                self._log.warning('Some required result not available')
            
            # Add the result to the list as a dictionary
            self.grid_ratios.append({'assym_ratio' : ratio})
                
    def write(self):
        """ Write info to the file."""
        try:
            file_handle = open(self.file_name, self.write_mode)
        except IOError, e:
            self._log.warning(e)
        else:
            self._write_header(file_handle)
            if self.grid_fine: self._write_fine(file_handle)
            if self.grid_coarse: self._write_coarse(file_handle)
            if self.grid_ratios: self._write_ratios(file_handle)
            self._write_trailer(file_handle)
            
    def _sort_list(self, get_grid):
    
        # Sort the grid list first, so that the finest is at the start of the list
        grid_list = sorted(get_grid, key=lambda grid: grid[0])
        
        # Remove any zero entries
        list_copy = []
        
        grid_num = 1
        
        for grid, value in grid_list:
            
            if abs(value) > self.zero_tol:
                
                list_copy.append([grid_num,grid,value])
            
                grid_num += 1
            
        # Now turn the list into a list of triplets and store it.
        self.grid_trips = []
        
        for trip in triplets(list_copy): self.grid_trips.append(trip)
    
    def _get_shared(self):
        
        """ Record the refinement rations and the order of convergence for each
        of the triplets in grid_trips.
        """
    
        # Initialise the shared data list
        self.grid_shared = []
        
        for trip in self.grid_trips:
            
            # Calculate the refinement ratios
            ratio_21 = float(trip[1][1] / trip[0][1])
            ratio_32 = float(trip[2][1] / trip[1][1])
            
            # Default p to None
            p = None

            # Get order of convergence if possible
            try:
                
                p = order_of_convergence(trip[0][2], trip[1][2], trip[2][2],
                                     ratio_21, ratio_32)

            except ArithmeticError, e:
                
                # log the error
                self._log.warning(e)

            # Make a dictionary
            shared_dict = {'ratio_21' : ratio_21, 'ratio_32' : ratio_32,
                           'p' : p}
                
            # Add the results to the list
            self.grid_shared.append(shared_dict)
            
    def _get_values(self, grid_one, grid_two, ratio, p):
        
        """ Get the values (for the given grids) of the 
        extrapolated value, relative and extrapolated relative error and GCI 
        fine and coarse. The refinment ratio and order of convergence, p, is
        required.
        """
            
        # Default the values to None
        f_exact = e21a = e21ext = gci_f = gci_c = None
        
        try:
            
            # Perform Richardson extrapolation to estimate a zero grid value.
            f_exact = richardson_extrapolate(grid_one[2], grid_two[2],
                                                ratio, p)
                                        
            # Get the approximate and extrapolated relative errors
            e21a, e21ext = error_estimates(grid_one[2], grid_two[2],
                                            f_exact)

            # Get the gcis
            gci_f, gci_c = gci(ratio, e21a, p)

        except ArithmeticError, e:
    
            # log the error
            self._log.warning(e)
            
        return f_exact, e21a, e21ext, gci_f, gci_c
            
    def _write_header(self, rep_file):
        """ Write a header to the given file handel listing the grid values. 
        rep_file is an open file handle.
        """
    
        rep_file.write('\n')
        rep_file.write('--- VERIFY: Performs verification calculations --- \n')
        
        # Check if the metric is named
        if self.met_name is not None:
            rep_file.write('--- Examining metric: %24s --- \n' % self.met_name)


        rep_file.write('\n')
        rep_file.write('Number of grids to be examined = %d \n' % 
                                        (len(self.grid_trips) + 2))

        rep_file.write('\n')
        rep_file.write('     Grid Size     Quantity \n')
        rep_file.write('\n')

        # Unpack the triplets. Take all 3 from the first trip and then the
        # last from all the others.
        trip_one = self.grid_trips[0]
        grid_list = []
        for grid in trip_one:
            grid_list.append((grid[1], grid[2]))
            
        trips_copy = self.grid_trips[1:]
        
        for trip in trips_copy:
            grid = trip[2]
            grid_list.append((grid[1], grid[2]))
        
        # Write out the grids
        for grid in grid_list:
            rep_file.write('%13.6f %13.6f \n' % (grid[0], grid[1]))
            
        rep_file.write('\n')
        
    def _write_fine(self, rep_file):
        """ Ok to attempt to use report.py to do this and make a Table to write
        here. """
        
        # OK, get the strings for the table using the fine errors
        tab_strings = self._write_errors_tab(self.grid_fine)
                           
        # Write to the file
        rep_file.write('\n')
        rep_file.write('Discretisation errors for fine grids:\n')
        rep_file.write('\n')
        
        for line in tab_strings: rep_file.write(line)
        
    def _write_coarse(self, rep_file):
        """ Ok to attempt to use report.py to do this and make a Table to write
        here. """
        
        # OK, get the strings for the table using the fine errors
        tab_strings = self._write_errors_tab(self.grid_coarse)
                           
        # Write to the file
        rep_file.write('\n')
        rep_file.write('Discretisation errors for coarse grids:\n')
        rep_file.write('\n')
        
        for line in tab_strings: rep_file.write(line)

    def _write_errors_tab(self, errors_list):
        """ Ok to attempt to use report.py to do this and make a Table to write
        here. """
        
        # Right so we need to build a bunch of records right. Those records will
        # need headings so I can do that now I guess. Might get a coke first.
        record_headings = ['r21', 'r32', 'p', 'f_exact', 'e_approx', 'e_extrap',
                           'gci_fine', 'gci_coarse']
                           
        head_keys = ['ratio_21', 'ratio_32', 'p', 'f_exact', 'e_a', 'e_ext',
                     'gci_f', 'gci_c']
                           
        # OK, better make a table
        fine_table = Table('Grids')
                           
        # Right now loop through the triplets making a record for each and
        # adding it to the table.
        for trip in self.grid_trips:
            
            # Get the index
            tripdex = self.grid_trips.index(trip)
            
            # Get the grid numbers that are being used.
            grids_string = '%d %d %d' % (trip[0][0], trip[1][0], trip[2][0])
            
            # Set up a list to store the values.
            vals_list = []
            
            # Add the shared and fine dictionaries
            total_dict = dict(self.grid_shared[tripdex])
            if errors_list[tripdex] is not None:
                total_dict.update(errors_list[tripdex])
            
            # Match the values to the headings list
            for key in head_keys:
                if key in total_dict:
                    vals_list.append(total_dict[key])
                else:
                    vals_list.append(None)
            
            # Build a record
            new_record = Record(record_headings, vals_list, grids_string)
            
            # Add the record to the table
            fine_table.add_record(new_record)
            
        # OK, now get the table strings.
        tab_strings = fine_table.write(12, 6)
        
        return tab_strings
    
    def _write_ratios(self, rep_file):
        """ Ok to attempt to use report.py to do this and make a Table to write
        here. """
        
        # Single record heading
        record_heading = ['Asymptotic ratio']
                           
        # OK, better make a table
        ratio_table = Table('Grids')
                           
        # Right now loop through the triplets making a record for each and
        # adding it to the table.
        for trip in self.grid_trips:
            
            # Get the index
            tripdex = self.grid_trips.index(trip)
            
            # Get the grid numbers that are being used.
            grids_string = '%d %d %d' % (trip[0][0], trip[1][0], trip[2][0])
            
            # Set up a list to store the values.
            vals_list = [self.grid_ratios[tripdex]['assym_ratio']]
            
            # Build a record
            new_record = Record(record_heading, vals_list, grids_string)
            
            # Add the record to the table
            ratio_table.add_record(new_record)
            
        # OK, now get the table strings.
        tab_strings = ratio_table.write(16, 6)
        
        # Write to the file
        rep_file.write('\n')
        rep_file.write('Asympototic ratio test:\n')
        rep_file.write('\n')
        
        for line in tab_strings: rep_file.write(line)

    def _write_trailer(self, rep_file):
        
        # Write Trailer.
        
        rep_file.write('\n')
        rep_file.write('--- End of VERIFY --- \n')
        rep_file.write('\n')
                
    def __call__(self, coarse=False, ratios=False):
        
        """Carry out the analysis including an analysis on the coarse grids if
        desired."""
        
        self.get_fine_values()
        if coarse: self.get_coarse_values()
        if ratios: self.get_ratios()
        
        # Write to file if possible
        if self.file_name: self.write()
        
    
def simple_read(file_name):
    """ Read in grids from a simple file. """
    
    # Open the file
    grid_file = open(file_name, 'r')
    
    # Get each grid
    grid_list = []
    
    for line in grid_file.readlines():
        
        # split the line
        values = line.split()
        
        values = [float(i) for i in values]
        
        # Add the grid to the list
        grid_list.append(values)
        
    # Close the file
    grid_file.close()
    
    return grid_list

        
def triplets(lst):
    i = iter(lst)
    first = i.next()
    second = i.next()
    for item in i:
        yield first, second, item
        first = second
        second = item

    
def main():
    
    # Prepare command line parser              
    desStr = "Perform grid verification study on input file."

    parser = argparse.ArgumentParser(description=desStr)
            
    parser.add_argument("-o", "--out",
                        type=str,
                        help=("output file path"),
                        default='verify_report.txt')
                        
    parser.add_argument("-m", "--metric",
                        type=str,
                        help=("Name of metric to verify"))
                        
    parser.add_argument("file",
                        type=str,
                        help=("Input file path"))

  
    args = parser.parse_args()
    
    in_path     = args.file
    out_path    = args.out 
    metric      = args.metric
            
    # Read in the file
    main_list = simple_read(in_path)
    
    # Run verify
    mainver = Verify(main_list, metric)
        
    # Write the report
    mainver.add_file(out_path, write_mode='w')
    mainver(coarse=True, ratios=True)


if __name__ == "__main__":
    
    main()

