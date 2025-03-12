# -*- coding: utf-8 -*-
from enum import Enum

import cv2
from sinapsis_core.data_containers.data_packet import ImageColor, ImagePacket
from sinapsis_core.utils.logging_utils import sinapsis_logger

color_mapping = {
    (ImageColor.RGB, ImageColor.BGR): cv2.COLOR_RGB2BGR,
    (ImageColor.RGB, ImageColor.GRAY): cv2.COLOR_RGB2GRAY,
    (ImageColor.RGB, ImageColor.RGBA): cv2.COLOR_RGB2RGBA,
    (ImageColor.BGR, ImageColor.RGB): cv2.COLOR_BGR2RGB,
    (ImageColor.BGR, ImageColor.GRAY): cv2.COLOR_BGR2GRAY,
    (ImageColor.BGR, ImageColor.RGBA): cv2.COLOR_BGR2RGBA,
    (ImageColor.GRAY, ImageColor.RGB): cv2.COLOR_GRAY2RGB,
    (ImageColor.GRAY, ImageColor.BGR): cv2.COLOR_GRAY2BGR,
    (ImageColor.GRAY, ImageColor.RGBA): cv2.COLOR_GRAY2RGBA,
    (ImageColor.RGBA, ImageColor.RGB): cv2.COLOR_RGBA2RGB,
    (ImageColor.RGBA, ImageColor.BGR): cv2.COLOR_RGBA2BGR,
    (ImageColor.RGBA, ImageColor.GRAY): cv2.COLOR_RGBA2GRAY,
}


def convert_color_space_cv(image: ImagePacket, desired_color_space: Enum) -> ImagePacket:
    """Converts an image from one color space to another, provided
        they are in the color mapping options.

    Args:
        image (ImagePacket): Image packet to apply the conversion
        desired_color_space (Enum): Color space to convert the image

    Returns:
        ImagePacket: Updated ImagePacket with content converted into the new color space
        
    Raises:
         ValueError: If the conversion is not possible, return an error.

    """
    current_color_space = image.color_space

    if (current_color_space, desired_color_space) in color_mapping:
        conversion_code = color_mapping[(current_color_space, desired_color_space)]
        try:
            image.content = cv2.cvtColor(image.content, conversion_code)
            image.color_space = desired_color_space

        except cv2.error:
            sinapsis_logger.error(f"Invalid conversion between {current_color_space} and {desired_color_space}")

    else:
        raise ValueError(f"Conversion from {current_color_space} to {desired_color_space} is not supported.")

    return image
