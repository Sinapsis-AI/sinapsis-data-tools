# -*- coding: utf-8 -*-
from typing import Callable

from sklearn import datasets

_sklearn_supported_loaders = {
    name: getattr(datasets, name) for name in dir(datasets) if name.startswith(("load", "fetch"))
}
excluded_loaders = [
    "fetch_lfw_pairs",
    "fetch_20newsgroups",
    "fetch_20newgroups_vectorized",
    "load_sample_images",
    "load_sample_image",
    "load_svmlight_file",
    "load_svmlight_files",
    "fetch_rcv1",
    "fetch_species_distribution",
    "fetch_file",
]


def __getattr__(name: str) -> Callable:
    if name in _sklearn_supported_loaders and name not in excluded_loaders:
        return _sklearn_supported_loaders[name]
    raise AttributeError(f"Function `{name}` not found in sklearn.datasets.")


__all__ = list(_sklearn_supported_loaders.keys())
