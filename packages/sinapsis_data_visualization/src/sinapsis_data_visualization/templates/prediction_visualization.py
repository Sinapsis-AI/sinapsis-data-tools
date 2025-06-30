# -*- coding: utf-8 -*-
import numpy as np
from sinapsis_core.data_containers.data_packet import DataContainer
from sinapsis_data_visualization.helpers.tags import Tags
from sinapsis_data_visualization.templates.base_visualization_template import (
    BasePlotAttributes,
    BaseVisualizationTemplate,
    PlotTypes,
)
from sklearn.metrics import auc, confusion_matrix, precision_recall_curve, roc_curve


class PredictionPlotTypes(PlotTypes):
    """Extends plot types with model prediction visualization types"""

    CONFUSION_MATRIX = "confusion_matrix"
    ROC_CURVE = "roc_curve"
    PRECISION_RECALL_CURVE = "precision_recall_curve"


class PredictionVisualizationAttributes(BasePlotAttributes):
    """
    Attributes for prediction visualization.

    Attributes:
        generic_field_key (str): Key to access prediction results in generic_data (inherited from BasePlotAttributes).
        generic_training_key (str): Key to access training data in generic_data.
        target_column (str): Name of the target column if needed.
        confusion_matrix (bool): Whether to create a confusion matrix.
        roc_curve (bool): Whether to create a ROC curve.
        precision_recall_curve (bool): Whether to create a precision-recall curve.
    """

    generic_training_key: str = "fetch_openmlWrapper_viz"
    target_column: str = "target"
    confusion_matrix: bool = True
    roc_curve: bool = True
    precision_recall_curve: bool = True


PredictionVisualizationUIProperties = BaseVisualizationTemplate.UIProperties
PredictionVisualizationUIProperties.tags.extend([Tags.CONFUSION, Tags.CURVES, Tags.METRICS])


class PredictionVisualization(BaseVisualizationTemplate):
    """
    Template for visualizing model predictions with evaluation metrics.

    This template supports confusion matrices, ROC curves, and precision-recall curves
    for classification models.
    """

    AttributesBaseModel = PredictionVisualizationAttributes
    UIProperties = PredictionVisualizationUIProperties

    def get_data_for_visualization(self, container: DataContainer) -> tuple[object, object]:
        """
        Extracts prediction and training data from the container.

        Args:
            container (DataContainer): Data container.

        Returns:
            tuple[object, object]: Tuple containing prediction results and training data.
        """
        predictions_data = self._get_generic_data(container, self.attributes.generic_field_key)

        if not predictions_data:
            self.logger.warning(f"No prediction data found with key '{self.attributes.generic_field_key}'")
            return (None, None)

        training_data = self._get_generic_data(container, self.attributes.generic_training_key)

        return predictions_data, training_data

    def _extract_true_and_predicted_values(self, data: tuple[object, object]) -> tuple[np.ndarray, np.ndarray]:
        """
        Extracts true and predicted values from data in a flexible way.

        Args:
            data (tuple[object, object]): Tuple containing prediction results and training data.

        Returns:
            tuple[np.ndarray, np.ndarray]: True values and predicted values.
        """
        predictions, training_data = data
        y_true = None
        y_pred = None

        if hasattr(predictions, "predictions"):
            y_pred = predictions.predictions

        if training_data is not None and hasattr(training_data, "y_test"):
            y_test = training_data.y_test
            y_true = y_test.values.flatten() if hasattr(y_test, "values") else np.array(y_test)

        return y_true, y_pred

    def prepare_confusion_matrix_data(self, data: tuple[object, object]) -> tuple[list[str], np.ndarray]:
        """
        Prepares data for a confusion matrix plot.

        Args:
            data (tuple[object, object]): Tuple containing prediction results and training data.

        Returns:
            tuple[list[str], np.ndarray]: Class labels and confusion matrix array.
        """
        y_true, y_pred = self._extract_true_and_predicted_values(data)

        if y_true is None or y_pred is None:
            self.logger.warning("Could not extract true and predicted values for confusion matrix")
            return [], np.array([])

        class_labels = sorted(set(np.concatenate([np.unique(y_true), np.unique(y_pred)])))
        class_labels = [str(label) for label in class_labels]

        cm = confusion_matrix(y_true, y_pred)

        return class_labels, cm

    def prepare_roc_curve_data(self, data: tuple[object, object]) -> tuple[list[str], np.ndarray]:
        """
        Prepares data for a ROC curve plot.

        Args:
            data (tuple[object, object]): Tuple containing prediction results and training data.

        Returns:
            tuple[list[str], np.ndarray]: Curve label and FPR/TPR values.
        """
        y_true, y_pred = self._extract_true_and_predicted_values(data)

        if y_true is None or y_pred is None:
            self.logger.warning("Could not extract true and predicted values for ROC curve")
            return [], np.array([])

        fpr, tpr, _ = roc_curve(y_true, y_pred)
        roc_auc = auc(fpr, tpr)

        curve_label = [f"ROC Curve (AUC = {roc_auc:.3f})"]

        curve_data = np.column_stack((fpr, tpr))

        return curve_label, curve_data

    def prepare_precision_recall_data(self, data: tuple[object, object]) -> tuple[list[str], np.ndarray]:
        """
        Prepares data f or a precision-recall curve plot.

        Args:
            data (tuple[object, object]): Tuple containing prediction results and training data.

        Returns:
            tuple[list[str], np.ndarray]: Curve label and precision/recall values.
        """
        y_true, y_pred = self._extract_true_and_predicted_values(data)

        if y_true is None or y_pred is None:
            self.logger.warning("Could not extract true and predicted values for precision-recall curve")
            return [], np.array([])

        precision, recall, _ = precision_recall_curve(y_true, y_pred)

        ap = np.mean(precision)

        curve_label = [f"Precision-Recall (AP = {ap:.3f})"]

        curve_data = np.column_stack((precision, recall))

        return curve_label, curve_data

    def generate_visualizations(self, container: DataContainer, data: tuple[object, object]) -> None:
        """
        Generates all requested visualizations for model predictions.

        Args:
            container (DataContainer): Data container.
            data (tuple[object, object]): Tuple containing prediction results and training data.
        """
        if not data or len(data) != 2 or not hasattr(data[0], "predictions"):
            self.logger.warning("No prediction data available for visualization")
            return

        if self.attributes.confusion_matrix:
            labels, cm_data = self.prepare_confusion_matrix_data(data)
            if len(labels) > 0 and cm_data.size > 0:
                self.plot_and_save(
                    container=container,
                    plot_type=PredictionPlotTypes.CONFUSION_MATRIX,
                    labels=labels,
                    counts=cm_data,
                )

        if self.attributes.roc_curve:
            labels, roc_data = self.prepare_roc_curve_data(data)
            if len(labels) > 0 and roc_data.size > 0:
                self.plot_and_save(
                    container=container,
                    plot_type=PredictionPlotTypes.ROC_CURVE,
                    labels=labels,
                    counts=roc_data,
                )

        if self.attributes.precision_recall_curve:
            labels, pr_data = self.prepare_precision_recall_data(data)
            if len(labels) > 0 and pr_data.size > 0:
                self.plot_and_save(
                    container=container,
                    plot_type=PredictionPlotTypes.PRECISION_RECALL_CURVE,
                    labels=labels,
                    counts=pr_data,
                )
