# -*- coding: utf-8 -*-
from typing import Any

from pydantic import BaseModel, ConfigDict


class ModelMetrics(BaseModel):
    """Base class for storing model metrics"""

    accuracy: float | None = None
    precision: float | None = None
    recall: float | None = None
    f1_score: float | None = None

    r2_score: float | None = None
    mean_squared_error: float | None = None
    mean_absolute_error: float | None = None

    mape: float | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class ModelPredictionResults(BaseModel):
    """Class to store model predictions and metrics"""

    predictions: Any
    metrics: ModelMetrics
    model_config = ConfigDict(arbitrary_types_allowed=True)
