# -*- coding: utf-8 -*-

import abc
import os
from pathlib import Path
from random import shuffle
from typing import Callable, cast

from sinapsis_core.data_containers.annotations import ImageAnnotations
from sinapsis_core.data_containers.data_packet import ImageColor, ImagePacket

from sinapsis_data_readers.templates.base_file_data_loader import (
    ContentNotSetException,
    _BaseDataReader,
    base_attributes_documentation,
    base_documentation,
    example_documentation,
)

SUPPORTED_IMAGE_TYPES: list[str] = [".jpg", ".jpeg", ".png", ".gif", ".tiff"]


class ImageBaseDataReader(_BaseDataReader, abc.ABC):
    __doc__ = f""" Base Class for Image Readers
        Templates that inherit from this will always load images in the DataContainer
        {base_documentation()}

        Example:
            my_data_loader  = ImageBaseDataReader({{'data_dir': 'some/path', 'batch_size': 2}})

            {example_documentation()}
         """

    class AttributesBaseModel(_BaseDataReader.AttributesBaseModel):
        __doc__ = f"""
        {base_attributes_documentation()}
        label_path_index: int = -2
                for datasets that rely on the dirname as the ground truth. The image file path will
                be split as 'data_label = data_file_path.ext.split(os.sep)[label_path_index]'.
        is_ground_truth: bool = False
                weather the data is a ground truth or not.
        """

        label_path_index: int = -2
        is_ground_truth: bool = False

    PACKET_ATT_NAME = "images"

    @staticmethod
    @abc.abstractmethod
    def get_reader_method() -> Callable:
        """abstract method to define how the image is to be read
        This method is defined in each template
        """

    def read_packet_content(self, data_packet: ImagePacket) -> None:
        """Method to extract the content for the Packet after image
        has been read using the _get_reader_method
        This method also checks the integrity of the image
        """
        data_packet.content = self.get_reader_method()(data_packet.source)
        if data_packet.content is None:
            raise ContentNotSetException(f"Failed to load {data_packet.source}, please check file and its integrity")

    def make_data_entries(self) -> list[ImagePacket]:
        """method to create ImagePackets with empty content
        and label set as the name of the image
        The method returns the number of ImagePackets set by batch_size

        """

        image_packets: list[ImagePacket] = []
        for img_path in self._find_valid_data_paths(return_as_str=True):
            img_path = cast(str, img_path)
            image_label = img_path.split(os.sep)[self.attributes.label_path_index]

            img_content = None
            image_packet = ImagePacket(
                content=img_content,
                source=img_path,
                color_space=ImageColor.RGB,
                annotations=[
                    ImageAnnotations(
                        label_str=image_label,
                        is_ground_truth=self.attributes.is_ground_truth,
                    )
                ],
            )

            if self.attributes.load_on_init:
                try:
                    self.read_packet_content(image_packet)
                except ContentNotSetException:  # do not add entry if image can't be read
                    continue

            image_packets.append(image_packet)
        return image_packets

    def _find_valid_data_paths(self, return_as_str: bool = False) -> list[str | Path]:
        """Method to find valid data paths in the root dir
        This method is to be used when creating the data entries as the image path
        If shuffle_data is True, the data items are randomly returned

        Args:
            return_as_str (bool): Flat to indicate the path should be returned as string. If False,
            the path is returned as a Path

        Returns:
            list[str| path]: the path as string or Path object
        """
        data_items = [
            img_path if not return_as_str else str(img_path.resolve())
            for img_path in Path(self.attributes.data_dir).glob(self.attributes.pattern)
            if img_path.suffix.lower() in SUPPORTED_IMAGE_TYPES
        ]

        if self.attributes.samples_to_load >= 0:
            data_items = data_items[: self.attributes.samples_to_load]
        if self.attributes.shuffle_data:
            shuffle(data_items)
        return data_items
