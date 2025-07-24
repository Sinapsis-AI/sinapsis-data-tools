# -*- coding: utf-8 -*-
import base64
from io import BytesIO

import numpy as np
import requests  # type:ignore[import-untyped]
from PIL import Image


def convert_image_ndarray_to_base64(np_image: np.ndarray, image_format: str = "JPEG") -> str:
    """
    Convert a numpy array image to a base64 encoded string using Pillow.

    Args:
        np_image (np.ndarray): The image represented as a numpy array.
        image_format (str): The image format for encoding ('JPEG', 'PNG', etc.)

    Returns:
        str: The base64 encoded image string.
    """
    pil_image = Image.fromarray(np_image)

    with BytesIO() as buffered:
        pil_image.save(buffered, format=image_format)
        binary_data = buffered.getvalue()

    base64_encoded_data = base64.b64encode(binary_data)

    return base64_encoded_data.decode("utf-8")


def decode_base64_to_numpy(base64_str: str) -> np.ndarray:
    image_bytes = base64.b64decode(base64_str)
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    return np.array(image)


def fetch_url_to_numpy(url: str) -> np.ndarray:
    response = requests.get(url)
    response.raise_for_status()
    image = Image.open(BytesIO(response.content)).convert("RGB")
    return np.array(image)
