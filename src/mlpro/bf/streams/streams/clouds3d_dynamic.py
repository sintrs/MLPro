## -------------------------------------------------------------------------------------------------
## -- Project : MLPro - A Synoptic Framework for Standardized Machine Learning Tasks
## -- Package : mlpro.bf.streams.streams
## -- Module  : clouds3d_dynamic.py
## -------------------------------------------------------------------------------------------------
## -- History :
## -- yyyy-mm-dd  Ver.      Auth.    Description
## -- 2023-03-22  0.0.0     DA       Creation 
## -- 2023-03-22  1.0.0     DA       First draft implementation
## -------------------------------------------------------------------------------------------------

"""
Ver. 1.0.0 (2023-03-22)

This module provides the native stream class StreamMLProStaticClouds3D. This stream provides 2000 
instances with 3-dimensional random feature data placed around eight centers which move over time.
"""

import numpy as np
from mlpro.bf.streams.models import *
from mlpro.bf.streams.streams.provider_mlpro import StreamMLProBase




## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class StreamMLProDynamicClouds3D (StreamMLProBase):
    """
    This demo stream provides 2000 3-dimensional instances randomly positioned around eight centers which move over time.
    """

    C_ID                = 'DynamicClouds3D'
    C_NAME              = 'Dynamic Clouds 3D'
    C_VERSION           = '1.0.0'
    C_NUM_INSTANCES     = 2000
    C_SCIREF_ABSTRACT   = 'Demo stream provides 2000 3-dimensional instances randomly positioned around eight centers which move over time.'
    C_BOUNDARIES        = [-10,10]

    def __init__(self, pattern='random'):
        super().__init__()
        self.pattern             = pattern # random, static, random chain and merge


## -------------------------------------------------------------------------------------------------
    def _setup_feature_space(self) -> MSpace:
        feature_space : MSpace = MSpace()

        for i in range(3):
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

        self._dataset = np.empty( (self.C_NUM_INSTANCES, 3))


        # Compute the initial positions of the centers
        centers = np.random.randint(self.C_BOUNDARIES[0], self.C_BOUNDARIES[1], size=(8, 3))

        if self.pattern == 'random':
            # Compute the final positions of the centers
            final_centers = np.random.randint(self.C_BOUNDARIES[0], self.C_BOUNDARIES[1], size=(8, 3))

        elif self.pattern == 'random chain':
            # Compute the final positions of the centers
            final_centers = np.zeros((8, 3))
            final_centers[0] = centers[-1]
            final_centers[1:] = centers[:-1]

        elif self.pattern == 'static':
            # Use the initial positions as the final positions
            final_centers = centers

        elif self.pattern == 'merge':
            # Compute the final positions of the centers
            final_centers = np.zeros((8, 3))
            final_centers[:4] = np.random.randint(self.C_BOUNDARIES[0], self.C_BOUNDARIES[1], size=(4, 3))
            final_centers[4:] = final_centers[:4]


        # 2 Create 250 noisy inputs around each of the 8 hotspots
        a = np.random.RandomState(seed=seed).rand(self.C_NUM_INSTANCES, 3)**3
        s = np.round(np.random.RandomState(seed=seed).rand(self.C_NUM_INSTANCES, 3))
        s[s==0] = -1
        fx = 5 * 0.75
        c = a*s * np.array([fx, fx, fx]) 
        
        # Create the dataset
        dataset = np.zeros((self.C_NUM_INSTANCES, 3))

        if self.pattern == 'static':
            for i in range(int(self.C_NUM_INSTANCES / 16)):
                for j in range(8):
                    dataset[i*8+j] = centers[j] + c[i*8+j]
                    centers[j] += (0-centers[j])/(int(self.C_NUM_INSTANCES / 16)-i)
            for i in range(int(self.C_NUM_INSTANCES / 16)):
                for j in range(8):
                    dataset[1000+i*8+j] = centers[j] + c[i*8+j]
                    centers[j] += (final_centers[j]-centers[j])/(int(self.C_NUM_INSTANCES / 16)-i)

        else:
            for i in range(int(self.C_NUM_INSTANCES / 8)):
                for j in range(8):
                    dataset[i*8+j] = centers[j] + c[i*8+j]
                    centers[j] += (final_centers[j]-centers[j])/(int(self.C_NUM_INSTANCES / 8)-i)

        self._dataset = dataset

## -------------------------------------------------------------------------------------------------
    def set_random_seed(self, p_seed=None):
        self._random_seed = p_seed

