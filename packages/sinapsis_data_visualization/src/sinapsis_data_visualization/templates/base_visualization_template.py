# -*- coding: utf-8 -*-
import io
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import PIL.Image
from pydantic import Field
from sinapsis_core.data_containers.data_packet import DataContainer, ImagePacket
from sinapsis_core.template_base import Template
from sinapsis_core.template_base.base_models import (
    OutputTypes,
    TemplateAttributes,
    TemplateAttributeType,
    UIPropertiesMetadata,
)
from sinapsis_core.utils.env_var_keys import SINAPSIS_CACHE_DIR
from sinapsis_data_visualization.helpers.plot_distributions import plot_distribution
from sinapsis_data_visualization.helpers.tags import Tags


@dataclass
class PlotTypes:
    """Dataclass with different types of plots."""

    HISTOGRAM: str = "histogram"
    BOX_PLOT: str = "box_plot"
    PIE_CHART: str = "pie_chart"
    CLUSTERING: str = "k_means_clustering"
    CORRELATION: str = "correlation"
    CATEGORICAL_DIST: str = "categorical_dist"


class BasePlotAttributes(TemplateAttributes):
    """Base attributes for all plot types.

    Attributes:
        generic_field_key (str): Key to extract data from the container.
        fig_title (str|None): Title for the figure.
        y_label (str|None): Label of the y-axis.
        x_label (str|None): Label of the x-axis.
        fig_width (int): Width of the figure.
        fig_height (int): Height of the figure.
        x_position (float): X-position for the legend and/or texts.
        y_position (float): Y-position for the legend and/or texts.
        save_image_dir (str): Directory to save the image.
        fig_name (str): Name of the figure.
        add_to_image_packets (bool): Whether to add generated plots to image packets.
        image_format (str): File format for saved images.
        histogram (bool): Whether to create a histogram visualization.
        box_plot (bool): Whether to create a box plot visualization.
        pie_chart (bool): Whether to create a pie chart visualization.
    """

    generic_field_key: str | None = None
    fig_title: str | None = None
    y_label: str | None = None
    x_label: str | None = None
    fig_width: int = 10
    fig_height: int = 10
    x_position: float = 0.5
    y_position: float = 0.5
    text: str | None = None
    save_image_dir: str | None = SINAPSIS_CACHE_DIR
    fig_name: str = "visualization"
    kwargs: dict[str, Any] = Field(default_factory=dict)
    add_to_image_packets: bool = True
    image_format: str = "png"
    histogram: bool = False
    box_plot: bool = False
    pie_chart: bool = False


class BaseVisualizationTemplate(Template, ABC):
    """
    Base class for all visualization templates.

    This class provides common functionality for creating, saving, and adding
    figures to data containers. Child classes should implement the required
    abstract methods.
    """

    UIProperties = UIPropertiesMetadata(
        category="Visualization",
        output_type=OutputTypes.IMAGE,
        tags=[Tags.IMAGE, Tags.MATPLOTLIB, Tags.VISUALIZATION],
    )
    AttributesBaseModel = BasePlotAttributes

    def __init__(self, attributes: TemplateAttributeType) -> None:
        super().__init__(attributes)
        self.saved_image_paths: list[str] = []
        if self.attributes.save_image_dir and not os.path.exists(self.attributes.save_image_dir):
            os.makedirs(self.attributes.save_image_dir)

    def create_figure(self, text: str | None = None, rotate_x_ticks: bool = False) -> matplotlib.figure.Figure:
        """
        Creates a matplotlib figure with basic configuration.

        Args:
            text (str | None): Optional text to add to the figure.
            rotate_x_ticks (bool): Whether to rotate x-axis tick labels.

        Returns:
            matplotlib.figure.Figure: The configured figure.
        """
        figure = plt.figure(figsize=(self.attributes.fig_width, self.attributes.fig_height))
        plt.xlabel(self.attributes.x_label or "X-Axis")
        plt.ylabel(self.attributes.y_label or "Y-Axis")
        plt.title(self.attributes.fig_title or "Plot Title")

        if text:
            plt.text(self.attributes.x_position, self.attributes.y_position, text)

        if rotate_x_ticks:
            plt.xticks(rotation=90)

        return figure

    def save_figure(
        self,
        figure: matplotlib.figure.Figure,
        name: str,
        container_id: str | None = None,
    ) -> str:
        """
        Saves the figure to disk and records the path.

        Args:
            figure (matplotlib.figure.Figure): The figure to save.
            name (str): Base name for the figure file.
            container_id (str | None): Optional container ID to append to filename.

        Returns:
            str: The saved file path with extension.
        """
        if not self.attributes.save_image_dir:
            self.logger.warning("No save directory specified, figure will not be saved to disk")
            return ""

        file_name = f"{name}_{self.attributes.fig_name}"
        if container_id:
            file_name = f"{file_name}_{container_id}"

        file_name_with_ext = f"{file_name}.{self.attributes.image_format}"
        fig_path = os.path.join(self.attributes.save_image_dir, file_name_with_ext)

        plt.savefig(fig_path)
        plt.close(figure)

        self.saved_image_paths.append(fig_path)

        return fig_path

    def add_figure_to_container(self, container: DataContainer, figure: matplotlib.figure.Figure, name: str) -> None:
        """
        Adds the figure to the container as an image packet if requested.

        Args:
            container (DataContainer): The data container to update.
            figure (matplotlib.figure.Figure): The figure to add.
            name (str): Name key for the figure.
        """
        if self.attributes.add_to_image_packets:
            buf = io.BytesIO()
            figure.savefig(buf, format=self.attributes.image_format)
            buf.seek(0)
            image = PIL.Image.open(buf)
            image_array = np.array(image)
            image_packet = ImagePacket(
                content=image_array,
                source=f"visualization_{name}",
            )
            container.images.append(image_packet)

    def plot_and_save(
        self,
        container: DataContainer,
        plot_type: str,
        labels: list[str] | np.ndarray,
        counts: list[float] | np.ndarray,
        text: str | None = None,
        rotate_x_ticks: bool = False,
    ) -> matplotlib.figure.Figure:
        """
        Creates a figure, plots data, saves it, and adds it to the container.

        Args:
            container (DataContainer): The data container.
            plot_type (str): Type of plot to create.
            labels (list[str] | np.ndarray): Labels for the plot.
            counts (list[float] | np.ndarray): Data values for the plot.
            text (str | None): Optional title text.
            rotate_x_ticks (bool): Whether to rotate x-axis tick labels.

        Returns:
            matplotlib.figure.Figure: The created figure.
        """
        figure = self.create_figure(text=text, rotate_x_ticks=rotate_x_ticks)

        figure = plot_distribution(
            figure=figure,
            labels=labels,
            counts=counts,
            plot_type=plot_type,
            kwargs=self.attributes.kwargs,
        )

        plot_name = f"{plot_type}" if not text else f"{plot_type}_{text}"
        self.save_figure(figure, plot_name, container.container_id)
        self.add_figure_to_container(container, figure, plot_name)
        return figure

    @abstractmethod
    def get_data_for_visualization(self, container: DataContainer) -> Any:
        """
        Extracts data from the container for visualization.

        Args:
            container (DataContainer): The data container.

        Returns:
            Any: The data to visualize.
        """

    @abstractmethod
    def generate_visualizations(self, container: DataContainer, data: Any) -> None:
        """
        Generates all visualizations for the given data.

        Args:
            container (DataContainer): The data container.
            data (Any): The data to visualize.
        """

    def execute(self, container: DataContainer) -> DataContainer:
        """
        Executes the visualization template.

        Args:
            container (DataContainer): The input data container.

        Returns:
            DataContainer: The updated data container with visualizations.
        """
        data = self.get_data_for_visualization(container)
        if data is not None:
            self.generate_visualizations(container, data)

        self._set_generic_data(container, self.saved_image_paths)

        return container
