## -------------------------------------------------------------------------------------------------
## -- Project : MLPro - A Synoptic Framework for Standardized Machine Learning Tasks
## -- Package : mlpro.oa.systems
## -- Module  : systems.py
## -------------------------------------------------------------------------------------------------
## -- History :
## -- yyyy-mm-dd  Ver.      Auth.    Description
## -- 2023-mm-mm  0.0.0     LSB      Creation
## -------------------------------------------------------------------------------------------------

"""
Ver. 0.0.0 (2023-02-16)

This module provides modules and template classes for adaptive systems and adaptive functions.
"""
import copy

from mlpro.bf.ml.systems import *
from mlpro.bf.systems import *
from mlpro.bf.ml import Model
from mlpro.bf.streams import *
from mlpro.oa.streams import *
from typing import Callable






## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class PseudoTask(OATask):




## -------------------------------------------------------------------------------------------------
    def __init__(self,
                 p_wrap_method:Callable[[List[State],
                                         List[State]],
                                         None],
                 p_name='PseudoTask',
                 p_range_max=Range.C_RANGE_NONE,
                 p_duplicate_data=True,
                 p_logging=Log.C_LOG_ALL,
                 p_visualize=False,
                 **p_kwargs):


        OATask.__init__(self,
                        p_name = p_name,
                        p_range_max = p_range_max,
                        p_duplicate_data = p_duplicate_data,
                        p_ada = False,
                        p_logging = p_logging,
                        p_visualize= p_visualize,
                        **p_kwargs)


        self._host_task = p_wrap_method


## -------------------------------------------------------------------------------------------------
    def _run( self,
              p_inst_new : list,
              p_inst_del : list ):

        self._host_task(p_inst_new = p_inst_new,
                        p_inst_del = p_inst_del)






## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class OAFctSTrans(FctSTrans, Model):
    """

    Parameters
    ----------
    p_name
    p_range_max
    p_class_shared
    p_visualize
    p_logging
    p_kwargs
    """

    def __init__(self,
                 p_id = None,
                 p_name: str = None,
                 p_range_max: int = Async.C_RANGE_PROCESS,
                 p_autorun: int = Task.C_AUTORUN_NONE,
                 p_class_shared = None,
                 p_ada:bool=True,
                 p_afct_cls = None,
                 p_state_space: MSpace = None,
                 p_action_space: MSpace = None,
                 p_input_space_cls=ESpace,
                 p_output_space_cls=ESpace,
                 p_output_elem_cls=State,  # Specific output element type
                 p_threshold=0,
                 p_buffer_size=0,
                 p_wf: OAWorkflow = None,
                 p_visualize:bool=False,
                 p_logging=Log.C_LOG_ALL,
                 **p_kwargs):

        self._afct_strans = None
        if p_afct_cls is not None:
            if (p_state_space is None) or (p_action_space is None):
                raise ParamError("Please provide mandatory parameters state and action space.")

            self._afct_strans = AFctSTrans(p_afct_cls = p_afct_cls,
                                          p_state_space=p_state_space,
                                          p_action_space=p_action_space,
                                          p_input_space_cls=p_input_space_cls,
                                          p_output_space_cls=p_output_space_cls,
                                          p_output_elem_cls=p_output_elem_cls,
                                          p_threshold=p_threshold,
                                          p_buffer_size=p_buffer_size,
                                          p_ada=p_ada,
                                          p_visualize=p_visualize,
                                          p_logging=p_logging,
                                          **p_kwargs)

        FctSTrans.__init__(self, p_logging = p_logging)

        Model.__init__(self,
                       p_id= p_id,
                       p_name=p_name,
                       p_range_max=p_range_max,
                       p_autorun=p_autorun,
                       p_class_shared=p_class_shared,
                       p_ada=p_ada,
                       p_visualize=p_visualize,
                       p_logging=p_logging,
                       **p_kwargs)

        if p_wf is None:
            self._wf = OAWorkflow(p_visualize=p_visualize,
                                  p_ada=p_ada,
                                  p_logging=p_logging)
        else:
            self._wf = p_wf

        self._action_obj:Action = None
        self._setup_wf_strans = False


## -------------------------------------------------------------------------------------------------
    def simulate_reaction(self, p_state: State, p_action: Action, p_t_step : timedelta = None) -> State:
        """
        Simulates a state transition based on a state and action. Custom method _simulate_reaction()
        is called.

        Parameters
        ----------
        p_state: State
            State of the System.

        p_action: Action
            External action provided for the action simulation

        p_t_step: timedelta, optional.
            The timestep for which the system is to be simulated

        Returns
        -------
        state: State
            The new state of the System.

        """
        # 1. copying the state and action object for the function level
        self._state_obj = p_state.copy()
        self._action_obj = copy.deepcopy(p_action)
        self.log(Log.C_LOG_TYPE_I, 'Reaction Simulation Started...')

        # 2. Checking for the first run
        if not self._setup_wf_strans:
            self._setup_wf_strans = self._setup_oafct_strans()

        # 3. Running the workflow
        self._wf.run(p_inst_new=[self._state_obj])


        # 4. get the results
        state = self._wf.get_so().get_results()[self.get_id()]

        return state

## -------------------------------------------------------------------------------------------------
    def _adapt(self, **p_kwargs) -> bool:
        """
        When called, the function and it's components adapt based on the provided parameters.

        Parameters
        ----------
        p_kwargs
            additional parameters for adaptation.

        Returns
        -------
        adapted: bool
            Returns true if the Function has adapted
        """

        adapted = False
        try:
            adapted = self._wf.adapt(**p_kwargs) or adapted
        except:
            adapted = adapted or False

        if self._afct_strans is not None:
            try:
                adapted = self._afct_strans.adapt(**p_kwargs) or adapted
            except:
                adapted = adapted or False

        return adapted

## -------------------------------------------------------------------------------------------------
    def _adapt_on_event(self, p_event_id:str, p_event_object:Event) -> bool:
        """

        Parameters
        ----------
        p_event_id
        p_event_object

        Returns
        -------

        """
        pass


## -------------------------------------------------------------------------------------------------
    def add_task(self, p_task:OATask, p_pred_task = None):
        """
        Adds a task to the workflow.

        Parameters
        ----------
        p_task: OATask, StreamTask
            The task to be added to the workflow

        p_pred_task: list[Task]
            Name of the predecessor tasks for the task to be added

        """
        self._wf.add_task(p_task, p_pred_task)


## -------------------------------------------------------------------------------------------------
    def _run(self, p_inst_new, p_inst_del):
        """
        Runs the processing workflow, for state transition.

        Parameters
        ----------
        p_inst_new: list[State]
            List of new instances to be processed.

        p_inst_del: list[State]
            List of old instances to be processed.

        """

        if self._afct_strans is not None:
            self._wf.get_so().add_result(self.get_id(), AFctSTrans.simulate_reaction(self,
                                                                                p_state=p_inst_new[0],
                                                                                p_action=self._action_obj))
        else:
            self._wf.get_so().add_result(self.get_id(), FctSTrans.simulate_reaction(self,
                                                                            p_state=p_inst_new[0],
                                                                            p_action=self._action_obj))


## -------------------------------------------------------------------------------------------------
    def _setup_oafct_strans(self):
        """
        Adds a pseudo task to the processing workflow, with the method to be wrapped.

        Returns
        -------
        bool
            False when successfully setup.

        """

        if len(self._wf._tasks) == 0:
            p_pred_tasks = None
        else:
            p_pred_tasks = [self._wf._tasks[-1]]
            self._wf = OAWorkflow()
        self._wf.add_task(p_task=PseudoTask(p_wrap_method = self._run), p_pred_tasks=p_pred_tasks)

        return True







## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class OAFctSuccess(FctSuccess, Model):
    """

    Parameters
    ----------
    p_name
    p_range_max
    p_class_shared
    p_visualize
    p_logging
    p_kwargs
    """


    ## -------------------------------------------------------------------------------------------------
    def __init__(self,
                 p_id = None,
                 p_name: str = None,
                 p_range_max: int = Async.C_RANGE_PROCESS,
                 p_autorun: int = Task.C_AUTORUN_NONE,
                 p_class_shared = None,
                 p_ada:bool=True,
                 p_afct_cls = None,
                 p_state_space: MSpace = None,
                 p_action_space: MSpace = None,
                 p_input_space_cls=ESpace,
                 p_output_space_cls=ESpace,
                 p_output_elem_cls=State,  # Specific output element type
                 p_threshold=0,
                 p_buffer_size=0,
                 p_wf_success: OAWorkflow = None,
                 p_visualize:bool=False,
                 p_logging=Log.C_LOG_ALL,
                 **p_kwargs):

        self._afct_success = None
        if p_afct_cls is not None:
            if (p_state_space is None) or (p_action_space is None):
                raise ParamError("Please provide mandatory parameters state and action space.")

            self._afct_success = AFctSuccess(p_afct_cls=p_afct_cls,
                                            p_state_space=p_state_space,
                                            p_action_space=p_action_space,
                                            p_input_space_cls=p_input_space_cls,
                                            p_output_space_cls=p_output_space_cls,
                                            p_output_elem_cls=p_output_elem_cls,
                                            p_threshold=p_threshold,
                                            p_buffer_size=p_buffer_size,
                                            p_ada=p_ada,
                                            p_visualize=p_visualize,
                                            p_logging=p_logging,
                                            **p_kwargs)
                #
        # else:
        FctSuccess.__init__(self, p_logging=p_logging)

        Model.__init__(self,
                       p_id= p_id,
                       p_name=p_name,
                       p_range_max=p_range_max,
                       p_autorun=p_autorun,
                       p_class_shared=p_class_shared,
                       p_ada=p_ada,
                       p_visualize=p_visualize,
                       p_logging=p_logging,
                       **p_kwargs)

        if p_wf_success is None:
            self._wf_success = OAWorkflow(p_visualize=p_visualize,
                                          p_ada=p_ada,
                                          p_logging=p_logging)
        else:
            self._wf_success = p_wf_success

        self._setup_wf_success = False

## -------------------------------------------------------------------------------------------------
    def compute_success(self, p_state: State) -> bool:
        """
        Assesses the given state regarding success criteria. Custom method _compute_success() is called.

        Parameters
        ----------
        p_state : State
            System state.

        Returns
        -------
        success : bool
            True, if given state is a success state. False otherwise.
        """

        self._state_obj = p_state.copy()
        self.log(Log.C_LOG_TYPE_I, 'Assessing Success...')


        if not self._setup_wf_success:
            self._setup_wf_success = self._setup_oafct_success()

        # 6. Run the workflow
        self._wf_success.run(p_inst_new=[self._state_obj])


        # 7. Return the results
        return self._wf_success.get_so().get_results()[self.get_id()]


## -------------------------------------------------------------------------------------------------
    def _adapt_on_event(self, p_event_id:str, p_event_object:Event) -> bool:
        """

        Parameters
        ----------
        p_event_id
        p_event_object

        Returns
        -------

        """
        pass


## -------------------------------------------------------------------------------------------------
    def add_task_success(self, p_task:StreamTask, p_pred_tasks:list = None):
        """
        Adds a task to the workflow.

        Parameters
        ----------
        p_task: OATask, StreamTask
            The task to be added to the workflow

        p_pred_task: list[Task]
            Name of the predecessor tasks for the task to be added

        """
        self._wf_success.add_task(p_task = p_task, p_pred_tasks=p_pred_tasks)


## -------------------------------------------------------------------------------------------------
    def _run_wf_success(self, p_inst_new, p_inst_del):
        """
        Runs the success computation workflow of the system.

        Parameters
        ----------
        p_inst_new: list[State]
            List of new instances to be processed by the workflow.

        p_inst_del: list[State]
            List of old instances to be processed by the workflow.

        """

        if self._afct_success is not None:
            self._wf_success.get_so().add_result(self.get_id(), AFctSuccess.compute_success(self,
                                                                                 p_state=p_inst_new[0]))
        else:
            self._wf_success.get_so().add_result(self.get_id(), FctSuccess.compute_success(self,
                                                                            p_state=p_inst_new[0]))


## -------------------------------------------------------------------------------------------------
    def _adapt(self, **p_kwargs) -> bool:
        """
        When called, the function and it's components adapt based on the provided parameters.

        Parameters
        ----------
        p_kwargs
            additional parameters for adaptation.

        Returns
        -------
        adapted: bool
            Returns true if the Function has adapted
        """

        adapted = False
        try:
            adapted = self._wf_success.adapt(**p_kwargs) or adapted
        except:
            adapted = False or adapted

        if self._afct_success is not None:
            try:
                adapted = self._afct_success.adapt(**p_kwargs) or adapted
            except:
                adapted = False or adapted

        return adapted


## -------------------------------------------------------------------------------------------------
    def _setup_oafct_success(self):
        """
        Adds a pseudo task to the success computation workflow, with the method to be wrapped.

        Returns
        -------
        bool
            False when successfully setup.

        """
        if len(self._wf_success._tasks) == 0:
            p_pred_tasks = None
        else:
            p_pred_tasks = [self._wf_success._tasks[-1]]

        self._wf_success.add_task(p_task = PseudoTask(p_wrap_method = self._run_wf_success),
                                  p_pred_tasks=p_pred_tasks)
        return True







## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class OAFctBroken(FctBroken, Model):
    """

    Parameters
    ----------
    p_name
    p_range_max
    p_class_shared
    p_visualize
    p_logging
    p_kwargs
    """


## -------------------------------------------------------------------------------------------------
    def __init__(self,
                 p_id = None,
                 p_name: str = None,
                 p_range_max: int = Async.C_RANGE_PROCESS,
                 p_autorun: int = Task.C_AUTORUN_NONE,
                 p_class_shared = None,
                 p_ada:bool=True,
                 p_afct_cls = None,
                 p_state_space: MSpace = None,
                 p_action_space: MSpace = None,
                 p_input_space_cls=ESpace,
                 p_output_space_cls=ESpace,
                 p_output_elem_cls=State,  # Specific output element type
                 p_threshold=0,
                 p_buffer_size=0,
                 p_wf_broken: OAWorkflow = None,
                 p_visualize:bool=False,
                 p_logging=Log.C_LOG_ALL,
                 **p_kwargs):

        self._afct_broken = None
        if p_afct_cls is not None:
            if (p_state_space is None) or (p_action_space is None):
                raise ParamError("Please provide mandatory parameters state and action space.")


            self._afct_broken = AFctSuccess(p_afct_cls=p_afct_cls,
                                            p_state_space=p_state_space,
                                            p_action_space=p_action_space,
                                            p_input_space_cls=p_input_space_cls,
                                            p_output_space_cls=p_output_space_cls,
                                            p_output_elem_cls=p_output_elem_cls,
                                            p_threshold=p_threshold,
                                            p_buffer_size=p_buffer_size,
                                            p_ada=p_ada,
                                            p_visualize=p_visualize,
                                            p_logging=p_logging,
                                            **p_kwargs)
        #
        # else:
        FctBroken.__init__(self, p_logging=p_logging)

        Model.__init__(self,
                       p_id= p_id,
                       p_name=p_name,
                       p_range_max=p_range_max,
                       p_autorun=p_autorun,
                       p_class_shared=p_class_shared,
                       p_ada=p_ada,
                       p_visualize=p_visualize,
                       p_logging=p_logging,
                       **p_kwargs)

        if p_wf_broken is None:
            self._wf_broken = OAWorkflow(p_visualize=p_visualize,
                                         p_ada=p_ada,
                                         p_logging=p_logging)
        else:
            self._wf_broken = p_wf_broken

        self._setup_wf_broken = False

## -------------------------------------------------------------------------------------------------
    def compute_broken(self, p_state: State) -> bool:
        """
        Assesses the given state regarding breakdown criteria. Custom method _compute_success() is called.

        Parameters
        ----------
        p_state : State
            System state.

        Returns
        -------
        broken : bool
            True, if given state is a breakdown state. False otherwise.
        """
        self._state_obj = p_state.copy()
        self.log(Log.C_LOG_TYPE_I, 'Assessing Broken...')


        if not self._setup_wf_broken:
            self._setup_wf_broken = self._setup_oafct_broken()

        # 6. Run the workflow
        self._wf_broken.run(p_inst_new=[self._state_obj])


        # 7. Return the results
        return self._wf_broken.get_so().get_results()[self.get_id()]


## -------------------------------------------------------------------------------------------------
    def add_task_broken(self, p_task: StreamTask, p_pred_tasks:list = None):
        """
        Adds a task to the workflow.

        Parameters
        ----------
        p_task: OATask, StreamTask
            The task to be added to the workflow

        p_pred_task: list[Task]
            Name of the predecessor tasks for the task to be added

        """
        self._wf_broken.add_task(p_task = p_task, p_pred_tasks = p_pred_tasks)


## -------------------------------------------------------------------------------------------------
    def _run_wf_broken(self, p_inst_new, p_inst_del):
        """
        Runs the success computation workflow of the system.

        Parameters
        ----------
        p_inst_new: list[State]
            List of new instances to be processed by the workflow.

        p_inst_del: list[State]
            List of old instances to be processed by the workflow.

        """
        if self._afct_broken is not None:
            self._wf_broken.get_so().add_result(self.get_id(), AFctBroken.compute_broken(self,
                                                                         p_state=p_inst_new[0]))
        else:
            self._wf_broken.get_so().add_result(self.get_id(), FctBroken.compute_broken(self,
                                                                         p_state=p_inst_new[0]))


## -------------------------------------------------------------------------------------------------
    def _adapt(self, **p_kwargs) -> bool:
        """

        Parameters
        ----------
        p_kwargs

        Returns
        -------

        """
        adapted = False
        try:
            adapted = self._wf_broken.adapt(**p_kwargs) or adapted
        except:
            adapted = False or adapted

        if self._afct_broken is not None:
            try:
                adapted = self._afct_broken.adapt(**p_kwargs) or adapted
            except:
                adapted = False or adapted

        return adapted


## -------------------------------------------------------------------------------------------------
    def _adapt_on_event(self, p_event_id:str, p_event_object:Event) -> bool:
        """

        Parameters
        ----------
        p_event_id
        p_event_object

        Returns
        -------

        """
        pass


## -------------------------------------------------------------------------------------------------
    def _setup_oafct_broken(self):
        """

        Returns
        -------

        """
        if len(self._wf_broken._tasks) == 0:
            p_pred_tasks = None
        else:
            p_pred_tasks = [self._wf_broken._tasks[-1]]
        self._wf_broken.add_task(p_task=PseudoTask(p_wrap_method = self._run_wf_broken),
                                 p_pred_tasks=p_pred_tasks)
        return True







## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class OASystem(OAFctBroken, OAFctSTrans, OAFctSuccess, ASystem):
    """

    Parameters
    ----------
    p_mode
    p_latency
    p_fct_strans
    p_fct_success
    p_fct_broken
    p_processing_wf
    p_visualize
    p_logging
    """


## -------------------------------------------------------------------------------------------------
    def __init__(self,
                 p_id=None,
                 p_name: str = None,
                 p_range_max: int = Range.C_RANGE_NONE,
                 p_autorun: int = Task.C_AUTORUN_NONE,
                 p_class_shared: Shared = None,
                 p_ada:bool = True,
                 p_mode = Mode.C_MODE_SIM,
                 p_latency = None,
                 p_t_step: timedelta = None,
                 p_fct_strans : FctSTrans = None,
                 p_fct_success : FctSuccess = None,
                 p_fct_broken : FctBroken = None,
                 p_wf : OAWorkflow = None,
                 p_wf_success : OAWorkflow = None,
                 p_wf_broken : OAWorkflow = None,
                 p_mujoco_file = None,
                 p_frame_skip: int = 1,
                 p_state_mapping = None,
                 p_action_mapping = None,
                 p_camera_conf: tuple = (None, None, None),
                 p_visualize: bool = False,
                 p_logging: bool = Log.C_LOG_ALL,
                 **p_kwargs):

        self._workflows = []
        self._fcts =[]

        OAFctSTrans.__init__(self, p_wf=p_wf)

        OAFctSuccess.__init__(self, p_wf=p_wf_success)

        OAFctBroken.__init__(self, p_wf_broken=p_wf_broken)

        self._workflows = [self._wf, self._wf_success, self._wf_broken]

        ASystem.__init__(self,
                         p_id = p_id,
                         p_name = p_name,
                         p_range_max = p_range_max,
                         p_autorun = p_autorun,
                         p_class_shared = p_class_shared,
                         p_mode = p_mode,
                         p_ada = p_ada,
                         p_latency = p_latency,
                         p_t_step = p_t_step,
                         p_fct_strans = p_fct_strans,
                         p_fct_success = p_fct_success,
                         p_fct_broken = p_fct_broken,
                         p_mujoco_file = p_mujoco_file,
                         p_frame_skip = p_frame_skip,
                         p_state_mapping = p_state_mapping,
                         p_action_mapping = p_action_mapping,
                         p_camera_conf = p_camera_conf,
                         p_visualize = p_visualize,
                         p_logging = p_logging,
                         **p_kwargs)



## -------------------------------------------------------------------------------------------------
    def _adapt(self, **p_kwargs) -> bool:
        """
        Adapts the system based on the parameters provided. Calls the adapt methods of all the adaptive
        elements of the system.

        Parameters
        ----------
        p_kwargs
            Additional parameters for the adaptation of the system.

        Returns
        -------
        bool
            True if any of the element has adapted.

        """

        adapted = False

        for workflow in self._workflows:
            try:
                adapted = workflow.adapt(**p_kwargs) or adapted
            except:
                pass

        for fct in self._fcts:
            try:
                adapted = fct.adapt(**p_kwargs) or adapted
            except:
                pass


        return adapted


## -------------------------------------------------------------------------------------------------
    def switch_adaptivity(self, p_ada:bool):
        """

        Parameters
        ----------
        p_ada

        Returns
        -------

        """
        for workflow in self._workflows:
            try:
                workflow.switch_adaptivity(p_ada=p_ada)
            except:
                pass

        for fct in self._fcts:
            try:
                fct.switch_adaptivity(p_ada = p_ada)
            except:
                pass

        Model.switch_adaptivity(self, p_ada=p_ada)

## -------------------------------------------------------------------------------------------------
    def _adapt_on_event(self, p_event_id:str, p_event_object:Event) -> bool:
        """

        Parameters
        ----------
        p_event_id
        p_event_object

        Returns
        -------

        """
        pass


## -------------------------------------------------------------------------------------------------
    def simulate_reaction(self, p_state: State, p_action: Action, p_t_step : timedelta = None) -> State:
        """
        Simulates a state transition based on a state and action. Custom method _simulate_reaction()
        is called.

        Parameters
        ----------
        p_state: State
            State of the System.

        p_action: Action
            External action provided for the action simulation

        p_t_step: timedelta, optional.
            The timestep for which the system is to be simulated

        Returns
        -------
        state: State
            The new state of the System.

        """

        if self._fct_strans is not None:
            return self._fct_strans.simulate_reaction(p_state, p_action, p_t_step)
        else:
            return OAFctSTrans.simulate_reaction(self, p_state, p_action, p_t_step)


## -------------------------------------------------------------------------------------------------
    def compute_success(self, p_state: State) -> bool:
        """
        Assesses the given state regarding success criteria. Custom method _compute_success() is called.

        Parameters
        ----------
        p_state : State
            System state.

        Returns
        -------
        success : bool
            True, if given state is a success state. False otherwise.

        """

        if self._fct_success is not None:
            return self._fct_success.compute_success(p_state)
        else:
            return OAFctSuccess.compute_success(self, p_state)


## -------------------------------------------------------------------------------------------------
    def compute_broken(self, p_state: State) -> bool:
        """
        Assesses the given state regarding breakdown criteria. Custom method _compute_success() is called.

        Parameters
        ----------
        p_state : State
            System state.

        Returns
        -------
        broken : bool
            True, if given state is a breakdown state. False otherwise.
        """
        if self._fct_broken is not None:
            return self._fct_broken.compute_broken(p_state)
        else:
            return OAFctBroken.compute_broken(self, p_state)