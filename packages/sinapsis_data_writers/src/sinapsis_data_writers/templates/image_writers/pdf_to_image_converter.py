# -*- coding: utf-8 -*-
"""PDF to image conversion template."""

from pathlib import Path
from typing import Literal

import numpy as np
from pdf2image import convert_from_path
from sinapsis_core.data_containers.data_packet import DataContainer, ImagePacket
from sinapsis_core.template_base import Template
from sinapsis_core.template_base.base_models import (
    OutputTypes,
    TemplateAttributes,
    TemplateAttributeType,
    UIPropertiesMetadata,
)
from sinapsis_core.utils.env_var_keys import SINAPSIS_CACHE_DIR


class PDFToImage(Template):
    """
    This template handles the conversion of PDF files to images using the
    pdf2image library, allowing each page of the PDF to be represented as an image.

    Usage example:
        agent:
          name: my_test_agent
        templates:
        - template_name: InputTemplate
          class_name: InputTemplate
          attributes: {}
        - template_name: PDFToImage
          class_name: PDFToImage
          template_input: InputTemplate
          attributes:
            pdf_path: '/path/to/pdf/file/to/be/converter'
            output_folder: /path/to/output/images
            file_format: png
            dpi: 200
    """

    UIProperties = UIPropertiesMetadata(output_type=OutputTypes.IMAGE)

    class AttributesBaseModel(TemplateAttributes):
        """
        Attributes for the PDFToImage template.

        Args:
            source_path (str):
                The path of the PDF file to be converted to images.
            output_folder (str):
                The path where the image will be saved
            file_format (Literal[str]):
                Output image format, defaults to “png”
            dpi (int):
                Image quality in DPI, defaults to 200

        """

        pdf_path: str
        output_folder: str = SINAPSIS_CACHE_DIR + "/artifacts"
        file_format: Literal["jpeg", "png", "tiff", "ppm"] = "png"
        dpi: int = 200

    def __init__(self, attributes: TemplateAttributeType) -> None:
        """Initializes the PDFToImage template with given attributes.

        Args:
            attributes (TemplateAttributeType): The attributes for the PDF to image conversion.
        """
        super().__init__(attributes)
        output_folder = Path(self.attributes.output_folder)
        output_folder.mkdir(parents=True, exist_ok=True)

    def convert_to_images(self) -> list[ImagePacket]:
        """Applies the PDF to image conversion using the provided PDF file.

        Returns:
            DataContainer: The updated data container with images.
        """
        img_list: list[ImagePacket] = []

        images_from_path = convert_from_path(
            self.attributes.pdf_path,
            dpi=min(self.attributes.dpi, 800),
            fmt=self.attributes.file_format,
            output_folder=self.attributes.output_folder,
        )
        for image in images_from_path:
            image_packet = ImagePacket(
                content=np.asarray(image),
                embedding=[],
            )
            img_list.append(image_packet)
        return img_list

    def execute(self, container: DataContainer) -> DataContainer:
        """
        Executes the pdf to image conversion process.

        Args:
            container (DataContainer): The data container for storing the converted images.

        Returns:
            DataContainer: The updated data container with images.
        """
        images = self.convert_to_images()
        container.images.extend(images)

        return container
