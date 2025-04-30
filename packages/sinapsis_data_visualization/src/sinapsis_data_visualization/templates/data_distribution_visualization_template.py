# -*- coding: utf-8 -*-
"""Data distribution visualization template"""

import os
from typing import Any

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from pydantic import Field
from pydantic.dataclasses import dataclass
from sinapsis_core.data_containers.data_packet import DataContainer
from sinapsis_core.template_base import Template
from sinapsis_core.template_base.base_models import (
    OutputTypes,
    TemplateAttributes,
    TemplateAttributeType,
    UIPropertiesMetadata,
)
from sinapsis_core.utils.env_var_keys import SINAPSIS_CACHE_DIR
from sinapsis_data_visualization.helpers.plot_distributions import (
    plot_distribution,
    plot_map,
)
from sinapsis_data_visualization.helpers.scikit_pca_analysis import (
    perform_k_means_analysis,
    pre_process_images,
)


class PlotAttributes(TemplateAttributes):
    """Base attributes for all plot types.

    Attributes:
        fig_title (str|None): Title for the figure.
        y_label (str|None): Label of the y-axis.
        x_label (str|None): Label of the x-axis.
        fig_width (int): Width of the figure.
        fig_height (int): Height of the figure.
        x_position (float): X-position for the legend and/or texts.
        y_position (float): Y-position for the legend and/or texts.
        save_image_dir (str): Directory to save the image.
        fig_name (str): Name of the figure.
    """

    fig_title: str | None = None
    y_label: str | None = None
    x_label: str | None = None
    fig_width: int = 10
    fig_height: int = 10
    x_position: float = 0.5
    y_position: float = 0.5
    text: str | None = None
    save_image_dir: str | None = SINAPSIS_CACHE_DIR
    fig_name: str
    kwargs: dict[str, Any] = Field(default_factory=dict)


@dataclass
class PlotTypes:
    """Dataclass with different types of plots.
    HISTOGRAM: Key for the histogram plot
    BOX_PLOT: Key for the box plot
    PIE_CHART: Key for the pie chart plot
    CLUSTERING: Key for the k-means custering plot
    """

    HISTOGRAM: str = "histogram"
    BOX_PLOT: str = "box_plot"
    PIE_CHART: str = "pie_chart"
    CLUSTERING: str = "k_means_clustering"


class DataDistributionVisualization(Template):
    """
    This template plots the distribution for image data, and can be
    extended to plot the distribution of different Packets, provided
    they have labels.
    The template allows for the drawing of histograms, box plots, pie charts
    and PCA from k-means cluster
    The template returns a figure in the container as an ImagePacket.

    Usage example:

    agent:
      name: my_test_agent
    templates:
    - template_name: InputTemplate
      class_name: InputTemplate
      attributes: {}
    - template_name: DataDistributionVisualization
      class_name: DataDistributionVisualization
      template_input: InputTemplate
      attributes:
        fig_title: null
        y_label: null
        x_label: null
        fig_width: 10
        fig_height: 10
        x_position: 0.5
        y_position: 0.5
        text: null
        save_image_dir: $SINAPSIS_CACHE_DIR
        fig_name: 'desired_name_for_the_figure'
        kwargs: '{}'
        histogram: false
        box_plot: false
        pie_chart: false
        k_means_clustering: false


    """

    UIProperties = UIPropertiesMetadata(output_type=OutputTypes.IMAGE)

    class AttributesBaseModel(PlotAttributes):
        """
        Attributes for data analysis using matplotlib.

        Attributes:
            histogram (bool): Whether to plot a histogram. Defaults to False.
            box_plot (bool): Whether to plot a box plot. Defaults to False.
            pie_chart (bool): Whether to plot a pie chart. Defaults to False.
            k_means_clustering (bool): Whether to plot k-means clustering. Defaults to False.
        """

        histogram: bool = False
        box_plot: bool = False
        pie_chart: bool = False
        k_means_clustering: bool = False

    def __init__(self, attributes: TemplateAttributeType) -> None:
        """Initializes the DataDistributionVisualization
            template with given attributes.

        Args:
            attributes (TemplateAttributeType): The attributes for
            configuring the data analysis.
        """
        super().__init__(attributes)

        if not os.path.exists(self.attributes.save_image_dir):
            os.makedirs(self.attributes.save_image_dir)

    def create_figure(self, text: str | None = None, rotate_x_ticks: bool = False) -> matplotlib.figure.Figure:
        """
        Creates the matplotlib.figure.Figure object and adds relevant
        information, such as the x-label, y-label and title.
        It also adds available text to the desired x and y positions and rotated
        the x-ticks is flag is True

        Args:
            text (str | None): Optional text to add to the figure. Defaults to None.
            rotate_x_ticks (bool): Flag to rotate x-ticks 90 degrees. Defaults to False
        Returns:
            The initialized figure with corresponding parameters

        """
        figure = plt.figure(figsize=(self.attributes.fig_width, self.attributes.fig_height))
        plt.xlabel(self.attributes.x_label or "X-Axis")
        plt.ylabel(self.attributes.y_label or "Y-Axis")
        plt.title(self.attributes.fig_title or "Plot Title")

        # Prepare the text for annotation
        if text:
            plt.text(self.attributes.x_position, self.attributes.y_position, text)

        if rotate_x_ticks:
            plt.xticks(rotation=90)
        return figure

    @staticmethod
    def retrieve_labels_from_images(
        container: DataContainer,
    ) -> tuple[list[str | int], list[int]]:
        """
        Iterates through the ImagePackets, extracting each of the
        annotations for all of them.
        Generates a dictionary with the label and number of points associated
        with that label.
        Returns:
            tuple[list[str | int], list[int]]: list of labels and number of coincidences for each label
        """
        labels: list[str | int] = [ann.label_str for image in container.images for ann in image.annotations]

        label_count: dict[str | int, int] = {}
        for label in labels:
            label_count[label] = label_count.get(label, 0) + 1
        labels, counts = list(label_count.keys()), list(label_count.values())
        return labels, counts

    @staticmethod
    def process_cluster(container: DataContainer) -> tuple[list[int | str], np.ndarray]:
        """
        For the k-means clustering, the images need to be flattened first
           and then returned as a reduced vector. This method calls the pre_process_images
           method from scikit-pca analysis to perform such preprocessing.
           Then, perform_k_means_analysis instantiates a KMeans class from scikit-learn
           and perform Principal Component Analysis (PCA) on the reduced vector.


        Args:
            container (DataContainer): Container to extract the images from

        Returns:
            list[str | int]: list of labels
            np.ndarray : transformed values from the pca analysis
        """
        images = container.images
        feature_arr = pre_process_images(images)
        label, counts = perform_k_means_analysis(feature_arr)
        return label, counts

    def execute(self, container: DataContainer) -> DataContainer:
        figure = self.create_figure()
        labels_to_plot, counts_to_plot = self.retrieve_labels_from_images(container)
        fig_name = self.attributes.fig_name

        if self.attributes.k_means_clustering:
            plot_type = PlotTypes.CLUSTERING
            fig_name = f"{PlotTypes.CLUSTERING}_{self.attributes.fig_name}"
            labels, feature_vec = self.process_cluster(container)
            figure = plot_distribution(
                figure=figure,
                labels=labels,
                counts=feature_vec,
                plot_type=plot_type,
                kwargs=self.attributes.kwargs,
            )
        else:
            for plot_type in plot_map:
                if not getattr(self.attributes, plot_type):
                    continue
                figure = plot_distribution(
                    figure=figure,
                    labels=labels_to_plot,
                    counts=counts_to_plot,
                    plot_type=plot_type,
                    kwargs=self.attributes.kwargs,
                )

                fig_name = f"{plot_type}_{self.attributes.fig_name}"
        fig_path = os.path.join(self.attributes.save_image_dir, fig_name)
        if figure:
            plt.savefig(f"{fig_path}_{container.container_id}")
            plt.close()
            container.generic_data[plot_type] = figure
        return container
