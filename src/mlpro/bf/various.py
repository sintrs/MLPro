## -------------------------------------------------------------------------------------------------
## -- Project : FH-SWF Automation Technology - Common Code Base (CCB)
## -- Package : mlpro
## -- Module  : various
## -------------------------------------------------------------------------------------------------
## -- History :
## -- yyyy-mm-dd  Ver.      Auth.    Description
## -- 2021-04-16  0.0.0     DA       Creation
## -- 2021-05-29  1.0.0     DA       Release of first version
## -- 2021-06-16  1.1.0     SY       Adding the first version of data storing,
## --                                data plotting, and data saving classes
## -- 2021-06-17  1.2.0     DA       New abstract classes Loadable, Saveable
## -- 2021-06-21  1.3.0     SY       Add extensions in classes Loadable,
## --                                Saveable, DataPlotting & DataStoring.
## -- 2021-07-01  1.4.0     SY       Extend save/load functionalities
## -- 2021-08-20  1.5.0     DA       Added property class Plottable
## -- 2021-08-28  1.5.1     DA       Added constant C_VAR0 to class DataStoring
## -- 2021-09-11  1.5.0     MRD      Change Header information to match our new library name
## -- 2021-10-06  1.5.2     DA       Moved class DataStoring to new module mlpro.bf.data.py and
## --                                classes DataPlotting, Plottable to new module mlpro.bf.plot.py
## -- 2021-10-07  1.6.0     DA       Class Log: 
## --                                - colored text depending on log type 
## --                                - new method set_log_level()
## -- 2021-10-25  1.7.0     SY       Add new class ScientificObjects
## -------------------------------------------------------------------------------------------------

"""
Ver. 1.7.0 (2021-10-25)

This module provides various classes with elementry functionalities for reuse in higher level classes. 
For example: logging, load/save, timer, ...
"""


from datetime import datetime, timedelta
from time import sleep
import pickle as pkl
import os
from mlpro.bf.exceptions import *




## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class Loadable:
    """
    This abstract class adds the ability to be loadable to inherited classes. 
    """

## -------------------------------------------------------------------------------------------------
    @staticmethod    
    def load(p_path, p_filename):
        """
        Loads content from the given path and file name. If file does not exist, it returns None.

        Parameters:
            p_path          Path that contains the file 
            p_filename      File name

        Returns: 
            A loaded object, if file content was loaded successfully. None otherwise.
        """
        
        if not os.path.exists(p_path + os.sep + p_filename):
            return None
        
        return pkl.load(open(p_path + os.sep + p_filename, 'rb'))





## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class Saveable: 
    """
    This abstract class adds the ability to be saveable to inherited classes. The filename can be
    generated internally by implementing the method get_filename() or provided from outside otherwise.
    """

## -------------------------------------------------------------------------------------------------
    def generate_filename(self):
        """
        To be redefined in case of use of internal generated file names.

        Returns: 
            Returns an internal unique filename. 
        """

        return None


## -------------------------------------------------------------------------------------------------
    def save(self, p_path, p_filename=None) -> bool:
        """
        Saves content to the given path and file name. If file name is None, a unique file name will
        be generated by calling method generate_filename(). If it returns False then the saving method is failed. 

        Parameters:
            p_path          Path where file will be saved
            p_filename      File name (if None an internal filename will be generated)

        Returns: 
            True, if file content was saved successfully. False otherwise.
        """

        if ( p_filename is not None ) and ( p_filename != '' ):
            self.filename = p_filename
        else:
            self.filename = self.generate_filename()

        if self.filename is None:
            return False
        
        try:
            if not os.path.exists(p_path):
                os.makedirs(p_path)
            pkl.dump(self, open(p_path + os.sep + self.filename, "wb"))
            return True
        except:
            return False





## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class LoadSave (Loadable, Saveable): 
    """
    This abstract class adds the ability to be loadable and saveable to inherited classes. The 
    filename can be generated internally by implementing the method generate_filename() or provided 
    from outside otherwise. See classes Loadable and Saveable for further information.
    """
    
    pass






## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class Log:
    """
    This class adds elementry log functionality to inherited classes.
    """

    C_TYPE          = '????'
    C_NAME          = '????'

    C_LOG_TYPE_I    = 'I'           # Information
    C_LOG_TYPE_W    = 'W'           # Warning
    C_LOG_TYPE_E    = 'E'           # Error

    C_LOG_TYPES     = [ C_LOG_TYPE_I, C_LOG_TYPE_W, C_LOG_TYPE_E ]

    C_COL_WARNING   = '\033[93m'    # Yellow
    C_COL_ERROR     = '\033[91m'    # Red
    C_COL_RESET     = '\033[0m'     # Reset color

## -------------------------------------------------------------------------------------------------
    def __init__(self, p_logging=True):
        """
        Parameters:
            p_logging     switch for logging 
        """

        self.switch_logging(p_logging)
        self.set_log_level(self.C_LOG_TYPE_I)
        self.log(self.C_LOG_TYPE_I, 'Instantiated')


## -------------------------------------------------------------------------------------------------
    def switch_logging(self, p_logging:bool):
        """
        Switches log functionality on/off.

        Parameters:
            p_logging   switch for logging 
        """

        self.logging = p_logging 


## -------------------------------------------------------------------------------------------------
    def set_log_level(self, p_level):
        """
        Sets the log level. 

        Parameters:
            p_level         Possible values are 
                            C_LOG_TYPE_I (everything will be looged) 
                            C_LOG_TYPE_W (warnings and errors will be logged)
                            C_LOG_TYPE_E (only errors will be logged)
        """

        if p_level in self.C_LOG_TYPES:
            self._level = p_level
        else:
            raise ParamError('Wrong log level. Please use constants C_LOG_TYPE_* of class Log')


## -------------------------------------------------------------------------------------------------
    def log(self, p_type, *p_args):
        """
        Writes log line to standard output in format:
        yyyy-mm-dd  hh:mm:ss.mmmmmm  [p_type  C_TYPE C_NAME]: [p_args] 

        Parameters:
            p_type      type of log entry
            p_args      log informations

        Returns: 
            Nothing
        """

        if not self.logging: return

        if self._level == self.C_LOG_TYPE_W:
            if p_type == self.C_LOG_TYPE_I: return
        elif self._level == self.C_LOG_TYPE_E:
            if ( p_type == self.C_LOG_TYPE_I ) or ( p_type == self.C_LOG_TYPE_W ): return

        now = datetime.now()

        if p_type == self.C_LOG_TYPE_W:
            col = self.C_COL_WARNING
        elif p_type == self.C_LOG_TYPE_E:
            col = self.C_COL_ERROR
        else:
            col = self.C_COL_RESET

        print(col + '%04d-%02d-%02d  %02d:%02d:%02d.%06d ' % (now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond), p_type + '  ' + self.C_TYPE + ' ' + self.C_NAME + ':', *p_args)





## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class Timer:
    """
    Timer class in two time modes (real/virtual) and with simple lap management.
    """

    C_MODE_REAL         = 0             # Real time 
    C_MODE_VIRTUAL      = 1             # Virtual time

    C_LAP_LIMIT         = 999999        

## -------------------------------------------------------------------------------------------------
    def __init__(self, p_mode, p_lap_duration:timedelta, p_lap_limit=C_LAP_LIMIT ) -> None:
        """
        Parameters:
            p_mode          C_MODE_REAL for real time mode,
                            C_MODE_VIRTUAL for virtual time mode
            p_lap_duration  Duration of a single lap
            p_lap_limit     maximum number of laps until the lap counter restarts with 0  
        """
        
        self.mode           = p_mode
        self.lap_duration   = p_lap_duration

        if p_lap_limit == 0:
            self.lap_limit = self.C_LAP_LIMIT
        else:
            self.lap_limit = p_lap_limit

        self.reset()


## -------------------------------------------------------------------------------------------------
    def reset(self) -> None:
        """
        Resets timer.

        Returns: 
            Nothing
        """

        self.time           = timedelta(0,0,0)
        self.lap_time       = timedelta(0,0,0)
        self.lap_id         = 0

        if self.mode == self.C_MODE_REAL:
            self.timer_start_real   = datetime.now()
            self.lap_start_real     = self.timer_start_real
            self.time_real          = self.timer_start_real


## -------------------------------------------------------------------------------------------------
    def get_time(self) -> timedelta:
        if self.mode == self.C_MODE_REAL:
            self.time_real  = datetime.now()
            self.time       = self.time_real - self.timer_start_real

        return self.time


## -------------------------------------------------------------------------------------------------
    def get_lap_time(self) -> timedelta:
        if self.mode == self.C_MODE_REAL:
            self.lap_time       = datetime.now() - self.lap_start_real

        return self.lap_time


## -------------------------------------------------------------------------------------------------
    def get_lap_id(self):
        return self.lap_id


## -------------------------------------------------------------------------------------------------
    def add_time(self, p_delta:timedelta):
        if self.mode == self.C_MODE_VIRTUAL:
            self.lap_time   = self.lap_time + p_delta
            self.time       = self.time + p_delta


## -------------------------------------------------------------------------------------------------
    def finish_lap(self) -> bool:
        """
        Finishes the current lap. In timer mode C_MODE_REAL the remaining time
        until the end of the lap will be paused. 

        Returns: 
            True, if the remaining time to the next lap was positive. False, if 
            the timer timed out.
        """
        
        timeout = False

        # Compute delay until next lap
        delay = self.lap_duration - self.get_lap_time()
        
        # Check for timeout
        if delay < timedelta(0,0,0): 
            timeout = True
            delay = timedelta(0,0,0)

        # Handle delay depending on timer mode
        if self.mode == self.C_MODE_REAL:
            # Wait until next lap start
            sleep(delay.total_seconds())
        else:
            # Just set next lap start time
            self.time = self.time + delay
            
        # Update lap data
        self.lap_id         = divmod( self.lap_id + 1, self.lap_limit )[1]
        self.lap_time       = timedelta(0,0,0)
        self.lap_start_real = datetime.now()

        return not timeout





## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class TStamp:
    """
    This class provides elementry time stamp functionality for inherited classes.
    """


## -------------------------------------------------------------------------------------------------
    def __init__(self, p_tstamp:timedelta=None):
        self.set_tstamp(p_tstamp)


## -------------------------------------------------------------------------------------------------
    def get_tstamp(self) -> timedelta:
        return self.tstamp


## -------------------------------------------------------------------------------------------------
    def set_tstamp(self, p_tstamp:timedelta):
        self.tstamp = p_tstamp





## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class ScientificObjects:
    """
    This class provides elementry functionality for storing scientific references.
    """


## -------------------------------------------------------------------------------------------------
    def __init__(self, p_type=None, p_author=None, p_title=None, p_journal=None, p_abstract=None,
                 p_year=None, p_month=None, p_day=None, p_pages=None, p_volume=None, p_issue=None, 
                 p_city=None, p_country=None, p_url=None, p_ror_id=None, p_doi=None,
                 p_editor=None, p_publisher=None, p_translator=None, p_institution=None,
                 p_conference=None, p_booktitle=None, p_notes=None):
        self.references = {}
        self.set_item("Type of source", p_type)
        self.set_item("Author", p_author)
        self.set_item("Title", p_title)
        self.set_item("Jorunal Name", p_journal)
        self.set_item("Abstract", p_abstract)
        self.set_item("Year", p_year)
        self.set_item("Month", p_month)
        self.set_item("Day", p_day)
        self.set_item("Pages", p_pages)
        self.set_item("Volume", p_volume)
        self.set_item("Issue", p_issue)
        self.set_item("City", p_city)
        self.set_item("Country", p_country)
        self.set_item("URL", p_url)
        self.set_item("ROR ID", p_ror_id)
        self.set_item("DOI", p_doi)
        self.set_item("Editor", p_editor)
        self.set_item("Publisher", p_publisher)
        self.set_item("Translator", p_translator)
        self.set_item("Institution", p_institution)
        self.set_item("Conference Publication Name", p_conference)
        self.set_item("Book Title", p_booktitle)
        self.set_item("Notes", p_notes)


## -------------------------------------------------------------------------------------------------
    def set_item(self, p_item, p_input):
        """
        It is possible to add all kinds of information to the dictionary or update
        the stored information.
        """
        if p_input:
            self.references[p_item] = p_input


## -------------------------------------------------------------------------------------------------
    def get_item(self, p_item):
        return self.references.get(p_item)


## -------------------------------------------------------------------------------------------------
    def get_references(self):
        return self.references