# -*- coding: utf-8 -*-

import torch
from sinapsis_core.data_containers.data_packet import ImageColor, ImagePacket
from sinapsis_core.utils.logging_utils import sinapsis_logger


def convert_color_space_torch(image_packet: ImagePacket, desired_color_space: ImageColor) -> ImagePacket:
    """Converts the color space of the image contained in the ImagePacket using PyTorch.

    Args:
        image_packet (ImagePacket): The ImagePacket containing the image and its current color space.
        desired_color_space (ImageColor): The target color space to which the image should be converted.

    Raises:
        ValueError: If the conversion between the current and desired color spaces is not supported.

    Returns:
        ImagePacket: The ImagePacket with the image converted to the desired color space.
    """
    tensor = image_packet.content
    current_color_space = image_packet.color_space
    if current_color_space is None:
        sinapsis_logger.info("Image has no color space associated")
        return image_packet
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
