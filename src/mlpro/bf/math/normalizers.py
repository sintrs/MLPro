 ## -------------------------------------------------------------------------------------------------
## -- Project : MLPro - A Synoptic Framework for Standardized Machine Learning Tasks
## -- Package : mlpro.bf.pool
## -- Module  : normalizers.py
## -------------------------------------------------------------------------------------------------
## -- History :
## -- yyyy-mm-dd  Ver.      Auth.    Description
## -- 2022-09-16  0.0.0     LSB      Creation
## -- 2022-09-20  1.0.0     LSB      Release of first version
## -- 2022-09-23  1.0.1     LSB      Refactoring
## -- 2022-09-26  1.0.2     LSB      Refatoring and reduced custom normalize and denormalize methods
## -- 2022-10-01  1.0.3     LSB      Refactoring and redefining the update parameter method
## -- 2022-10-16  1.0.4     LSB      Updating z-transform parameters based on a new data/element(np.ndarray)
## -- 2022-10-17  1.0.5     LSB      Refactoring following the review
## -------------------------------------------------------------------------------------------------

"""
Ver. 1.0.5 (2022-10-17)
This module provides base class for Normalizers and normalizer objects including MinMax normalization and 
normalization by Z transformation.

"""

from mlpro.bf.math import *
from mlpro.rl.models_sar import *
import numpy as np
from typing import Union





## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class Normalizer:
    """
    Base template class for normalizer objects.
    """

## -------------------------------------------------------------------------------------------------
    def __init__(self):

        self._param = None
        self._param_old = None
        self._param_new = None


## -------------------------------------------------------------------------------------------------
    def _set_parameters(self, p_param):
        """
        custom method to set the normalization parameters

        Parameters
        ----------
        p_set:Set
            Set related to the elements to be normalized

        Returns
        -------
        boolean:True
            Returns true after setting the parameters
        """
        self._param = p_param


## -------------------------------------------------------------------------------------------------
    def normalize(self, p_data:Union[Element, np.ndarray]):
        """
        Method to normalize a data (Element/ndarray) element based on MinMax or Z-transformation

        Parameters
        ----------
        p_data:Element or a numpy array
            Data element to be normalized

        Returns
        -------
        element:Element or numpy array
            Normalized Data
        """

        if self._param is None:
            raise ImplementationError('Normalization parameters not set')
        if isinstance(p_data, Element):
            normalized_element = Element(p_data.get_related_set())
            normalized_element.set_values(np.multiply(p_data.get_values(), self._param[0]) - self._param[1])
        elif isinstance(p_data, np.ndarray):
            normalized_element = np.multiply(p_data, self._param[0]) - self._param[1]
        else: raise ParamError('Wrong data type provided for normalization')
        return normalized_element


## -------------------------------------------------------------------------------------------------
    def denormalize(self, p_data:Union[Element, np.ndarray]):
        """
        Method to denormalize a data (Element/ndarray) element based on MinMax or Z-transformation

        Parameters
        ----------
        p_data:Element or a numpy array
            Data element to be denormalized

        Returns
        -------
        element:Element or numpy array
            Denormalized Data
        """

        if self._param is None:
            raise ImplementationError('Normalization parameters not set')
        if isinstance(p_data, Element):
            denormalized_element = Element(p_data.get_related_set())
            denormalized_element.set_values(np.multiply(p_data.get_values(), 1 / self._param[0]) + (
                        self._param[1] / self._param[0]))
        elif isinstance(p_data, np.ndarray):
            denormalized_element = np.multiply(p_data, 1 / self._param[0]) + \
                                   (self._param[1] / self._param[0])
        else:
            raise ParamError('Wrong datatype provided for denormalization')

        return denormalized_element


## -------------------------------------------------------------------------------------------------
    def renormalize(self, p_data:Union[Element, np.ndarray]):
        """
        Method to denormalize and renormalize an element based on old and current normalization parameters.

        Parameters
        ----------
        p_data:Element or numpy array
            Element to be renormalized.

        Returns
        -------
        renormalized_element:Element or numpy array
            Renormalized Data

        """
        
        self._set_parameters(self._param_old)
        denormalized_element = self.denormalize(p_data)
        self._set_parameters(self._param_new)
        renormalized_element = self.normalize(denormalized_element)
        return renormalized_element


## -------------------------------------------------------------------------------------------------
    def update_parameters(self, p_data:Union[Set, Element, np.ndarray]):
        """
        Custom method to update normalization parameters.

        Parameters
        ----------
        p_data
            arguments specific to normalization parameters. Check the normalizer objects for specific parameters

        """

        raise NotImplementedError





## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class NormalizerMinMax (Normalizer):
    """
    Class to normalize elements based on MinMax normalization.
    """

## -------------------------------------------------------------------------------------------------
    def update_parameters(self, p_set:Set=None, p_boundaries=None):
        """
        Method to update the normalization parameters of MinMax normalizer.

        Parameters
        ----------
        p_set:Set
            Set related to the elements to be normalized
        p_boundaries:ndarray
            array consisting of boundaries related to the dimension of the array

        """

        try:
            a = np.zeros(len(p_set.get_dim_ids()))
            b = np.zeros(len(p_set.get_dim_ids()))
            boundaries = [p_set.get_dim(i).get_boundaries() for i in p_set.get_dim_ids()]
        except:
            try:
                a = np.zeros(len(p_boundaries))
                b = np.zeros(len(p_boundaries))
                boundaries = p_boundaries.reshape(-1,2)
            except:
                raise ParamError("Wrong parameters provided for update. Please provide a set as p_set or boundaries as "
                                 "p_boundaries")

        for i in range(len(boundaries)):
            min_boundary = boundaries[i][0]
            max_boundary = boundaries[i][1]
            value_range = max_boundary - min_boundary
            a[i] = (2 / (value_range))
            b[i] = (2 * min_boundary / (value_range) + 1)

        self._param_old = self._param_new
        self._param_new = np.vstack(([a],[b]))
        self._param = self._param_new





## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class NormalizerZTrans(Normalizer):
    """
    Class for Normalization based on Z transformation.
    """


## -------------------------------------------------------------------------------------------------
    def update_parameters(self, p_dataset = None, p_data = None):
        """
        Method to update the normalization parameters for Z transformer

        Parameters
        ----------
        p_dataset:numpy array
            Dataset related to the elements to be normalized. Using this parameter will reset the normalization
            parameters based on the dataset provided.
        p_data:numpy array
            New element to update the normalization parameters. Using this parameter will set/update the
            normalization parameters based on the data provided.

        """
        try: p_data = p_data.get_values()
        except: pass

        if p_data is None and isinstance(p_dataset, np.ndarray):
            self._std = np.std(p_dataset, axis=0, dtype=np.float64)
            self._mean = np.mean(p_dataset, axis = 0, dtype=np.float64)

            self._n = len(p_dataset)

        elif isinstance(p_data, np.ndarray) and p_dataset is None:
            # this try/except block checks if the parameters are previously set with a dataset, otherwise sets the
            # parameters based on a single element
            try:
                old_mean = self._mean
                self._n += 1
                self._mean = (old_mean * (self._n - 1) + p_data) / (self._n)
                self._std = np.sqrt((np.square(self._std) * (self._n - 1)
                                     + (p_data - self._mean) * (p_data - old_mean)) / (self._n))
            except:
                self._n = 1
                self._mean = p_data.copy()
                self._std = np.zeros(shape=p_data.shape)



        else: raise ParamError("Wrong parameters for update_parameters(). Please either provide a dataset as p_dataset "
                               "or a new data element as p_data ")

        a = 1 / self._std
        b = self._mean / self._std

        self._param_old = self._param_new
        self._param_new = np.vstack(([a], [b]))
        self._param = self._param_new

