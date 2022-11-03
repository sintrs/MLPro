## -------------------------------------------------------------------------------------------------
## -- Project : MLPro - A Synoptic Framework for Standardized Machine Learning Tasks
## -- Package : mlpro.wrappers
## -- Module  : openml.py
## -------------------------------------------------------------------------------------------------
## -- History :
## -- yyyy-mm-dd  Ver.      Auth.    Description
## -- 2022-01-11  0.0.0     DA       Creation
## -- 2022-05-25  1.0.0     LSB      First Release with Stream and StreamProvider class
## -- 2022-05-27  1.0.1     LSB      Feature space setup
## -- 2022-06-09  1.0.2     LSB      Downloading, resetting OpenML stream and handling instances
## -- 2022-06-10  1.0.3     LSB      Code Optmization
## -- 2022-06-13  1.0.4     LSB      Bug Fix
## -- 2022-06-23  1.0.5     LSB      fetching meta data
## -- 2022-06-25  1.0.6     LSB      Refactoring due to new label and instance class, new instance
## -- 2022-08-15  1.1.0     DA       Introduction of root class Wrapper
## -- 2022-11-03  1.2.0     DA       Class WrStreamOpenML: refactoring after changes on class 
## --                                bf.streams.Stream
## -------------------------------------------------------------------------------------------------

"""
Ver. 1.2.0 (2022-11-03)

This module provides wrapper functionalities to incorporate public data sets of the OpenML ecosystem.

Learn more: 
https://www.openml.org/
https://new.openml.org/
https://docs.openml.org/APIs/

"""

import numpy
from mlpro.bf.various import ScientificObject, Log
from mlpro.bf.ops import Mode
from mlpro.wrappers.models import Wrapper
from mlpro.bf.streams import Feature, Label, Instance, StreamProvider, Stream
from mlpro.bf.math import Element, MSpace
import openml





## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class WrStreamProviderOpenML (Wrapper, StreamProvider):
    """
    Wrapper class for OpenML as StreamProvider.
    """

    C_NAME              = 'Stream Provider OpenML'
    C_WRAPPED_PACKAGE   = 'openml'

    C_SCIREF_TYPE       = ScientificObject.C_SCIREF_TYPE_ONLINE
    C_SCIREF_AUTHOR     = 'OpenML'
    C_SCIREF_URL        = 'new.openml.org'


## -------------------------------------------------------------------------------------------------
    def __init__(self, p_logging = Log.C_LOG_ALL):

        StreamProvider.__init__(self, p_logging = p_logging)
        Wrapper.__init__(self, p_logging = p_logging)
        self._stream_list = []
        self._stream_ids = []


## -------------------------------------------------------------------------------------------------
    def _get_stream_list(self, p_logging = Log.C_LOG_ALL, **p_kwargs) -> list:
        """
        Custom class to get alist of stream objects from OpenML

        Returns
        -------
        list_streams : List
            Returns a list of Streams in OpenML

        """
        if len(self._stream_list) == 0:
            list_datasets = openml.datasets.list_datasets(output_format='dict')


            for d in list_datasets.items():
                try:
                    name = d[1]['name']
                except:
                    name = ''
                try:
                    id = d[1]['did']
                except:
                    id = ''
                try:
                    num_instances = d[1]['NumberOfInstances']
                except:
                    num_instances = 0
                try:
                    version = d[1]['Version']
                except:
                    version = 0

                s = WrStreamOpenML( p_id=id, 
                                    p_name=name, 
                                    p_num_instances=num_instances, 
                                    p_version=version, 
                                    p_logging=p_logging)

                self._stream_list.append(s)
                self._stream_ids.append(id)

        return self._stream_list


## -------------------------------------------------------------------------------------------------
    def _get_stream(self, p_id) -> Stream:
        """
        Custom class to fetch an OpenML stream object

        Parameters
        ----------
        p_id
            id of the stream to be fetched

        Returns
        -------
        stream: Stream
            Returns the stream corresponding to the id
        """
        try:

            try:
                stream = self._stream_list[self._stream_ids.index(int(p_id))]

            except:
                self.get_stream_list()
                stream = self._stream_list[self._stream_ids.index(int(p_id))]

            return stream


        except ValueError:
            raise ValueError('Stream id not in the available list')





## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class WrStreamOpenML(Wrapper, Stream):
    """
    Wrapper class for Streams from OpenML

    Parameters
    ----------
    p_id
        Id of the stream.
    p_name : str
        Name of the stream. 
    p_num_instances : int
        Number of instances in the stream. 
    p_version : str
        Version of the stream. Default = ''.
    p_feature_space : MSpace
        Optional feature space. Default = None.
    p_label_space : MSpace
        Optional label space. Default = None.
    p_mode
        Operation mode. Valid values are stored in constant C_VALID_MODES.
    p_logging
        Log level (see constants of class Log). Default: Log.C_LOG_ALL.
    p_kwargs : dict
        Further stream specific parameters.
    """

    C_NAME              = 'OpenML stream'
    C_WRAPPED_PACKAGE   = 'openml'
    C_SCIREF_TYPE       = ScientificObject.C_SCIREF_TYPE_ONLINE


## -------------------------------------------------------------------------------------------------
    def __init__( self, 
                  p_id, 
                  p_name : str, 
                  p_num_instances : int, 
                  p_version : str, 
                  p_mode = Mode.C_MODE_SIM, 
                  p_logging = Log.C_LOG_ALL, 
                  **p_kwargs ):

        self._downloaded = False
        self.C_ID = self._id = p_id
        self._name = p_name

        Wrapper.__init__( self, p_logging=p_logging )

        Stream.__init__( self,
                         p_id=p_id,
                         p_name=self.C_NAME + ' "' + p_name + '"',
                         p_num_instances=p_num_instances,
                         p_version=p_version,
                         p_feature_space=None,
                         p_label_space=None,
                         p_mode=p_mode,
                         p_logging=p_logging,
                         **p_kwargs )


## -------------------------------------------------------------------------------------------------
    def __repr__(self):
        return str(dict(id=str(self._id), name=self._name))


## -------------------------------------------------------------------------------------------------
    def _reset(self, p_seed=None):
        """
        Custom reset method to download and reset an OpenML stream

        Parameters
        ----------
        p_seed
            Seed for resetting the stream
        """

        # Just to ensure the data download and set up of feature and label space
        self.get_feature_space()
        self.get_label_space()

        self._index = 0


## --------------------------------------------------------------------------------------------------
    def _setup_feature_space(self) -> MSpace:

        if not self._downloaded:
            self._downloaded = self._download()
            if not self._downloaded: return None       

        feature_space = MSpace()

        _, _, _, features = self._dataset
        for feature in features:
            feature_space.add_dim(Feature(p_name_long=str(feature), p_name_short=str(self.C_NAME[0:5])))

        return feature_space


## --------------------------------------------------------------------------------------------------
    def _setup_label_space(self) -> MSpace:
        if not self._downloaded:
            self._downloaded = self._download() 
            if not self._downloaded: return None       

        label_space = MSpace()
        label_space.add_dim(Label(p_name_long=str(self._label), p_name_short=str(self._label[0:5])))
        return label_space


## --------------------------------------------------------------------------------------------------
    def _download(self) -> bool:
        """
        Custom method to download the corresponding OpenML dataset

        Returns
        -------
        bool
            True for the download status of the stream
        """
        self._stream_meta = openml.datasets.get_dataset(self._id)
        self._label = self._stream_meta.default_target_attribute

        try:
            self.C_SCIREF_URL = self._stream_meta.url
        except:
            self.C_SCIREF_URL = ''
        try:
            self.C_SCIREF_AUTHOR = self._stream_meta.creator
            if isinstance(self.C_SCIREF_AUTHOR, list):
                self.C_SCIREF_AUTHOR = ' and '.join(self.C_SCIREF_AUTHOR)
        except:
            self.C_SCIREF_AUTHOR =''
        try:
            self.C_SCIREF_ABSTRACT = self._stream_meta.description
        except:
            self.C_SCIREF_ABSTRACT =''

        self._dataset = self._stream_meta.get_data(dataset_format = 'array')

        if self._dataset is not None:
            return True

        else:
            raise ValueError("Dataset not downloaded or not available")


## ------------------------------------------------------------------------------------------------------
    def _get_next(self) -> Instance:
        """
        Custom method to get the instances one after another sequentially in the OpenML stream

        Returns
        -------
        instance : Instance
            Next instance in the OpenML stream object (None after the last instance in the dataset).
        """

        if self._index < len(self._dataset[0]):

            # Determine feature data
            feature_data  = Element( self.get_feature_space() )
            feature_data.set_values(numpy.delete(self._dataset[0][self._index] , self._dataset[3].index(self._label)))

            # Determine label data
            label_data = Element(self.get_label_space())
            label_data.set_values(numpy.asarray([self._dataset[0][self._index][self._dataset[3].index(self._label)]]))
            instance = Instance( p_feature_data=feature_data, p_label_data=label_data )
            self._index += 1

            return instance

        return None