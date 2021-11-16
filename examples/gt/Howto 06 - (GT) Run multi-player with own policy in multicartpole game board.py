## -------------------------------------------------------------------------------------------------
## -- Project : FH-SWF Automation Technology - Common Code Base (CCB)
## -- Package : mlpro
## -- Module  : Howto 06 - (GT) Run own multi-player with multicartpole environment
## -------------------------------------------------------------------------------------------------
## -- History :
## -- yyyy-mm-dd  Ver.      Auth.    Description
## -- 2021-06-06  0.0.0     DA       Creation
## -- 2021-06-06  1.0.0     DA       Release of first version
## -- 2021-08-28  1.0.1     DA       Adjustments after changings on rl models
## -- 2021-09-11  1.0.1     MRD      Change Header information to match our new library name
## -- 2021-10-06  1.0.2     DA       Adjustments after changings on rl models
## -- 2021-11-15  1.1.0     DA       Refactoring 
## -------------------------------------------------------------------------------------------------

"""
Ver. 1.1.0 (2021-11-15)

This module shows how to run an own multi-player with the enhanced multi-action game board 
MultiCartPole based on the OpenAI Gym CartPole environment.
"""


from mlpro.rl.models import *
from mlpro.gt.models import *
from mlpro.gt.pool.boards.multicartpole import MultiCartPolePGT
import random
import numpy as np





# 1 Implement your own agent policy
class MyPolicy (Policy):

    C_NAME      = 'MyPolicy'

    def set_random_seed(self, p_seed=None):
        random.seed(p_seed)


    def compute_action(self, p_state: State) -> Action:
        # 1 Create a numpy array for your action values 
        my_action_values = np.zeros(self._action_space.get_num_dim())

        # 2 Computing action values is up to you...
        for d in range(self._action_space.get_num_dim()):
            my_action_values[d] = random.random() 

        # 3 Return an action object with your values
        return Action(self._id, self._action_space, my_action_values)


    def _adapt(self, *p_args) -> bool:
        # 1 Adapting the internal policy is up to you...
        self.log(self.C_LOG_TYPE_W, 'Sorry, I am a stupid agent...')

        # 2 Only return True if something has been adapted...
        return False




# 2 Implement your own game
class MyGame (Game):

    C_NAME      = 'Matrix'

    def _setup(self, p_mode, p_ada, p_logging):

        # 1 Setup Multi-Player Environment (consisting of 3 OpenAI Gym Cartpole envs)
        self._env   = MultiCartPolePGT(p_num_envs=3, p_logging=p_logging)


        # 2 Setup Multi-Player

        # 2.1 Create empty Multi-Player
        multi_player = MultiPlayer(
            p_name='Human Beings',
            p_ada=True,
            p_logging=p_logging
        )

        # 2.2 Add Single-Player #1 with own policy (controlling sub-environment #1)
        multi_player.add_player(
            p_player=Player(
                p_policy=MyPolicy(
                    p_observation_space=self._env.get_state_space().spawn([0,1,2,3]),
                    p_action_space=self._env.get_action_space().spawn([0]),
                    p_ada=True,
                    p_logging=p_logging
                ),
                p_name='Neo',
                p_id=0,
                p_ada=True,
                p_logging=p_logging
            ),
            p_weight=0.3
        )


        # 2.3 Add Single-Player #2 with own policy (controlling sub-environments #2,#3)
        multi_player.add_player(
            p_player=Player(
                p_policy=MyPolicy(
                    p_observation_space=self._env.get_state_space().spawn([4,5,6,7,8,9,10,11]),
                    p_action_space=self._env.get_action_space().spawn([1,2]),
                    p_ada=True,
                    p_logging=p_logging
                ),
                p_name='Trinity',
                p_id=1,
                p_ada=True,
                p_logging=p_logging
            ),
            p_weight=0.7
        )

        # 2.4 Adaptive ML model (here: our multi-player) is returned
        return multi_player




# 3 Create game and run some cycles

if __name__ == "__main__":
    # 3.1 Parameters for demo mode
    logging     = Log.C_LOG_ALL
    visualize   = True
  
else:
    # 3.2 Parameters for internal unit test
    logging     = Log.C_LOG_NOTHING
    visualize   = False


mygame  = MyGame(
    p_mode=Mode.C_MODE_SIM,
    p_ada=True,
    p_cycle_limit=200,
    p_visualize=visualize,
    p_logging=logging
)

mygame.run()