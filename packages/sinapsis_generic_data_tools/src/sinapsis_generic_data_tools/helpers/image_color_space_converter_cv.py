# -*- coding: utf-8 -*-
import cv2
from sinapsis_core.data_containers.data_packet import ImageColor, ImagePacket
from sinapsis_core.utils.logging_utils import sinapsis_logger

color_mapping_cv = {
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


def convert_color_space_cv(image_packet: ImagePacket, desired_color_space: ImageColor) -> ImagePacket:
    """Converts the color space of the image contained in the ImagePacket using OpenCV.

    Args:
        image_packet (ImagePacket): The ImagePacket containing the image and its current color space.
        desired_color_space (ImageColor): The target color space to which the image should be converted.

    Raises:
        ValueError: If the conversion between the current and desired color spaces is not supported.

    Returns:
        ImagePacket: The ImagePacket with the image converted to the desired color space.
    """
    current_color_space = image_packet.color_space

    if current_color_space is None:
        sinapsis_logger.debug("No color conversion was performed due to current color space being None.")
        return image_packet

    if current_color_space == desired_color_space:
        return image_packet

    if (current_color_space, desired_color_space) in color_mapping_cv:
        conversion_code = color_mapping_cv[(current_color_space, desired_color_space)]
        try:
            image_packet.content = cv2.cvtColor(image_packet.content, conversion_code)
            image_packet.color_space = desired_color_space

        except cv2.error:
            sinapsis_logger.error(f"Invalid conversion between {current_color_space} and {desired_color_space}")

    else:
        raise ValueError(f"Conversion from {current_color_space} to {desired_color_space} is not supported.")

    return image_packet
