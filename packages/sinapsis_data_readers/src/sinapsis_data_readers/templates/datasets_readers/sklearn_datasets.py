# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from sinapsis_core.data_containers.data_packet import DataContainer, TimeSeriesPacket
from sinapsis_core.template_base import Template
from sinapsis_core.template_base.base_models import TemplateAttributes, TemplateAttributeType, UIPropertiesMetadata
from sinapsis_core.template_base.dynamic_template import (
    BaseDynamicWrapperTemplate,
    WrapperEntryConfig,
)
from sinapsis_core.template_base.dynamic_template_factory import make_dynamic_template
from sinapsis_core.template_base.multi_execute_template import (
    execute_template_n_times_wrapper,
)
from sinapsis_core.utils.env_var_keys import SINAPSIS_BUILD_DOCS
from sklearn.model_selection import train_test_split
from sklearn.utils import Bunch

from sinapsis_data_readers.helpers import sklearn_dataset_subset
from sinapsis_data_readers.helpers.tags import Tags
from sinapsis_data_readers.templates.datasets_readers.dataset_splitter import (
    TabularDatasetSplit,
)

TARGET: str = "target"


class SKLearnDatasets(BaseDynamicWrapperTemplate):
    """Template to select a sklearn dataset and from the sklearn.datasets module
    and insert into the container as a pandas dataframe in the generic_data field of
    the DataContainer.
    The available datasets are those starting with 'load' and 'fetch' from
    'https://scikit-learn.org/stable/api/sklearn.datasets.html'

    Usage example:
        agent:
          name: my_test_agent
        templates:
        - template_name: InputTemplate
          class_name: InputTemplate
          attributes: {}
        - template_name: load_irisWrapper
          class_name: load_irisWrapper ## Note that since this is a dynamic template
          template_input: InputTemplate         ##, the class name depends on the actual dataset being imported
          attributes:
            split_dataset: true
            train_size: 1
            load_iris:
              return_X_y: false
              as_frame: false

    """

    WrapperEntry = WrapperEntryConfig(wrapped_object=sklearn_dataset_subset, signature_from_doc_string=True)

    UIProperties = UIPropertiesMetadata(
        category="SKLearn",
        tags=[Tags.DATASET, Tags.DATAFRAMES, Tags.DYNAMIC, Tags.READERS],
    )

    class AttributesBaseModel(TemplateAttributes):
        """Attributes for the template
        split_dataset (bool): flag to indicate if dataset should be split
        train_size (float): size of the train sample if the dataset is split.
        store_as_time_series: Flag to store the dataset as a TimeSeries packet
        """

        split_dataset: bool = True
        train_size: float = 0.9
        store_as_time_series: bool = False

    def __init__(self, attributes: TemplateAttributeType) -> None:
        super().__init__(attributes)
        self.dataset_attributes = getattr(self.attributes, self.wrapped_callable.__name__)

    @staticmethod
    def process_bunch(bunch: Bunch) -> tuple:
        data = bunch.get("data")
        original_target = bunch.get("target")

        target = np.asarray(original_target)
        target = target.reshape(-1, 1) if target.ndim == 1 else target
        feature_column = bunch.get("feature_names", None)
        target_column = bunch.get("target_names", None)
        if target.shape[1] == 1:
            target_column = ["target"]
        elif target_column is not None and len(target_column) == target.shape[1]:
            target_column = list(target_column)
        else:
            target_column = [f"target_{i}" for i in range(target.shape[1])]
        return data, target, feature_column, target_column

    def parse_results(self, results: pd.DataFrame) -> tuple[pd.DataFrame, list, list, int]:
        """Parses the dataset as a pandas dataframe with the feature names as columns

        Args:
            results (pd.DataFrame): scikit-learn dataset as a pd.DataFrame

        Returns:
            pd.DataFrame: the dataframe with the columns being the feature_names and
            the additional column for target values

        """
        if isinstance(results, tuple):
            data = results[0]
            target = results[1]
            feature_column = None
            target_column = None
        elif isinstance(results, Bunch):
            data, target, feature_column, target_column = self.process_bunch(results)
        else:
            try:
                data = results.data

            except (KeyError, AttributeError, ValueError):
                data = None
            try:
                target = results.target
            except (KeyError, AttributeError, ValueError):
                target = None
            try:
                feature_column = results.feature_names
                target_column = results.target_names
            except AttributeError:
                feature_column = None
                target_column = None
        _, n_features = data.shape

        feature_data_frame = pd.DataFrame(data=data, columns=feature_column)
        target_data_frame = pd.DataFrame(data=target, columns=target_column)
        data_frame = pd.concat([feature_data_frame, target_data_frame], axis=1)
        return data_frame, feature_column, target_column, n_features

    @staticmethod
    def split_dataset(
        results: pd.DataFrame, feature_name_cols: list, target_name_cols: list, n_features: int, split_size: float
    ) -> dict:
        """Method to split the dataset into training and testing samples"""
        if feature_name_cols:
            X = results[feature_name_cols]
            y = results[target_name_cols]
        else:
            X = results.iloc[:, :n_features]
            y = results.iloc[:, n_features:]


        x_train, x_test, y_train, y_test = train_test_split(X, y, train_size=split_size, random_state=0)
        split_data = TabularDatasetSplit(
            x_train=pd.DataFrame(x_train),
            x_test=pd.DataFrame(x_test),
            y_train=pd.DataFrame(y_train),
            y_test=pd.DataFrame(y_test),
        )

        return split_data.model_dump_json(indent=2)

    def execute(self, container: DataContainer) -> DataContainer:
        sklearn_dataset = self.wrapped_callable.__func__(**self.dataset_attributes.model_dump())
        dataset, feature_columns, target_columns, n_features = self.parse_results(sklearn_dataset)
        if self.attributes.store_as_time_series:
            time_series_packet = TimeSeriesPacket(content=dataset)
            container.time_series.append(time_series_packet)

        if self.attributes.split_dataset:
            split_dataset = self.split_dataset(
                dataset, feature_columns, target_columns, n_features, split_size=self.attributes.train_size
            )
            self._set_generic_data(container, split_dataset)
        if sklearn_dataset and not self.attributes.split_dataset:
            self._set_generic_data(container, dataset)

        return container


@execute_template_n_times_wrapper
class ExecuteNTimesSkLearnDatasets(SKLearnDatasets):
    """The template extends the functionality of the SKLearnDatasets template
    by reading a scikit-learn dataset n times
    """

    WrapperEntry = WrapperEntryConfig(
        wrapped_object=sklearn_dataset_subset,
        signature_from_doc_string=True,
        template_name_suffix="ExecuteNTimes",
    )


def __getattr__(name: str) -> Template:
    """
    Only create a template if it's imported, this avoids creating all the base models for all templates
    and potential import errors due to not available packages.
    """
    if name in SKLearnDatasets.WrapperEntry.module_att_names:
        return make_dynamic_template(name, SKLearnDatasets)
    if name in ExecuteNTimesSkLearnDatasets.WrapperEntry.module_att_names:
        return make_dynamic_template(name, ExecuteNTimesSkLearnDatasets)
    raise AttributeError(f"template `{name}` not found in {__name__}")


__all__ = SKLearnDatasets.WrapperEntry.module_att_names + ExecuteNTimesSkLearnDatasets.WrapperEntry.module_att_names


if SINAPSIS_BUILD_DOCS:
    dynamic_templates = [__getattr__(template_name) for template_name in __all__]
    for template in dynamic_templates:
        globals()[template.__name__] = template
        del template
