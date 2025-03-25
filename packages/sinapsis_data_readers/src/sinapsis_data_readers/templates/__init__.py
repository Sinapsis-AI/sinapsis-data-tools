# -*- coding: utf-8 -*-
import importlib
from typing import Callable

from sinapsis.templates import _import_template_package

_root_lib_path = "sinapsis_data_readers.templates"

_template_lookup = {
    "AudioReaderPydub": f"{_root_lib_path}.audio_readers.audio_reader_pydub",
    "AudioReaderSoundfile": f"{_root_lib_path}.audio_readers.audio_reader_soundfile",
    "AudioReaderToBytes": f"{_root_lib_path}.audio_readers.audio_reader_to_bytes",
    "CSVImageDataset": f"{_root_lib_path}.image_readers.csv_dataset_reader",
    "CocoDetectionDatasetCV2": f"{_root_lib_path}.image_readers.coco_dataset_reader",
    "CocoKeypointsDatasetCV2": f"{_root_lib_path}.image_readers.coco_dataset_reader",
    "CocoSegmentationDatasetCV2": f"{_root_lib_path}.image_readers.coco_dataset_reader",
    "ExecuteNTimesAudioReaderPydub": f"{_root_lib_path}.audio_readers.audio_reader_pydub",
    "ExecuteNTimesAudioReaderSoundfile": f"{_root_lib_path}.audio_readers.audio_reader_soundfile",
    "ExecuteNTimesLazyAudioReaderPydub": f"{_root_lib_path}.audio_readers.audio_reader_pydub",
    "ExecuteNTimesLazyAudioReaderSoundfile": f"{_root_lib_path}.audio_readers.audio_reader_soundfile",
    "FolderImageDatasetCV2": f"{_root_lib_path}.image_readers.image_folder_reader_cv2",
    "ImageDatasetSplitter": f"{_root_lib_path}.datasets_readers.dataset_splitter",
    "LazyAudioReaderPydub": f"{_root_lib_path}.audio_readers.audio_reader_pydub",
    "LazyAudioReaderSoundfile": f"{_root_lib_path}.audio_readers.audio_reader_soundfile",
    "MultiVideoReaderCV2": f"{_root_lib_path}.video_readers.video_reader_cv2",
    "MultiVideoReaderDali": f"{_root_lib_path}.video_readers.video_reader_dali",
    "MultiVideoReaderPytorch": f"{_root_lib_path}.video_readers.video_reader_dali",
    "MultiVideoReaderFFMPEG": f"{_root_lib_path}.video_readers.video_reader_ffmpeg",
    "MultiVideoReaderTorchCodec": f"{_root_lib_path}.video_readers.video_reader_torchcodec",
    "TabularDatasetSplitter": f"{_root_lib_path}.datasets_readers.dataset_splitter",
    "TextInput": f"{_root_lib_path}.text_readers.text_input",
    "VideoReaderCV2": f"{_root_lib_path}.video_readers.video_reader_cv2",
    "VideoReaderDali": f"{_root_lib_path}.video_readers.video_reader_dali",
    "VideoReaderDaliPytorch": f"{_root_lib_path}.video_readers.video_reader_dali",
    "VideoReaderFFMPEG": f"{_root_lib_path}.video_readers.video_reader_ffmpeg",
    "VideoReaderTorchCodec": f"{_root_lib_path}.video_readers.video_reader_torchcodec",
}


_ADDITIONAL_TEMPLATE_MODULES = [
    f"{_root_lib_path}.datasets_readers.sklearn_datasets",
    f"{_root_lib_path}.datasets_readers.sktime_datasets",
]
for t_module in _ADDITIONAL_TEMPLATE_MODULES:
    _template_lookup |= _import_template_package(t_module)


def __getattr__(name: str) -> Callable:
    if name in _template_lookup:
        module = importlib.import_module(_template_lookup[name])
        return getattr(module, name)
    raise AttributeError(f"template `{name}` not found in {_root_lib_path}")


__all__ = list(_template_lookup.keys())
