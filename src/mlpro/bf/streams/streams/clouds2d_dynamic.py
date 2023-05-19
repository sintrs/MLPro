## -------------------------------------------------------------------------------------------------
## -- Project : MLPro - A Synoptic Framework for Standardized Machine Learning Tasks
## -- Package : mlpro.bf.streams.streams
## -- Module  : clouds2d_dynamic.py
## -------------------------------------------------------------------------------------------------
## -- History :
## -- yyyy-mm-dd  Ver.      Auth.    Description
## -- 2023-03-22  0.0.0     SP       Creation 
## -- 2023-03-22  1.0.0     SP       First draft implementation
## -- 2023-03-29  1.0.1     SP       Updated to speed up the code
## -- 2023-04-07  1.0.2     SP       Added new parameter p_variance, update the parameter p_pattern with constants
## -- 2023-05-08  1.0.3     SP       Added new parameter p_no_clouds
## -- 2023-05-18  1.0.4     SP       Added new parameter p_velocity
## -------------------------------------------------------------------------------------------------

"""
Ver. 1.0.4 (2023-05-18)

This module provides the native stream class StreamMLProStaticClouds2D. This stream provides 250 
instances per cluster with 2-dimensional random feature data placed around centers which move over time.
"""

import numpy as np
from mlpro.bf.streams.models import *
from mlpro.bf.streams.streams.provider_mlpro import StreamMLProBase



## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class StreamMLProDynamicClouds2D (StreamMLProBase):
    """
    This demo stream provides 250 2-dimensional instances per cluster randomly positioned around centers which move over time.
    """

    C_ID                = 'DynamicClouds2D'
    C_NAME              = 'Dynamic Clouds 2D'
    C_TYPE              = 'Demo'
    C_VERSION           = '1.0.0'
    C_NUM_INSTANCES     = 1000
    C_SCIREF_ABSTRACT   = 'Demo stream provides 250 2-dimensional instances per cluster randomly positioned around centers which move over time.'
    C_BOUNDARIES        = [-60,60]
    C_PATTERN           = ['random', 'random chain', 'static', 'merge']

## -------------------------------------------------------------------------------------------------
    def __init__(self, 
                 p_pattern='random', 
                 p_no_clouds=4, 
                 p_variance=5.0,
                 p_velocity=0.1, 
                 p_logging=Log.C_LOG_ALL, 
                 **p_kwargs):

        StreamMLProBase.__init__(self, 
                                 p_logging=p_logging, 
                                 **p_kwargs)
        
        if str.lower(p_pattern) not in self.C_PATTERN:
            raise ValueError(f"Invalid value for pattern, allowed values are {self.C_PATTERN}")
        self.pattern = str.lower(p_pattern)
        self.variance = p_variance
        self.no_clouds = int(p_no_clouds)
        self.C_NUM_INSTANCES = 250*self.no_clouds
        self.velocity = p_velocity


## -------------------------------------------------------------------------------------------------
    def _setup_feature_space(self) -> MSpace:
        # sourcery skip: use-fstring-for-concatenation
        feature_space : MSpace = MSpace()

        for i in range(2):
            feature_space.add_dim( Feature( p_name_short = 'f' + str(i),
                                            p_base_set = Feature.C_BASE_SET_R,
                                            p_name_long = 'Feature #' + str(i),
                                            p_name_latex = '',
                                            p_boundaries = self.C_BOUNDARIES,
                                            p_description = '',
                                            p_symmetrical = False,
                                            p_logging=Log.C_LOG_NOTHING, ) )

        return feature_space


## -------------------------------------------------------------------------------------------------
    def _init_dataset(self):

        # 1 Preparation
        try:
            seed = Stream.set_random_seed(p_seed=32)
        except:
            seed = random.seed(32)

        self._dataset = np.empty((self.C_NUM_INSTANCES, 2))


        # Compute the initial positions of the centers
        centers = np.random.RandomState(seed=seed).randint(self.C_BOUNDARIES[0],
                                                           self.C_BOUNDARIES[1], size=(self.no_clouds, 2))
        centers = centers.astype(np.float64)

        # Compute the final positions of the centers
        final_centers = np.random.RandomState(seed=seed).randint(self.C_BOUNDARIES[0],
                                                                    self.C_BOUNDARIES[1], size=(self.no_clouds, 2))
        final_centers = final_centers.astype(np.float64)

        for x in range(self.no_clouds):
            mag = ((centers[x][0]-final_centers[x][0])**2 + (centers[x][1]-final_centers[x][1])**2)**0.5
            if mag != 0:
                final_centers[x][:] = centers[x][:] + ((centers[x][:]-final_centers[x][:])/ mag)*250*self.velocity
            else:
                final_centers[x][:] = centers[x][:] + (0.5**0.5)*250*self.velocity
            if x<(self.no_clouds-1) and self.pattern=='random chain':
                centers[x+1] = centers[x] + final_centers[x]*250*self.velocity

        if self.pattern == 'merge':
            if self.no_clouds%2==0:
                e1 = self.no_clouds
                e2 = 0
                m = int(e1/2)
            else:
                e1 = self.no_clouds-1
                e2 = e1
                m = int(e1/2)
            final_centers[m:e1] = final_centers[:m]
            if e2!=0:
                final_centers[e2] = final_centers[e1-1]

            for x in range(self.no_clouds-m):
                mag = ((centers[m+x][0]-final_centers[m+x][0])**2 + (centers[m+x][1]-final_centers[m+x][1])**2)**0.5
                if mag != 0:
                    centers[m+x][:] = final_centers[m+x][:] - ((final_centers[m+x][:] - centers[m+x][:])/ mag)*250*self.velocity
                else:
                    centers[m+x][:] = final_centers[m+x][:] - (0.5**0.5)*250*self.velocity


        # 2 Create 250 noisy inputs around each of the 4 hotspots
        a = np.random.RandomState(seed=seed).rand(self.C_NUM_INSTANCES, 2)**3
        s = np.round(np.random.RandomState(seed=seed).rand(self.C_NUM_INSTANCES, 2))
        s[s==0] = -1
        fx = self.variance
        c = a*s * np.array([fx, fx]) 
        
        # Create the dataset
        dataset = np.zeros((self.C_NUM_INSTANCES, 2))

        if self.pattern == 'static':
            centers_diff = (final_centers - centers) / 500

            i = 0
            while i<125:
                dataset[i*self.no_clouds:(i+1)*self.no_clouds] = centers + c[i*self.no_clouds:(i+1)*self.no_clouds]
                centers = centers + centers_diff
                i += 1

            while i<250:
                dataset[i*self.no_clouds:(i+1)*self.no_clouds] = centers + c[i*self.no_clouds:(i+1)*self.no_clouds]
                centers = centers - centers_diff
                i += 1

        else:
            centers_diff = (final_centers - centers) / 250

            for i in range(250):
                dataset[i*self.no_clouds:(i+1)*self.no_clouds] = centers + c[i*self.no_clouds:(i+1)*self.no_clouds]
                centers = centers + centers_diff

        self._dataset = dataset

