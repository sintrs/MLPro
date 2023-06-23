## -------------------------------------------------------------------------------------------------
## -- Project : MLPro - A Synoptic Framework for Standardized Machine Learning Tasks
## -- Package : mlpro.sl
## -- Module  : basics.py
## -------------------------------------------------------------------------------------------------
## -- History :
## -- yyyy-mm-dd  Ver.      Auth.    Description
## -- 2023-06-13  0.0.0     LSB      Creation
## -------------------------------------------------------------------------------------------------

"""
Ver. 0.0.0 (2023-06-13)

This module provides training classes for supervised learning tasks.
"""


from mlpro.bf.data import *
from mlpro.sl.basics import *





## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class SLDataStoring(DataStoring):


    C_VAR0 = "Epoch ID"
    C_VAR_CYCLE = "Cycle ID"
    C_VAR_DAY = "Day"
    C_VAR_SEC = "Second"
    C_VAR_MICROSEC = "Microsecond"


## -------------------------------------------------------------------------------------------------
    def __init__(self, p_variables:list):

        self.space = p_variables

        self.variables = [self.C_VAR_CYCLE, self.C_VAR_DAY, self.C_VAR_SEC, self.C_VAR_MICROSEC]

        self.var_space = []
        for dim in self.space:
            self.var_space.append(dim)

        self.variables.extend(self.var_space)

        DataStoring.__init__(self,p_variables=self.variables)


## -------------------------------------------------------------------------------------------------
    def memorize_row(self, p_cycle_id, p_data):


        self.memorize(self.C_VAR_CYCLE, self.current_epoch, p_cycle_id)


        for i, var in enumerate(self.var_space):
            self.memorize(var, self.current_epoch, p_data[i])


## -------------------------------------------------------------------------------------------------
    def get_variables(self):
        return self.variables


## -------------------------------------------------------------------------------------------------
    def add_epoch(self, p_epoch_id):
        self.add_frame(p_frame_id=p_epoch_id)
        self.current_epoch = p_epoch_id






## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class SLScenario (Scenario):
    """
    To be designed.
    """

    C_TYPE = 'SL-Scenario'


## -------------------------------------------------------------------------------------------------
    def __init__(self,
                 p_mode=Mode.C_MODE_SIM,
                 p_ada: bool = True,
                 p_cycle_limit: int = 0,
                 p_visualize: bool = True,
                 p_logging=Log.C_LOG_ALL):
        """

        Parameters
        ----------
        p_mode
        p_ada
        p_cycle_limit
        p_visualize
        p_logging
        """

        self._dataset = None
        self._model : SLAdaptiveFunction = None
        self.ds : dict = {}
        self._metrics = []


        Scenario.__init__(self,
                          p_mode = p_mode,
                          p_ada = p_ada,
                          p_cycle_limit = p_cycle_limit,
                          p_visualize = p_visualize,
                          p_logging = p_logging)

        # TODO: Check if i need a cycle limit specific to models

        self.connect_dataloggers()
        # raise NotImplementedError

        if self._dataset is None:
            raise ImplementationError("Please bind your SL dataset to the _dataset attribute in the _setup method.")

        self._metrics = self._model.get_metrics()

## -------------------------------------------------------------------------------------------------
    def _run_cycle(self):

        # Check if the first run
        success = False
        error = False

        data = self._dataset.get_next()
        adapted = self._model.adapt(p_dataset = data)

        output = self._model(data[0])
        mapping = (data[0], data[1], output)
        logging_data = self._model.get_logging_data()

        for metric in self._metrics:
            logging_data.extend(metric.compute(self._model))

        if self._cycle_id >= ( self._dataset.num_batches - 1 ):
            end_of_data = True
        else:
            end_of_data = False

        if self.ds_cycles is not None:
            self.ds_cycles.memorize_row(p_cycle_id=self.get_cycle_id(), p_data = logging_data)

        if self.ds_mappings is not None:
            self.ds_mappings.memorize_row(p_cycle_id=self.get_cycle_id(), p_data= mapping)

        # get success from the model
        # Future implementation to terminate a training based on a goal criterion

        # Error computations such as Stagnation, etc.
        # Future implementation to terminate a training based on an undesirable criterion

        return success, error, adapted, end_of_data


## -------------------------------------------------------------------------------------------------
    def _setup(self, p_mode, p_ada:bool, p_visualize:bool, p_logging) -> Model:

        raise NotImplementedError


## -------------------------------------------------------------------------------------------------
    def _reset(self, p_seed):

        if self._visualize:
            self._model.init_plot()


## -------------------------------------------------------------------------------------------------
    def connect_dataloggers(self, p_mapping = None, p_cycle = None):

        self.ds_mappings = p_mapping
        self.ds_cycles = p_cycle


## -------------------------------------------------------------------------------------------------
    def get_dataset(self):
        return self._dataset


## -------------------------------------------------------------------------------------------------
    def _init_plot(self):
        pass


## -------------------------------------------------------------------------------------------------
    def _update_plot(self):
        pass





## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class SLTrainingResults(TrainingResults):

    C_NAME = "SL"

    C_FNAME_EPOCH = 'Epoch Scores'
    C_FNAME_TRAIN_SCORE = 'Training Scores'
    C_FNAME_EVAL_SCORE = 'Evaluation Scores'
    C_FNAME_TEST_SCORE = 'Test Scores'
    C_FNAME_TRAIN_MAP = 'Training Predictions'
    C_FNAME_EVAL_MAP = 'Evaluation Predictions'
    C_FNAME_TEST_MAP = 'Test Predictions'

    C_CPAR_NUM_EPOCH_TRAIN = 'Training Epochs'
    C_CPAR_NUM_EPOCH_EVAL = 'Evaluation Epochs'
    C_CPAR_NUM_EPOCH_TEST = 'Test Epochs'


## -------------------------------------------------------------------------------------------------
    def __init__(self,
                 p_scenario: SLScenario,
                 p_run,
                 p_cycle_id,
                 p_logging = Log.C_LOG_WE ):


        TrainingResults.__init__(self,
                                 p_scenario=p_scenario,
                                 p_run=p_run,
                                 p_cycle_id=p_cycle_id,
                                 p_logging=p_logging)

        self.num_epochs_train = 0
        self.num_epochs_eval = 0
        self.num_epochs_test = 0
        self.ds_epoch = None
        self.ds_cycles_train = None
        self.ds_cycles_eval = None
        self.ds_cycles_test = None
        self.ds_mapping_train = None
        self.ds_mapping_eval = None
        self.ds_mapping_test = None

## -------------------------------------------------------------------------------------------------
    def close(self):
        TrainingResults.close(self)

        self.add_custom_result(self.C_CPAR_NUM_EPOCH_TRAIN, self.num_epochs_train)
        self.add_custom_result(self.C_CPAR_NUM_EPOCH_EVAL, self.num_epochs_eval)
        self.add_custom_result(self.C_CPAR_NUM_EPOCH_TEST, self.num_epochs_test)


## -------------------------------------------------------------------------------------------------
    def _log_results(self):
        TrainingResults._log_results(self)

        self.log(Log.C_LOG_WE, "Training Epochs:", self.num_epochs_train)
        self.log(Log.C_LOG_WE, "Evaluation Epochs:", self.num_epochs_eval)
        self.log(Log.C_LOG_WE, "Test Epochs:", self.num_epochs_test)



## -------------------------------------------------------------------------------------------------
    def save(self, p_path, p_filename = 'summary.csv') -> bool:
        if not TrainingResults.save(self, p_path = p_filename):
            return False

        if self.ds_epoch is not None:
            self.ds_epoch.save_data(p_path, self.C_FNAME_EPOCH)
        if self.ds_cycles_train is not None:
            self.ds_cycles_train.save_data(p_path, self.C_FNAME_TRAIN_SCORE)
        if self.ds_cycles_eval is not None:
            self.ds_cycles_eval.save_data(p_path, self.C_FNAME_EVAL_SCORE)
        if self.ds_cycles_test is not None:
            self.ds_cycles_test.save_data(p_path, self.C_FNAME_TEST_SCORE)
        if self.ds_mapping_train is not None:
            self.ds_mapping_train.save_data(p_path, self.C_FNAME_TRAIN_MAP)
        if self.ds_mapping_eval is not None:
            self.ds_mapping_eval.save_data(p_path, self.C_FNAME_EVAL_MAP)
        if self.ds_mapping_test is not None:
            self.ds_mapping_test.save_data(p_path, self.C_FNAME_TEST_MAP)







## -------------------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
class SLTraining (Training):
    """
    To be designed.
    """

    C_NAME = 'SL'
    C_MODE_TEST = 2

    C_CLS_RESULTS = SLTrainingResults

## -------------------------------------------------------------------------------------------------
    def __init__(self,
                 p_collect_epoch_scores = True,
                 p_collect_mappings = True,
                 p_collect_cycles = True,
                 p_eval_freq = 0,
                 p_test_freq = 0,
                 **p_kwargs):

        self._collect_epoch_scores = p_collect_epoch_scores
        self._collect_mappings = p_collect_mappings
        self._collect_cycles = p_collect_cycles

        self._eval_freq = p_eval_freq
        self._test_freq = p_test_freq

        self._scenario : SLScenario = None

        Training.__init__(self, **p_kwargs)

        self._model:SLAdaptiveFunction = self.get_scenario().get_model()
        self.metric_variables = []

        for metric in self._scenario.get_metrics():
            dims = metric.get_output_space().get_dims()
            for dim in dims:
                self.metric_variables.append(dim.get_name_short())
        self._score_metric = self._model.get_score_metric()

        self._logging_space = self._model.get_logging_space()

        self._eval_freq = p_eval_freq
        self._test_freq = p_test_freq
        self._epoch_id = 0

        raise NotImplementedError


## -------------------------------------------------------------------------------------------------
    def _init_results(self) -> TrainingResults:

        Training._init_results(self)

        results = Training._init_results(self)

        self._results._ds_list = []

        if self._collect_epoch_scores:
            variables = self.metric_variables
            results.ds_epoch = SLDataStoring(variables)
            self._results._ds_list.append(results.ds_epoch)

        if self._collect_cycles:
            variables = self._logging_space.extend(self.metric_variables)
            results.ds_cycles_train = SLDataStoring(p_variables=variables)
            self._results._ds_list.append(results.ds_cycles_train)

            if self._eval_freq > 0:
                results.ds_cycles_eval = SLDataStoring(p_variables=variables)
                self._results._ds_list.append(results.ds_cycles_eval)

            if self._test_freq > 0:
                results.ds_cycles_test = SLDataStoring(p_variables=variables)
                self._results._ds_list.append(results.ds_cycles_test)


        if self._collect_mappings:
            variables = []
            for dim in self._model.get_input_space().get_dims():
                variables.append(dim.get_name_long())
            for dim in self._model.get_output_space().get_dims():
                variables.append(dim.get_name_long())
            for dim in self._model.get_output_space().get_dims():
                variables.append("pred"+dim.get_name_long())

            results.ds_mapping_train = SLDataStoring(p_variables=variables)
            if self._eval_freq > 0:
                results.ds_mapping_eval = SLDataStoring(p_variables=variables)
            if self._test_freq > 0:
                results.ds_mapping_test = SLDataStoring(p_variables=variables)


        self._scenario.connect_datalogger(p_mapping = results.ds_mapping_train, p_cycle = results.ds_cycles_train)


        return results


## -------------------------------------------------------------------------------------------------
    def _run_cycle(self) -> bool:

        eof_training = False
        eof_epoch = False

        if self._cycles_epoch == 0:
            self._init_epoch()

        success, error, timeout, limit, adapted, end_of_data = self._scenario.run_cycle()
        self._cycles_epoch += 1

        if adapted:
            self._results.num_adaptatios += 1

        self._update_epoch()

        if end_of_data:


            if self._mode == self.C_MODE_TRAIN:
                self._results.num_train_epochs += 1

            elif self._mode == self.C_MODE_EVAL:
                self._results.num_eval_epochs += 1
                self._epoch_eval = False

            elif self._mode == self.C_MODE_TEST:
                self._results.num_test_epochs += 1
                self._epoch_test = False

            if self._epoch_eval:
                self._mode = self.C_MODE_EVAL
                self._init_eval()

            elif self._epoch_test:
                self._mode = self.C_MODE_TEST
                self._init_test()

            else:
                eof_epoch = True


        if eof_epoch:
            self._close_epoch()

        if (self._adaptation_limit > 0) and (self._results.num_adaptations == self._adaptation_limit):
            self.log(self.C_LOG_TYPE_W, 'Adaptation limit ', str(self._adaptation_limit), ' reached')
            eof_training = True


        return eof_training


## -------------------------------------------------------------------------------------------------
    def _init_epoch(self):

        self._epoch_id += 1
        self._mode = self.C_MODE_TRAIN
        self._model.switch_adaptivity(p_ada = True)

        self._scenario.get_dataset().reset(self._epoch_id)

        if self._epoch_id % self._eval_freq == 0:
            self._epoch_eval = True

        if self._epoch_id % self._test_freq == 0:
            self._epoch_test = True

        for ds in self._results._ds_list:
            ds.add_epoch(self._epoch_id)


        self._scenario.connect_datalogger(p_mapping = self._results.ds_mapping_train,
            p_cycle = self._results.ds_cycle_train)


        self._scenario.set_dataset(self._dataset_train)

        self.metric_list_train = []
        self.metric_list_eval = []
        self.metric_list_test = []



## -------------------------------------------------------------------------------------------------
    def setup_dataset(self):

        dataset = self._scenario.get_dataset()

        dataset.setup()


## -------------------------------------------------------------------------------------------------
    def _update_epoch(self):


        if self._mode == self.C_MODE_TRAIN:
            self.metric_list_train.append(self._model._prev_metrics)
        elif self._mode == self.C_MODE_EVAL:
            self.metric_list_eval.append(self._model._prev_metrics)
        elif self._mode == self.C_MODE_TEST:
            self.metric_list_test.append(self._model._prev_metrics)


## -------------------------------------------------------------------------------------------------
    def _close_epoch(self):


        score_train = np.nanmean(self.metric_list_train, dtype=float, axis=0)
        score_eval = np.nanmean(self.metric_list_eval, dtype=float, axis=0)
        score_val = np.nanmean(self.metric_list_test, dtype=float, axis=0)

        score = [*score_train, *score_eval, *score_val]
        self._results.ds_epoch.memorize_row(p_data=score)

        score_metric_value = score_eval[self.metric_variables.index(self._score_metric.get_state_space().get_dims()[0].get_name_long())]

        if self._results.highscore < score_metric_value:
            self._results.highscore = score_metric_value

        self._cycles_epoch = 0


## -------------------------------------------------------------------------------------------------
    def _init_eval(self):
        
        self._model.switch_adaptivity(p_ada=False)
        self._mode = self.C_MODE_EVAL
        self._scenario.connect_datalogger(p_mapping=self._results.ds_mapping_eval, p_cycle=self._results.ds_cycle_eval)
        self._scenario.get_dataset().set_mode("evaluation")


## -------------------------------------------------------------------------------------------------
    def _init_test(self):

        self._model.switch_adaptivity(p_ada=False)
        self._mode = self.C_MODE_TEST
        self._scenario.connect_datalogger(p_mapping=self._results.ds_mapping_test, p_cycle=self._results.ds_cycle_test)
        self._scenario.get_dataset().set_mode("test")




