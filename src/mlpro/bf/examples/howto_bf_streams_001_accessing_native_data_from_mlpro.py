## -------------------------------------------------------------------------------------------------
## -- Project : MLPro - A Synoptic Framework for Standardized Machine Learning Tasks
## -- Package : mlpro.bf.examples
## -- Module  : howto_bf_streams_001_accessing_native_data_from_mlpro.py
## -------------------------------------------------------------------------------------------------
## -- History :
## -- yyyy-mm-dd  Ver.      Auth.    Description
## -- 2022-11-08  1.0.0     DA       Creation
## -------------------------------------------------------------------------------------------------

"""
Ver. 1.0.0 (2022-11-08)

This module demonstrates the use of native generic data streams provided by MLPro. To this regard,
all data streams of the related provider class will be determined and iterated. 

You will learn:

1) How to access MLPro's native data streams.

2) How to iterate the instances of a native stream.

3) How to access feature data of a native stream.

"""


from datetime import datetime
from mlpro.bf.streams import Stream
from mlpro.bf.streams.native import StreamProviderMLPro
from mlpro.bf.various import Log



# 0 Prepare Demo/Unit test mode
if __name__ == '__main__':
    logging     = Log.C_LOG_ALL
else:
    logging     = Log.C_LOG_NOTHING


# 1 Create a Wrapper for OpenML stream provider
mlpro = StreamProviderMLPro(p_logging=logging)


# 2 Determine and iterate all native data streams provided by MLPro
for stream in mlpro.get_stream_list( p_logging=logging ):
    stream.switch_logging( p_logging=logging )
    stream.log(Log.C_LOG_W, 'Number of features:', stream.get_feature_space().get_num_dim(), ', Number of instances:', stream.get_num_instances() )

    # 2.1 Iterate all instances of the stream
    myiterator = iter(stream)
    for i, curr_instance in enumerate(myiterator):
        curr_data = curr_instance.get_feature_data().get_values()
        stream.log(Log.C_LOG_I, 'Instance ' + str(i) + ':\n   Data:', curr_data)


# 3 Performance test: reset and iterate all data streams dark and measure the time
for stream in mlpro.get_stream_list( p_logging=logging ):
    stream.switch_logging( p_logging=logging )
    stream.log(Log.C_LOG_TYPE_W, 'Number of features:', stream.get_feature_space().get_num_dim(), ', Number of instances:', stream.get_num_instances() )
    stream.switch_logging( p_logging=Log.C_LOG_NOTHING )

    # 3.1 Iterate all instances of the stream
    tp_start = datetime.now()
    myiterator = iter(stream)
    for i, curr_instance in enumerate(myiterator):
        curr_data = curr_instance.get_feature_data().get_values()

    tp_end       = datetime.now()
    duration     = tp_end - tp_start
    duration_sec = duration.seconds + ( duration.microseconds / 1000000 )
    rate         = myiterator.get_num_instances() / duration_sec

    myiterator.switch_logging( p_logging=logging )
    myiterator.log(Log.C_LOG_TYPE_W, 'Done in', round(duration_sec,3), ' seconds (throughput =', round(rate), 'instances/sec)')    
