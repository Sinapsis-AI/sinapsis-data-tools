# -*- coding: utf-8 -*-

from pathlib import PosixPath
from typing import Callable

import cv2
import numpy as np

from sinapsis_data_readers.templates.image_readers.base_image_folder_data_loader import (
    ImageBaseDataReader,
)


def read_image_file(file_path: str | PosixPath | bytes) -> np.ndarray:
    """Method to read the image whether from a bytes object or local path

    Args:
        file_path (str | PosixPath | bytes): either the file path in disk or the bytes object
    Returns:
        np.ndarray: the image as a numpy array
    """
    np_image: np.ndarray

    if isinstance(file_path, bytes):
        image_arr = np.frombuffer(file_path, np.uint8)
        np_image = cv2.imdecode(image_arr, cv2.IMREAD_COLOR)

    else:
        if isinstance(file_path, PosixPath):
            file_path = str(file_path.resolve())
        np_image = cv2.imread(file_path, cv2.IMREAD_COLOR)

    np_image = cv2.cvtColor(np_image, cv2.COLOR_BGR2RGB)

    return np_image


class FolderImageDatasetCV2(ImageBaseDataReader):
    """Dataset creation for images in a directory in the disk with opencv

    Methods:
        - _create_data_entries : Creates the data entries based in the
        path and name of the image.

        - _read_entry : Reads the content of the folder defined in the data
        directory and returns the content.

    Usage example:

    agent:
      name: my_test_agent
    templates:
    - template_name: InputTemplate
      class_name: InputTemplate
      attributes: {}
    - template_name: FolderImageDatasetCV2
      class_name: FolderImageDatasetCV2
      template_input: InputTemplate
      attributes:
        data_dir: '/path/to/data/dit'
        pattern: '**/*'
        batch_size: 1
        shuffle_data: false
        samples_to_load: -1
        load_on_init: false
        label_path_index: -2
        is_ground_truth: false

    """

    IMAGE_READER_METHOD = read_image_file

    @staticmethod
    def get_reader_method() -> Callable:
        """Defines the method to read the images. In this case, using cv2"""
        return read_image_file
