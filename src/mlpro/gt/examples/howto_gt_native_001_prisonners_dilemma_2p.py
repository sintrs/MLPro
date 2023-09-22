## -------------------------------------------------------------------------------------------------
## -- Project : MLPro - A Synoptic Framework for Standardized Machine Learning Tasks
## -- Package : mlpro.gt.examples
## -- Module  : howto_gt_native_001_prisonners_dilemma_2p.py
## -------------------------------------------------------------------------------------------------
## -- History :
## -- yyyy-mm-dd  Ver.      Auth.    Description
## -- 2023-09-22  0.0.0     SY       Creation
## -- 2023-09-22  1.0.0     SY       Release of first version
## -------------------------------------------------------------------------------------------------

"""
Ver. 1.0.0 (2023-09-22)

This module shows how to run a game, namely 2P Prisoners' Dilemma.

You will learn:
    
1) How to set up a game, including solver, competition, coalition, payoff, and more
    
2) How to run the game

3) How to analyse the game
    
"""

from mlpro.gt.native.basics import *
from mlpro.gt.pool.native.games.prisonersdilemma_2p import *
from pathlib import Path




if __name__ == "__main__":
    cycle_limit = 1
    logging     = Log.C_LOG_WE
    visualize   = False
    path        = str(Path.home())
 
else:
    cycle_limit = 1
    logging     = Log.C_LOG_NOTHING
    visualize   = False
    path        = None

PD2P_Game = PrisonersDilemma2PGame()

training = GTTraining(
        p_game_cls=PrisonersDilemma2PGame,
        p_cycle_limit=cycle_limit,
        p_path=path,
        p_visualize=visualize,
        p_logging=logging
        )

training.run()