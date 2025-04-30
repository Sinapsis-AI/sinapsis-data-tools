# -*- coding: utf-8 -*-
from typing import Any

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
from sktime import datasets
from sktime.split import temporal_train_test_split

from sinapsis_data_readers.templates.datasets_readers.dataset_splitter import (
    TabularDatasetSplit,
)

EXCLUDE_MODULES = ["load_forecastingdata", "DATASET_NAMES_FPP3"]


class SKTimeDatasets(BaseDynamicWrapperTemplate):
    """Template to process SKTime datasets module.

    The DataContainer stores the Pandas Series or DataFrame in the generic_field_key
    defined in the attributes. To check the available datasets, refer to
    'https://www.sktime.net/en/stable/api_reference/datasets.html'

    Usage example:
        agent:
          name: my_test_agent
        templates:
        - template_name: InputTemplate
          class_name: InputTemplate
          attributes: {}
        - template_name: load_airlineWrapper
          class_name: load_airlineWrapper
          template_input: InputTemplate
          attributes:
            split_dataset: true
            train_size: 0.7
            load_airline:
              {}
    """

    WrapperEntry = WrapperEntryConfig(
        wrapped_object=datasets,
        signature_from_doc_string=True,
        exclude_module_atts=EXCLUDE_MODULES,
    )
    UIProperties = UIPropertiesMetadata(category="SKTime")

    class AttributesBaseModel(TemplateAttributes):
        """Attributes for the SKTimeDatasets template

        Attributes:
            split_dataset (bool): Flag to indicate if dataset should be split.
                Defaults to True.
            train_size (float): Size of the train sample if the dataset is split.
                Defaults to 0.7.
            store_as_time_series: Flag to store the dataset as a TimeSeries packet
        """

        split_dataset: bool = True
        train_size: float = 0.7
        store_as_time_series: bool = False

    def __init__(self, attributes: TemplateAttributeType) -> None:
        super().__init__(attributes)
        self.dataset_attributes = getattr(self.attributes, self.wrapped_callable.__name__)

    def split_time_series_dataset(self, dataset: Any) -> TabularDatasetSplit:
        """Split a time series dataset into training and testing sets

        Args:
            dataset: The time series dataset to split

        Returns:
            TabularDatasetSplit: Object containing the split time series data
        """
        y_train, y_test = temporal_train_test_split(dataset, train_size=self.attributes.train_size)
        return TabularDatasetSplit(
            x_train=pd.DataFrame(index=y_train.index),
            x_test=pd.DataFrame(index=y_test.index),
            y_train=pd.DataFrame(y_train),
            y_test=pd.DataFrame(y_test),
        )

    def split_classification_dataset(self, X: Any, y: Any) -> TabularDatasetSplit:
        """Split a classification dataset into training and testing sets

        Args:
            X: The feature data
            y: The target labels

        Returns:
            TabularDatasetSplit: Object containing the split dataset.
        """
        X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=self.attributes.train_size, random_state=0)
        return TabularDatasetSplit(
            x_train=pd.DataFrame(X_train),
            x_test=pd.DataFrame(X_test),
            y_train=pd.DataFrame(y_train),
            y_test=pd.DataFrame(y_test),
        )

    def execute(self, container: DataContainer) -> DataContainer:
        """Execute the SKTimeDatasets template to load and process a dataset.

        Loads a dataset from sktime and optionally splits it into training
        and testing sets before storing it in the container.

        Args:
            container (DataContainer): The data container to store the dataset in.

        Returns:
            DataContainer: The container with the dataset added to it.
        """
        dataset = self.wrapped_callable.__func__(**self.dataset_attributes.model_dump())
        split_dataset = dataset
        if isinstance(dataset, tuple):
            if self.attributes.split_dataset:
                split_dataset = self.split_classification_dataset(dataset[0], dataset[1])
        else:
            if self.attributes.split_dataset:
                split_dataset = self.split_time_series_dataset(dataset)

        if self.attributes.store_as_time_series:
            time_series_packet = TimeSeriesPacket(content=split_dataset)
            container.time_series.append(time_series_packet)
        else:
            self._set_generic_data(container, split_dataset)

        return container


@execute_template_n_times_wrapper
class ExecuteNTimesSKTimeDatasets(SKTimeDatasets):
    """This template extends the functionality of the SKTimeDatasets template
    by loading the sktime dataset n times.

    This is useful for running the same dataset loading operation multiple
    times with different parameters or for benchmark purposes.
    """

    WrapperEntry = WrapperEntryConfig(
        wrapped_object=datasets,
        signature_from_doc_string=True,
        exclude_module_atts=EXCLUDE_MODULES,
        template_name_suffix="ExecuteNTimes",
    )


def __getattr__(name: str) -> Template:
    """
    Only create a template if it's imported, this avoids creating all the base models for all templates
    and potential import errors due to not available packages.
    """
    if name in SKTimeDatasets.WrapperEntry.module_att_names:
        return make_dynamic_template(name, SKTimeDatasets)
    if name in ExecuteNTimesSKTimeDatasets.WrapperEntry.module_att_names:
        return make_dynamic_template(name, ExecuteNTimesSKTimeDatasets)
    raise AttributeError(f"template `{name}` not found in {__name__}")


__all__ = SKTimeDatasets.WrapperEntry.module_att_names + ExecuteNTimesSKTimeDatasets.WrapperEntry.module_att_names


if SINAPSIS_BUILD_DOCS:
    dynamic_templates = [__getattr__(template_name) for template_name in __all__]
    for template in dynamic_templates:
        globals()[template.__name__] = template
        del template
