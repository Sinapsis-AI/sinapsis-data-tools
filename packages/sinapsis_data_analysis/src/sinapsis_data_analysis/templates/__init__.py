# -*- coding: utf-8 -*-
import importlib

from sinapsis.templates import _import_template_package
from sinapsis_core.template_base import Template

_root_lib_path: str = "sinapsis_data_analysis.templates"

_ADDITIONAL_TEMPLATE_MODULES = [
    f"{_root_lib_path}.sklearn_manifold",
    f"{_root_lib_path}.sklearn_train",
    f"{_root_lib_path}.xgboost_train",
]
_template_lookup: dict = {
    "SKLearnInference": f"{_root_lib_path}.sklearn_inference",
    "XGBoostInference": f"{_root_lib_path}.xgboost_inference",
}
for t_module in _ADDITIONAL_TEMPLATE_MODULES:
    _template_lookup |= _import_template_package(t_module)


def __getattr__(name: str) -> Template:
    if name in _template_lookup:
        module = importlib.import_module(_template_lookup[name])
        return getattr(module, name)


__all__ = list(_template_lookup.keys())
