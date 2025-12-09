# -*- coding: utf-8 -*-
from typing import Callable

from sktime import datasets

class_datasets = ["Airline","Longley",
"Lynx",
"Macroeconomic",
"ShampooSales",
"Solar",
"USChange"
]


def __getattr__(name: str) -> Callable:
    if name in class_datasets:
        return getattr(datasets, name)
    raise AttributeError(f"Class `{name}` not found in sktime.datasets.")


__all__ = class_datasets
