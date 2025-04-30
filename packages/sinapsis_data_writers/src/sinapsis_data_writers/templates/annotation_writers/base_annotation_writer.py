# -*- coding: utf-8 -*-


import json
from abc import abstractmethod
from pathlib import Path
from typing import Literal, cast

from sinapsis_core.data_containers.data_packet import DataContainer, ImagePacket
from sinapsis_core.template_base import Template
from sinapsis_core.template_base.base_models import (
    OutputTypes,
    TemplateAttributes,
    TemplateAttributeType,
    UIPropertiesMetadata,
)
from sinapsis_core.utils.env_var_keys import SINAPSIS_CACHE_DIR
from sinapsis_data_readers.helpers.coco_dataclasses import CocoJsonKeys

FORMATTED_ANNOTATIONS = list[dict]


class BaseAnnotationWriter(Template):  # type:ignore
    """
    Base Image Annotation Writer that saves annotations to a specified format.
    This template defines the base classes for storing data annotations in a
    structured format. It provides functionalities for accumulating and storing
    annotations in JSON format, with methods for processing the data packets and
    folders.
    """

    class AttributesBaseModel(TemplateAttributes):  # type:ignore
        """Attributes for the Base Annotation Writer.

        Attributes:
            root_dir (str): Local path for cache storage.
            save_dir (str): Local path to save the JSON file.
            output_file (str): Name of the annotations file.

            extension (Literal['json', 'txt']): extension of the file.
        """

        root_dir: str = SINAPSIS_CACHE_DIR
        save_dir: str
        output_file: str = "annotations"
        extension: Literal["json", "txt"] = "json"

    UIProperties = UIPropertiesMetadata(output_type=OutputTypes.IMAGE)

    def __init__(self, attributes: TemplateAttributeType) -> None:
        """Initialize the annotation writer and prepared to accumulate annotations."""
        super().__init__(attributes)
        self.folder_annotations: dict[str, dict[str, FORMATTED_ANNOTATIONS]] = {}

    @staticmethod
    def image_has_annotations(image: ImagePacket) -> bool:
        """
        Checks whether the image packet has annotations.

        Args:
            image (ImagePacket): The image packet to check.

        Returns:
            bool: True if the image has annotations, False otherwise.
        """
        return image.annotations is not None

    @staticmethod
    def get_folder_name_from_source(image_packet: ImagePacket) -> str:
        """
        Extracts the folder name from the image packet's source path.

        Args:
            image_packet (ImagePacket): The image packet containing the source file path.

        Returns:
            str: The name of the folder containing the image.
        """
        if image_packet.source:
            return Path(image_packet.source).parent.name
        return "unknown_folder"

    @staticmethod
    def load_existing_annotations(
        output_path: Path,
    ) -> dict[str, FORMATTED_ANNOTATIONS]:
        """
        Loads existing annotations from a JSON file if it exists.

        Args:
            output_path (Path): Path to the existing JSON file.

        Returns:
            dict[str, FORMATTED_ANNOTATIONS]: The existing annotations
                or an empty dictionary
            if no file exists.
        """
        if output_path.exists():
            with open(output_path, encoding="utf-8") as f:
                data = json.load(f)
                return cast(dict[str, FORMATTED_ANNOTATIONS], data)
        return {"images": [], "annotations": []}

    def save_annotations(self, all_annotations: dict[str, FORMATTED_ANNOTATIONS], folder_name: str) -> None:
        """Saves annotations to a JSON file for a specified folder.

        Args:
            all_annotations (dict[str, FORMATTED_ANNOTATIONS]):
                the dictionary with annotations from the data packets
            folder_name (str): The name of the folder where the annotations file
                is saved.
        """
        save_path = Path(self.attributes.root_dir) / self.attributes.save_dir
        save_path.mkdir(parents=True, exist_ok=True)
        output_file = save_path / f"{Path(self.attributes.output_file).stem}_{folder_name}.{self.attributes.extension}"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_annotations, f, separators=(",", ":"))

    @abstractmethod
    def _annotations_to_format(self, image_packet: ImagePacket) -> FORMATTED_ANNOTATIONS:
        """Converts image annotations to the target format.

        This method should be implemented by subclasses to provide specific logic
        for converting annotations in the image packet to the desired format.

        Args:
            image_packet (ImagePacket): The image packet containing annotations.

        Returns:
            FORMATTED_ANNOTATIONS: A list of formatted annotations for the image.
        """

    def _process_image(self, image_packet: ImagePacket, folder_name: str) -> None:
        """Processes a single image packet, extracts annotations, and adds them to folder
        annotations.

        Args:
            image_packet (ImagePacket): The image packet to process.
            folder_name (str): The folder name to store annotations.
        """
        if not self.image_has_annotations(image_packet):
            return

        formatted_annotations = self._annotations_to_format(image_packet)

        if not any(
            img[CocoJsonKeys.IMAGE_ID] == image_packet.id for img in self.folder_annotations[folder_name]["images"]
        ):
            file_name = Path(image_packet.source).name
            self.folder_annotations[folder_name]["images"].append(
                {
                    CocoJsonKeys.IMAGE_ID: str(image_packet.id),
                    CocoJsonKeys.WIDTH: image_packet.shape[0],
                    CocoJsonKeys.HEIGHT: image_packet.shape[1],
                    CocoJsonKeys.FILE_NAME: file_name,
                    CocoJsonKeys.COCO_URL: "",
                }
            )

        self.folder_annotations[folder_name]["annotations"].extend(formatted_annotations)

    def _process_folder(self, container: DataContainer) -> None:
        """
        Processes all images within the folder and saves annotations.

        Args:
            container (DataContainer): The container holding image packets.
        """
        for image_packet in container.images:
            folder_name = self.get_folder_name_from_source(image_packet)

            if folder_name not in self.folder_annotations:
                output_file = (
                    Path(self.attributes.root_dir)
                    / self.attributes.save_dir
                    / f"{Path(self.attributes.output_file).stem}_{folder_name}.{self.attributes.extension}"
                )
                self.folder_annotations[folder_name] = self.load_existing_annotations(output_file)

            self._process_image(image_packet, folder_name)

    def execute(self, container: DataContainer) -> DataContainer:
        """Executes the annotation process by processing all images and saving annotations.

        Args:
            container (DataContainer): The container holding image packets.

        Returns:
            DataContainer: The processed data container.
        """
        if not container.images:
            return container

        self._process_folder(container)

        current_folder_name = self.get_folder_name_from_source(container.images[-1])
        if current_folder_name in self.folder_annotations:
            self.save_annotations(self.folder_annotations[current_folder_name], current_folder_name)

        return container
