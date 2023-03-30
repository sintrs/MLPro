## -------------------------------------------------------------------------------------------------
## -- Project : MLPro - A Synoptic Framework for Standardized Machine Learning Tasks
## -- Package : mlpro.gt
## -- Module  : basics.py
## -------------------------------------------------------------------------------------------------
## -- History :
## -- yyyy-mm-dd  Ver.      Auth.    Description
## -- 2023-03-30  0.0.0     SY       Creation
## -- 2023-??-??  1.0.0     SY       Release of first version
## -------------------------------------------------------------------------------------------------

"""
Ver. 1.0.0 (2023-03-30)

This module provides model classes for tasks related to a Native Game Theory.
"""


from mlpro.bf.various import TStamp, Log, Saveable
from mlpro.bf.systems import Action
from mlpro.bf.ml import Model, Scenario



## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class GTGame (Scenario):


## -------------------------------------------------------------------------------------------------
    def __init__(self):
        pass



## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class GTPayoffMatrix (TStamp):


## -------------------------------------------------------------------------------------------------
    def __init__(self):
        pass



## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class GTStrategy (Action):


## -------------------------------------------------------------------------------------------------
    def __init__(self):
        pass



## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class GTSolver (Model):


## -------------------------------------------------------------------------------------------------
    def __init__(self):
        pass



## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class GTPlayer (GTSolver):


## -------------------------------------------------------------------------------------------------
    def __init__(self):
        pass



## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class GTMultiPlayer (GTPlayer):


## -------------------------------------------------------------------------------------------------
    def __init__(self):
        pass



## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class GTEvaluation (Log, Saveable):


## -------------------------------------------------------------------------------------------------
    def __init__(self):
        pass