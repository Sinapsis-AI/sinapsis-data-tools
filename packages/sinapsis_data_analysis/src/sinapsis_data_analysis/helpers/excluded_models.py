# -*- coding: utf-8 -*-
excluded_linear_models = [
    "enet_path",
    "lars_path",
    "lars_path_gram",
    "lasso_path",
    "orthogonal_mp",
    "orthogonal_mp_gram",
    "ridge_regression",
    "_sgd_fast",
    "ElasticNetCV",
    "LassoCV",
    "OrthogonalMatchingPursuit",
]
excluded_neighbors_models = [
    "_ball_tree.BallTree",
    "_ball_tree.KDTree",
    "sort_graph_by_row_values",
    "kneighbors_graph",
    "radius_neighbors_graph",
    "sort_graph_by_row_values",
    "VALID_METRICS",
    "VALID_METRICS_SPARSE",
    "LocalOutlierFactor",
]
excluded_tree_models = ["plot_tree", "export_text", "export_graphviz", "BaseDecisionTree"]
excluded_svm_models = ["l1_min_c"]
excluded_cluster_models = ["affinity_propagation",
    "cluster_optics_dbscan",
    "cluster_optics_xi",
    "compute_optics_graph",
    "dbscan",
    "estimate_bandwidth",
    "get_bin_seeds",
    "k_means",
    "kmeans_plusplus",
    "linkage_tree",
    "mean_shift",
    "spectral_clustering",
    "ward_tree"]
