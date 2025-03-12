# -*- coding: utf-8 -*-
from typing import Callable

from sklearn import datasets

_sklearn_supported_loaders = {
    name: getattr(datasets, name) for name in dir(datasets) if name.startswith(("load", "fetch"))
}


def __getattr__(name: str) -> Callable:
    if name in _sklearn_supported_loaders:
        return _sklearn_supported_loaders[name]
    raise AttributeError(f"Function `{name}` not found in sklearn.datasets.")


__all__ = list(_sklearn_supported_loaders.keys())
