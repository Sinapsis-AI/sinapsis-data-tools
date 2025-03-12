# -*- coding: utf-8 -*-

import cv2
import numpy as np
from sinapsis_core.data_containers.data_packet import ImagePacket
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA


def perform_k_means_analysis(feature_vec: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Instantiates a class of KMeans clustering, predicts the cluster that each sample
    from the feature_vector belongs to, and then performs a PCA to
    return the transformed values with shape (n_samples, n_components)

    Args:
        feature_vec (np.ndarray): array of shape (n_samples, n_features)

    Returns:
        (np.ndarray): the array of labels corresponding to the indices of the
            cluster each sample belongs to the labels and transformed data
        (np.ndarray): the reduced vectors to be plotted
    """
    k_means = KMeans(n_clusters=3, random_state=0)
    pca = PCA(n_components=2, random_state=0)
    labels: np.ndarray = k_means.fit_predict(feature_vec)
    reduced_vectors = pca.fit_transform(feature_vec)

    return labels, reduced_vectors


def pre_process_images(images: list[ImagePacket], size: int = 28) -> np.ndarray | None:
    """Resizes and flatten images to homogenize them

    Args:
        images (list[ImagePacket]): list of ImagePackets to resize
        size (int): new size for the images.
        
    Returns:
        np.ndarray : The array with flattened and resized image"""

    feature_vec: list[np.ndarray] = []
    for image in images:
        resized_img = cv2.resize(image.content, (size, size))
        flattened_img = resized_img.flatten()

        feature_vec.append(flattened_img)

    feature_arr = np.array(feature_vec)

    return feature_arr
