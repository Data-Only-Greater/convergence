# -*- coding: utf-8 -*-

# Copyright 2013 SuperGen UK Centre for Marine Energy Research
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

import argparse
import warnings

from .functions import (order_of_convergence,
                        richardson_extrapolate,
                        error_estimates,
                        gci,
                        asymptotic_ratio,
                        required_resolution)
from .tables import Record, Table


class Convergence(object):
    """ Calculate convergence for a set of grids (each grid being of the
    form [grid spacing, value]) examining the order of convergence, richardson
    extrapolated value to zero, GCI, and test whether the grids are in the
    asmptotic range. It will also calculate errors with an analytical value.
    Each of these tests can be carried out independantly and written to a file.
    The outputs are stored in dictionaries for easy access by parameter.
    """
    
    def __init__(self, met_name=None, f_anal=None, zero_tol=1E-4):
    
        self.met_name = met_name
        self._f_anal = f_anal
        self._zero_tol = zero_tol
        self._grids = []
        self._grid_shared = None
        self._grid_fine = None
        self._grid_coarse = None
        self._grid_ratios = None
        self._grid_triplets = None
        self._grid_nspaces = None
        
        return
    
    def add_grids(self, grids):
        
        self._set_grids(grids)
        self._set_grid_triplets()
        self._get_shared()
        self._get_fine_values()
        self._get_coarse_values()
        self._get_ratios()
        self._make_attributes()
        
        return
    
    def _set_grids(self, grids):
        
        pre_sort = list(self._grids)
        pre_sort.extend(grids)
        sorted_grids = sorted(pre_sort, key=lambda grid: grid[0])
        self._grids = tuple(sorted_grids)
        
        if len(self._grids) < 3:
            warnings.warn("Insufficient grids for analysis")
        
        return
    
    def _set_grid_triplets(self):
        
        numbered_grids = []
        
        grid_num = 1
        
        for grid, value in self._grids:
            
            if abs(value) > self._zero_tol:
                numbered_grids.append([grid_num, grid, value])
                grid_num += 1
        
        grid_trips = []
        
        for trip in _triplets(numbered_grids):
            grid_trips.append(trip)
        
        self._grid_triplets = grid_trips
        
        return
    
    def _get_shared(self):
        
        """ Record the refinement rations and the order of convergence for each
        of the triplets in grid_trips.
        """
        
        # Initialise the shared data list
        self._grid_shared = []
        
        for trip in self._grid_triplets:
            
            # Calculate the refinement ratios
            ratio_21 = float(trip[1][1] / trip[0][1])
            ratio_32 = float(trip[2][1] / trip[1][1])
            
            # Default p to None
            p = None
            
            # Get order of convergence if possible
            try:
                p = order_of_convergence(trip[0][2],
                                         trip[1][2],
                                         trip[2][2],
                                         ratio_21,
                                         ratio_32)
            except (ArithmeticError, RuntimeError) as e:
                warnings.warn(e)
            
            # Make a dictionary
            shared_dict = {'ratio_21' : ratio_21, 'ratio_32' : ratio_32,
                           'p' : p}
            
            # Add the results to the list
            self._grid_shared.append(shared_dict)
    
    def _get_fine_values(self):
        
        """ Get the fine values (for grids 1 and 2 of the triplet) of the 
        extrapolated value, relative and extrapolated relative error and GCI 
        fine and coarse.
        """
        
        # Initialise the fine grid results list
        self._grid_fine = []
        
        for trip in self._grid_triplets:
            
            tripdex = self._grid_triplets.index(trip)
            
            ratio_21 = self._grid_shared[tripdex]['ratio_21']
            p = self._grid_shared[tripdex]['p']
            
            # if p is None then nothing can be done
            if p is None:
                self._grid_fine.append(None)
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
            if self._f_anal is not None:
                
                f_delta = e21_anal = None
                
                if f_exact is not None:
                    f_delta = float(self._f_anal) - f_exact
                
                try:
                    _, e21_anal = error_estimates(trip[0][2],
                                                  trip[1][2],
                                                  float(self._f_anal))
                except ArithmeticError as e:
                    warnings.warn(e)
                
                # Add these to the dictionary
                anal_dict = {'f_anal': float(self._f_anal), 
                             'f_delta' : f_delta, 
                             'e_anal' : e21_anal}
                
                fine_dict.update(anal_dict)
            
            # Write the results to the list.
            self._grid_fine.append(fine_dict)
    
    def _get_coarse_values(self):
        
        """ Get the coarse values (for grids 2 and 3 of the triplet) of the 
        extrapolated value, relative and extrapolated relative error and GCI 
        fine and coarse.
        """
        
        # Initialise the coarse grid results list
        self._grid_coarse = []
        
        for trip in self._grid_triplets:
            
            tripdex = self._grid_triplets.index(trip)
            
            ratio_32 = self._grid_shared[tripdex]['ratio_32']
            p = self._grid_shared[tripdex]['p']
            
            # if p is None then nothing can be done
            if p is None:
                self._grid_coarse.append(None)
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
            if self._f_anal is not None:
                
                f_delta = e23_anal = None
                
                if f_exact is not None:
                    f_delta = float(self._f_anal) - f_exact
                
                try:
                    _, e23_anal = error_estimates(trip[1][2],
                                                  trip[2][2],
                                                  float(self._f_anal))
                except ArithmeticError as e:
                    warnings.warn(e)
                
                # Add these to the dictionary
                anal_dict = {'f_anal': float(self._f_anal), 
                             'f_delta' : f_delta, 
                             'e_anal' : e23_anal}
                
                coarse_dict.update(anal_dict)
            
            # Write the results to the list.
            self._grid_coarse.append(coarse_dict)
    
    def _get_values(self, grid_one, grid_two, ratio, p):
        
        """ Get the values (for the given grids) of the 
        extrapolated value, relative and extrapolated relative error and GCI 
        fine and coarse. The refinment ratio and order of convergence, p, is
        required.
        """
        
        # Default the values to None
        f_exact = e21a = e21ext = gci_f = gci_c = None
        
        # Perform Richardson extrapolation to estimate a zero grid value.
        try:
            f_exact = richardson_extrapolate(grid_one[2],
                                             grid_two[2],
                                             ratio,
                                             p)
        except ArithmeticError as e:
            warnings.warn(e)
            return f_exact, e21a, e21ext, gci_f, gci_c
        
        # Get the approximate and extrapolated relative errors
        try:
            e21a, e21ext = error_estimates(grid_one[2],
                                           grid_two[2],
                                           f_exact)
        except ArithmeticError as e:
            warnings.warn(e)
            return f_exact, e21a, e21ext, gci_f, gci_c
        
        # Get the gcis
        try:
            gci_f, gci_c = gci(ratio, e21a, p)
        except ArithmeticError as e:
            warnings.warn(e)
        
        return f_exact, e21a, e21ext, gci_f, gci_c
    
    def _get_ratios(self):
        
        """ Get the asymptotic ratios for the triplets to check to see if the
        simulations are in the asymptotic range."""
        
        # If the fine are coarse values are not calculated then they need to be
        if self._grid_fine is None: self.get_fine_values()
        if self._grid_coarse is None: self.get_coarse_values()
        
        # Initialise the ratios list
        self._grid_ratios = []
        
        for shared, fine, coarse in zip(self._grid_shared,
                                        self._grid_fine,
                                        self._grid_coarse):
            
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
                    ratio = asymptotic_ratio(gci_fine_21,
                                             gci_fine_32,
                                             ratio_21, p)
                except ArithmeticError as e:
                    warnings.warn(e)
            
            else:
                
                warnings.warn('get_ratios: failed none_check')
                warnings.warn('Some required result not available')
            
            # Add the result to the list as a dictionary
            self._grid_ratios.append({'assym_ratio' : ratio})
    
    def _make_attributes(self):
        
        grid_nspaces = {}
        
        for trip in self._grid_triplets:
            
            tripdex = self._grid_triplets.index(trip)
            
            grids_string = '%d %d %d' % (trip[0][0], trip[1][0], trip[2][0])
            grids_sizes = [trip[0][1], trip[1][1], trip[2][1]]
            grids_values = [trip[0][2], trip[1][2], trip[2][2]]
            
            # Add the shared and fine dictionaries
            total_dict = dict(self._grid_shared[tripdex])
            if self._grid_fine[tripdex] is not None:
                total_dict.update(self._grid_fine[tripdex])
            
            nsdict = {"r21": total_dict['ratio_21'],
                      "r32": total_dict['ratio_32']}
            
            if total_dict['p'] is not None:
            
                nsdict["e_approx"] = total_dict['e_a']
                nsdict["e_extrap"] = total_dict['e_ext']
                nsdict["f_exact"] = total_dict['f_exact']
                nsdict["gci_coarse"] = total_dict['gci_c']
                nsdict["gci_fine"] = total_dict['gci_f']
                nsdict["p"] = total_dict['p']
                nsdict["r21"] = total_dict['ratio_21']
                nsdict["r32"] = total_dict['ratio_32']
                
                if self._f_anal is not None:
                    
                    nsdict['e_analytic'] = total_dict['e_anal']
                    nsdict['f_analytic'] = total_dict['f_anal']
                    nsdict['f_delta'] = total_dict['f_delta']
            
            fspace = argparse.Namespace(**nsdict)
            
            # Add the shared and coarse dictionaries
            total_dict = dict(self._grid_shared[tripdex])
            if self._grid_fine[tripdex] is not None:
                total_dict.update(self._grid_coarse[tripdex])
            
            nsdict = {"r21": total_dict['ratio_21'],
                      "r32": total_dict['ratio_32']}
            
            if total_dict['p'] is not None:
            
                nsdict["e_approx"] = total_dict['e_a']
                nsdict["e_extrap"] = total_dict['e_ext']
                nsdict["f_exact"] = total_dict['f_exact']
                nsdict["gci_coarse"] = total_dict['gci_c']
                nsdict["gci_fine"] = total_dict['gci_f']
                nsdict["p"] = total_dict['p']
                nsdict["r21"] = total_dict['ratio_21']
                nsdict["r32"] = total_dict['ratio_32']
            
                if self._f_anal is not None:
                    
                    nsdict['e_analytic'] = total_dict['e_anal']
                    nsdict['f_analytic'] = total_dict['f_anal']
                    nsdict['f_delta'] = total_dict['f_delta']
            
            cspace = argparse.Namespace(**nsdict)
            
            assym_ratio = self._grid_ratios[tripdex]['assym_ratio']
            
            nspace = argparse.Namespace(**{"grids": grids_string,
                                           "sizes": grids_sizes,
                                           "values": grids_values,
                                           "fine": fspace,
                                           "coarse": cspace,
                                           "asymptotic_ratio": assym_ratio})
            
            grid_nspaces[tripdex] = nspace
        
        self._grid_nspaces = grid_nspaces
        
        return
    
    def _write_header(self, msgs):
        
        msgs.append('')
        
        # Check if the metric is named
        if self.met_name is not None:
            msgs.append('--- Examining metric: %24s --- ' % self.met_name)
            msgs.append('')
        
        msgs.append('Number of grids to be examined = %d ' % len(self._grids))
        msgs.append('')
        
        if len(self._grids) == 0: return msgs
        
        msgs.append('     Grid Size     Quantity ')
        msgs.append('')
        
        # Write out the grids
        for grid in self._grids:
            msgs.append('%13.6f %13.6f ' % (grid[0], grid[1]))
            
        msgs.append('')
        
        return msgs
    
    def _write_fine(self, msgs):
        
        # OK, get the strings for the table using the fine errors
        tab_strings = self._write_errors_tab(self._grid_fine)
        
        # Write to the file
        msgs.append('')
        msgs.append('Discretisation errors for fine grids: ')
        msgs.append('')
        
        for line in tab_strings: msgs.append(line)
        
        return msgs
    
    def _write_coarse(self, msgs):
        
        # OK, get the strings for the table using the fine errors
        tab_strings = self._write_errors_tab(self._grid_coarse)
        
        # Write to the file
        msgs.append('')
        msgs.append('Discretisation errors for coarse grids: ')
        msgs.append('')
        
        for line in tab_strings: msgs.append(line)
        
        return msgs
    
    def _write_errors_tab(self, errors_list):
        
        record_headings = ['r21', 'r32', 'p', 'f_exact']
        head_keys = ['ratio_21', 'ratio_32', 'p', 'f_exact']
        
        if self._f_anal is not None:
            record_headings += ["f_analytic", "f_delta"]
            head_keys += ["f_anal", "f_delta"]
        
        record_headings += ['e_approx', 'e_extrap']
        head_keys += ['e_a', 'e_ext']
        
        if self._f_anal is not None:
            record_headings += ["e_analytic"]
            head_keys += ["e_anal"]
        
        record_headings += ['gci_fine', 'gci_coarse']
        head_keys += ['gci_f', 'gci_c']
        
        # OK, better make a table
        fine_table = Table('Grids')
        
        # Right now loop through the triplets making a record for each and
        # adding it to the table.
        for trip in self._grid_triplets:
            
            # Get the index
            tripdex = self._grid_triplets.index(trip)
            
            # Get the grid numbers that are being used.
            grids_string = '%d %d %d' % (trip[0][0], trip[1][0], trip[2][0])
            
            # Set up a list to store the values.
            vals_list = []
            
            # Add the shared and fine dictionaries
            total_dict = dict(self._grid_shared[tripdex])
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
    
    def _write_ratios(self, msgs):
        
        # Single record heading
        record_heading = ['Asymptotic ratio']
                           
        # OK, better make a table
        ratio_table = Table('Grids')
                           
        # Right now loop through the triplets making a record for each and
        # adding it to the table.
        for trip in self._grid_triplets:
            
            # Get the index
            tripdex = self._grid_triplets.index(trip)
            
            # Get the grid numbers that are being used.
            grids_string = '%d %d %d' % (trip[0][0], trip[1][0], trip[2][0])
            
            # Set up a list to store the values.
            vals_list = [self._grid_ratios[tripdex]['assym_ratio']]
            
            # Build a record
            new_record = Record(record_heading, vals_list, grids_string)
            
            # Add the record to the table
            ratio_table.add_record(new_record)
            
        # OK, now get the table strings.
        tab_strings = ratio_table.write(16, 6)
        
        # Write to the file
        msgs.append('')
        msgs.append('Asymptotic ratio test: ')
        msgs.append('')
        
        for line in tab_strings: msgs.append(line)
        
        return msgs
    
    def _write_trailer(self, msgs):
        
        if len(self._grid_triplets) > 0: return msgs
        
        msgs.append(' *** Insufficient grids for analysis *** ')
        msgs.append('')
        
        return msgs
    
    def get_resolution(self, gci, estimate="fine"):
        
        if not self._grid_coarse:
            raise RuntimeError("Insufficient grids")
        
        if estimate == "fine":
            gci12 = self[0].fine.gci_fine
        elif estimate == "coarse":
            gci12 = self[0].fine.gci_coarse
        else:
            raise ValueError("Unrecognised value passed to estimate. Should "
                             "be one of 'fine' or 'coarse'")
        
        p = self[0].coarse.p
        h1 = self._grids[0][0]
        
        return required_resolution(gci, gci12, p, h1)
        
    def __len__(self):
        
        if self._grid_nspaces is None:
            result = 0
        else:
            result = len(self._grid_nspaces)
        
        return result
    
    def __getitem__(self, key):
        
        if self._grid_nspaces is None:
            raise IndexError(key)
        
        if not isinstance(key, int):
            raise TypeError(type(key))
        
        try:
            nspace = self._grid_nspaces[key]
        except KeyError:
            raise IndexError(key)
        
        return nspace
    
    def __str__(self):
        
        msgs = []
        
        msgs = self._write_header(msgs)
        if self._grid_fine: msgs = self._write_fine(msgs)
        if self._grid_coarse: msgs = self._write_coarse(msgs)
        if self._grid_ratios: msgs = self._write_ratios(msgs)
        msgs = self._write_trailer(msgs)
        
        return "\n".join(msgs)


def _triplets(lst):
    
    if len(lst) < 2: return
    
    i = iter(lst)
    first = next(i)
    second = next(i)
    
    for item in i:
        yield first, second, item
        first = second
        second = item


def main(in_path, out_path, analytical=None):
    
    # Read in the file
    main_list = simple_read(in_path)
    
    # Run convergence study
    convergence = Convergence(f_anal=analytical)
    convergence.add_grids(main_list)
    
    # Write the report
    with open(out_path, 'w') as f:
        f.write(str(convergence))
    
    return


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


def cl_interface():
    
    # Prepare command line parser
    desStr = "Perform grid convergence study on input file."
    
    parser = argparse.ArgumentParser(description=desStr)
    
    parser.add_argument("-o", "--out",
                        type=str,
                        help=("output file path"),
                        default='verify_report.txt')
                        
    parser.add_argument("-a", "--analytical",
                        type=str,
                        help=("Expected analytical value"))
                        
    parser.add_argument("file",
                        type=str,
                        help=("Input file path"))
    
    args = parser.parse_args()
    
    in_path = args.file
    out_path = args.out 
    analytical = args.analytical
    
    main(in_path, out_path, analytical)
    
    return
