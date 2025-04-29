# -*- coding: utf-8 -*-
from sinapsis_core.data_containers.data_packet import (
    DataContainer,
    ImageColor,
)
from sinapsis_core.template_base import Template
from sinapsis_core.template_base.base_models import TemplateAttributes

from sinapsis_generic_data_tools.helpers.image_color_space_converter import convert_color_space


class ImageColorConversion(Template):
    """A template for converting the color space of images within a DataContainer.

    This template applies color space conversion to all image packets contained within a DataContainer.
    The target color space is specified in the template's attributes.

    Usage example:

    agent:
        name: my_test_agent
    templates:
    -   template_name: InputTemplate
        class_name: InputTemplate
        attributes: {}
    -   template_name: ColorConversion
        class_name: ColorConversion
        template_input: InputTemplate
        attributes:
            target_color_space: 2
    """

    class AttributesBaseModel(TemplateAttributes):
        """Defines the attributes required for the ColorConversion template.

        Attributes:
            target_color_space (ImageColor): The target color space to which all images will be converted.
                - RGB = 1
                - BGR = 2
                - GRAY = 3
                - RGBA = 4
        """

        target_color_space: ImageColor

    def execute(self, container: DataContainer) -> DataContainer:
        """Executes the color space conversion on all image packets within the provided DataContainer.

        Args:
            container (DataContainer): The DataContainer containing the image packets to be processed.

        Returns:
            DataContainer: The DataContainer with all image packets converted to the target color space.
        """
        new_image_packets = [
            convert_color_space(image_packet, self.attributes.target_color_space) for image_packet in container.images
        ]

        container.images = new_image_packets
        return container
