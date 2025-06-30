# -*- coding: utf-8 -*-
import numpy as np
from sinapsis_core.data_containers.data_packet import DataContainer
from sinapsis_data_visualization.helpers.scikit_pca_analysis import (
    perform_k_means_analysis,
    pre_process_images,
)
from sinapsis_data_visualization.helpers.tags import Tags
from sinapsis_data_visualization.templates.base_visualization_template import (
    BasePlotAttributes,
    BaseVisualizationTemplate,
    PlotTypes,
)


class DataDistributionAttributes(BasePlotAttributes):
    """
    Attributes for data distribution visualization.

    Attributes:
        histogram (bool): Whether to plot a histogram.
        box_plot (bool): Whether to plot a box plot.
        pie_chart (bool): Whether to plot a pie chart.
        k_means_clustering (bool): Whether to plot k-means clustering.
    """

    histogram: bool = False
    box_plot: bool = False
    pie_chart: bool = False
    k_means_clustering: bool = False


DataDistributionUIProperties = BaseVisualizationTemplate.UIProperties
DataDistributionUIProperties.tags.extend([Tags.CHARTS, Tags.CLUSTERING, Tags.DISTRIBUTION, Tags.PLOTS])


class DataDistributionVisualization(BaseVisualizationTemplate):
    """
    This template plots the distribution for image data and can be
    extended to plot the distribution of different Packets, provided
    they have labels.

    The template allows for drawing histograms, box plots, pie charts,
    and PCA from k-means clusters.
    """

    AttributesBaseModel = DataDistributionAttributes
    UIProperties = DataDistributionUIProperties

    def retrieve_labels_from_images(self, container: DataContainer) -> tuple[list[str | int], list[int]]:
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

    def process_cluster(self, container: DataContainer) -> tuple[list[int | str], np.ndarray]:
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

    def get_data_for_visualization(self, container: DataContainer) -> tuple[list[str | int], list[int]]:
        """
        Gets labels and counts from images in the container.

        Args:
            container (DataContainer): Data container.

        Returns:
            tuple[list[str | int], list[int]]: Labels and counts.
        """
        return self.retrieve_labels_from_images(container)

    def generate_visualizations(self, container: DataContainer, data: tuple[list[str | int], list[int]]) -> None:
        """
        Generates all requested visualizations.

        Args:
            container (DataContainer): Data container.
            data (tuple[list[str | int], list[int]]): Labels and counts.
        """
        labels_to_plot, counts_to_plot = data

        if self.attributes.k_means_clustering:
            labels, feature_vec = self.process_cluster(container)
            self.plot_and_save(
                container=container,
                plot_type=PlotTypes.CLUSTERING,
                labels=labels,
                counts=feature_vec,
                text="K-means Clustering",
            )

        if self.attributes.histogram:
            self.plot_and_save(
                container=container,
                plot_type=PlotTypes.HISTOGRAM,
                labels=labels_to_plot,
                counts=counts_to_plot,
                text="Histogram",
            )

        if self.attributes.box_plot:
            self.plot_and_save(
                container=container,
                plot_type=PlotTypes.BOX_PLOT,
                labels=labels_to_plot,
                counts=counts_to_plot,
                text="Box Plot",
            )

        if self.attributes.pie_chart:
            self.plot_and_save(
                container=container,
                plot_type=PlotTypes.PIE_CHART,
                labels=labels_to_plot,
                counts=counts_to_plot,
                text="Pie Chart",
            )
