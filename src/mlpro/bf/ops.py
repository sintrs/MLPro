## -------------------------------------------------------------------------------------------------
## -- Project : MLPro - A Synoptic Framework for Standardized Machine Learning Tasks
## -- Package : mlpro.bf
## -- Module  : ops
## -------------------------------------------------------------------------------------------------
## -- History :
## -- yyyy-mm-dd  Ver.      Auth.    Description
## -- 2022-10-28  0.0.0     DA       Creation 
## -------------------------------------------------------------------------------------------------

"""
Ver. 0.0.0 (2022-10-28)

This module provides classes for operation.
"""


import sys
from datetime import timedelta
from matplotlib.figure import Figure
from mlpro.bf.various import Log, LoadSave, Timer
from mlpro.bf.plot import Plottable
from mlpro.bf.events import *



## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class Mode (Log):
    """
    Property class that adds a mode and related methods to a child class.

    Parameters
    ----------
    p_mode
        Operation mode. Valid values are stored in constant C_VALID_MODES.
    p_logging
        Log level (see constants of class Log). Default: Log.C_LOG_ALL

    Attributes
    ----------
    C_MODE_SIM = 0
        Simulation mode.
    C_MODE_REAL = 1
        Real operation mode.
    C_VALID_MODES : list
        List of valid modes.
    """

    C_MODE_INITIAL  = -1
    C_MODE_SIM      = 0
    C_MODE_REAL     = 1

    C_VALID_MODES   = [ C_MODE_SIM, C_MODE_REAL ]

## -------------------------------------------------------------------------------------------------
    def __init__(self, p_mode, p_logging=Log.C_LOG_ALL):
        super().__init__(p_logging)
        self._mode = self.C_MODE_INITIAL
        self.set_mode(p_mode)


## -------------------------------------------------------------------------------------------------
    def get_mode(self):
        """
        Returns current mode.
        """

        return self._mode


## -------------------------------------------------------------------------------------------------
    def set_mode(self, p_mode):
        """
        Sets new mode.

        Parameters
        ----------
        p_mode
            Operation mode. Valid values are stored in constant C_VALID_MODES.
        """

        if not p_mode in self.C_VALID_MODES: raise ParamError('Invalid mode')
        if self._mode == p_mode: return
        self._mode = p_mode
        self.log(self.C_LOG_TYPE_I, 'Operation mode set to', self._mode)





## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class Scenario (Mode, LoadSave, Plottable):
    """
    Root class for scenarios that can be executed. To be inherited and specialized in higher layers.
    
    The following key features are included:
      - Operation mode
      - Cycle management
      - Timer
      - Latency 

    Parameters
    ----------
    p_mode
        Operation mode. See Mode.C_VALID_MODES for valid values. Default = Mode.C_MODE_SIM.
    p_cycle_len : timedelta
        Cycle length. 
    p_cycle_limit : int
        Maximum number of cycles. Default = 0 (no limit).
    p_visualize 
        Boolean switch for env/agent visualisation. Default = True.
    p_logging
        Log level (see constants of class Log). Default: Log.C_LOG_ALL.  
    """

    C_TYPE      = 'Scenario'
    C_NAME      = '????'

## -------------------------------------------------------------------------------------------------
    def __init__(self, 
                 p_mode,       
                 p_cycle_len:timedelta,            
                 p_cycle_limit=0,  
                 p_visualize=True,              
                 p_logging=Log.C_LOG_ALL ):    

        # 1 Intro
        self._cycle_max     = sys.maxsize
        self._cycle_id      = 0
        self._cycle_len     = p_cycle_len
        self._visualize     = p_visualize
        self.set_cycle_limit(p_cycle_limit)
        
        Mode.__init__(self, p_mode, p_logging)


        # 2 Init timer
        if self.get_mode() == Mode.C_MODE_SIM:
            t_mode = Timer.C_MODE_VIRTUAL
        else:
            t_mode = Timer.C_MODE_REAL

        self._timer     = Timer(t_mode, self._cycle_len, self._cycle_limit)


## -------------------------------------------------------------------------------------------------
    def set_mode(self, p_mode):
        """
        Sets operation mode of the scenario. Custom method _set_mode() is called.

        Parameter
        ---------
        p_mode
            Operation mode. See class bf.ops.Mode for further details.
        """

        super().set_mode(p_mode)
        self._set_mode(p_mode)


## -------------------------------------------------------------------------------------------------
    def _set_mode(self, p_mode):
        """
        Custom method to set the operation mode of components of the scenario. See method set_mode()
        for further details.

        Parameter
        ---------
        p_mode
            Operation mode. See class bf.ops.Mode for further details.
        """

        raise NotImplementedError


## -------------------------------------------------------------------------------------------------
    def get_latency(self) -> timedelta:
        """
        Returns the latency of the scenario. To be implemented in child class.
        """

        raise NotImplementedError


## -------------------------------------------------------------------------------------------------
    def set_cycle_limit(self, p_limit):
        """
        Sets the maximum number of cycles to run.

        Parameters
        ----------
        p_cycle_limit : int
            Maximum number of cycles. Default = 0 (no limit).
        """

        self._cycle_limit = p_limit


## -------------------------------------------------------------------------------------------------
    def reset(self, p_seed=1):
        """
        Resets the scenario and especially the ML model inside. Internal random generators are seed 
        with the given value. Custom reset actions can be implemented in method _reset().

        Parameters
        ----------
        p_seed : int          
            Seed value for internal random generator
        """

        # 1 Intro
        self.log(self.C_LOG_TYPE_I, 'Process time', self._timer.get_time(), ': Scenario reset with seed', str(p_seed))

        # 2 Custom reset of further scenario-specific components
        self._reset(p_seed)

        # 3 Timer reset
        self._timer.reset()

        # 4 Cycle counter reset
        self._cycle_id = 0


## -------------------------------------------------------------------------------------------------
    def _reset(self, p_seed):
        """
        Custom method to reset the components of the scenario and to set the given random seed value. 
        See method reset() for further details.

        Parameters
        ----------
        p_seed : int          
            Seed value for internal random generator
        """

        pass


## -------------------------------------------------------------------------------------------------
    def run_cycle(self):
        """
        Runs a single process cycle.

        Returns
        -------
        success : bool
            True on success. False otherwise.
        error : bool
            True on error. False otherwise.
        timeout : bool
            True on timeout. False otherwise.
        cycle_limit : bool
            True, if cycle limit has reached. False otherwise.
        adapted : bool
            True, if something within the scenario has adapted something in this cycle. False otherwise.
        """

        # 1 Run a single custom cycle
        self.log(self.C_LOG_TYPE_I, 'Process time', self._timer.get_time(), ': Start of cycle', str(self._cycle_id))
        success, error, adapted = self._run_cycle()
        self.log(self.C_LOG_TYPE_I, 'Process time', self._timer.get_time(), ': End of cycle', str(self._cycle_id), '\n')


        # 2 Update visualization
        if self._visualize:
            self.update_plot()


        # 3 Update cycle id and check for optional limit
        if ( self._cycle_limit > 0 ) and ( self._cycle_id >= ( self._cycle_limit -1 ) ): 
            limit = True
        else:
            self._cycle_id = ( self._cycle_id + 1 ) & self._cycle_max
            limit = False


        # 4 Wait for next cycle (real mode only)
        if ( self._timer.finish_lap() == False ) and ( self._cycle_len is not None ):
            self.log(self.C_LOG_TYPE_W, 'Process time', self._timer.get_time(), ': Process timed out !!!')
            timeout = True
        else:
            timeout = False


        # 5 Return result of custom cycle execution
        return success, error, timeout, limit, adapted


## -------------------------------------------------------------------------------------------------
    def _run_cycle(self):
        """
        Custom implementation of a single process cycle. To be redefined.

        Returns
        -------
        success : bool
            True on success. False otherwise.
        error : bool
            True on error. False otherwise.
        adapted : bool
            True, if something within the scenario has adapted something in this cycle. False otherwise.
        """

        raise NotImplementedError


## -------------------------------------------------------------------------------------------------
    def get_cycle_id(self):
        """
        Returns current cycle id.
        """

        return self._cycle_id


## -------------------------------------------------------------------------------------------------
    def run(self, 
            p_term_on_success:bool=True,        
            p_term_on_error:bool=True,          
            p_term_on_timeout:bool=False ):    
        """
        Runs the scenario as a sequence of single process steps until a terminating event occures.

        Parameters
        ----------
        p_term_on_success : bool
            If True, the run terminates on success. Default = True.
        p_term_on_error : bool
            If True, the run terminates on error. Default = True.
        p_term_on_timeout : bool
            If True, the run terminates on timeout. Default = False.

        Returns
        -------
        success : bool
            True on success. False otherwise.
        error : bool
            True on error. False otherwise.
        timeout : bool
            True on timeout. False otherwise.
        cycle_limit : bool
            True, if cycle limit has reached. False otherwise.
        adapted : bool
            True, if ml model adapted something. False otherwise.
        num_cycles: int
            Number of cycles.
        """

        self._cycle_id  = 0
        adapted         = False
        self.log(self.C_LOG_TYPE_I, 'Process time', self._timer.get_time(), 'Start of processing')

        while True:
            success, error, timeout, limit, adapted_cycle = self.run_cycle()
            adapted = adapted or adapted_cycle
            if p_term_on_success and success: break
            if p_term_on_error and error: break
            if p_term_on_timeout and timeout: break
            if limit: break

        self.log(self.C_LOG_TYPE_I, 'Process time', self._timer.get_time(), 'End of processing')

        return success, error, timeout, limit, adapted, self._cycle_id