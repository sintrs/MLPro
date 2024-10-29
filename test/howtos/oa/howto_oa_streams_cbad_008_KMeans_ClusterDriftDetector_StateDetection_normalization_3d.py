## -------------------------------------------------------------------------------------------------
## -- Project : MLPro - The integrative middleware framework for standardized machine learning
## -- Package : test.howtos.oa
## -- Module  : howto_oa_streams_cbad_008_KMeans_ClusterDriftDetector_StateDetection_normalization_3d.py
## -------------------------------------------------------------------------------------------------
## -- History :
## -- yyyy-mm-dd  Ver.      Auth.    Description
## -- 2024-08-04  1.0.0     SK       Creation
## -- 2024-10-29  1.0.1     DA       Refactoring
## -------------------------------------------------------------------------------------------------

"""
Ver. 1.0.1 (2024-10-29)

This module is done as a part of the Master's Thesis named Online Adaptive Cluster-based Anomaly
Detection, authored by Syamraj Purushamparambil Satheesh, as a part of the course
"Systems Engineering and Engineering Management" in the Department of "Electrical Energy Engineering",
supervised by Dipl.-Info. Detlef Arend.


This module demonstrates cluster-based anomlay detection, on synthetic 2-dimensional data generated by
the StreamMLProClusterGenerator, using the ClusterDriftDetector anomaly detection algorithm employing
the KMeans clustering algorithm wrapped from River library, to detect ClusterDrift anomaly.

You will learn:

1. Generating synthetic data using the native StreamMLProClusterGenerator.

2. Creating a workflow and tasks in MLPro-OA.

3. Normalizing streaming data using the MinMax Normalizer, with boundary detector as a predecessor task.

4. Clustering the normalized streaming data using the WrRiverKMeans2MLPro, with normalizer as a predecessor.

5. Detecting drift anomalies in the clustered data using the ClusterDriftDetector.

In the visualization, the cross hair designating the cluster's centroid becomes'red' in colour when
an anomaly is detected linked to that specific cluster. An overview of the anomalies is displayed on
the screen following the run.

"""

from mlpro.bf.streams.streams import *
from mlpro.bf.various import Log
from mlpro.oa.streams import *
from mlpro_int_river.wrappers.clusteranalyzers import WrRiverKMeans2MLPro
from mlpro.oa.streams.tasks import BoundaryDetector, NormalizerMinMax, ClusterDriftDetector



## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
# 1 Prepare a scenario
class MyScenario(OAScenario):
    C_NAME = 'ClusterDriftScenario'

    def _setup(self, p_mode, p_ada: bool, p_visualize: bool, p_logging):

        # 1.1 Get MLPro benchmark Clutser Generator
        stream = StreamMLProClusterGenerator(p_num_dim=3,
                                             p_num_instances=5000,
                                             p_num_clusters=3,
                                             p_radii=[100],
                                             p_velocities=[0.0],
                                             p_change_velocities=True,
                                             p_changed_velocities=[0.5, 0.6],
                                             p_points_of_change_velocities=[1000, 1200, 1500],
                                             p_num_clusters_for_change_velocities=2,
                                             p_seed=23,
                                             p_logging=p_logging)


        # 1.2 Set up a stream workflow

        # 1.2.1 Creation of a workflow
        workflow = OAWorkflow( p_name='Anomaly Detection',
                               p_range_max=OAWorkflow.C_RANGE_NONE,
                               p_ada=p_ada,
                               p_visualize=p_visualize,
                               p_logging=p_logging )


        # 1.2.2 Creation of tasks and add them to the workflow

        task_bd = BoundaryDetector( p_name='T1 - Boundary Detector', 
                                    p_ada=p_ada, 
                                    p_visualize=p_visualize,
                                    p_logging=p_logging )
        
        workflow.add_task(p_task = task_bd)
        
        
        task_norm = NormalizerMinMax( p_name='T2 - MinMax Normalizer', 
                                      p_ada=p_ada, 
                                      p_visualize=p_visualize,
                                      p_logging=p_logging)
        
        workflow.add_task(p_task = task_norm, p_pred_tasks=[task_bd])

        task_bd.register_event_handler(
            p_event_id=BoundaryDetector.C_EVENT_ADAPTED,
            p_event_handler=task_norm.adapt_on_event
            )

        # Cluster Analyzer
        task_clusterer = WrRiverKMeans2MLPro( p_name='#1: KMeans@River',
                                              p_n_clusters=3,
                                              p_halflife=0.05, 
                                              p_sigma=3, 
                                              p_seed=42,
                                              p_visualize=p_visualize,
                                              p_logging=p_logging )

        workflow.add_task(p_task = task_clusterer)

        task_norm.register_event_handler( p_event_id=NormalizerMinMax.C_EVENT_ADAPTED,
                                                 p_event_handler=task_clusterer.renormalize_on_event )


        # Anomaly Detector
        task_anomaly_detector = ClusterDriftDetector(p_clusterer=task_clusterer,
                                                     p_with_time_calculation=False,
                                                     p_state_change_detection=True,
                                                     p_instantaneous_velocity_change_detection=False,
                                                     p_min_velocity_threshold=0.01,
                                                     p_initial_skip=400,
                                                     p_buffer_size=50,
                                                     p_visualize=p_visualize,
                                                     p_logging=p_logging)
        
        workflow.add_task(p_task=task_anomaly_detector, p_pred_tasks=[task_clusterer])

        # 1.3 Return stream and workflow
        return stream, workflow



# 2 Prepare for test
if __name__ == "__main__":
    cycle_limit = 2000
    logging     = Log.C_LOG_ALL
    visualize   = True
    step_rate   = 1
else:
    cycle_limit = 5
    logging     = Log.C_LOG_NOTHING
    visualize   = False
    step_rate   = 1


# 3 Instantiate the stream scenario
myscenario = MyScenario( p_mode=Mode.C_MODE_SIM,
                               p_cycle_limit=cycle_limit,
                               p_visualize=visualize,
                               p_logging=logging )

# 4 Reset and run own stream scenario
myscenario.reset()

if __name__ == "__main__":
    myscenario.init_plot( p_plot_settings=PlotSettings( p_view = PlotSettings.C_VIEW_2D,
                                                            p_step_rate = step_rate ) )
    input('\nPlease arrange all windows and press ENTER to start stream processing...')



tp_before           = datetime.now()
myscenario.run()
tp_after            = datetime.now()
tp_delta            = tp_after - tp_before
duraction_sec       = ( tp_delta.seconds * 1000000 + tp_delta.microseconds + 1 ) / 1000000
myscenario.log(Log.C_LOG_TYPE_W, 'Duration [sec]:', round(duraction_sec,2), ', Cycles/sec:', round(cycle_limit/duraction_sec,2))



# 5 Summary
anomalies         = myscenario.get_workflow()._tasks[3].get_anomalies()
detected_anomalies= len(anomalies)

myscenario.log(Log.C_LOG_TYPE_W, '-------------------------------------------------------')
myscenario.log(Log.C_LOG_TYPE_W, '-------------------------------------------------------')
myscenario.log(Log.C_LOG_TYPE_W, 'Here is the recap of the anomaly detector')
myscenario.log(Log.C_LOG_TYPE_W, 'Number of anomalies: ', detected_anomalies )

for anomaly in anomalies.values():
     anomaly_name = anomaly.C_NAME
     anomaly_id = str(anomaly.id)
     clusters_affected = {}
     clusters = anomaly.get_clusters()
     properties = anomaly.get_properties()
     for x in clusters.keys():
        clusters_affected[x] = {}
        clusters_affected[x]["velocity"] = properties[x]["velocity"]
        clusters_affected[x]["acceleration"] = properties[x]["acceleration"]

     
     inst = anomaly.get_instances()[-1].get_id()
     myscenario.log(Log.C_LOG_TYPE_W, 
                    'Anomaly : ', anomaly_name,
                    '\n Anomaly ID : ', anomaly_id,
                    '\n Instance ID : ', inst,
                    '\n Clusters : ', clusters_affected)

myscenario.log(Log.C_LOG_TYPE_W, '-------------------------------------------------------')
myscenario.log(Log.C_LOG_TYPE_W, '-------------------------------------------------------')

if __name__ == "__main__":
    input('Press ENTER to exit...')