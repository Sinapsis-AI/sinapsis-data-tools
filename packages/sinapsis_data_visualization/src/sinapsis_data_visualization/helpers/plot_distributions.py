# -*- coding: utf-8 -*-
from typing import Sequence

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from sinapsis_core.utils.logging_utils import sinapsis_logger
from sklearn.metrics import ConfusionMatrixDisplay


def plot_distribution(
    figure: matplotlib.figure.Figure,
    labels: Sequence[str] | np.ndarray,
    counts: list[float] | np.ndarray,
    plot_type: str,
    kwargs: dict,
) -> matplotlib.figure.Figure:
    """
    Base method to plot a distribution.

    Args:
        figure (matplotlib.figure.Figure): Original figure to add the plot on
        labels (str | int): labels to group the data by
        counts (list[float] | np.ndarray): number of
            incidences a certain label is repeated
        plot_type (str): Type of plot to be drawn on the figure. Options are: box,
        histogram, pie chat and clustering
        kwargs (dict): Extra kwargs for the plot, including color, size, symbol, etc.
    returns:
        matplotlib.figure.Figure : Modified figure with the actual distribution plotted
    """
    if (isinstance(labels, np.ndarray) and not labels.any()) or (isinstance(labels, Sequence) and not labels):
        sinapsis_logger.warning("No labels found to plot.")

    elif (isinstance(counts, np.ndarray) and not counts.any()) or (isinstance(counts, list) and not labels):
        sinapsis_logger.warning("No counts found to plot.")

    else:
        plot_map[plot_type](labels, counts, kwargs)
    return figure


def plot_histogram(labels: Sequence[str], counts: list[float] | np.ndarray, kwargs: dict) -> None:
    """
    Plots a histogram of the data.

    Args:

        labels (Sequence[str]): The categories or bins for the histogram.
        counts (list [float] | np.ndarray): The values corresponding to each label.
            Represents the height of the bars.
        **kwargs (dic): Additional keyword arguments passed to 'matplotlib.pyplot.bar'.

    The method plots a bar plot
    """
    plt.bar(labels, counts, **kwargs)


def plot_boxplot(labels: Sequence[str], counts: list[float] | np.ndarray, kwargs: dict) -> None:
    """
    Plots a boxplot.

    Args:
    labels (Sequence[str]): The categories or labels for the data.
    counts (list[float] | np.ndarray): The values representing the
        frequency of data points for each label.
    **kwargs (dict): Additional keyword arguments passed to
        'matplotlib.pyplot.boxplot'.

    Note:

        Logs an error if the provided arguments are incompatible with
        'plt.boxplot'.
    """
    data_points = []

    for label, count in zip(labels, counts):
        data_points.extend([label] * count)
    try:
        plt.boxplot(x=data_points, label=labels, **kwargs)
    except ValueError as e:
        sinapsis_logger.logger.error(f"Incompatible arguments for boxplot: {e}")


def plot_piechart(labels: Sequence[str], counts: list[float] | np.ndarray, kwargs: dict) -> None:
    """
    Plots a basic pie chart.
    Args:
        labels (Sequence[str]): The labels for each section of
            the pie chart.
        counts (list[float], np.ndarray): The values representing
            the size of each section.
        **kwargs (dict): Additional keyword arguments passed to
            'matplotlib.pyplot.pie'.


    Notes:
        The function supports various `matplotlib` pie chart customization options,
        such as 'autopct', 'startangle', and 'rotatelabels'.
    """

    plt.pie(
        counts,
        labels=labels,
        **kwargs,
    )


def plot_cluster(labels: Sequence[str], counts: list[float] | np.ndarray, kwargs: dict) -> None:
    """
    Plots a scatter plot for clustered data.

    Args:
        labels (Sequence[str]): Cluster labels for each data point.
        counts (list[float] | np.ndarray): A 2D array with shape (n_samples, 2),
            where each row represents a data point's coordinates.
        **kwargs (dict): Additional keyword arguments passed to
            'matplotlib.pyplot.scatter'.


    """
    counts = np.asarray(counts)
    plt.scatter(counts[:, 0], counts[:, 1], c=labels, **kwargs)


def plot_correlation(labels: Sequence[str], counts: list[float] | np.ndarray, kwargs: dict) -> None:
    """
    Plots a correlation heatmap for numeric features.

    Args:
        labels (Sequence[str]): Column names for the correlation matrix
        counts (list[float] | np.ndarray): Correlation matrix values
        kwargs (dict): Additional keyword arguments (cmap, etc.)
    """
    plt.imshow(counts)
    plt.colorbar()

    plt.xticks(np.arange(len(labels)), labels, rotation=45, ha="right")
    plt.yticks(np.arange(len(labels)), labels)

    counts_array = np.asarray(counts)
    for i in range(len(labels)):
        for j in range(len(labels)):
            color = "white" if abs(counts_array[i, j]) > 0.5 else "black"
            plt.text(j, i, f"{counts_array[i, j]:.2f}", ha="center", va="center", color=color, **kwargs)


def plot_categorical_dist(labels: Sequence[str], counts: list[float] | np.ndarray, kwargs: dict) -> None:
    """
    Plots a bar chart for categorical data distribution.

    Args:
        labels (Sequence[str]): Category labels
        counts (list[float]): Frequency of each category
        kwargs (dict): Additional keyword arguments (color, etc.)
    """
    plt.bar(range(len(labels)), counts, **kwargs)
    plt.xticks(range(len(labels)), labels, rotation=45, ha="right")


def plot_confusion_matrix(labels: Sequence[str], counts: np.ndarray, kwargs: dict) -> None:
    """
    Plots a confusion matrix for model evaluation.

    Args:
        labels (Sequence[str]): Class labels (typically ["0", "1"] for binary classification)
        counts (np.ndarray): Confusion matrix array
        kwargs (dict): Additional keyword arguments (cmap, etc.)
    """

    cmap = kwargs.pop("cmap", plt.cm.Blues)
    disp = ConfusionMatrixDisplay(confusion_matrix=counts, display_labels=labels)
    disp.plot(cmap=cmap, **kwargs)
    plt.tight_layout()


def plot_roc_curve(labels: Sequence[str], counts: np.ndarray, kwargs: dict) -> None:
    """
    Plots a ROC curve for model evaluation.

    Args:
        labels (Sequence[str]): Label for the ROC curve
        counts (np.ndarray): 2D array with columns [fpr, tpr]
        kwargs (dict): Additional keyword arguments
    """
    fpr, tpr = counts[:, 0], counts[:, 1]

    from sklearn.metrics import auc

    roc_auc = auc(fpr, tpr)

    plt.plot(fpr, tpr, lw=2, label=f"{labels[0]} (AUC = {roc_auc:.2f})", **kwargs)

    plt.plot([0, 1], [0, 1], "--", color="gray", lw=1)

    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.legend(loc="lower right")
    plt.grid(True, alpha=0.3)


def plot_precision_recall_curve(labels: Sequence[str], counts: np.ndarray, kwargs: dict) -> None:
    """
    Plots a precision-recall curve for model evaluation.

    Args:
        labels (Sequence[str]): Label for the PR curve
        counts (np.ndarray): 2D array with columns [precision, recall]
        kwargs (dict): Additional keyword arguments
    """
    precision, recall = counts[:, 0], counts[:, 1]

    plt.plot(recall, precision, lw=2, label=f"{labels[0]}", **kwargs)

    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.legend(loc="lower left")
    plt.grid(True, alpha=0.3)


plot_map: dict = {
    "histogram": plot_histogram,
    "pie_chart": plot_piechart,
    "box_plot": plot_boxplot,
    "k_means_clustering": plot_cluster,
    "correlation": plot_correlation,
    "categorical_dist": plot_categorical_dist,
    "confusion_matrix": plot_confusion_matrix,
    "roc_curve": plot_roc_curve,
    "precision_recall_curve": plot_precision_recall_curve,
}
