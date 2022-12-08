## -------------------------------------------------------------------------------------------------
## -- Project : MLPro - A Synoptic Framework for Standardized Machine Learning Tasks
## -- Package : mlpro.oa.examples.howto_oa_001_normalizer_minmax
## -- Module  : howto_oa_001_normalizer_minmax.py
## -------------------------------------------------------------------------------------------------
## -- History :
## -- yyyy-mm-dd  Ver.      Auth.    Description
## -- 2022-12-07  0.0.0     LSB      Creation
## -------------------------------------------------------------------------------------------------

"""
Ver. 0.0.0 (2022-12-07)
This module is an example of adaptive normalization of streaming data using MinMax Normalizer

You will learn:

1. ...

2.

3.

"""

from mlpro.oa.tasks.normalizers import *
from mlpro.oa.tasks.boundarydetectors import *
from mlpro.bf.streams.models import *
from mlpro.wrappers.openml import *






## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class MyAdaptiveScenario(StreamScenario):

    C_NAME = 'Dummy'


## -------------------------------------------------------------------------------------------------
    def _setup(self, p_mode, p_visualize:bool, p_logging):
        # 1 Import a stream from OpenML
        openml = WrStreamProviderOpenML(p_logging=p_logging)
        stream = openml.get_stream(p_name='BNG(autos,nominal,1000000)', p_mode=p_mode, p_logging=p_logging)

        # 2 Set up a stream workflow based on a custom stream task

        # 2.1 Creation of a task
        TaskBoundaryDetector = BoundaryDetector(p_name='Demo Boundary Detector', p_logging=p_logging)
        TaskNormalizerMinMax = NormalizerMinMax(p_name='Demo MinMax Normalizer', p_ada=True, p_logging=p_logging)

        # 2.2 Creation of a workflow
        workflow = OAWorkflow(p_name='wf1',
            p_range_max=OAWorkflow.C_RANGE_NONE,  # StreamWorkflow.C_RANGE_THREAD,
            p_logging=p_logging)

        # 2.3 Addition of the task to the workflow
        workflow.add_task(p_task = TaskBoundaryDetector)
        workflow.add_task(p_task = TaskNormalizerMinMax)

        # 3 Return stream and workflow
        return stream, workflow


if __name__ == "__main__":
    # 1.1 Parameters for demo mode
    cycle_limit = 100
    logging = Log.C_LOG_ALL
    visualize = False

else:
    # 1.2 Parameters for internal unit test
    cycle_limit = 2
    logging = Log.C_LOG_NOTHING
    visualize = False

# 2 Instantiate the stream scenario
myscenario = MyAdaptiveScenario(p_mode=Mode.C_MODE_REAL,
    p_cycle_limit=cycle_limit,
    p_visualize=visualize,
    p_logging=logging)

# 3 Reset and run own stream scenario
myscenario.reset()

if __name__ == '__main__':
    myscenario.init_plot()
    input('Press ENTER to start stream processing...')

myscenario.run()

if __name__ == '__main__':
    input('Press ENTER to exit...')