## -------------------------------------------------------------------------------------------------
## -- Project : MLPro - A Synoptic Framework for Standardized Machine Learning Tasks
## -- Package : mlpro.bf.streams.streams
## -- Module  : clouds2d_static.py
## -------------------------------------------------------------------------------------------------
## -- History :
## -- yyyy-mm-dd  Ver.      Auth.    Description
## -- 2022-12-15  0.0.0     DA       Creation 
## -- 2022-12-15  1.0.0     DA       First draft implementation
## -------------------------------------------------------------------------------------------------

"""
Ver. 1.0.0 (2022-12-15)

This module provides the native stream class StreamMLProStaticClouds2D. This stream provides 1000 
instances with 2-dimensional random feature data placed around four fixed center points.
"""

import numpy as np
import math
from mlpro.bf.streams.models import *
from mlpro.bf.streams.streams.provider_mlpro import StreamMLProBase




## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class StreamMLProStaticClouds2D (StreamMLProBase):
    """
    This demo stream provides 1000 2-dimensional instances randomly positioned around four fixed centers.
    """

    C_ID                = 'StaticClouds2D'
    C_NAME              = 'Static Clouds 2D'
    C_VERSION           = '1.0.0'
    C_NUM_INSTANCES     = 1000

    C_SCIREF_ABSTRACT   = 'Demo stream provides 1000 2-dimensional instances randomly positioned around four fixed centers.'

    C_BOUNDARIES        = [-10,10]

## -------------------------------------------------------------------------------------------------
    def _setup_feature_space(self) -> MSpace:
        feature_space : MSpace = MSpace()

        for i in range(2):
            feature_space.add_dim( Feature( p_name_short = 'f' + str(i),
                                            p_base_set = Feature.C_BASE_SET_R,
                                            p_name_long = 'Feature #' + str(i),
                                            p_name_latex = '',
                                            p_boundaries = self.C_BOUNDARIES,
                                            p_description = '',
                                            p_symmetrical = False,
                                            p_logging=Log.C_LOG_NOTHING ) )

        return feature_space


## -------------------------------------------------------------------------------------------------
    def _init_dataset(self):

        # 1 Preparation
        try:
            seed = self._random_seed
        except:
            self.set_random_seed()
            seed = self._random_seed

        self._dataset = np.empty( (self.C_NUM_INSTANCES, 2))


        # 2 Create 4 fixed hotspots
        dx1             = ( self.C_BOUNDARIES[1] - self.C_BOUNDARIES[0] ) / 4
        x1_1            = self.C_BOUNDARIES[0] + dx1
        x1_2            = self.C_BOUNDARIES[1] - dx1
        
        dx2             = ( self.C_BOUNDARIES[1] - self.C_BOUNDARIES[0] ) / 4
        x2_1            = self.C_BOUNDARIES[0] + dx2
        x2_2            = self.C_BOUNDARIES[1] - dx2
        
        hotspots        = [ [ x1_1, x2_1 ], [ x1_2, x2_1 ], [ x1_1, x2_2 ], [ x1_2, x2_2 ] ]
       
        
        # 2 Create 250 noisy inputs around each of the 4 fixed hotspots
        a = np.random.RandomState(seed=seed).rand(self.C_NUM_INSTANCES, 2)**3
        s = np.round(np.random.RandomState(seed=seed).rand(self.C_NUM_INSTANCES, 2))
        s[s==0] = -1
        fx1 = dx1 * 0.75
        fx2 = dx2 * 0.75
        c = a*s * np.array([fx1, fx2]) 
        
        index  = 0
        
        for i in range(int(self.C_NUM_INSTANCES / 4)):
            for hsp in hotspots:
                self._dataset[index][0] = hsp[0] + c[index][0]
                self._dataset[index][1] = hsp[1] + c[index][1]
                index += 1


## -------------------------------------------------------------------------------------------------
    def set_random_seed(self, p_seed=None):
        self._random_seed = p_seed