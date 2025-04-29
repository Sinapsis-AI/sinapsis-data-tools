# -*- coding: utf-8 -*-
from abc import abstractmethod
from typing import Any

import numpy as np
from sinapsis_core.data_containers.data_packet import DataContainer
from sinapsis_core.template_base.base_models import TemplateAttributes
from sinapsis_core.template_base.template import Template


class MLBaseInference(Template):
    """Abstract base class for machine learning model inference.

    This class provides a framework for loading a trained model
    and using it to make predictions on new data.
    """

    class AttributesBaseModel(TemplateAttributes):
        """Attributes for the MLBaseInference template.

        Attributes:
            model_path (str): Path to the saved model file.
            generic_field_key (str): Key of the generic field where data is stored.
        """

        model_path: str
        generic_field_key: str

    def __init__(self, attributes: TemplateAttributes) -> None:
        super().__init__(attributes)
        self.model = self.load_model(self.attributes.model_path)

    def get_data(self, container: DataContainer) -> Any:
        """Get the data from the data container

        Args:
            container (DataContainer): The data container with the data

        Returns:
            Any: The data from the generic field
        """
        return self._get_generic_data(container, self.attributes.generic_field_key)

    @staticmethod
    def data_is_valid(data: Any) -> bool:
        """Check if the data is valid for inference

        Args:
            data (Any): The data to validate

        Returns:
            bool: True if the data is valid, False otherwise
        """
        return data is not None

    def preprocess_data(self, data: Any) -> Any:
        """
        This method can be overridden by subclasses to implement
        specific preprocessing steps

        Args:
            data (Any): The data to preprocess

        Returns:
            Any: The preprocessed data
        """
        try:
            data.pop("target")
        except (KeyError, IndexError):
            self.logger.info("No target column")
        return data

    @abstractmethod
    def load_model(self, model_path: str) -> Any:
        """
        This abstract method should be implemented by subclasses to define
        how the model should be loaded

        Args:
            model_path (str): Path to the saved model file

        Returns:
            Any: The loaded model
        """

    def predict(self, data: np.ndarray) -> np.ndarray:
        """Generate predictions using the loaded model

        Args:
            data (Any): The data to make predictions on

        Returns:
            np.ndarray: The model's predictions
        """

        return self.model.predict(data)

    def execute(self, container: DataContainer) -> DataContainer:
        """
        Gets the data, validates it, preprocesses it, makes predictions,
        and stores the results

        Args:
            container (DataContainer): The data container with the input data

        Returns:
            DataContainer: The container with added predictions
        """
        data = self.get_data(container)

        if not self.data_is_valid(data):
            self.logger.warning("Invalid or missing data")
            return container

        data = self.preprocess_data(data)
        predictions = self.predict(data)

        self._set_generic_data(container, predictions)

        return container
