# -*- coding: utf-8 -*-
import importlib
from typing import Callable

_root_lib_path = "sinapsis_data_writers.templates"

_template_lookup = {
    "BaseAnnotationWriter": f"{_root_lib_path}.annotation_writers.image_annotation_writer",
    "COCOAnnotationWriter": f"{_root_lib_path}.annotation_writers.coco_annotation_writer",
    "ImageSaver": f"{_root_lib_path}.image_writers.image_saver",
    "PDFToImage": f"{_root_lib_path}.image_writers.pdf_to_image_converter",
    "VideoWriterCV2": f"{_root_lib_path}.video_writers.video_writer_cv2",
    "VideoWriterFFMPEG": f"{_root_lib_path}.video_writers.video_writer_ffmpeg",
    "AudioWriterSoundfile": f"{_root_lib_path}.audio_writers.audio_writer_soundfile",
}


def __getattr__(name: str) -> Callable:
    if name in _template_lookup:
        module = importlib.import_module(_template_lookup[name])
        return getattr(module, name)

    raise AttributeError(f"template `{name}` not found in {_root_lib_path}")


__all__ = list(_template_lookup.keys())
