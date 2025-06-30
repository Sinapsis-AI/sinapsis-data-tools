# -*- coding: utf-8 -*-

from io import BytesIO
from pathlib import PosixPath
from typing import Callable

from kornia.core import Tensor
from kornia.io import ImageLoadType, load_image
from kornia.utils import image_to_tensor
from PIL import Image

from sinapsis_data_readers.helpers.tags import Tags
from sinapsis_data_readers.templates.image_readers.base_image_folder_data_loader import (
    ImageBaseDataReader,
)


def read_image_file(file_path: str | PosixPath | bytes) -> Tensor:
    """Method to read the image whether from a bytes object or local path

    Args:
        file_path (str | PosixPath | bytes): either the file path in disk or the bytes object
    Returns:
        torch.Tensor: the image as a torch tensor
    """
    img_tensor: Tensor

    if isinstance(file_path, bytes):
        image = Image.open(BytesIO(file_path)).convert("RGB")
        img_tensor = image_to_tensor(image).float() / 255.0

    else:
        if isinstance(file_path, PosixPath):
            file_path = str(file_path.resolve())
        img_tensor = load_image(file_path, ImageLoadType.RGB32)

    return img_tensor.unsqueeze(0)


FolderImageDatasetKorniaUIProperties = ImageBaseDataReader.UIProperties
FolderImageDatasetKorniaUIProperties.tags.extend([Tags.KORNIA, Tags.OPENCV, Tags.DATASET])


class FolderImageDatasetKornia(ImageBaseDataReader):
    """Dataset creation for images in a directory in the disk with kornia

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
    UIProperties = FolderImageDatasetKorniaUIProperties

    @staticmethod
    def get_reader_method() -> Callable:
        """Defines the method to read the images. In this case, using kornia"""
        return read_image_file
