# -*- coding: utf-8 -*-
from typing import cast

import cv2
import numpy as np
from sinapsis_core.data_containers.annotations import BoundingBox, ImageAnnotations
from sinapsis_data_visualization.helpers.annotation_drawer_types import (
    TextInstanceProperties,
    TextStyle,
)
from sinapsis_data_visualization.helpers.color_utils import RGB_TYPE


def get_text_coordinates(
    image_shape: tuple[int, int],
    text_coordinates: tuple[int, int],
    text_box_to_border_offset: float = 0.01,
    label_position: str = "top_right",
) -> tuple[int, int]:
    """
    Compute x,y coordinates for text label according to selected label position.

    Args:
        image_shape (tuple[int, int]): shape if the target image in width,
        height coordinates.
        text_coordinates (tuple[int, int]): coordinates where the text is
        to be placed in width, height.
        text_box_to_border_offset (float, optional): Weight to control offset of
        text box to the image border. It defaults to 0.01.
        label_position (str): Indicate location of label text box. Defaults to: "top_right"
            Available options: "top_left", "top_right".

    Returns:
        tuple[int, int]: Tuple of computed x and y coordinates.
    """
    image_width, image_height = image_shape
    text_height, text_width = text_coordinates
    x, y = image_shape
    match label_position:
        case "top_left":
            x = int(image_width * text_box_to_border_offset)
            y = int(image_height * text_box_to_border_offset + text_height)

        case "top_right":
            x = int(
                max(
                    (image_width * text_box_to_border_offset),
                    image_width - text_width - (image_width * text_box_to_border_offset),
                )
            )
            y = int(image_height * text_box_to_border_offset + text_height)
    return x, y


def get_dynamic_text_properties(image: np.ndarray) -> tuple[float, float]:
    """Compute font size and font thickness according to image shape

    Args:
        image (np.ndarray): image to be drawn

    Returns:
        tuple[float, float]: Tuple of computed font scale and font thickness
    """
    size = max(round(sum(image.shape) / 2 * 0.003), 2)
    font_thickness = max(size - 1, 1)
    font_scale = size / 3
    return font_scale, font_thickness


def get_numeric_str(label: str, numeric_val: float | int) -> str:
    """Writes numeric value of label as string

    Args:
        label (str): label of the annotation
        numeric_val (float|int): numeric_val to convert to string
    Returns
        string label
    """

    extra_text = f"{label}: {numeric_val:.2f}%" if isinstance(numeric_val, float) else f"{label}: {numeric_val}"
    return extra_text


def get_text_size(text: str, text_style: TextStyle) -> tuple[int, int]:
    """
    Returns the width and height of the text to be drawn.

    Args:
        text (str): The text, whose size is to be calculated.
        text_style (TextStyle): Properties of the text: font, size and thickness.

    Returns:
        tuple[int, int]: The (width, height) of the text.
    """
    text_size = cv2.getTextSize(
        text,
        text_style.font,
        text_style.font_scale,
        text_style.thickness,
    )[0]
    text_size = cast(tuple[int, int], text_size)
    return text_size


def draw_text(
    image: np.ndarray,
    text: str,
    text_properties: TextInstanceProperties,
    text_style: TextStyle,
) -> np.ndarray:
    """
    Draws the specified text on the image at the given position.

    Args:
        image (np.ndarray): The image to draw on.
        text (str): The text to be drawn.
        text_properties (TextInstanceProperties): The properties of the text (position, color).
        text_style (TextStyle): Properties of the text: font, size and thickness.

    Returns:
        np.ndarray: The image with the text drawn.
    """
    cv2.putText(
        image,
        text,
        (
            int(text_properties.x_position),
            int(text_properties.y_position),
        ),
        text_style.font,
        text_style.font_scale,
        text_properties.text_color,
        text_style.thickness,
    )
    return image


def draw_extra_labels(
    image: np.ndarray,
    bbox: BoundingBox,
    extra_str_repr: list[str],
    text_y_offsets: list[int],
    text_color: RGB_TYPE,
    text_style: TextStyle,
) -> np.ndarray:
    """Draws additional labels (e.g., confidence score, extra annotations)
    under the primary label.

    Args:
        image (np.ndarray): The image to draw on.
        bbox (BoundingBox): Bounding box with the X-coordinate and
            Y-coordinates of the starting point for the text.

        extra_str_repr (list[str]): List of extra label strings.
        text_y_offsets (list[int]): List of Y offsets
        text_color (RGB_TYPE): The color of the label text.
        text_style (TextStyle): Properties of the text: font,
            scale, and thickness.

    Returns:
        np.ndarray: The image with the extra labels drawn.
    """

    y_position = int(bbox.y)

    for str_repr, y_offset in zip(extra_str_repr, text_y_offsets):
        y_position -= y_offset
        image = draw_text(
            image,
            str_repr,
            TextInstanceProperties(bbox.x, y_position, text_color),
            text_style,
        )

    return image


def draw_annotation_rectangle(
    image: np.ndarray,
    bbox: BoundingBox,
    ann_color: RGB_TYPE,
    text_h: float,
    text_w: float,
) -> np.ndarray:
    """Draws the background rectangle for the label.

    Args:
        image (np.ndarray): The image to draw on.
        bbox (BoundingBox): The bounding box for positioning the rectangle.
        ann_color (RGB_TYPE): The color of the rectangle.
        text_h (float): The height of the text label.
        text_w (float): The width of the text label.

    Returns:
        np.ndarray: The image with the background rectangle drawn.
    """

    cv2.rectangle(
        image,
        (int(bbox.x), int(bbox.y - text_h)),
        (int(bbox.x + text_w), int(bbox.y + 12)),
        ann_color,
        -1,
    )
    return image


def get_extra_ann_labels(
    annotation: ImageAnnotations,
    text_w: int,
    text_h: int,
    text_style: TextStyle,
    spacing: int = 5,
) -> tuple[list[int], list[str], int, int]:
    """
    Extracts additional annotation labels and calculates their dimensions
    and offsets for rendering.

    Args:
        annotation (ImageAnnotations): The annotation object containing
            extra label information.
        text_w (int): The initial width of the text bounding box.
        text_h (int): The initial height of the text bounding box.
        text_style (TextStyle): Properties for the text: font, size
            and thickness.
        spacing (int, optional): The vertical spacing between labels.
            The default value is 5.

    Returns:
        tuple[list[int], list[str]]:
            - 'list[int]': A list of vertical offsets for each
                additional label.
            - 'list[str]': A list of formatted strings for the
                additional labels.
    """
    text_y_offsets = []
    extra_str_repr = []
    for label_k, label_v in annotation.extra_labels.items():
        extra_text: str = label_k
        if isinstance(label_v, (float, int)):
            extra_text = get_numeric_str(extra_text, label_v)
        else:
            extra_text = f"{label_k}: {label_v}"
        extra_text_w, extra_text_h = get_text_size(extra_text, text_style)

        extra_text_h += spacing
        text_h += extra_text_h
        text_w = max(extra_text_w, text_w)
        text_y_offsets.append(extra_text_h)
        extra_str_repr.append(extra_text)
    return text_y_offsets, extra_str_repr, text_h, text_w
