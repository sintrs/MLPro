## -------------------------------------------------------------------------------------------------
## -- Project : MLPro - A Synoptic Framework for Standardized Machine Learning Tasks
## -- Package : mlpro.rl.pool.envs.mujoco
## -- Module  : doublependulum.py
## -------------------------------------------------------------------------------------------------
## -- History :
## -- yyyy-mm-dd  Ver.      Auth.    Description
## -- 2022-09-19  0.0.0     MRD       Creation
## -- 2022-12-11  0.0.1     MRD       Refactor due to new bf.Systems
## -------------------------------------------------------------------------------------------------


import numpy as np

from mlpro.rl.models import *
from mlpro.wrappers.mujoco import WrEnvMujoco




## ---------------------------------------------------------------------------------------------------------------------
## ---------------------------------------------------------------------------------------------------------------------
class DoublePendulum(WrEnvMujoco, FctReward):
    def __init__(self, p_frame_skip=1, p_logging=False):
        p_model_path = None
        p_model_file = "doublependulum.xml"
        super().__init__(p_model_file, p_frame_skip=p_frame_skip, p_model_path=p_model_path, p_logging=p_logging)

        self._state = State(self._state_space)

        self.get_cycle_limit = Environment.get_cycle_limit

        self.reset()


## ------------------------------------------------------------------------------------------------------
    def setup_spaces(self):
        """
        Method to setup the spaces for the Double Pendulum root environment. This method sets up four dimensional
        Euclidean space for the root DP environment.
        """

        state_space = ESpace()
        action_space = ESpace()

        state_space.add_dim(
            Dimension(p_name_long='theta 1', p_name_short='th1', p_description='Angle of Pendulum 1', p_name_latex='',
                    p_unit='radian', p_unit_latex='\textdegrees'))
        state_space.add_dim(
            Dimension(p_name_long='theta 2', p_name_short='th2', p_description='Angle of pendulum 2', p_name_latex='',
                    p_unit='radian', p_unit_latex='\textdegrees'))
        state_space.add_dim(
            Dimension(p_name_long='omega 1', p_name_short='w1', p_description='Angular Velocity of Pendulum 1',
                    p_name_latex='', p_unit='radian/second', p_unit_latex='\textdegrees/s'))
        state_space.add_dim(
            Dimension(p_name_long='omega 2', p_name_short='w2', p_description='Angular Velocity of Pendulum 2',
                    p_name_latex='', p_unit='radian/second', p_unit_latex='\textdegrees/s'))

        action_space.add_dim(
            Dimension(p_name_long='torque', p_name_short='tau', p_description='Torque Joint 1',
                    p_name_latex='', p_unit='radian/second', p_unit_latex='\textdegrees/s', p_boundaries=[-1, 1])
                    )
        

        return state_space, action_space


## ------------------------------------------------------------------------------------------------------
    def _reset_model(self):
        qpos = self._init_qpos + np.random.uniform(
            size=self._model.nq, low=-0.01, high=0.01
        )
        qvel = self._init_qpos + np.random.uniform(
            size=self._model.nv, low=-0.01, high=0.01
        )
        self.set_state(qpos, qvel)
        return self._get_obs()


## ------------------------------------------------------------------------------------------------------
    def _get_obs(self):
        return np.concatenate([self._data.qpos, self._data.qvel]).ravel()


## ------------------------------------------------------------------------------------------------------
    def _compute_reward(self, p_state: State, p_state_new: State) -> Reward:
        current_reward = Reward()
        current_reward.set_overall_reward(1)
        return current_reward


## ------------------------------------------------------------------------------------------------------
    def _compute_broken(self, p_state: State) -> bool:
        """
        Custom method to compute broken state. In this case always returns false as the environment doesn't break
        """

        return False


## ------------------------------------------------------------------------------------------------------
    def _compute_success(self, p_state:State):
        """
        Custom method to return the success state of the environment based on the distance between current state,
        goal state and the goal threshold parameter

        Parameters
        ----------
        p_state:State
            current state of the environment

        Returns
        -------
        bool
            True if the distance between current state and goal state is less than the goal threshold else false
        """

        return False


## ------------------------------------------------------------------------------------------------------
    def init_plot(self, p_figure=None):
        pass


## ------------------------------------------------------------------------------------------------------
    def update_plot(self):
        return super().update_plot()
