# -*- coding: utf-8 -*-
import colorsys
import math
import random

from matplotlib import colors
from sinapsis_data_visualization.helpers.annotation_drawer_types import RGB_TYPE


def build_color_map(color_names: list[str] | None = None, shuffle: bool = True) -> dict[int, RGB_TYPE]:
    """
    Method to generate a mapping of indices to RGB color values.
    By default, it uses the CSS4 color names provided by Matplotlib,
    but a custom list of color names can be supplied.
    Optionally, the colors can be shuffled to randomize their order in the mapping.

    Args:
        color_names (list[str] | None): A list of color names as strings. If 'None',
            the full list of CSS4 color names is used.
        shuffle (bool): If 'True', the order of colors in the color map is randomized. Defaults to 'True'.

    Returns:
        dict[int, RGB_TYPE]: A dictionary where keys are integers (starting from 0) and values
            are RGB color tuples with values normalized to the 0-255 range.

    """
    color_keys = list(colors.CSS4_COLORS.keys()) if color_names is None else color_names
    if shuffle:
        random.shuffle(color_keys)
    color_dict: dict[int, RGB_TYPE] = {}
    for idx, color_name in enumerate(color_keys):
        normalized_color = colors.to_rgb(color_name)
        color_dict[idx] = (
            normalized_color[0] * 255,
            normalized_color[1] * 255,
            normalized_color[2] * 255,
        )
    return color_dict


def get_color_rgb_tuple(
    color_map: dict[int, RGB_TYPE],
    class_id: int | None = None,
    randomized: bool = True,
) -> RGB_TYPE:
    """
    Method to fetch the RGB color combination associated with a specific class_id
    from the provided color_map dictionary. If 'class_id' is not provided, or if it is
    invalid, a random color is selected from the color_map dictionary. If randomized
    is True, a random color is selected from the color_map dictionary.

    Args:
        color_map (dict[int, RGB_TYPE]): A dictionary mapping class IDs (integers)
            to RGB color tuples.
        class_id (int | None): The class ID for which the color is requested. If 'None'
            or invalid, a random color is selected. Defaults to 'None'.
        randomized (bool): If 'True', the function ignores the provided 'class_id'
            and returns a random color from the color map. Defaults to 'True'.

    Returns:
        RGB_TYPE: A tuple representing the RGB color, where each component is an
            integer in the range 0-255.

    Raises:
        ValueError: If 'color_map' is empty or invalid.
    """
    if class_id is None or isinstance(class_id, str) or randomized:
        class_id = random.randrange(0, len(color_map))
    try:
        return color_map[class_id]
    except IndexError:
        return color_map[random.randrange(0, len(color_map))]


def is_light_colour(rgb: RGB_TYPE) -> bool:
    """Checks the brightness of image to determine whether it is above a certain
    threshold.
    Args:
        rgb (RGB_TYPE): Color model for RED, GREEN and BLUE
    Returns
        True if brightness is above the threshold. False otherwise
    """
    red, green, blue = rgb
    perceived_brightness = math.sqrt(0.299 * (red * red) + 0.587 * (green * green) + 0.114 * (blue * blue))
    return perceived_brightness > 127.5


def darken_or_lighten_color(rgb: RGB_TYPE, dark_scale: float = 1.5, light_scale: float = 0.2) -> RGB_TYPE:
    """Darkens or lightens the color based on brightness of the input color

    Args:
        rgb (RGB_TYPE): Color model for RED, GREEN and BLUE
        dark_scale (float): the value of scale for dark color.
        light_scale (float): the value of scale for lighter colors.

    Returns:
        RGB_TYPE: New RGB model for image
    """
    scale = light_scale if is_light_colour(rgb) else dark_scale
    max_rgb_val = 255.0
    red, green, blue = rgb

    hue, luminance, saturation = colorsys.rgb_to_hls(red / max_rgb_val, green / max_rgb_val, blue / max_rgb_val)

    lightness = max(0, min(1, int(luminance * scale)))
    red, green, blue = colorsys.hls_to_rgb(hue, lightness, saturation)
    return int(red * 255), int(green * 255), int(blue * 255)
