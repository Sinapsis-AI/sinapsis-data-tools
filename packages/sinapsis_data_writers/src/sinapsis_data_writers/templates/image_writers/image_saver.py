# -*- coding: utf-8 -*-
from pathlib import Path
from typing import Literal

import cv2
from sinapsis_core.data_containers.data_packet import DataContainer, ImageColor, ImagePacket
from sinapsis_core.template_base import Template
from sinapsis_core.template_base.base_models import OutputTypes, TemplateAttributes, UIPropertiesMetadata
from sinapsis_core.utils.env_var_keys import SINAPSIS_CACHE_DIR
from sinapsis_generic_data_tools.helpers.image_color_space_converter import convert_color_space


class ImageSaver(Template):
    """Template for saving images to a specified directory,
    with options to save the original image, cropped bounding boxes,
    and segmentation masks.

    Usage example:

    agent:
      name: my_test_agent
    templates:
    - template_name: InputTemplate
      class_name: InputTemplate
      attributes: {}
    - template_name: ImageSaver
      class_name: ImageSaver
      template_input: InputTemplate
      attributes:
        save_dir: '/path/to/desired/destination'
        extension: jpg
        root_dir: $SINAPSIS_CACHE_DIR
        save_full_image: true
        save_bbox_crops: false
        save_mask_crops: false
        min_bbox_dim: 5
    """

    UIProperties = UIPropertiesMetadata(output_type=OutputTypes.IMAGE)

    class AttributesBaseModel(TemplateAttributes):
        """Attributes for the ImageSaver template.

        Args:
            save_dir (str):
                Local path to save the image.
            extension (Literal):
                The image file extension to use. Defaults to 'jpg'.
            root_dir (str):
                The root directory for saving images.
            save_full_image (bool):
                Flag to determine whether to save the original image.
            save_bbox_crops (bool):
                Whether to save the cropped images. Defaults to False.
            save_mask_crops (bool):
                Whether to save the segmentation masks. Defaults to False.
            min_bbox_dim (int):
                Minimum value for the image size.
        """

        save_dir: str
        extension: Literal[
            "jpg",
            "png",
            "tif",
            "bmp",
            "ppm",
            "webp",
            "jp2",
            "hdr",
            "ras",
        ] = "jpg"
        root_dir: str = SINAPSIS_CACHE_DIR
        save_full_image: bool = True
        save_bbox_crops: bool = False
        save_mask_crops: bool = False
        min_bbox_dim: int = 5

    @staticmethod
    def image_has_annotations(image: ImagePacket) -> bool:
        """Checks whether the image has annotations.

        Args:
            image (ImagePacket): Image to check for annotations.

        Returns:
            bool: True if the image has annotations, otherwise False.
        """
        return image.annotations is not None

    def save_image(self, img_destination: Path, image_packet: ImagePacket) -> str:
        """Saves an image to the specified path.

        Args:
            img_destination (Path): Path to save the image.
            image (np.ndarray): Image to be saved.

        Returns:
            str: The path where the image was saved.
        """
        try:
            img_destination.parent.mkdir(parents=True, exist_ok=True)
            if img_destination.suffix != f".{self.attributes.extension}":
                img_destination = img_destination.with_suffix(f".{self.attributes.extension}")

            path_to_save = str(img_destination)
            if image_packet.content is not None and image_packet.content.size > 0:
                if image_packet.color_space is not None and image_packet.color_space != ImageColor.GRAY:
                    image_packet = convert_color_space(image_packet, ImageColor.BGR)
                cv2.imwrite(str(img_destination.absolute()), image_packet.content)
                self.logger.debug(f"Saved image to: {img_destination.absolute()}")
                return path_to_save
            else:
                self.logger.warning(f"Attempted to save an invalid image: {img_destination}")
                return ""
        except OSError as e:
            self.logger.error(f"File system error while saving image to {img_destination}: {e}")
            return ""

    def save_ann_box_crops(self, image_packet: ImagePacket, img_destination: Path) -> None:
        """Saves cropped images based on annotations.

        Args:
            image_packet (ImagePacket): Image to extract crops from.
            img_destination (Path): Path to save the crops.
        """
        img_num = 0
        for ann in image_packet.annotations:
            if not ann.bbox or ann.bbox.h < self.attributes.min_bbox_dim or ann.bbox.w < self.attributes.min_bbox_dim:
                continue

            # Ensure bbox coordinates are non-negative
            ann.bbox.x = max(0, int(ann.bbox.x))
            ann.bbox.y = max(0, int(ann.bbox.y))
            ann.bbox.w = max(0, int(ann.bbox.w))
            ann.bbox.h = max(0, int(ann.bbox.h))

            # Crop the image using the adjusted bbox
            image_bbox = image_packet.content[
                int(ann.bbox.y) : int(ann.bbox.y) + int(ann.bbox.h),
                int(ann.bbox.x) : int(ann.bbox.x) + int(ann.bbox.w),
            ]

            # Generate the save path for the cropped image
            save_path = img_destination.with_name(img_destination.stem + f"_crop_{img_num}" + img_destination.suffix)

            # Save the cropped image
            self.save_image(save_path, image_bbox)
            img_num += 1

    def save_ann_mask_crop(self, image_packet: ImagePacket, img_destination: Path) -> None:
        """Saves cropped segmentation masks based on annotations.

        Args:
            image_packet (ImagePacket): Image to extract mask crops from.
            img_destination (Path): Path to save the mask crops.
        """
        raise NotImplementedError

    def execute(self, container: DataContainer) -> DataContainer:
        """
        Saves the image to the local environment

        Args:
            container (DataContainer): The data container with images.

        Returns:
            DataContainer: The modified container.
        """

        for image_packet in container.images:
            img_destination = Path(self.attributes.root_dir) / self.attributes.save_dir / Path(image_packet.source).name

            # Save the full image if specified
            path_to_source = None
            if self.attributes.save_full_image:
                path_to_source = self.save_image(img_destination, image_packet)

            # Save bounding box crops if specified and annotations exist
            if self.attributes.save_bbox_crops and image_packet.annotations:
                self.save_ann_box_crops(image_packet, img_destination)

            # Update the source of the image packet with the saved path
            if path_to_source:
                image_packet.source = str(path_to_source)

        return container
