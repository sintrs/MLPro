## -------------------------------------------------------------------------------------------------
## -- Project : MLPro - A Synoptic Framework for Standardized Machine Learning Tasks
## -- Package : mlpro.rl.envs
## -- Module  : doublependulum.py
## -------------------------------------------------------------------------------------------------
## -- History :
## -- yyyy-mm-dd  Ver.      Auth.    Description
## -- 2022-01-25  0.0.0     WB       Creation
## -- 2022-01-26  0.9.0     WB       Initial trial of the environment
## -- 2022-01-27  0.9.1     WB       Trial without animation 
## -- 2022-01-28  0.9.2     WB       Fix the  update_plot method
## -- 2022-01-31  0.9.3     WB       Taking account of the new state in _compute_reward method 
## -- 2022-01-31  0.9.4     WB       Add Circular arrow to the plot 
## -- 2022-02-02  1.0.0     WB       Release of first version 
## -------------------------------------------------------------------------------------------------

"""
Ver. 1.0.0 (2022-02-02)

This module provides an RL environment of double pendulum.
"""


from mlpro.rl.models import *
from mlpro.bf.various import *
import numpy as np
from numpy import sin, cos
import random
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, RegularPolygon
import scipy.integrate as integrate
from collections import deque



## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class DoublePendulum (Environment):
    """
    This is the main class of the Double Pendulum environment that inherits 
    Environment class from MLPro.
    
    Parameters
    ----------
    p_logging : Log, optional
        logging functionalities. The default is Log.C_LOG_ALL.
    t_step : float, optional
        time for each time step (in seconds). The default is 0.01.
    t_act : int, optional
        action frequency (with respect to the time step). The default is 20.
    max_torque : float, optional
        maximum torque applied to pendulum 1. The default is 20.
    max_speed : float, optional
        maximum speed applied to pendulum 1. The default is 10.
    l1 : float, optional
        length of pendulum 1 in m. The default is 0.5
    l2 : float, optional
        length of pendulum 2 in m. The default is 0.5
    m1 : float, optional
        mass of pendulum 1 in kg. The default is 0.5
    m2 : float, optional
        mass of pendulum 2 in kg. The default is 0.5
    th1 : float, optional 
        initial angle of pendulum 1 in degrees. The default is 0.0
    th1dot : float, optional 
        initial angular velocities of pendulum 1 in degrees per second. The default is 0.0
    th2 : float, optional 
        initial angle of pendulum 2 in degrees. The default is 0.0
    th2dot : float, optional 
        initial angular velocities of pendulum 2 in degrees per second. The default is 0.0
    g : float, optional
        gravitational acceleration. The default is 9.8
    history_length : int, optional
        historical trajectory points to display. The default is 2.
        
    Attributes
    ----------
    C_NAME : str
        name of the environment.
    C_CYCLE_LIMIT : int
        the number of cycle limit.
    C_LATENCY : timedelta()
        latency.
    C_REWARD_TYPE : Reward
        rewarding type.
    """
    C_NAME              = "DoublePendulum"
    C_CYCLE_LIMIT       = 0
    C_LATENCY           = timedelta(0,0,0)    
    C_REWARD_TYPE       = Reward.C_TYPE_OVERALL
    
    
## -------------------------------------------------------------------------------------------------
    def __init__(self, p_logging=Log.C_LOG_ALL, t_step=0.01, t_act=20, max_torque=20,
                max_speed=10, l1=0.5, l2=0.5, m1=0.5, m2=0.5, th1=0.0, th2=0.0, 
                th1dot=0.0, th2dot=0.0, g=9.8, history_length=3):
        self.t_step = t_step
        self.t_act  = t_act
        
        self.set_latency(timedelta(0,t_act*t_step,0))
        
        self.max_torque = max_torque
        self.max_speed  = max_speed
        
        self.l1     = l1
        self.l2     = l2
        self.L      = l1+l2
        self.m1     = m1
        self.m2     = m2
        self.th1    = th1
        self.th2    = th2
        self.th1dot = th1dot
        self.th2dot = th2dot
        self.g      = g
        
        self.history_x = deque(maxlen=history_length)
        self.history_y = deque(maxlen=history_length)
        
        super().__init__(p_mode=Environment.C_MODE_SIM, p_logging=p_logging)
        
        self.C_SCIREF_TYPE    = self.C_SCIREF_TYPE_ONLINE
        self.C_SCIREF_AUTHOR  = "John Hunter, Darren Dale, Eric Firing, Michael \
                                Droettboom and the Matplotlib development team"
        self.C_SCIREF_TITLE   = "The Double Pendulum Problem"
        self.C_SCIREF_URL     = "https://matplotlib.org/stable/gallery/animation/double_pendulum.html"
        
        self._state = State(self._state_space)
        
        self.reset()  


## -------------------------------------------------------------------------------------------------
    def setup_spaces(self):
        """
        This method is used to setup action and state spaces of the system.

        Returns
        -------
        state_space : ESpace()
            state space of the system.
        action_space : ESpace()
            action space of the system.

        """
        state_space     = ESpace()
        action_space    = ESpace()
        
        state_space.add_dim(Dimension(0, 'theta 1', 'th1', 'Angle of Pendulum 1', '', 'degrees', 
                            '\textdegrees',[-np.pi, np.pi]))
        state_space.add_dim(Dimension(1, 'omega 1', 'w1', 'Angular Velocity of Pendulum 1', '', 
                            'degrees/second', '\textdegrees/s',[-np.inf, np.inf]))
        state_space.add_dim(Dimension(2, 'theta 2', 'th2', 'Angle of pendulum 2', '', 'degrees', 
                            '\textdegrees',[-np.pi, np.pi]))
        state_space.add_dim(Dimension(3, 'omega 2', 'w2', 'Angular Velocity of Pendulum 2', '', 
                            'degrees/second', '\textdegrees/s',[-np.inf, np.inf]))
        
        action_space.add_dim(Dimension(0, 'torque 1', 'tau1', 'Applied Torque of Motor 1', '', 
                            'Nm', 'Nm', [-self.max_torque, self.max_torque]))

        return state_space, action_space
        

## -------------------------------------------------------------------------------------------------
    def derivs(self, state, t):
        """
        This method is used to calculate the derrivatives of the system, given the 
        current states.

        Parameters
        ----------
        state : list
            [th, th1dot, th2, th2dot]

        Returns
        -------
        dydx : list
            The derrivatives of the given state

        """
        dydx = np.zeros_like(state)
        dydx[0] = state[1]

        delta = state[2] - state[0]
        den1 = (self.m1+self.m2) * self.l1 - self.m2 * self.l1 * cos(delta) * cos(delta)
        dydx[1] = ((self.m2 * self.l1 * state[1] * state[1] * sin(delta) * cos(delta)
                    + self.m2 * self.g * sin(state[2]) * cos(delta)
                    + self.m2 * self.l2 * state[3] * state[3] * sin(delta)
                    - (self.m1+self.m2) * self.g * sin(state[0]))
                   / den1)

        dydx[2] = state[3]

        den2 = (self.l2/self.l1) * den1
        dydx[3] = ((- self.m2 * self.l2 * state[3] * state[3] * sin(delta) * cos(delta)
                    + (self.m1+self.m2) * self.g * sin(state[0]) * cos(delta)
                    - (self.m1+self.m2) * self.l1 * state[1] * state[1] * sin(delta)
                    - (self.m1+self.m2) * self.g * sin(state[2]))
                   / den2)

        return dydx
        

## -------------------------------------------------------------------------------------------------
    @staticmethod
    def angle_normalize(x):
        """
        This method is called to ensure a normalized angle in radians.

        Returns
        -------
        angle : float
            Normalized angle.

        """
        return ((x + np.pi) % (2 * np.pi)) - np.pi
        

## -------------------------------------------------------------------------------------------------
    def _reset(self, p_seed=None) -> None:
        """
        This method is used to reset the environment.

        Parameters
        ----------
        p_seed : int, optional
            Not yet implemented. The default is None.

        """
        self._state.set_value(0, np.radians(self.th1))
        self._state.set_value(1, np.radians(self.th1dot))
        self._state.set_value(2, np.radians(self.th2))
        self._state.set_value(3, np.radians(self.th2dot))
        
        self.history_x.clear()
        self.history_y.clear()
        self.action_cw = False


## -------------------------------------------------------------------------------------------------
    def _simulate_reaction(self, p_state:State, p_action:Action) -> State:
        """
        This method is used to calculate the next states of the system after a set of actions.

        Parameters
        ----------
        p_state : State
            State.
        p_action : Action
            ACtion.

        Returns
        -------
        _state : State
            current states.

        """
        state = p_state.get_values()
        th1, th1dot, th2, th2dot = state
        torque = p_action.get_sorted_values()[0]
        torque = np.clip(torque, -self.max_torque, self.max_torque)
        
        state[1] = th1dot + (3 * self.g / (2 * self.l1) * sin(th1) + 3.0 / 
                (self.m1 * self.l1 ** 2) * torque) * self.t_step
                
        if abs(th1dot) > self.max_speed:
            state[1] = np.clip(state[1], -th1dot, th1dot)
        else:
            state[1] = np.clip(state[1], -self.max_speed, self.max_speed)
        
        self.y = integrate.odeint(self.derivs, state, np.arange(0, self.t_act*self.t_step, self.t_step))
        state = self.y[-1]
        
        self.action_cw = True if torque >= 0 else False
        for i in range(len(state)):
            self._state.set_value(i, state[i])
        
        return self._state


## -------------------------------------------------------------------------------------------------
    def _compute_broken(self, p_state:State) -> bool:
        """
        This method computes the broken flag. This method can be redefined.

        Parameters
        ----------
        p_state : State
            state.

        Returns
        -------
        bool
            broken or not.

        """ 

        return False


## -------------------------------------------------------------------------------------------------
    def _compute_success(self, p_state:State) -> bool:
        """
        This method computes the success flag. This method can be redefined.

        Parameters
        ----------
        p_state : State
            state.

        Returns
        -------
        bool
            success or not success.

        """
        
        return False
    

## -------------------------------------------------------------------------------------------------
    def _compute_reward(self, p_state_old:State, p_state_new:State) -> Reward:
        """
        This method calculates the reward for C_TYPE_OVERALL reward type.

        Parameters
        ----------
        p_state_old : State
            previous state.
        p_state_new : State
            new state.

        Returns
        -------
        reward : Reward
            reward values.

        """
        reward = Reward(Reward.C_TYPE_OVERALL)
        
        state = p_state_new.get_values()
        
        count = 0
        for th1 in self.y[:,0]:
            if np.degrees(th1) > 179 or np.degrees(th1) < 181 or \
                np.degrees(th1) < -179 or np.degrees(th1) > -181:
                count += 1
        
        speed_costs = np.pi * abs(state[1]) / self.max_speed
        reward.set_overall_reward((abs(state[0])-speed_costs) * count/len(self.y))
        
        return reward
    

## -------------------------------------------------------------------------------------------------
    def init_plot(self, p_figure=None):
        """
        This method initializes the plot figure of each episodes. When the environment
        is reset, the previous figure is closed and reinitialized. 
        
        Parameters
        ----------
        p_figure : matplotlib.figure.Figure
            A Figure object of the matplotlib library.
        """
        if hasattr(self, 'fig'):
            plt.close(self.fig)
        
        if p_figure==None:
            self.fig = plt.figure(figsize=(5,4)) 
            self.embedded_fig = False
        else:
            self.fig = p_figure
            self.embedded_fig = True
            
        self.ax = self.fig.add_subplot(autoscale_on=False, 
                    xlim=(-self.L*1.2, self.L*1.2), ylim=(-self.L*1.2, self.L*1.2))
        self.ax.set_aspect('equal')
        self.ax.grid()
        
        self.cw_arc = Arc([0,0], 0.5*self.l1, 0.5*self.l1, angle=0, theta1=0, 
                            theta2=250, color='crimson')
        endX = (0.5*self.l1/2) * np.cos(np.radians(250))
        endY = (0.5*self.l1/2) * np.sin(np.radians(250))
        self.cw_arrow = RegularPolygon((endX, endY), 3, 0.5*self.l1/9, np.radians(250), 
                                        color='crimson')
        
        self.ccw_arc = Arc([0,0], 0.5*self.l1, 0.5*self.l1, angle=70, theta1=0, 
                            theta2=320, color='crimson')
        endX = (0.5*self.l1/2) * np.cos(np.radians(70+320))
        endY = (0.5*self.l1/2) * np.sin(np.radians(70+320))
        self.ccw_arrow = RegularPolygon((endX, endY), 3, 0.5*self.l1/9, np.radians(70+320), 
                                        color='crimson')
                                        
        self.ax.add_patch(self.cw_arc)
        self.ax.add_patch(self.cw_arrow)
        self.ax.add_patch(self.ccw_arc)
        self.ax.add_patch(self.ccw_arrow)
        
        self.cw_arc.set_visible(False)
        self.cw_arrow.set_visible(False)
        self.ccw_arc.set_visible(False)
        self.ccw_arrow.set_visible(False)
        
        self.line, = self.ax.plot([], [], 'o-', lw=2)
        self.trace, = self.ax.plot([], [], '.-', lw=1, ms=2)


## -------------------------------------------------------------------------------------------------
    def update_plot(self):
        """
        This method updates the plot figure of each episodes. When the figure is 
        detected to be an embedded figure, this method will only set up the 
        necessary data of the figure.
        
        """
        x1 = self.l1*sin(self.y[:, 0])
        y1 = -self.l1*cos(self.y[:, 0])

        x2 = self.l2*sin(self.y[:, 2]) + x1
        y2 = -self.l2*cos(self.y[:, 2]) + y1

        thisx = [0, x1[-1], x2[-1]]
        thisy = [0, y1[-1], y2[-1]]            
        self.history_x.appendleft(thisx[2])
        self.history_y.appendleft(thisy[2])
        self.line.set_data(thisx, thisy)
        self.trace.set_data(self.history_x, self.history_y)
        
        if self.action_cw:
            self.cw_arc.set_visible(True)
            self.cw_arrow.set_visible(True)
            self.ccw_arc.set_visible(False)
            self.ccw_arrow.set_visible(False)
        else:
            self.cw_arc.set_visible(False)
            self.cw_arrow.set_visible(False)
            self.ccw_arc.set_visible(True)
            self.ccw_arrow.set_visible(True)
        
        if not self.embedded_fig:
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()