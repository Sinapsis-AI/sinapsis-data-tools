# -*- coding: utf-8 -*-
import os
from abc import abstractmethod
from typing import Any

import numpy as np
from sinapsis_core.data_containers.data_packet import DataContainer
from sinapsis_core.template_base.base_models import TemplateAttributes
from sinapsis_core.template_base.dynamic_template import BaseDynamicWrapperTemplate
from sinapsis_data_readers.templates.datasets_readers.dataset_splitter import TabularDatasetSplit
from sklearn.base import is_classifier, is_regressor
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
)

from sinapsis_data_analysis.helpers.model_metrics import (
    ModelMetrics,
    ModelPredictionResults,
)


class MLBaseAttributes(TemplateAttributes):
    """Base attributes for machine learning model templates.

    Attributes:
        generic_field_key (str): Key of the generic field where datasets are stored.
        model_save_path (str): Path where the trained model will be saved.
    """

    generic_field_key: str
    model_save_path: str


class MLBaseTraining(BaseDynamicWrapperTemplate):
    """
    This abstract class provides common functionality for loading data,
    training models, making predictions, calculating metrics, and saving
    models.


    """

    AttributesBaseModel = MLBaseAttributes

    def __init__(self, attributes: TemplateAttributes) -> None:
        """Initialize the MLBase template.

        Args:
            attributes (TemplateAttributes): The attributes for this template.
        """
        super().__init__(attributes)
        self.model = self.wrapped_callable
        self.trained_model = None

    def get_dataset(self, container: DataContainer) -> Any:
        """Get the dataset from the data container.

        Args:
            container (DataContainer): The data container with the dataset.

        Returns:
            Any: The dataset from the generic field.
        """
        return self._get_generic_data(container, self.attributes.generic_field_key)

    @staticmethod
    def dataset_is_valid(dataset: Any) -> bool:
        """Check if the dataset is valid

        Args:
            dataset (Any): The dataset to validate.

        Returns:
            bool: True if the dataset is valid, False otherwise.
        """
        return dataset is not None

    def process_dataset(self, dataset: TabularDatasetSplit) -> tuple | None:
        """
        Extracts x_train, y_train, x_test, y_test from the dataset

        Args:
            dataset (Any): The dataset to process

        Returns:
            tuple | None: A tuple containing (x_train, y_train, x_test, y_test)
                or None if the dataset doesn't have the expected attributes
        """
        try:
            x_train = dataset.x_train
            y_train = dataset.y_train
            x_test = dataset.x_test
            y_test = dataset.y_test

            return x_train, y_train, x_test, y_test
        except AttributeError:
            self.logger.warning("Dataset doesn't have the expected attributes")
            return None

    def train_model(self, x_train: Any, y_train: Any) -> None:
        """Train the model using the training data

        Args:
            x_train (Any): The training features
            y_train (Any): The training targets
        """
        self.trained_model = self.model.fit(x_train, y_train)

    @staticmethod
    def calculate_classification_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> ModelMetrics:
        """Calculate metrics specific to classification models

        Args:
            y_true (np.ndarray): The ground truth labels
            y_pred (np.ndarray): The predicted labels

        Returns:
            ModelMetrics: Object containing classification metrics
        """
        metrics = ModelMetrics()
        metrics.accuracy = float(accuracy_score(y_true, y_pred))
        metrics.precision = float(precision_score(y_true, y_pred, average="weighted", zero_division=0))
        metrics.recall = float(recall_score(y_true, y_pred, average="weighted", zero_division=0))
        metrics.f1_score = float(f1_score(y_true, y_pred, average="weighted", zero_division=0))
        return metrics

    @staticmethod
    def calculate_regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> ModelMetrics:
        """Calculate metrics specific to regression models

        Args:
            y_true (np.ndarray): The ground truth values
            y_pred (np.ndarray): The predicted values

        Returns:
            ModelMetrics: Object containing regression metrics
        """
        metrics = ModelMetrics()
        metrics.r2_score = float(r2_score(y_true, y_pred))
        metrics.mean_squared_error = float(mean_squared_error(y_true, y_pred))
        metrics.mean_absolute_error = float(mean_absolute_error(y_true, y_pred))

        return metrics

    def calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> ModelMetrics:
        """
        Detects whether the model is a classifier or regressor and calculates
        the appropriate metrics

        Args:
            y_true (np.ndarray): The ground truth values/labels
            y_pred (np.ndarray): The predicted values/labels

        Returns:
            ModelMetrics: Object containing the appropriate metrics
        """
        if self.trained_model is not None:
            if is_classifier(self.trained_model):
                return self.calculate_classification_metrics(y_true, y_pred)
            elif is_regressor(self.trained_model):
                return self.calculate_regression_metrics(y_true, y_pred)
        return ModelMetrics()

    def generate_predictions(self, x_test: np.ndarray, y_test: np.ndarray) -> ModelPredictionResults | None:
        """
        Uses the trained model to make predictions on the test data
        and calculates the appropriate metrics

        Args:
            x_test (np.ndarray): The test features
            y_test (np.ndarray): The test targets

        Returns:
            ModelPredictionResults: Object containing predictions and metrics
        """
        if self.trained_model is not None:
            predictions = self.trained_model.predict(x_test)

            metrics = self.calculate_metrics(y_test, predictions)

            return ModelPredictionResults(predictions=predictions, metrics=metrics)
        return None

    def handle_model_training(self, processed_data: tuple) -> ModelPredictionResults | None:
        """Handle the model training and prediction workflow.

        Extracts data from the processed dataset, trains the model,
        and generates predictions.

        Args:
            processed_data (tuple): Tuple containing training and testing data.

        Returns:
            ModelPredictionResults: Object containing predictions and metrics.
        """
        x_train, y_train, x_test, y_test = processed_data

        self.train_model(x_train, y_train)
        return self.generate_predictions(x_test, y_test)

    def save_model(self) -> None:
        """
        Creates the necessary directories and calls the implementation-specific
        method to save the model to the path specified in attributes.
        If no trained model exists or an error occurs, it will be logged.
        """
        if self.trained_model is None:
            self.logger.error("No model to save")
            return

        try:
            os.makedirs(os.path.dirname(self.attributes.model_save_path), exist_ok=True)
            self._save_model_implementation()
            self.logger.info(f"Model saved at {self.attributes.model_save_path}")
        except (MemoryError, TypeError) as e:
            self.logger.error(f"Error saving model: {e}")

    @abstractmethod
    def _save_model_implementation(self) -> None:
        """Save the trained model using an implementation-specific method.

        This abstract method should be implemented by subclasses to define
        how the model should be serialized and saved to disk.
        """

    def execute(self, container: DataContainer) -> DataContainer:
        """
        Gets the dataset, validates it, processes it, trains the model,
        generates predictions, and stores the results

        Args:
            container (DataContainer): The data container with the dataset

        Returns:
            DataContainer: The container with added predictions and metrics
        """
        dataset = self.get_dataset(container)

        if not self.dataset_is_valid(dataset):
            self.logger.warning("Invalid or missing dataset")
            return container

        processed_data = self.process_dataset(dataset)

        if processed_data is None:
            self.logger.warning("Failed to process dataset")
            return container

        results = self.handle_model_training(processed_data)

        if results is not None:
            self._set_generic_data(container, results)
            self.save_model()

        return container
