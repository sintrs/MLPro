## -------------------------------------------------------------------------------------------------
## -- Project : MLPro - A Synoptic Framework for Standardized Machine Learning Tasks
## -- Package : mlpro.bf
## -- Module  : mt
## -------------------------------------------------------------------------------------------------
## -- History :
## -- yyyy-mm-dd  Ver.      Auth.    Description
## -- 2022-08-27  0.0.0     DA       Creation 
## -- 2022-09-10  0.1.0     DA       Initial class definition
## -- 2022-09-xx  1.0.0     DA       Initial implementation
## -------------------------------------------------------------------------------------------------

"""
Ver. 1.0.0 (2022-09-xx)

This module provides classes for multitasking with optional interprocess communication (IPC) based
on shared objects.
"""


import uuid
import threading as mt
import multiprocessing as mp
from multiprocessing.managers import BaseManager
from mlpro.bf.exceptions import *
from mlpro.bf.various import Log
from mlpro.bf.events import EventManager, Event




## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class Range:
    """
    Property class that adds the range of asynchronicity to a child class.

    Parameters
    ----------
    p_range : int
        Range of asynchonicity 
    """

    # Possible ranges for child classes
    C_RANGE_THREAD          = 0         # separate thread inside the same process
    C_RANGE_PROCESS         = 1         # separate process inside the same machine    

    C_VALID_RANGES          = [ C_RANGE_THREAD, C_RANGE_PROCESS ] 

## -------------------------------------------------------------------------------------------------
    def __init__(self, p_range=C_RANGE_PROCESS):
        if p_range not in self.C_VALID_RANGES: raise ParamError
        self._range = p_range


## -------------------------------------------------------------------------------------------------
    def get_range(self):
        return self._range





## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class Shared (Range): 
    """
    Template class for shared objects. It is ready to use and the default class for IPC. It is also
    possible to inherit and enrich this class for special needs. It provides elementary mechanisms 
    for access control and messaging.

    Parameters
    ----------
    p_range : int
        Range of asynchonicity 
    """

    C_MSG_TYPE_DATA         = 0
    C_MSG_TYPE_TERM         = 1

## -------------------------------------------------------------------------------------------------
    def __init__(self, p_range=Range.C_RANGE_PROCESS):

        super().__init__(p_range)

        if p_range == self.C_RANGE_THREAD:
            self._lock_obj  = mt.Lock()
        elif p_range == self.C_RANGE_PROCESS:
            self._lock_obj  = mp.Lock()
        else:
            raise ParamError

        self._locking_task  = None
        self._active_tasks  = []
        self._messages      = {}


# -------------------------------------------------------------------------------------------------
    def lock(self, p_tid=None, p_timeout:float=None) -> bool: 
        """
        Locks the shared object for a specific process.

        Parameters
        ----------
        p_tid
            Unique task id. If None then the internal locking mechanism is disabled.
        p_timeout : float
            Optional timeout in seconds. If None, timeout is infinite.

        Returns
        True, if shared object was locked successfully. False otherwise.
        """

        if p_tid == self._locking_task: return True
        if p_timeout is None:
            return self._lock_obj.acquire()
        else:
            return self._lock_obj.acquire(timeout=p_timeout)


## -------------------------------------------------------------------------------------------------
    def unlock(self):
        """
        Unlocks the shared object.
        """

        if self._locking_task is None: return
        self._locking_task = None
        self._lock.release()


### -------------------------------------------------------------------------------------------------
    def checkin(self, p_tid):
        """
        Registers a task.

        Parameters
        ----------
        p_tid
            Task id.
        """

        self.lock()
        self._active_tasks.append(p_tid)
        self.unlock()


## -------------------------------------------------------------------------------------------------
    def checkout(self, p_tid):
        """
        Unregisters a task.

        Parameters
        ----------
        p_tid
            Task id.
        """

        self.lock()
        self._active_tasks.remove(p_tid)
        self.unlock()


## -------------------------------------------------------------------------------------------------
    def send_message ( self, p_msg_type, p_tid=None, **p_kwargs):
        raise NotImplementedError


## -------------------------------------------------------------------------------------------------
    def receive_message(self, p_tid, p_msg_type=None):
        raise NotImplementedError





## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class Async (Range, Log):
    """
    Property class that enables child classes to run sub-tasks asynchronously. Depending on the
    given range a task can be executed as a separate thread in the same process or a separate
    process on the same machine.

    Parameters
    ----------
    p_range : int
        Range of asynchonicity. See class Range. Default is Range.C_RANGE_PROCESS.
    p_class_shared
        Optional class name for a shared object (class Shared or a child class of Shared)
    p_logging
        Log level (see constants of class Log). Default: Log.C_LOG_ALL   
    """

## -------------------------------------------------------------------------------------------------
    def __init__( self,
                  p_range=Range.C_RANGE_PROCESS,
                  p_class_shared=None, 
                  p_logging=Log.C_LOG_ALL ):

        Log.__init__(p_logging=p_logging)
        Range.__init__(self, p_range=p_range)

        if p_class_shared is not None:
            # Instantiation of shared object
            if p_range == self.C_RANGE_THREAD:
                self._so = p_class_shared(p_range)
            else:
                BaseManager.register('Shared', p_class_shared)
                self._mpmanager = BaseManager()
                self._mpmanager.start()
                self._so = self._mpmanager.Shared(p_range=p_range)
        else:
            self._so = None

        self._async_tasks   = []


## -------------------------------------------------------------------------------------------------
    def _get_so(self) -> Shared: 
        """
        Returns the associated shared object.

        Returns
        -------
        so : Shared
            Shared object of type Shared (or inherited)
        """

        return self._so


## -------------------------------------------------------------------------------------------------
    def _run_async( self, 
                    p_method=None,
                    p_class=None,
                    **p_kwargs ):
        """
        Runs a method or a new instance of a given class asynchronously. If neither a method nor a
        class is specified, a new instance of the current class is created asynchronously.

        Parameters
        ----------
        p_method
            Optional method to be called asynchronously
        p_class
            Optional class to be instantiated asynchronously
        p_kwargs : dictionary
            Parameters to be handed over to asynchonous method/instance
        """

        if p_method is not None:
            # 1 Prepares a new task for a single method 
            if self._range == self.C_RANGE_THREAD:
                # 1.1 ... as a thread
                task = mt.Thread(target=p_method, kwargs=p_kwargs, group=None)

            else:
                # 1.2 ... as a process
                task = mp.Process(target=p_method, kwargs=p_kwargs, group=None)

        else:
            # 2 Prepares a new task for a new object of a given class
            if p_class is not None: 
                c = p_class
            else:
                c = self.__class__

            kwargs = p_kwargs
            kwargs['p_class'] = c

            if self._range == self.C_RANGE_THREAD:
                # 2.1 ... as a thread
                task = mt.Thread(target=self._run_object_async, kwargs=kwargs, group=None)

            else:
                # 2.2 ... as a process
                task = mp.Process(target=self._run_object_async, kwargs=kwargs, group=None)


        # 3 Registers and runs the new task
        self._async_tasks.append(task)
        task.start()


## -------------------------------------------------------------------------------------------------
    def _run_object_async(self, p_class, **p_kwargs):
        p_class(p_kwargs)


## -------------------------------------------------------------------------------------------------
    def _wait_async_tasks(self):
        for task in self._async_tasks: task.join()
        self._async_tasks.clear()





## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class Task (Async, EventManager): 
    """
    Template class for a task, that can run things - and even itself - asynchronously in a thread
    or process. Tasks can run standalone or as part of a workflow (see class Workflow). The integrated
    event manager allows callbacks on specific events inside the same process(!).

    Parameters
    ----------
    p_range : int
        Range of asynchonicity. See class Range. Default is Range.C_RANGE_PROCESS.
    p_autorun : int
        On value C_AUTORUN_RUN method run() is called imediately during instantiation.
        On vaule C_AUTORUN_LOOP method run_loop() is called.
        Value C_AUTORUN_NONE (default) causes an object instantiation without starting further
        actions.    
    p_class_shared
        Optional class name for a shared object (class Shared or a child class of Shared)
    p_logging
        Log level (see constants of class Log). Default: Log.C_LOG_ALL
    """

    C_TYPE              = 'Task'

    C_AUTORUN_NONE      = 0
    C_AUTURUN_RUN       = 1
    C_AUTORUN_LOOP      = 2

    C_EVENT_FINISHED    = 0

## -------------------------------------------------------------------------------------------------
    def __init__( self, 
                  p_range=Async.C_RANGE_PROCESS, 
                  p_autorun=C_AUTORUN_NONE,
                  p_class_shared=None, 
                  p_logging=Log.C_LOG_ALL,
                  **p_kwargs ):

        self._tid       = uuid.uuid4()
        self._kwargs    = p_kwargs.copy()

        Async.__init__(self, p_range=p_range, p_class_shared=p_class_shared, p_logging=p_logging)
        EventManager.__init__(self, p_logging=p_logging)

        if self._so is not None: self._so.checkin(p_tid=self._tid)
        self._autorun(p_autorun=p_autorun, p_kwargs=self._kwargs)


## -------------------------------------------------------------------------------------------------
    def get_tid(self):
        """
        Returns unique task id.
        """

        return self._tid


## -------------------------------------------------------------------------------------------------
    def _autorun(self, p_autorun, **p_kwargs):
        """
        Internal method to automate a single or looped run.

        Parameters
        ----------
        p_autorun : int
            On value C_AUTORUN_RUN method run() is called imediately during instantiation.
            On vaule C_AUTORUN_LOOP method run_loop() is called.
            Value C_AUTORUN_NONE (default) causes an object instantiation without starting further
            actions.    
        p_kwargs : dict
            Further parameters handed over to method run().
        """

        if p_autorun == self.C_AUTURUN_RUN:
            self.run(p_kwargs=p_kwargs)
        elif p_autorun == self.C_AUTORUN_LOOP:
            self.run_loop(p_kwargs=p_kwargs)


## -------------------------------------------------------------------------------------------------
    def run(self, **p_kwargs):
        """
        Executes the task specific actions implemented in custom method _run(). At the end event
        C_EVENT_FINISHED is raised to start subsequent actions.

        Parameters
        ----------
        p_kwargs : dict
            Further parameters handed over to custom method _run().
        """

        self._run(p_kwargs=p_kwargs)

        self._raise_event( self.C_EVENT_FINISHED, Event(p_raising_object=self, p_kwargs=p_kwargs))
        

## -------------------------------------------------------------------------------------------------
    def _run(self, **p_kwargs):
        """
        Custom method that is called by method run(). 

        Parameters
        ----------
        p_kwargs : dict
            Further parameters handed over to custom method _run().
        """

        raise NotImplementedError


## -------------------------------------------------------------------------------------------------
    def run_loop(self, **p_kwargs):
        """
        Executes method run() in a loop, until a message of type Shared.C_MSG_TYPE_TERM is sent to
        the task.

        Parameters
        ----------
        p_kwargs : dict
            Parameters for method run()
        """
        
        while True:
            self.run(p_kwargs=p_kwargs)

            if self._so is not None:
                msg_type, = self._so.receive_message( p_tid=self.get_tid(), p_msg_type=Shared.C_MSG_TYPE_TERM )
                if msg_type is not None: break


## -------------------------------------------------------------------------------------------------
    def run_on_event(self, p_event_id, p_event_object:Event):
        """
        Can be used as event handler - in particular for other tasks in combination with event 
        C_EVENT_FINISHED.

        Parameters
        ----------
        p_event_id 
            Event id.
        p_event_object : Event
            Event object with further context informations.
        """

        self.run(p_kwargs=p_event_object.get_data())


## -------------------------------------------------------------------------------------------------
    def __del__(self):
        if self._so is not None: self._so.checkout(self.get_tid())





## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class Workflow (Task): 
    """
    Ready-to-use container class for task groups. Objects of type Task (or inherited) can be added and
    chained to sequences or hierarchies of tasks. 

    Parameters
    ----------
    p_range : int
        Range of asynchonicity. See class Range. Default is Range.C_RANGE_PROCESS.
    p_class_shared
        Optional class name for a shared object (class Shared or a child class of Shared)
    p_logging
        Log level (see constants of class Log). Default: Log.C_LOG_ALL
    """
    
    C_TYPE          = 'Workflow'

## -------------------------------------------------------------------------------------------------
    def __init__( self, 
                  p_range=Async.C_RANGE_PROCESS, 
                  p_class_shared=None, 
                  p_logging=Log.C_LOG_ALL, 
                  **p_kwargs ):

        self._tasks         = []
        self._entry_tasks   = []

        super().__init__( p_range=p_range,
                          p_autorun=self.C_AUTORUN_NONE,
                          p_class_shared=p_class_shared,
                          p_logging=p_logging,
                          p_kwargs=p_kwargs )


## -------------------------------------------------------------------------------------------------
    def switch_logging(self, p_logging):
        """
        Sets log level for the workflow and all tasks inside.

        Parameters
        ----------
        p_logging
            Log level (see constants of class Log).
        """

        super().switch_logging(p_logging)
        for task in self._tasks: task.switch_logging(p_logging=p_logging)


## -------------------------------------------------------------------------------------------------
    def _run(self, **p_kwargs):
        for task in self._entry_tasks: task.run(p_kwargs=p_kwargs)


## -------------------------------------------------------------------------------------------------
    def add_task(self, p_task:Task, p_pred_tasks:list=None):
        """
        Adds a task to the workflow.

        Parameters
        ----------
        p_task : Task
            Task object to be added.
        p_pred_tasks : list
            Optional list of predecessor task objects
        """

        p_task.switch_logging(p_logging=self._level)
        self._tasks.append(p_task)

        if ( p_pred_tasks is None ) or ( len(p_pred_tasks == 0 )):
            self._entry_tasks.append(p_task)

        else:
            for t_pred in p_pred_tasks: 
                t_pred.register_event_handler(p_event_id=self.C_EVENT_FINISHED, p_event_handler=p_task.run_on_event)