## -------------------------------------------------------------------------------------------------
## -- Project : MLPro - A Synoptic Framework for Standardized Machine Learning Tasks
## -- Package : mlpro.rl
## -- Module  : models_env.py
## -------------------------------------------------------------------------------------------------
## -- History :
## -- yyyy-mm-dd  Ver.      Auth.    Description
## -- 2022-11-29  1.0.0     DA       Creation due to refactoring of bf.systems and rl.models_env
## -- 2023-03-08  1.0.1     SY       Update EnvModel
## -- 2023-03-10  1.0.2     SY       Update AFctReward: _setup_spaces, _compute_reward, and _adapt
## -------------------------------------------------------------------------------------------------

"""
Ver. 1.0.2 (2023-03-10)

This module provides model classes for adaptive environment models.
"""

from mlpro.bf.ml import *
from mlpro.sl import SLAdaptiveFunction
from mlpro.rl.models_env import *




## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class AFctBase (Model):
    """
    Base class for all special adaptive functions (state transition, reward, success, broken). 

    Parameters
    ----------
    p_afct_cls 
        Adaptive function class (compatible to class mlpro.sl.SLAdaptiveFunction)
    p_state_space : MSpace
        State space of an environment or observation space of an agent
    p_action_space : MSpace
        Action space of an environment or agent
    p_input_space_cls
        Space class that is used for the generated input space of the embedded adaptive function (compatible to class
        MSpace)
    p_output_space_cls
        Space class that is used for the generated output space of the embedded adaptive function (compatible to class
        MSpace)
    p_output_elem_cls 
        Output element class (compatible to/inherited from class Element)
    p_threshold : float
        Threshold for the difference between a set point and a computed output. Computed outputs with
        a difference less than this threshold will be assessed as 'good' outputs. Default = 0.
    p_buffer_size : int
        Initial size of internal data buffer. Default = 0 (no buffering).
    p_ada : bool
        Boolean switch for adaptivity. Default = True.
    p_visualize : bool
        Boolean switch for visualisation. Default = False.
    p_logging
        Log level (see constants of class Log). Default: Log.C_LOG_ALL
    p_kwargs : Dict
        Further model specific parameters (to be specified in child class).

    Attributes
    ----------
    _state_space : MSpace
        State space
    _action_space : MSpace
        Action space
    _input_space : MSpace
        Input space of embedded adaptive function
    _output_space : MSpace
        Output space oof embedded adaptive function
    _afct : SLAdaptiveFunction
        Embedded adaptive function
    """

    C_TYPE = 'AFct Base'

## -------------------------------------------------------------------------------------------------
    def __init__( self,
                  p_afct_cls,
                  p_state_space : MSpace,
                  p_action_space : MSpace,
                  p_input_space_cls = ESpace,
                  p_output_space_cls = ESpace,
                  p_output_elem_cls = Element,
                  p_threshold = 0,
                  p_buffer_size = 0,
                  p_ada : bool = True,
                  p_visualize : bool = False,
                  p_logging = Log.C_LOG_ALL,
                  **p_kwargs ):

        self._state_space = p_state_space
        self._action_space = p_action_space
        self._input_space = p_input_space_cls()
        self._output_space = p_output_space_cls()

        self._setup_spaces(self._state_space, self._action_space, self._input_space, self._output_space)

        try:
            self._afct = p_afct_cls( p_input_space=self._input_space,
                                     p_output_space=self._output_space,
                                     p_output_elem_cls=p_output_elem_cls,
                                     p_threshold=p_threshold,
                                     p_buffer_size=p_buffer_size,
                                     p_ada=p_ada,
                                     p_visualize=p_visualize,
                                     p_logging=p_logging,
                                     **p_kwargs )
        except:
            raise ParamError('Class ' + str(p_afct_cls) + ' is not compatible to class mlpro.sl.SLAdaptiveFunction')

        super().__init__(p_buffer_size=0, p_ada=p_ada, p_logging=p_logging)


## -------------------------------------------------------------------------------------------------
    def _setup_spaces(self, p_state_space: MSpace, p_action_space: MSpace, p_input_space: MSpace,
                      p_output_space: MSpace):
        """
        Custom method to set up the input and output space of the embedded adaptive function. Use the
        method add_dimension() of the empty spaces p_input_space and p_output_space to enrich them
        with suitable dimensions.

        Parameters
        ----------
        p_state_space : MSpace
            State space of an environment respectively observation space of an agent.
        p_action_space : MSpace
            Action space of an environment or agent.
        p_input_space : MSpace
            Empty input space of embedded adaptive function to be enriched with dimension.
        p_output_space : MSpace
            Empty output space of embedded adaptive function to be enriched with dimension.

        """

        raise NotImplementedError


## -------------------------------------------------------------------------------------------------
    def get_afct(self) -> SLAdaptiveFunction:
        return self._afct


## -------------------------------------------------------------------------------------------------
    def get_state_space(self) -> MSpace:
        return self._state_space


## -------------------------------------------------------------------------------------------------
    def get_action_space(self) -> MSpace:
        return self._action_space


## -------------------------------------------------------------------------------------------------
    def _init_hyperparam(self, **p_par):
        pass


## -------------------------------------------------------------------------------------------------
    def get_hyperparam(self) -> HyperParamTuple:
        return self._afct.get_hyperparam()


## -------------------------------------------------------------------------------------------------
    def switch_adaptivity(self, p_ada: bool):
        super().switch_adaptivity(p_ada)
        self._afct.switch_adaptivity(p_ada)


## -------------------------------------------------------------------------------------------------
    def switch_logging(self, p_logging):
        super().switch_logging(p_logging)
        if self._afct is not None:
            self._afct.switch_logging(p_logging)


## -------------------------------------------------------------------------------------------------
    def set_random_seed(self, p_seed=None):
        self._afct.set_random_seed(p_seed=p_seed)


## -------------------------------------------------------------------------------------------------
    def get_adapted(self) -> bool:
        return self._afct.get_adapted()


## -------------------------------------------------------------------------------------------------
    def clear_buffer(self):
        self._afct.clear_buffer()


## -------------------------------------------------------------------------------------------------
    def get_accuracy(self):
        return self._afct.get_accuracy()


## -------------------------------------------------------------------------------------------------
    def init_plot( self, 
                   p_figure: Figure = None, 
                   p_plot_settings: list = [], 
                   p_plot_depth: int = 0, 
                   p_detail_level: int = 0, 
                   p_step_rate: int = 0, 
                   **p_kwargs ):

        self._afct.init_plot( p_figure=p_figure,
                              p_plot_settings=p_plot_settings,
                              p_plot_depth=p_plot_depth,
                              p_detail_level=p_detail_level,
                              p_step_rate=p_step_rate,
                              **p_kwargs )


## -------------------------------------------------------------------------------------------------
    def update_plot(self, **p_kwargs):
        self._afct.update_plot( **p_kwargs )





## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class AFctSTrans (AFctBase, FctSTrans):
    """
    Online adaptive version of a state transition function. See parent classes for further details.
    """

    C_TYPE = 'AFct STrans'

## -------------------------------------------------------------------------------------------------
    def __init__( self,
                  p_afct_cls,
                  p_state_space: MSpace,
                  p_action_space: MSpace,
                  p_input_space_cls=ESpace,
                  p_output_space_cls=ESpace,
                  p_output_elem_cls=State,  # Specific output element type
                  p_threshold=0,
                  p_buffer_size=0,
                  p_ada:bool=True,
                  p_visualize:bool=False,
                  p_logging=Log.C_LOG_ALL,
                  **p_par):

        super().__init__(p_afct_cls,
                         p_state_space,
                         p_action_space,
                         p_input_space_cls=p_input_space_cls,
                         p_output_space_cls=p_output_space_cls,
                         p_output_elem_cls=p_output_elem_cls,
                         p_threshold=p_threshold,
                         p_buffer_size=p_buffer_size,
                         p_ada=p_ada,
                         p_visualize=p_visualize,
                         p_logging=p_logging,
                         **p_par)


## -------------------------------------------------------------------------------------------------
    def _setup_spaces(self, p_state_space: MSpace, p_action_space: MSpace, p_input_space: MSpace,
                      p_output_space: MSpace):
        # 1 Setup input space
        p_input_space.append( p_set=p_state_space )
        p_input_space.append( p_set=p_action_space, p_ignore_duplicates=True)

        # 2 Setup output space
        p_output_space.append(p_state_space)


## -------------------------------------------------------------------------------------------------
    def _simulate_reaction(self, p_state: State, p_action: Action) -> State:
        # 1 Create input vector from given state and action
        input_values = p_state.get_values().copy()
        if isinstance(input_values, np.ndarray):
            input_values = np.append(input_values, p_action.get_sorted_values())
        else:
            input_values.extend(p_action.get_sorted_values())
        input = Element(self._input_space)
        input.set_values(input_values)

        # 2 Compute and return new state
        return self._afct.map(input)


## -------------------------------------------------------------------------------------------------
    def _adapt(self, p_state:State, p_action:Action, p_state_new:State) -> bool:
        """
        Triggers adaptation of the embedded adaptive function.

        Parameters
        ----------
        p_state : State
            State.
        p_action : Action
            Action
        p_state_new : State
            New state

        Returns
        -------
        bool
            True, if something was adapted. False otherwise.
        """

        input_values = p_state.get_values().copy()
        if isinstance(input_values, np.ndarray):
            input_values = np.append(input_values, p_action.get_sorted_values())
        else:
            input_values.extend(p_action.get_sorted_values())
        input = Element(self._input_space)
        input.set_values(input_values)

        return self._afct.adapt(p_input=input, p_output=p_state_new)





## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class AFctSuccess (AFctBase, FctSuccess):
    """
    Online adaptive version of a function that determine whether or not a state is a success state.
    See parent classes for further details.
    """

    C_TYPE = 'AFct Success'

## -------------------------------------------------------------------------------------------------
    def _setup_spaces(self, p_state_space: MSpace, p_action_space: MSpace, p_input_space: MSpace,
                      p_output_space: MSpace):

        # 1 Setup input space
        p_input_space.append(p_state_space)

        # 2 Setup output space
        p_output_space.add_dim(
            Dimension(p_name_short='Success', p_base_set=Dimension.C_BASE_SET_R, p_name_long='Success',
                      p_boundaries=[0, 1]))


## -------------------------------------------------------------------------------------------------
    def _compute_success(self, p_state: State) -> bool:
        output = self._afct.map(p_state)

        if output.get_values()[0] >= 0.5:
            return True
        return False


## -------------------------------------------------------------------------------------------------
    def _adapt(self, p_state:State) -> bool:
        output = Element(self._output_space)
        ids_ = output.get_dim_ids()
        if p_state.get_success():
            output.set_value(ids_[0], 1)
        else:
            output.set_value(ids_[0], 0)

        return self._afct.adapt(p_input=p_state, p_output=output)





## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class AFctBroken (AFctBase, FctBroken):
    """
    Online adaptive version of a function that determine whether or not a state is a broken state.
    See parent classes for further details.
    """

    C_TYPE = 'AFct Broken'

## -------------------------------------------------------------------------------------------------
    def _setup_spaces( self, 
                       p_state_space:MSpace, 
                       p_action_space:MSpace, 
                       p_input_space:MSpace,
                       p_output_space: MSpace ):

        # 1 Setup input space
        p_input_space.append(p_state_space)

        # 2 Setup output space
        p_output_space.add_dim(
            Dimension(p_name_short='Success', p_base_set=Dimension.C_BASE_SET_R, p_name_long='Success',
                      p_boundaries=[0, 1]))


## -------------------------------------------------------------------------------------------------
    def _compute_broken(self, p_state:State) -> bool:
        output = self._afct.map(p_state)

        if output.get_values()[0] >= 0.5:
            return True
        return False


## -------------------------------------------------------------------------------------------------
    def _adapt(self, p_state:State) -> bool:
        output = Element(self._output_space)
        ids_ = output.get_dim_ids()
        if p_state.get_success():
            output.set_value(ids_[0], 1)
        else:
            output.set_value(ids_[0], 0)

        return self._afct.adapt(p_input=p_state, p_output=output)





## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class AFctReward (AFctBase, FctReward):
    """
    Online adaptive version of a reward function. See parent classes for further details.
    """

    C_TYPE = 'AFct Reward'

## -------------------------------------------------------------------------------------------------
    def _setup_spaces(self, p_state_space: MSpace, p_action_space: MSpace, p_input_space: MSpace,
                      p_output_space: MSpace):
        # 1 Setup input space
        p_input_space.append(p_state_space)
        p_input_space.append(p_state_space, p_ignore_duplicates=True)

        # 2 Setup output space
        p_output_space.add_dim(
            Dimension(p_name_short='Rwd', p_base_set=Dimension.C_BASE_SET_R, p_name_long='Reward'))


## -------------------------------------------------------------------------------------------------
    def _compute_reward(self, p_state_old: State = None, p_state_new: State = None) -> Reward:
        if (p_state_old is None) or (p_state_new is None):
            raise ParamError('Both parameters p_state and p_state_new are needed to compute the reward')

        # 1 Create input vector from both states
        input_values = p_state_old.get_values().copy()
        if isinstance(input_values, np.ndarray):
            input_values = np.append(input_values, p_state_new.get_values())
        else:
            input_values.extend(p_state_new.get_values())
        input = Element(self._input_space)
        input.set_values(input_values)

        # 2 Compute and return reward
        output = self._afct.map(input)
        reward = output.get_values()[0]
        return Reward(p_type=Reward.C_TYPE_OVERALL, p_value=reward)


## -------------------------------------------------------------------------------------------------
    def _adapt(self, p_state:State, p_state_new:State, p_reward:Reward) -> bool:
        """
        Triggers adaptation of the embedded adaptive function.

        Parameters
        ----------
        p_state : State
            Previous state.
        p_state_new : State
            New state.
        p_reward : Reward
            Setpoint reward.

        Returns
        -------
        adapted: bool
            True, if something was adapted. False otherwise.
        """

        # 1 Create input vector from both states
        input_values = p_state.get_values().copy()
        if isinstance(input_values, np.ndarray):
            input_values = np.append(input_values, p_state_new.get_values())
        else:
            input_values.extend(p_state_new.get_values())
        input = Element(self._input_space)
        input.set_values(input_values)

        # 2 Create setpoint output vector
        output = Element(self._output_space)
        ids_ = output.get_dim_ids()
        output.set_value(ids_[0], p_reward.get_overall_reward())

        # 3 Trigger adaptation of embedded adaptive function
        return self._afct.adapt(p_input=input, p_output=output)




## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class SARSElement(BufferElement):
    """
    Element of a SARSBuffer.
    """

## -------------------------------------------------------------------------------------------------
    def __init__(self, p_state: State, p_action: Action, p_reward: Reward, p_state_new: State):
        """
        Parameters:
            p_state         State of an environment
            p_action        Action of an agent
            p_reward        Reward of an environment
            p_state_new     State of the environment as reaction to the action
        """

        super().__init__({"state": p_state, "action": p_action, "reward": p_reward, "state_new": p_state_new})





## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class SARSBuffer(Buffer):
    """
    State-Action-Reward-State-Buffer in dictionary.
    """

    pass





## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class EnvModel (EnvBase, Model):
    """
    Environment model class as part of a model-based agent.

    Parameters
    ----------
    p_observation_space : MSpace
        Observation space of related agent.
    p_action_space : MSpace
        Action space of related agent.
    p_latency : timedelta
        Latency of related environment.
    p_afct_strans : AFctSTrans
        Mandatory external adaptive function for state transition. 
    p_afct_reward : AFctReward
        Optional external adaptive function for reward computation.
    p_afct_success : AFctSuccess
        Optional external adaptive function for state assessment 'success'.
    p_afct_broken : AFctBroken
        Optional external adaptive function for state assessment 'broken'.
    p_ada : bool
        Boolean switch for adaptivity.
    p_init_states : State
        Initial state of the env models.
    p_visualize : bool
        Boolean switch for env/agent visualisation. Default = False.
    p_logging 
        Log level (see class Log for more details).
    """

    C_TYPE      = 'EnvModel'
    C_NAME      = 'Default'

## -------------------------------------------------------------------------------------------------
    def __init__(self,
                 p_observation_space : MSpace,
                 p_action_space : MSpace,
                 p_latency : timedelta,
                 p_afct_strans : AFctSTrans,
                 p_afct_reward : AFctReward = None,
                 p_afct_success : AFctSuccess = None,
                 p_afct_broken : AFctBroken = None,
                 p_ada : bool = True,
                 p_init_states : State = None,
                 p_visualize : bool = False,
                 p_logging = Log.C_LOG_ALL ):

        # 1 Intro
        EnvBase.__init__( self,
                          p_mode = self.C_MODE_SIM,
                          p_latency = p_latency,
                          p_fct_strans = p_afct_strans,
                          p_fct_reward = p_afct_reward,
                          p_fct_success = p_afct_success,
                          p_fct_broken = p_afct_broken,
                          p_visualize = p_visualize,
                          p_logging = p_logging )

        Model.__init__( self,
                        p_buffer_size = 0,
                        p_ada = p_ada,
                        p_visualize = p_visualize,
                        p_logging = p_logging )

        self._state_space  = p_observation_space
        self._action_space = p_action_space
        self._cycle_limit  = 0
        
        if p_init_states is None:
            raise NotImplementedError("p_init_states is missing!")
        else:
            self._init_states = p_init_states


        # 2 Check adaptive functions for compatibility with agent

        # 2.1 Check state transition function
        try:
            if self._fct_strans.get_state_space() != self._state_space:
                raise ParamError(
                    'Observation spaces of environment model and adaptive state transition function are not equal')
            if self._fct_strans.get_action_space() != self._action_space:
                raise ParamError(
                    'Action spaces of environment model and adaptive state transition function are not equal')
        except:
            raise ParamError('Adaptive state transition function is mandatory')

        # 2.2 Check reward function
        if (self._fct_reward is not None) and (self._fct_reward.get_state_space() != self._state_space):
            raise ParamError(
                'Observation spaces of environment model and adaptive function for reward computation are not equal')
        
        if isinstance(self._fct_reward, Environment):
            self._compute_reward = self._fct_reward._compute_reward

        # 2.3 Check function 'success'
        if (self._fct_success is not None) and (self._fct_success.get_state_space() != self._state_space):
            raise ParamError(
                'Observation spaces of environment model and adaptive function for assessment success are not equal')
        
        if isinstance(self._fct_success, Environment):
            self._compute_success = self._fct_success._compute_success
        
        # 2.4 Check function 'broken'
        if (self._fct_broken is not None) and (self._fct_broken.get_state_space() != self._state_space):
            raise ParamError(
                'Observation spaces of environment model and adaptive function for assessment broken are not equal')
        
        if isinstance(self._fct_broken, Environment):
            self._compute_broken = self._fct_broken._compute_broken


## -------------------------------------------------------------------------------------------------
    @staticmethod
    def setup_spaces():
        return None, None


## -------------------------------------------------------------------------------------------------
    def _init_hyperparam(self, **p_par):

        # 1 Create overall hyperparameter space of all adaptive components inside
        hyperparam_space_init = False
        try:
            self._hyperparam_space = self._fct_strans.get_hyperparam().get_related_set().copy(p_new_dim_ids=False)
            hyperparam_space_init = True
        except:
            pass
        
        try:
            if hyperparam_space_init:
                self._hyperparam_space.append(self._fct_reward.get_hyperparam().get_related_set(), p_new_dim_ids=False)
            else:
                self._hyperparam_space = self._fct_reward.get_hyperparam().get_related_set().copy(p_new_dim_ids=False)
                hyperparam_space_init = True
        except:
            pass
        
        try:
            if hyperparam_space_init:
                self._hyperparam_space.append(self._fct_success.get_hyperparam().get_related_set(), p_new_dim_ids=False)
            else:
                self._hyperparam_space = self._fct_success.get_hyperparam().get_related_set().copy(p_new_dim_ids=False)
                hyperparam_space_init = True
        except:
            pass
        
        try:
            if hyperparam_space_init:
                self._hyperparam_space.append(self._fct_broken.get_hyperparam().get_related_set(), p_new_dim_ids=False)
            else:
                self._hyperparam_space = self._fct_broken.get_hyperparam().get_related_set().copy(p_new_dim_ids=False)
                hyperparam_space_init = True
        except:
            pass
        
        # 2 Create overall hyperparameter (dispatcher) tuple
        self._hyperparam_tuple = HyperParamDispatcher(p_set=self._hyperparam_space)
        try:
            self._hyperparam_tuple.add_hp_tuple(self._fct_strans.get_hyperparam())
        except:
            pass
        
        try:
            self._hyperparam_tuple.add_hp_tuple(self._fct_reward.get_hyperparam())
        except:
            pass
        
        try:
            self._hyperparam_tuple.add_hp_tuple(self._fct_success.get_hyperparam())
        except:
            pass
        
        try:
            self._hyperparam_tuple.add_hp_tuple(self._fct_broken.get_hyperparam())
        except:
            pass
        
        
## -------------------------------------------------------------------------------------------------
    def _reset(self, p_seed=None):
        self.set_random_seed(p_seed=p_seed)
        self._state = self._init_states
        self._prev_state = None


## -------------------------------------------------------------------------------------------------
    def get_cycle_limit(self) -> int:
        """
        Returns limit of cycles per training episode.
        """

        return self._cycle_limit


## -------------------------------------------------------------------------------------------------
    def _process_action(self, p_action: Action) -> bool:

        # 1 State transition
        self._set_state(self.simulate_reaction(self.get_state(), p_action))

        # 2 State evaluation
        state = self.get_state()
        state.set_success(self.compute_success(state))
        state.set_broken(self.compute_broken(state))

        return True


## -------------------------------------------------------------------------------------------------
    def switch_adaptivity(self, p_ada: bool):
        Model.switch_adaptivity(self, p_ada)

        self._fct_strans.switch_adaptivity(p_ada)

        try:
            if self._fct_reward is not None:
                self._fct_reward.switch_adaptivity(p_ada)
        except:
            pass

        try:
            if self._fct_success is not None:
                self._fct_success.switch_adaptivity(p_ada)
        except:
            pass

        try:
            if self._fct_broken is not None:
                self._fct_broken.switch_adaptivity(p_ada)
        except:
            pass


## -------------------------------------------------------------------------------------------------
    def adapt(self, **p_kwargs) -> bool:
        """
        Reactivated adaptation mechanism. See method Model.adapt() for further details.
        """

        return Model.adapt(self, **p_kwargs)


## -------------------------------------------------------------------------------------------------
    def _adapt(self, p_sars_elem:SARSElement ) -> bool:
        """
        Adapts the environment model based on State-Action-Reward-State (SARS) data.

        Parameters
        ----------
        p_sars_elem : SARSElement
            Object of type SARSElement.
        """

        try:
            sars_dict = p_sars_elem.get_data()
            state = sars_dict['state']
            action = sars_dict['action']
            reward = sars_dict['reward']
            state_new = sars_dict['state_new']
        except:
            raise ParamError('Parameter must be of type SARSElement')

        adapted = self._fct_strans.adapt(p_state=state, p_action=action, p_state_new=state_new)

        if ( self._fct_reward is not None ) and ( not isinstance(self._fct_reward, Environment) ):
            adapted = adapted or self._fct_reward.adapt(p_state=state, p_state_new=state_new, p_reward=reward)

        if self._fct_success is not None and ( not isinstance(self._fct_success, Environment) ):
            adapted = adapted or self._fct_success.adapt(p_state=state_new)

        if self._fct_broken is not None and ( not isinstance(self._fct_broken, Environment) ):
            adapted = adapted or self._fct_broken.adapt(p_state=state_new)

        if (self._cycle_limit == 0) and state_new.get_timeout():
            # First timeout state defines the cycle limit
            self._cycle_limit = self._num_cycles

        return adapted


## -------------------------------------------------------------------------------------------------
    def get_adapted(self) -> bool:
        return Model.get_adapted(self)


## -------------------------------------------------------------------------------------------------
    def get_accuracy(self):
        """
        Returns accuracy of environment model as average accuracy of the embedded adaptive functions.
        """

        accuracy = self._fct_strans.get_accuracy()
        num_afct = 1

        try:
            if self._fct_reward is not None:
                accuracy += self._fct_reward.get_accuracy()
                num_afct += 1
        except:
            pass

        try:
            if self._fct_success is not None:
                accuracy += self._fct_success.get_accuracy()
                num_afct += 1
        except:
            pass

        try:
            if self._fct_broken is not None:
                accuracy += self._fct_broken.get_accuracy()
                num_afct += 1
        except:
            pass

        return accuracy / num_afct


## -------------------------------------------------------------------------------------------------
    def clear_buffer(self):
        self._fct_strans.clear_buffer()
        if ( self._fct_reward is not None ) and ( not isinstance(self._fct_reward, Environment) ):
            self._fct_reward.clear_buffer()
        if self._fct_success is not None and ( not isinstance(self._fct_success, Environment) ):
            self._fct_success.clear_buffer()
        if self._fct_broken is not None and ( not isinstance(self._fct_broken, Environment) ):
            self._fct_broken.clear_buffer()
