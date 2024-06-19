## -- ----------------------------------------------------------------------------------------------
## -- Project : MLPro - The integrative middleware framework for standardized machine learning
## -- Package : mlpro.oa.tasks.anomalydetectors.cb_detectors
## -- Module  : new_cluster_detector.py
## -------------------------------------------------------------------------------------------------
## -- History :
## -- yyyy-mm-dd  Ver.      Auth.    Description
## -- 2023-06-08  0.0.0     SK       Creation
## -- 2023-09-12  1.0.0     SK       Release
## -- 2023-11-21  1.0.1     SK       Time Stamp update
## -- 2024-02-25  1.1.0     SK       Visualisation update
## -- 2024-04-10  1.2.0     DA/SK    Refactoring
## -- 2024-05-28  1.2.1     SK       Refactoring
## -------------------------------------------------------------------------------------------------

"""
Ver. 1.2.1 (2024-05-28)

This module provides new cluster detector algorithm.
"""

from mlpro.oa.streams.basics import *
from mlpro.oa.streams.tasks.anomalydetectors.cb_detectors.basics import AnomalyDetectorCB
from mlpro.oa.streams.tasks.anomalydetectors.anomalies.clusterbased.new_cluster import NewClusterAppearance
from mlpro.oa.streams.tasks.clusteranalyzers.basics import ClusterAnalyzer
from mlpro.bf.streams import Instance, InstDict
from mlpro.bf.math.properties import *




## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class NewClusterDetector(AnomalyDetectorCB):
    """
    This is the class for detecting new clusters.

    """
    C_PROPERTIY_DEFINITIONS : PropertyDefinitions = []

## -------------------------------------------------------------------------------------------------
    def __init__(self,
                 p_clusterer : ClusterAnalyzer = None,
                 p_name:str = None,
                 p_range_max = StreamTask.C_RANGE_THREAD,
                 p_ada : bool = True,
                 p_duplicate_data : bool = False,
                 p_visualize : bool = False,
                 p_logging=Log.C_LOG_ALL,
                 **p_kwargs):

        super().__init__(p_clusterer = p_clusterer,
                         p_name = p_name,
                         p_range_max = p_range_max,
                         p_ada = p_ada,
                         p_duplicate_data = p_duplicate_data,
                         p_visualize = p_visualize,
                         p_logging = p_logging,
                         **p_kwargs)
        
        for x in self.C_PROPERTIY_DEFINITIONS:
            if x not in self.C_REQ_CLUSTER_PROPERTIES:
                self.C_REQ_CLUSTER_PROPERTIES.append(x)

        unknown_prop = self._clusterer.align_cluster_properties(p_properties=self.C_REQ_CLUSTER_PROPERTIES)

        if len(unknown_prop) > 0:
            raise RuntimeError("The following cluster properties need to be provided by the clusterer: ", unknown_prop)

        self._prev_clusters = {}
        

## -------------------------------------------------------------------------------------------------
    def _run(self, p_inst: InstDict):
        new_instances = []
        for inst_id, (inst_type, inst) in sorted(p_inst.items()):
            new_instances.append(inst)

        clusters = self._clusterer.get_clusters()

        if len(clusters) > len(self._prev_clusters):
            new_clusters = {}
            for x in clusters.keys():
                if x not in self._prev_clusters.keys():
                    new_clusters[x] = clusters[x]

            if new_clusters:  # Only raise an event if there are new clusters
                anomaly = NewClusterAppearance(p_id=self._get_next_anomaly_id,
                                               p_instances=new_instances,
                                               p_clusters=new_clusters,
                                               p_det_time=str(inst.get_tstamp()))
                self._raise_anomaly_event(anomaly)

            self._prev_clusters.update(new_clusters) 

