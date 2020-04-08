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

__copyright__ = "Copyright 2011, SuperGen Marine"

try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest


class Record(object):
    """ A Record is a single line in a report containing values for the columns
    at a particular grid resolution etc.
    """
    
    def __init__(self, column_list, column_values=None, data_point=None):
        
        """
            <> data_point is the fixed value for this set of column values.
            
            <> col_pairs is the name of the column given in column_list and its 
        value for this particular record.
            
            <> If the record is to be read then neither the data point or the
        values need be known, but the column list must be known in case
        additions are to be made.
        
        """
        
        self.data_point = data_point
        self.col_pairs = [(col_name, None) for col_name in column_list]
        
        # If column values is given then call add_values
        if column_values is not None: self.add_values(column_values)
        
#        self._log = logging.getLogger("fifthwave.fifthwave.Record")
        
        return
        
    def read(self, text_line):
        
        # Split the line and take everything up to the first separator
        # as the data point.
        row_entries = text_line.split()
        
        val_string = ''
        
        while row_entries[0] != '|':
            
            val_string += row_entries.pop(0)
            
            # Add a space if the next entry is not the separator
            if row_entries[0] != '|': val_string += ' '
        
        # Try to get the data point as a float if possible
        try:
            self.data_point = float(val_string)
        except ValueError:
            self.data_point = val_string
        
        # Peel off the first separator
        del(row_entries[0])
        
        # Make a list to store the values and iterate till there is just the
        # last separator remaining.
        val_list = []
        while len(row_entries) > 1:
            
            # Make a string and add everything to it that is not the separator
            val_string = ''
            
            while row_entries[0] != '|': val_string += row_entries.pop(0)
            
            # Add to the values list depending on what was read.
            if val_string == '':
                val_list.append(None)
            else:
                val_list.append(float(val_string))
            
            # Peel off the separator
            del(row_entries[0])
        
        self.add_values(val_list)
            
    def add_values(self, values):
        
        for value, col_pair in zip_longest(values, self.col_pairs):
            try:
                coldex = self.col_pairs.index(col_pair)
                self.col_pairs[coldex] = (col_pair[0], value)
            except TypeError as e:
#                self._log.error("Could be too many values for number of \
#                                 columns.")
                raise e
    
    def update_bylist(self, column_list, column_values):
        
        # OK, start by making lists of the existing columns and values
        col_list = []
        val_list = []
        for column, value in self.col_pairs:
            col_list.append(column)
            val_list.append(value)
        
        # Now update the lists
        for column, value in zip(column_list, column_values):
            try:
                coldex = col_list.index(column)
                val_list[coldex] = value
            except:
                col_list.append(column)
                val_list.append(value)
        
        # Load up the col_pairs
        self.col_pairs = [(column, value) for column, value in
                                                    zip(col_list, val_list)]
        
        return
    
    def update_byrecord(self, record):
        
        # OK, start by making lists of the existing columns and values
        col_list = []
        val_list = []
        for column, value in self.col_pairs:
            col_list.append(column)
            val_list.append(value)
        
        # Now update the lists
        for column, value in record.col_pairs:
            try:
                coldex = col_list.index(column)
                val_list[coldex] = value
            except:
                col_list.append(column)
                val_list.append(value)
                
        # Load up the col_pairs
        self.col_pairs = [(column, value) for column, value in
                                                    zip(col_list, val_list)]
        
        return


class Table(object):
    """ A Table is the bit that display records with values for column 
    headings at a particular data point. It can write new tables or read
    existing tables and update them. The columns can also be read separately.
    Unlike a report it doesn't handle files it just takes a list of strings 
    to read or will output a list of strings for writing.
    """

    def __init__(self, row_type=''):
        self.row_type = row_type
        self._records = []
#        self._log = logging.getLogger("fifthwave.fifthwave.Table")
    
    def reset_data(self):
        """ Clear the records in the Table."""
        self._records = []
    
    def reverse(self):
        """ Reverse the order of the records."""
        self._records.reverse()
    
    def order_rows(self, ordered_list):
        """ Reorder the list of records to the reverse of the given list.
        This will delete any data points not given in ordered_list. """
        
        new_records = [None] * len(ordered_list)
        
        for data_point in ordered_list:
            
            datdex = ordered_list.index(data_point)
            
            for old_rec in self._records:
                
                if old_rec.data_point == data_point:
                    
                    new_records[datdex] = old_rec
                    
                    break
        
        # Weed out any remaining Nones.
        self._records = [a for a in new_records if a != None]
    
    def column_read(self, get_strings):
        """ Read in an existing table and return the name of the columns
        in a list and the values in those columns in a list of lists. Assume the
        first string in the list is the right place to get the columns.
        """
            
        # Collect the column headers
        column_line = get_strings.pop(0)
        col_list = column_line.split()
        
        col_names = self._rep_line_reader(col_list)
        
        # Collect a list of the rows
        row_list = []
        
        # Split the entries into rows
        for line in get_strings:

            # Protect the reader from data beyond the table
            if len(line) < 2: break                

            words = line.split()
            row_entries = self._rep_line_reader(words)
            row_list.append(row_entries)
        
        # set up the column list
        col_list = [[] for entry in row_list[0]]
        
        # Now turn the row list into a column list
        for row in row_list:
            for index, entry in enumerate(row):
                col_list[index].append(entry)
        
        return col_names, col_list
    
    def read(self, get_strings):
        """ Read in an existing table given by a list of strings. This will 
        overwrite the row_type and update any existing records.
        """
        
        # Collect the column headers
        column_line = get_strings.pop(0)
        col_list = column_line.split()
        
        # Entries up to the first separator are the row_type so get it.
        # Make a string and add everything to it that is not the separator
        val_string = ''
        
        while col_list[0] != '|':
        
            val_string += col_list.pop(0)
            
            # Add a space if the next entry is not the separator
            if col_list[0] != '|': val_string += ' '
        
        # If the val_string is not empty set the row_type.
        if len(val_string) > 0: self.row_type = val_string
        
        # Peel off the separator
        del(col_list[0])
        
        # Make a list to store the values and iterate till there is just the
        # last separator remaining.
        read_columns = []
        while len(col_list) > 1:
            
            # Make a string and add everything to it that is not the separator
            val_string = ''
            
            while col_list[0] != '|':
            
                val_string += col_list.pop(0)
                
                # Add a space if the next entry is not the separator
                if col_list[0] != '|': val_string += ' '
            
            # Add to the values list depending on what was read.
            # Don't like this None case. Very ambiguous!
            if val_string == '':
                read_columns.append(None)
            else:
                read_columns.append(val_string)
            
            # Peel off the separator
            del(col_list[0])
        
        # Read each entry into list of records until any blank space
        for line in get_strings:
            if line == '\n': break
            new_record = Record(read_columns)
            new_record.read(line)
            self.add_record(new_record)
    
    def add_record(self, get_record):
        """ Add or update a record for the given data point using the supplied
        record.
        """
        
         # Add a new record to the records list or update an existing record
        current_dat_points = [record.data_point for record in self._records]
        
        # Check the given records data point against the existing data point.
        if get_record.data_point in current_dat_points:
            datdex = current_dat_points.index(get_record.data_point)
            self._records[datdex].update_byrecord(get_record)
        else:
            self._records.append(get_record)
    
    def write(self, col_width=20, dec_places=8, row_sort=True, tab_width=80):
        
        """ Write out the table to a list of strings. The column width can
        be manually set and setting the decimal places seems sensible too."""
        
        # Initialise the list of strings
        table_strings = []
        
        # Need to collect the column names from the records into a list
        all_columns = []
        for record in self._records:
            for col_pair in list(record.col_pairs):
                
                # Collect the column headings
                if col_pair[0] not in all_columns:
                    all_columns.append(col_pair[0])
                    
                # Knock off any entries with no value
                if col_pair[1] == None:
                    record.col_pairs.remove(col_pair)
        
        all_columns.sort()
        
        # Prepare the formatting strings
        string_format = '%' + str(col_width) + 's | '
        float_format = '%' + str(col_width) + '.' + str(dec_places) + 'f | '
        
        # I think some sort of while loop here should be used to keep writing
        # the colums in useful chunks until we run out.
        while all_columns:
            
            onetab, all_columns = self._set_width_write( all_columns, 
                                                         tab_width,
                                                         string_format,
                                                         float_format)
            
            table_strings.extend(onetab)
            table_strings.append('\n')
         
        # Return the list of string
        return table_strings
        
    def _rep_line_reader(self, word_list):
        """ Return the values in line as a list, removing the separation
        character."""
        
        entries_list = []
        
        # Iterate till there is just the last separator remaining.
        while len(word_list) > 1:
            
            # Make a string and add everything to it that is not the separator
            val_string = ''
            
            while word_list[0] != '|':
                
                val_string += word_list.pop(0)
                
                # Add a space if the next entry is not the separator
                if word_list[0] != '|':
                    val_string += ' '
            
            # Add to the values list depending on what was read.
            # Don't like this None case. Very ambiguous!
            if val_string == '':
                entries_list.append(None)
            else:
                entries_list.append(val_string)
            
            # Peel off the separator
            del(word_list[0])
        
        return entries_list
    
    def _set_width_write( self, sorted_column_list, tab_width, string_format,
                          float_format, row_sort=True ):
        
        # Copy the column list and reverse it
        reverse_list = sorted_column_list[:]
        reverse_list.reverse()
        
        write_columns = []
        table_strings = []
        
        # Write the column headings checking the length and popping OK columns 
        # into a new list
        headings_string = string_format % self.row_type
        for column in sorted_column_list:
            
            col_string = string_format % column
            
            if len(headings_string + col_string) <= tab_width:
                headings_string += col_string
                write_columns.append(reverse_list.pop())
            else:
                break
        
        dashrule = ' ' + '-' * (len(headings_string) - 2)
        eqrule = ' ' + '=' * (len(headings_string) - 2)
        
        headings_string += '\n'
        dashrule += '\n'
        eqrule += '\n'
    
        # Record the headings string
        table_strings.append(headings_string)
        table_strings.append(eqrule)
        
        # Write out the records. First sort by the data_point value.
        if row_sort: 
            sorted_records = sorted(self._records, 
                                    key=lambda record: record.data_point)
        else:
            sorted_records = self._records
        
        for record in sorted_records:
            
            # Want to allow strings and numbers for the data point so convert
            # to a string 
            record_string = string_format % record.data_point
            # Search for each column in write_columns within the record
            col_list =  [col for col, val in record.col_pairs]
            for column in write_columns:
                if column in col_list:
                    coldex = col_list.index(column)
                    record_string += float_format % record.col_pairs[coldex][1]
                else:
                    record_string += string_format % ''
            record_string += '\n'
            
            # Record the record string
            table_strings.append(record_string)
        
        table_strings.append(dashrule)
        reverse_list.reverse()
        
        # Return the strings and the unused columns
        return table_strings, reverse_list

