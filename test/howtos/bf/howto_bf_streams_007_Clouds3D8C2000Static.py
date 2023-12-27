## -------------------------------------------------------------------------------------------------
## -- Project : MLPro - A Synoptic Framework for Standardized Machine Learning Tasks
## -- Package : mlpro.bf.examples
## -- Module  : howto_bf_streams_007_Clouds3D8C2000Static.py
## -------------------------------------------------------------------------------------------------
## -- History :
## -- yyyy-mm-dd  Ver.      Auth.    Description
## -- 2023-11-09  0.0.0     SP       Creation
## -- 2023-11-09  1.0.0     SP       First implementation
## -- 2023-12-26  1.0.1     DA       Bugfixes
## -- 2023-12-27  1.1.0     DA       Refactoring
## -------------------------------------------------------------------------------------------------

"""
Ver. 1.1.0 (2023-12-27)

This module demonstrates the principles of stream processing with MLPro. To this regard, stream tasks
are added to a stream workflow. This in turn is combined with a stream of a stream provider to a
a stream scenario. The latter one can be executed.

You will learn:

1) How to implement an own custom stream task.

2) How to set up a stream workflow based on stream tasks.

3) How to set up a stream scenario based on a stream and a processing stream workflow.

4) How to run a stream scenario dark or with default visualization.

"""


from mlpro.bf.streams import *
from mlpro.bf.streams.streams import *
from mlpro.bf.streams.tasks import Window
from mlpro.bf.streams.models import StreamTask
from mlpro.bf.various import Log



## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class MyTask (StreamTask):
    """
    Demo implementation of a stream task with custom method _run().
    """

    # needed for proper logging (see class mlpro.bf.various.Log)
    C_NAME      = 'My stream task'

## -------------------------------------------------------------------------------------------------
    def _run(self, p_inst_new: list, p_inst_del: list):
        pass





## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class MyScenario (StreamScenario):
    """
    Example of a custom stream scenario including a stream and a stream workflow. See class 
    mlpro.bf.streams.models.StreamScenario for further details and explanations.
    """

    C_NAME      = 'My stream scenario'

## -------------------------------------------------------------------------------------------------
    def _setup(self, p_mode, p_visualize:bool, p_logging):

        # 1 Import a native stream from MLPro
        provider_mlpro = StreamProviderMLPro(p_seed=2, p_logging=p_logging)
        stream = provider_mlpro.get_stream('StreamMLProClouds3D8C2000Static', p_mode=p_mode, p_logging=p_logging)


        # 2 Set up a stream workflow

        # 2.1 Creation of tasks

        # 2.1 Set up and add a window task and an empty task
        task_window1 = Window( p_buffer_size=50, 
                               p_name = 't1', 
                               p_delay = True,
                               p_visualize = p_visualize, 
                               p_enable_statistics = True,
                               p_logging=logging )
        task_empty = MyTask(p_name='t2', p_visualize=p_visualize, p_logging=p_logging)


        # 2.2 Create a workflow and add the tasks
        workflow = StreamWorkflow( p_name='wf1', 
                                   p_range_max=StreamWorkflow.C_RANGE_NONE, 
                                   p_visualize=p_visualize,
                                   p_logging=logging )

        # 2.2.1 Add the tasks to our workflow
        workflow.add_task( p_task=task_window1 )
        workflow.add_task( p_task=task_empty, p_pred_tasks=[task_window1] )


        # 3 Return stream and workflow
        return stream, workflow





# 1 Preparation of demo/unit test mode
if __name__ == "__main__":
    # 1.1 Parameters for demo mode
    cycle_limit = 1000
    logging     = Log.C_LOG_ALL
    visualize   = True
  
else:
    # 1.2 Parameters for internal unit test
    cycle_limit = 2
    logging     = Log.C_LOG_NOTHING
    visualize   = False


# 2 Instantiate the stream scenario
myscenario = MyScenario( p_mode=Mode.C_MODE_SIM,
                         p_cycle_limit=cycle_limit,
                         p_visualize=visualize,
                         p_logging=logging )


# 3 Reset and run own stream scenario
myscenario.reset()

if __name__ == '__main__':
    myscenario.init_plot()
    input('Press ENTER to start stream processing...')

myscenario.run()

if __name__ == '__main__':
    input('Press ENTER to exit...')