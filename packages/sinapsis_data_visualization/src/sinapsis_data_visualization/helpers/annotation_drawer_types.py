# -*- coding: utf-8 -*-
from pydantic.dataclasses import dataclass

RGB_TYPE = tuple[int, int, int] | tuple[float, float, float]


@dataclass
class KeyPointAppearance:
    """
    Appearance of the keypoint

    color (RGB_TYPE): color of the bounding box
    thickness (Optional[int]): Line thickness.
        The default value is 2.
    radius (Optional[int], optional): radius o:75
    f the circle. The default value is 2.
    """

    color: RGB_TYPE
    thickness: int = 2
    radius: int = 2


@dataclass
class TextStyle:
    """
    font (int): Style of font
            Available options:
                FONT_HERSHEY_SIMPLEX = 0.
                FONT_HERSHEY_PLAIN = 1.
                FONT_HERSHEY_DUPLEX = 2.
                FONT_HERSHEY_COMPLEX = 3.
                FONT_HERSHEY_TRIPLEX = 4.
                FONT_HERSHEY_COMPLEX_SMALL = 5.
                FONT_HERSHEY_SCRIPT_SIMPLEX = 6.
                FONT_HERSHEY_SCRIPT_COMPLEX = 7.
    font_scale (float): Scale of font
    thickness (int): Thickness of font
    """

    font: int = 0
    font_scale: float = 0.5
    thickness: int = 2


@dataclass
class TextInstanceProperties:
    """
    x_position (float): x coordinate for text
    y_position (float): y coordinate for text
    text_color (RGB_TYPE): color for text string
    """

    x_position: float
    y_position: float
    text_color: RGB_TYPE
