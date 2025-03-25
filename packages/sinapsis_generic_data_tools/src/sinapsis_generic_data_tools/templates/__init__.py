# -*- coding: utf-8 -*-
import importlib
from typing import Callable

_root_lib_path = "sinapsis_generic_data_tools.templates"

_template_lookup = {
    "ImageColorConversion": f"{_root_lib_path}.image_color_conversion",
    "MaskNonROIs": f"{_root_lib_path}.mask_non_roi",
    "PacketBufferQueue": f"{_root_lib_path}.packet_buffer_queue",
}


def __getattr__(name: str) -> Callable:
    if name in _template_lookup:
        module = importlib.import_module(_template_lookup[name])
        return getattr(module, name)
    raise AttributeError(f"template `{name}` not found in {_root_lib_path}")


__all__ = list(_template_lookup.keys())
