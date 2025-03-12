# -*- coding: utf-8 -*-
import abc
import random

import numpy as np
from sinapsis_core.data_containers.data_packet import DataContainer, ImagePacket
from sinapsis_core.template_base import (
    Template,
    TemplateAttributes,
    TemplateAttributeType,
)

from sinapsis_data_visualization.helpers.color_utils import (
    RGB_TYPE,
    build_color_map,
    get_color_rgb_tuple,
)

random.seed(0)


class BaseAnnotationDrawer(Template, abc.ABC):
    """Base template to handle and draw annotations in images.

    This class incorporates methods to determine if an ImagePacket
    has annotations and to draw annotations on images.

    The execute method calls the draw_annotation method for
    the list of ImagePackets
    """

    COLOR_MAP = build_color_map()

    class AttributesBaseModel(TemplateAttributes):
        """
        Attributes for Image Annotation Drawer

        Args:
            overwrite (bool): Enable overwriting original image content.
                If False Image drawing is performed on a copy of the original one.
            randomized_color (bool): Flag to use random colors in the annotations.
                Defaults to True
        """

        overwrite: bool = False
        randomized_color: bool = True

    def __init__(self, attributes: TemplateAttributeType) -> None:
        """Initializes the Image Annotation Drawer with the given attributes."""
        super().__init__(attributes)
        self.drawing_strategies: list = []
        self.set_drawing_strategy()

    def set_drawing_strategy(self) -> None:
        """Abstract method to determine which annotations to draw
        (e.g., labels, bbox, kpts, etc.)"""

    @staticmethod
    def image_has_annotations(image: ImagePacket) -> bool:
        """
        Checks if the image packet contains annotations.

        Args:
            image (ImagePacket): The image packet to check.
            
        Returns:
            bool: True if the image has annotations, False otherwise.
        """
        return image.annotations is not None

    def draw_annotation(self, image_packet: ImagePacket) -> None:
        """
        Abstract method for drawing annotations on an image packet.
        Args:
            image_packet (ImagePacket): The image packet containing annotations to draw.
        """
        image_packet.content = np.ascontiguousarray(image_packet.content)

        if self.image_has_annotations(image_packet):
            for ann in image_packet.annotations:
                ann_color: RGB_TYPE = get_color_rgb_tuple(
                    color_map=self.COLOR_MAP,
                    class_id=ann.label,
                    randomized=self.attributes.randomized_color,
                )
                for strategy in self.drawing_strategies:
                    image_packet.content = strategy(image_packet.content, ann, ann_color)

    def execute(self, container: DataContainer) -> DataContainer:
        """
        Executes image drawer for images in the container.

        Args:
            container (DataContainer): The data container containing image packets.

        Returns:
            DataContainer: The updated data container with images annotated.
        """

        for image_packet in container.images:
            self.draw_annotation(image_packet)

        return container
