# -*- coding: utf-8 -*-
import abc
import random
from pathlib import Path

import numpy as np
from sinapsis_core.data_containers.annotations import ImageAnnotations
from sinapsis_core.data_containers.data_packet import DataContainer, ImagePacket
from sinapsis_core.template_base import Template
from sinapsis_core.template_base.base_models import (
    OutputTypes,
    TemplateAttributes,
    TemplateAttributeType,
    UIPropertiesMetadata,
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
    UIProperties = UIPropertiesMetadata(output_type=OutputTypes.IMAGE)

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

    def get_annotation_color(self, ann: ImageAnnotations) -> RGB_TYPE:
        """
        Retrieves the color for an annotation.

        Args:
            ann: The annotation to fetch the color for.

        Returns:
            RGB_TYPE: The color corresponding to the annotation.
        """
        return get_color_rgb_tuple(
            color_map=self.COLOR_MAP,
            class_id=ann.label,
            randomized=self.attributes.randomized_color,
        )

    def apply_drawing_strategies(self, image_packet: ImagePacket) -> np.ndarray:
        """
        Applies drawing strategies to the image packet.

        Args:
            image_packet (ImagePacket): The image packet containing annotations to draw.

        Returns:
            np.ndarray: The image content after applying the drawing strategies.
        """
        annotated_image = image_packet.content
        for ann in image_packet.annotations:
            ann_color = self.get_annotation_color(ann)
            for strategy in self.drawing_strategies:
                annotated_image = strategy(annotated_image, ann, ann_color)
        return annotated_image

    def draw_annotation(self, image_packet: ImagePacket) -> np.ndarray:
        """
        Draws annotations on the provided image packet.

        This method checks if the image packet contains annotations and, if so, applies
        drawing strategies to annotate the image.

        Args:
            image_packet (ImagePacket): The image packet containing annotations to draw.

        Returns:
            np.ndarray: The annotated image content as a NumPy array. If the image doesn't
                have annotations, the original image content is returned without modification.
        """
        image_packet.content = np.ascontiguousarray(image_packet.content)

        if not self.image_has_annotations(image_packet):
            return image_packet.content

        annotated_image = self.apply_drawing_strategies(image_packet)

        return annotated_image

    def process_images(self, container: DataContainer) -> None:
        """
        Process and annotate images in the container.
        If self.attributes.overwrite is True, it overwrites the image content;
        otherwise, it adds annotated images to the container.

        Args:
            container (DataContainer): The data container containing image packets.
        """
        if self.attributes.overwrite:
            for image_packet in container.images:
                image_packet.content = self.draw_annotation(image_packet)
        else:
            annotated_images: list[ImagePacket] = []
            for image_packet in container.images:
                annotated_image = self.draw_annotation(image_packet)

                if annotated_image is not image_packet.content:
                    annotated_images.append(
                        ImagePacket(
                            content=annotated_image,
                            color_space=image_packet.color_space,
                            source=f"a_{Path(image_packet.source).name}",
                        )
                    )
            container.images.extend(annotated_images)

    def execute(self, container: DataContainer) -> DataContainer:
        """
        Executes image drawer for images in the container.

        Args:
            container (DataContainer): The data container containing image packets.

        Returns:
            DataContainer: The updated data container with images annotated.
        """
        self.process_images(container)

        return container
