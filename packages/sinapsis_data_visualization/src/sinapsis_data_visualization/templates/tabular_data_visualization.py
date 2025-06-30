# -*- coding: utf-8 -*-
from typing import Sequence

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pydantic import Field
from sinapsis_core.data_containers.data_packet import DataContainer
from sinapsis_data_visualization.helpers.tags import Tags
from sinapsis_data_visualization.templates.base_visualization_template import (
    BasePlotAttributes,
    BaseVisualizationTemplate,
    PlotTypes,
)


class TabularPlotTypes(PlotTypes):
    """Extends plot types with tabular-specific types"""

    CORRELATION = "correlation"
    CATEGORICAL_DIST = "categorical_dist"


class TabularDataVisualizationAttributes(BasePlotAttributes):
    """
    Attributes for tabular data visualization.

    Attributes:
        target_column (str): Name of the target column.
        correlation (bool): Whether to create a correlation matrix for numeric columns.
        categorical_dist (bool): Whether to create distribution plots for categorical columns.
        selected_features (list[str]): List of features to plot (empty means all).
    """

    target_column: str = "target"
    correlation: bool = False
    categorical_dist: bool = False
    selected_features: list[str] = Field(default_factory=list)


TabularDataVisualizationUIProperties = BaseVisualizationTemplate.UIProperties
TabularDataVisualizationUIProperties.tags.extend([Tags.CHARTS, Tags.PLOTS, Tags.CORRELATION, Tags.PANDAS])


class TabularDataVisualization(BaseVisualizationTemplate):
    """
    Template for visualizing tabular data with various plot types.

    This template supports histograms, box plots, pie charts, correlation matrices,
    and categorical distributions for tabular data in pandas format.
    """

    AttributesBaseModel = TabularDataVisualizationAttributes

    def get_data_for_visualization(self, container: DataContainer) -> pd.DataFrame | None:
        """
        Extracts and converts tabular data from the container.

        Args:
            container (DataContainer): Data container.

        Returns:
            pd.DataFrame | None: Pandas DataFrame or None if no valid data found.
        """
        if not self.attributes.generic_field_key:
            self.logger.warning("No generic_field_key specified")
            return None

        data_dict = self._get_generic_data(container, self.attributes.generic_field_key)

        if data_dict is None:
            self.logger.warning(f"No data found with key '{self.attributes.generic_field_key}'")
            return None

        if isinstance(data_dict, pd.DataFrame):
            dataset = data_dict
        else:
            self.logger.warning(f"Data format not recognized: {type(data_dict)}")
            return None

        self.logger.info(f"Available columns: {dataset.columns}")
        return dataset

    def identify_feature_types(self, df: pd.DataFrame) -> tuple[list[str], list[str]]:
        """
        Identifies numeric and categorical columns in the DataFrame.

        Args:
            df (pd.DataFrame): Pandas DataFrame.

        Returns:
            tuple[list[str], list[str]]: Lists of numeric and categorical column names.
        """
        numeric_cols = []
        categorical_cols = []

        for col_name, dtype in zip(df.columns, df.dtypes):
            if col_name == self.attributes.target_column and col_name in df.columns:
                continue

            if pd.api.types.is_numeric_dtype(dtype):
                numeric_cols.append(col_name)
            elif (
                pd.api.types.is_categorical_dtype(dtype)
                or pd.api.types.is_object_dtype(dtype)
                or pd.api.types.is_bool_dtype(dtype)
            ):
                categorical_cols.append(col_name)

        if self.attributes.selected_features:
            numeric_cols = [c for c in numeric_cols if c in self.attributes.selected_features]
            categorical_cols = [c for c in categorical_cols if c in self.attributes.selected_features]

        return numeric_cols, categorical_cols

    def prepare_histogram_data(self, df: pd.DataFrame, feature: str) -> tuple[list[float], list[float]]:
        """
        Prepares data for a histogram plot.

        Args:
            df (pd.DataFrame): Pandas DataFrame.
            feature (str): Feature name to plot.

        Returns:
            tuple[list[float], list[float]]: Bin centers and counts.
        """
        min_val = float(df[feature].min())
        max_val = float(df[feature].max())

        bins = np.linspace(min_val, max_val, 20)
        counts, edges = np.histogram(df[feature].to_numpy(), bins=bins)

        labels = [(edges[i] + edges[i + 1]) / 2 for i in range(len(edges) - 1)]

        return labels, counts

    def prepare_boxplot_data(self, df: pd.DataFrame, feature: str) -> tuple[list[str], list[np.ndarray]]:
        """
        Prepares data for a box plot, grouped by target if available.

        Args:
            df (pd.DataFrame): Pandas DataFrame.
            feature (str): Feature name to plot.

        Returns:
            tuple[list[str], list[np.ndarray]]: Group labels and data arrays.
        """
        if self.attributes.target_column not in df.columns:
            self.logger.warning(
                f"Target column '{self.attributes.target_column}' not found. Using all data without grouping."
            )
            values = df[feature].to_numpy()
            return ["All"], [values]

        target_values = df[self.attributes.target_column].unique().tolist()
        labels = [str(val) for val in target_values]
        data_points = []

        for target_val in target_values:
            values = df[df[self.attributes.target_column] == target_val][feature].to_numpy()
            data_points.append(values)

        return labels, data_points

    def prepare_correlation_data(self, df: pd.DataFrame, numeric_cols: list[str]) -> tuple[list[str], np.ndarray]:
        """
        Prepares data for a correlation matrix plot.

        Args:
            df (pd.DataFrame): Pandas DataFrame.
            numeric_cols (list[str]): List of numeric column names.

        Returns:
            tuple[list[str], np.ndarray]: Column names and correlation matrix.
        """
        features_to_correlate = numeric_cols.copy()

        if (
            self.attributes.target_column in df.columns
            and pd.api.types.is_numeric_dtype(df[self.attributes.target_column].dtype)
            and self.attributes.target_column not in features_to_correlate
        ):
            features_to_correlate.append(self.attributes.target_column)

        corr_matrix = df[features_to_correlate].corr().to_numpy()

        return features_to_correlate, corr_matrix

    def prepare_categorical_data(self, df: pd.DataFrame, feature: str) -> tuple[list[str], list[int]]:
        """
        Prepares data for a categorical distribution plot.

        Args:
            df (pd.DataFrame): Pandas DataFrame.
            feature (str): Feature name to plot.

        Returns:
            tuple[list[str], list[int]]: Category labels and counts.
        """
        value_counts = df[feature].value_counts().sort_values(ascending=False)
        labels = value_counts.index.astype(str).tolist()
        counts = value_counts.values.tolist()
        return labels, counts

    def prepare_target_pie_data(self, df: pd.DataFrame) -> tuple[list[str], list[int]]:
        """
        Prepares data for a target distribution pie chart.

        Args:
            df (pd.DataFrame): Pandas DataFrame.

        Returns:
            tuple[list[str], list[int]]: Target value labels and counts.
        """
        if self.attributes.target_column not in df.columns:
            self.logger.warning(f"Target column '{self.attributes.target_column}' not found.")
            return [], []

        value_counts = df[self.attributes.target_column].value_counts().sort_values(ascending=False)
        labels = value_counts.index.astype(str).tolist()
        counts = value_counts.values.tolist()
        return labels, counts

    def create_boxplot(
        self, labels: Sequence[str], data_points: Sequence[np.ndarray], title: str | None = None
    ) -> matplotlib.figure.Figure:
        """
        Creates a boxplot figure.

        Args:
            labels (Sequence[str]): Group labels.
            data_points (Sequence[np.ndarray]): Arrays of data points.
            title (str | None): Plot title.

        Returns:
            matplotlib.figure.Figure: The created boxplot.
        """
        fig = self.create_figure(text=title)
        plt.boxplot(data_points, labels=labels)
        plt.ylabel("Value")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        return fig

    def generate_visualizations(self, container: DataContainer, dataset: pd.DataFrame) -> None:
        """
        Generates all requested visualizations for the tabular data.

        Args:
            container (DataContainer): Data container.
            dataset (pd.DataFrame): The tabular data.
        """
        numeric_cols, categorical_cols = self.identify_feature_types(dataset)
        self.logger.info(f"Found {len(numeric_cols)} numeric features and {len(categorical_cols)} categorical features")

        if not numeric_cols and not categorical_cols:
            self.logger.warning("No features found for visualization")
            return

        if self.attributes.histogram:
            for feature in numeric_cols:
                labels, counts = self.prepare_histogram_data(dataset, feature)
                if len(labels) > 0 and len(counts) > 0:
                    self.plot_and_save(
                        container=container,
                        plot_type=PlotTypes.HISTOGRAM,
                        labels=labels,
                        counts=counts,
                        text=f"{feature}",
                    )

        if self.attributes.box_plot:
            for feature in numeric_cols:
                box_labels, data_points = self.prepare_boxplot_data(dataset, feature)
                if len(box_labels) > 0 and len(data_points) > 0:
                    fig = self.create_boxplot(labels=box_labels, data_points=data_points, title=f"{feature}")
                    self.save_figure(fig, f"boxplot_{feature}", container.container_id)
                    self.add_figure_to_container(container, fig, f"boxplot_{feature}")

        if self.attributes.correlation and len(numeric_cols) > 1:
            corr_labels, corr_matrix = self.prepare_correlation_data(dataset, numeric_cols)
            if len(corr_labels) > 0 and corr_matrix.size > 0:
                self.plot_and_save(
                    container=container,
                    plot_type=TabularPlotTypes.CORRELATION,
                    labels=corr_labels,
                    counts=corr_matrix,
                    rotate_x_ticks=True,
                )

        if self.attributes.categorical_dist and categorical_cols:
            for feature in categorical_cols:
                cat_labels, cat_counts = self.prepare_categorical_data(dataset, feature)
                if len(cat_labels) > 0 and len(cat_counts) > 0:
                    self.plot_and_save(
                        container=container,
                        plot_type=TabularPlotTypes.CATEGORICAL_DIST,
                        labels=cat_labels,
                        counts=cat_counts,
                        text=f"{feature}",
                        rotate_x_ticks=True,
                    )

        if self.attributes.pie_chart:
            pie_labels, pie_counts = self.prepare_target_pie_data(dataset)
            if len(pie_labels) > 0 and len(pie_counts) > 0:
                self.plot_and_save(
                    container=container,
                    plot_type=PlotTypes.PIE_CHART,
                    labels=pie_labels,
                    counts=pie_counts,
                )
