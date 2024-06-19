## -------------------------------------------------------------------------------------------------
## -- Project : MLPro - The integrative middleware framework for standardized machine learning
## -- Package : mlpro.oa.tasks.anomalydetectors.anomalies.clusterbased
## -- Module  : disappearance.py
## -------------------------------------------------------------------------------------------------
## -- History :
## -- yyyy-mm-dd  Ver.      Auth.    Description
## -- 2023-06-08  0.0.0     SK       Creation
## -- 2023-09-12  1.0.0     SK       Release
## -- 2023-11-21  1.0.1     SK       Time Stamp update
## -- 2024-02-25  1.1.0     SK       Visualisation update
## -- 2024-04-10  1.2.0     DA/SK    Refactoring
## -- 2024-05-22  1.2.1     SK       Refactoring
## -- 2024-05-28  1.2.2     SK       Refactoring
## -------------------------------------------------------------------------------------------------

"""
Ver. 1.2.2 (2024-05-28)

This module provides templates for anomaly detection to be used in the context of online adaptivity.
"""

from mlpro.oa.streams.basics import Instance
from mlpro.bf.mt import Figure, PlotSettings
from mlpro.bf.various import *
from mlpro.bf.plot import *
from mlpro.oa.streams.tasks.clusteranalyzers.clusters.basics import Cluster
from mlpro.oa.streams.tasks.anomalydetectors.anomalies.clusterbased.basics import CBAnomaly





## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class ClusterDisappearance (CBAnomaly):
    """
    Event class to be raised when a cluster disappears.
    
    """

    C_NAME      = 'Cluster disappearance'

## -------------------------------------------------------------------------------------------------
    def __init__(self,
                 p_id : int = 0,
                 p_instances : list[Instance] = None,
                 p__clusters : dict[Cluster] = None,
                 p_ano_scores : list = None,
                 p_visualize : bool = False,
                 p_raising_object : object = None,
                 p_det_time : str = None,
                 **p_kwargs):
        
        super().__init__(p_id=p_id,
                         p_instances=p_instances,
                         p_clusters=p__clusters,
                         p_ano_scores=p_ano_scores,
                         p_visualize=p_visualize,
                         p_raising_object=p_raising_object,
                         p_det_time=p_det_time,
                         **p_kwargs)

## -------------------------------------------------------------------------------------------------
    def _init_plot_2d(self, p_figure: Figure, p_settings: PlotSettings):
        super()._init_plot_2d(p_figure=p_figure, p_settings=p_settings)


## -------------------------------------------------------------------------------------------------
    def _init_plot_3d(self, p_figure: Figure, p_settings: PlotSettings):
        super()._init_plot_3d(p_figure=p_figure, p_settings=p_settings)
    

## -------------------------------------------------------------------------------------------------
    def _update_plot_2d(self, p_settings: PlotSettings, **p_kwargs):
        super()._update_plot_2d(p_settings, **p_kwargs)


## -------------------------------------------------------------------------------------------------
    def _update_plot_3d(self, p_settings: PlotSettings, **p_kwargs):
        super()._update_plot_3d(p_settings, **p_kwargs) 


## -------------------------------------------------------------------------------------------------
    def _remove_plot_2d(self):
        super()._remove_plot_2d()


## -------------------------------------------------------------------------------------------------
    def _remove_plot_3d(self):
        super()._remove_plot_3d()
  

