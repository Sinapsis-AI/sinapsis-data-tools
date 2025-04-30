# -*- coding: utf-8 -*-
from typing import cast

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict
from sinapsis_core.data_containers.data_packet import DataContainer
from sinapsis_core.template_base import Template
from sinapsis_core.template_base.base_models import TemplateAttributes, UIPropertiesMetadata
from sinapsis_core.template_base.dynamic_template import (
    BaseDynamicWrapperTemplate,
    WrapperEntryConfig,
)
from sinapsis_core.template_base.dynamic_template_factory import make_dynamic_template
from sinapsis_core.utils.env_var_keys import SINAPSIS_BUILD_DOCS
from sinapsis_data_readers.templates.datasets_readers.dataset_splitter import (
    TabularDatasetSplit,
)
from sklearn import manifold


class ManifoldResults(BaseModel):
    """Class to store the results of manifold learning.

    Attributes:
        labels (np.ndarray | list): The original labels.
        x_transformed (np.ndarray): The data after dimensionality reduction.
    """

    labels: np.ndarray | list
    x_transformed: np.ndarray

    model_config = ConfigDict(arbitrary_types_allowed=True)


class SKLearnManifold(BaseDynamicWrapperTemplate):
    """
    This template dynamically wraps sklearn's manifold module,
    providing access to dimensionality reduction techniques like
    TSNE, MDS, Isomap, etc.
    """

    WrapperEntry = WrapperEntryConfig(
        wrapped_object=manifold,
        signature_from_doc_string=True,
        exclude_module_atts=["locally_linear_embedding"],
        force_init_as_method=False,
    )

    UIProperties = UIPropertiesMetadata(category="SKLearn")

    class AttributesBaseModel(TemplateAttributes):
        """Attributes for the SKLearnManifold template.

        Attributes:
            generic_field_key (str): Key of the generic field
                where the input data is stored.
        """

        generic_field_key: str

    def __init__(self, attributes: TemplateAttributes) -> None:
        super().__init__(attributes)
        self.manifold_model = self.wrapped_callable

    @staticmethod
    def reshape_arrays(feature_arrays: pd.DataFrame) -> np.ndarray:
        """
        Converts a list of arrays into a 2D numpy array suitable for
        manifold learning algorithms

        Args:
            feature_arrays (list): List of feature arrays

        Returns:
            np.ndarray: Reshaped array suitable for manifold learning
        """
        array_data = np.array(feature_arrays)
        return array_data.reshape(array_data.shape[0], -1)

    def get_dataset(self, container: DataContainer) -> TabularDatasetSplit | None:
        """Get the dataset from the data container

        Args:
            container (DataContainer): The data container with the dataset

        Returns:
            TabularDatasetSplit | None: The dataset from the generic field,
                or None if not found
        """
        dataset = self._get_generic_data(container, self.attributes.generic_field_key)
        dataset = cast(TabularDatasetSplit, dataset)
        if dataset:
            return dataset
        return None

    def process_dataset(self, dataset: TabularDatasetSplit) -> ManifoldResults | None:
        """
        Extracts the training data, reshapes it, and applies the
        manifold learning transformation

        Args:
            dataset (TabularDatasetSplit): The dataset to process

        Returns:
            ManifoldResults | None: Results of the manifold transformation,
                or None if the dataset is empty
        """
        x_train = dataset.x_train
        y_train = dataset.y_train

        if x_train is None or x_train.empty:
            return None

        x_train_reshaped = self.reshape_arrays(x_train)
        x_transformed = self.manifold_model.fit_transform(x_train_reshaped)

        return ManifoldResults(labels=y_train, x_transformed=x_transformed)

    def execute(self, container: DataContainer) -> DataContainer:
        """
        Gets the dataset, processes it using the manifold learning algorithm,
        and stores the results

        Args:
            container (DataContainer): The data container with the dataset

        Returns:
            DataContainer: The container with added manifold learning results
        """
        dataset = self.get_dataset(container)
        if not dataset:
            self.logger.warning("There is no dataset to process")
            return container

        results = self.process_dataset(dataset)

        if results is not None:
            self._set_generic_data(container, results)

        return container


def __getattr__(name: str) -> Template:
    """
    Only create a template if it's imported, this avoids creating all the base models for all templates
    and potential import errors due to not available packages.
    """
    if name in SKLearnManifold.WrapperEntry.module_att_names:
        return make_dynamic_template(name, SKLearnManifold)
    raise AttributeError(f"template `{name}` not found in {__name__}")


__all__ = SKLearnManifold.WrapperEntry.module_att_names


if SINAPSIS_BUILD_DOCS:
    dynamic_templates = [__getattr__(template_name) for template_name in __all__]
    for template in dynamic_templates:
        globals()[template.__name__] = template
        del template
