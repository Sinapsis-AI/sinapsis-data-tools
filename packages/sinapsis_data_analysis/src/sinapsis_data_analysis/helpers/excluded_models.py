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
]
excluded_tree_models = ["plot_tree", "export_text", "export_graphviz"]
