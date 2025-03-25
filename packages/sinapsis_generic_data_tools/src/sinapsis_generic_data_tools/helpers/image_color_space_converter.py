# -*- coding: utf-8 -*-
import cv2
import torch
from numpy import ndarray
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


def convert_color_space(image_packet: ImagePacket, desired_color_space: ImageColor) -> ImagePacket:
    """Converts the color space of the image contained in the ImagePacket to the desired color space.

    Args:
        image_packet (ImagePacket): The ImagePacket containing the image and its current color space.
        desired_color_space (ImageColor): The target color space to which the image should be converted.

    Raises:
        TypeError: If the content of the ImagePacket is neither a numpy.ndarray nor a torch.Tensor.

    Returns:
        ImagePacket: The ImagePacket with the image converted to the desired color space.
    """
    current_color_space = image_packet.color_space

    if current_color_space == desired_color_space:
        return image_packet

    if isinstance(image_packet.content, ndarray):
        return convert_color_space_cv(image_packet, current_color_space, desired_color_space)
    elif isinstance(image_packet.content, torch.Tensor):
        return convert_color_space_torch(image_packet, current_color_space, desired_color_space)
    else:
        raise TypeError(f"Unsupported content type: {type(image_packet.content)}")


def convert_color_space_cv(
    image_packet: ImagePacket, current_color_space: ImageColor, desired_color_space: ImageColor
) -> ImagePacket:
    """Converts the color space of the image contained in the ImagePacket using OpenCV.

    Args:
        image_packet (ImagePacket): The ImagePacket containing the image and its current color space.
        current_color_space (ImageColor): The current color space of the image.
        desired_color_space (ImageColor): The target color space to which the image should be converted.

    Raises:
        ValueError: If the conversion between the current and desired color spaces is not supported.

    Returns:
        ImagePacket: The ImagePacket with the image converted to the desired color space.
    """
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


def convert_color_space_torch(
    image_packet: ImagePacket, current_color_space: ImageColor, desired_color_space: ImageColor
) -> ImagePacket:
    """Converts the color space of the image contained in the ImagePacket using PyTorch.

    Args:
        image_packet (ImagePacket): The ImagePacket containing the image and its current color space.
        current_color_space (ImageColor): The current color space of the image.
        desired_color_space (ImageColor): The target color space to which the image should be converted.

    Raises:
        ValueError: If the conversion between the current and desired color spaces is not supported.

    Returns:
        ImagePacket: The ImagePacket with the image converted to the desired color space.
    """
    tensor = image_packet.content

    if (current_color_space, desired_color_space) in {
        (ImageColor.RGB, ImageColor.BGR),
        (ImageColor.BGR, ImageColor.RGB),
    }:
        if tensor.shape[-1] == 3:
            image_packet.content = tensor[..., [2, 1, 0]]
        else:
            image_packet.content = tensor.permute(2, 1, 0)
        image_packet.color_space = desired_color_space

    elif (current_color_space, desired_color_space) in {
        (ImageColor.RGB, ImageColor.GRAY),
        (ImageColor.BGR, ImageColor.GRAY),
    }:
        if current_color_space == ImageColor.BGR:
            tensor = tensor[..., [2, 1, 0]] if tensor.shape[-1] == 3 else tensor.permute(2, 1, 0)

        weights = torch.tensor([0.299, 0.587, 0.114], dtype=tensor.dtype, device=tensor.device)
        if tensor.shape[-1] == 3:
            image_packet.content = (tensor * weights).sum(dim=-1, keepdim=True)
        else:
            image_packet.content = (tensor.permute(1, 2, 0) * weights).sum(dim=-1, keepdim=True).permute(2, 0, 1)
        image_packet.color_space = desired_color_space

    elif (current_color_space, desired_color_space) in {
        (ImageColor.GRAY, ImageColor.RGB),
        (ImageColor.GRAY, ImageColor.BGR),
    }:
        if tensor.shape[-1] == 1:
            image_packet.content = tensor.repeat(1, 1, 3)
        else:
            image_packet.content = tensor.repeat(3, 1, 1)
        image_packet.color_space = desired_color_space

    else:
        raise ValueError(f"Unsupported Torch conversion: {current_color_space} -> {desired_color_space}")

    return image_packet
