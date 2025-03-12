# -*- coding: utf-8 -*-
import importlib
from typing import Callable

_root_lib_path = "sinapsis_data_visualization.templates"

_template_lookup = {
    "DataDistributionVisualization": f"{_root_lib_path}.data_distribution_visualization_template",
    "LabelDrawer": f"{_root_lib_path}.label_drawer",
    "BBoxDrawer": f"{_root_lib_path}.bbox_drawer",
    "KeyPointsDrawer": f"{_root_lib_path}.key_points_drawer",
    "OrientedBBoxDrawer": f"{_root_lib_path}.oriented_bbox_drawer",
    "SegmentationMaskDrawer": f"{_root_lib_path}.segmentation_mask_drawer",
}


def __getattr__(name: str) -> Callable:  # type:ignore
    if name in _template_lookup:
        module = importlib.import_module(_template_lookup[name])
        return getattr(module, name)

    raise AttributeError(f"template `{name}` not found in {_root_lib_path}")


__all__ = list(_template_lookup.keys())
