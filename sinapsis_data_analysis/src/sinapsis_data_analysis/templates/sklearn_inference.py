# -*- coding: utf-8 -*-
from typing import Any

import joblib

from sinapsis_data_analysis.templates.ml_base_inference import MLBaseInference


class SKLearnInference(MLBaseInference):
    """Template for inference using sklearn models.

    This template loads a saved sklearn model using joblib
    and uses it to make predictions on new data.
    """

    CATEGORY = "SKLearn"

    def load_model(self, model_path: str) -> Any:
        """
        Uses joblib to load a previously saved sklearn model

        Args:
            model_path (str): Path to the saved model file

        Returns:
            Any: The loaded sklearn model
        """
        return joblib.load(model_path)
