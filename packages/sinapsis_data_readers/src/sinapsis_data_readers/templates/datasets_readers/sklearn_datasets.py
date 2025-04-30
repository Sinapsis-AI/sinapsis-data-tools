# -*- coding: utf-8 -*-

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

from sinapsis_data_readers.helpers import sklearn_dataset_subset
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

    UIProperties = UIPropertiesMetadata(category="SKLearn")

    class AttributesBaseModel(TemplateAttributes):
        """Attributes for the template
        split_dataset (bool): flag to indicate if dataset should be split
        train_size (float): size of the train sample if the dataset is split.
        store_as_time_series: Flag to store the dataset as a TimeSeries packet
        """

        split_dataset: bool = True
        train_size: float = 1
        store_as_time_series: bool = False

    def __init__(self, attributes: TemplateAttributeType) -> None:
        super().__init__(attributes)
        self.dataset_attributes = getattr(self.attributes, self.wrapped_callable.__name__)

    @staticmethod
    def parse_results(results: pd.DataFrame) -> pd.DataFrame:
        """Parses the dataset as a pandas dataframe with the feature names as columns

        Args:
            results (pd.DataFrame): scikit-learn dataset as a pd.DataFrame

        Returns:
            pd.DataFrame: the dataframe with the columns being the feature_names and
            the additional column for target values

        """

        data_frame = pd.DataFrame(data=results.data, columns=results.feature_names)
        data_frame[TARGET] = results.target
        return data_frame

    @staticmethod
    def split_dataset(results: pd.DataFrame, split_size: float) -> TabularDatasetSplit:
        """Method to split the dataset into training and testing samples"""
        x_vals = results.drop(columns=[TARGET], axis=1)
        y_vals = results[TARGET]
        x_train, x_test, y_train, y_test = train_test_split(x_vals, y_vals, train_size=split_size, random_state=0)
        split_data = TabularDatasetSplit(
            x_train=pd.DataFrame(x_train),
            x_test=pd.DataFrame(x_test),
            y_train=pd.DataFrame(y_train),
            y_test=pd.DataFrame(y_test),
        )

        return split_data

    def execute(self, container: DataContainer) -> DataContainer:
        sklearn_dataset = self.wrapped_callable.__func__(**self.dataset_attributes.model_dump())
        dataset = self.parse_results(sklearn_dataset)
        if self.attributes.store_as_time_series:
            time_series_packet = TimeSeriesPacket(content=dataset)
            container.time_series.append(time_series_packet)

        if self.attributes.split_dataset:
            split_dataset = self.split_dataset(dataset, split_size=self.attributes.train_size)
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
