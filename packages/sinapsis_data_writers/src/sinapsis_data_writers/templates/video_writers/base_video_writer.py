# -*- coding: utf-8 -*-

import abc
from typing import Any, Literal

import numpy as np
from sinapsis_core.data_containers.data_packet import DataContainer, ImagePacket
from sinapsis_core.template_base.base_models import (
    OutputTypes,
    TemplateAttributes,
    TemplateAttributeType,
    UIPropertiesMetadata,
)
from sinapsis_core.template_base.template import Template


def base_documentation() -> str:
    return """This template handles video writing, allowing the addition of frames
    to create a video file based on specified attributes such as path, dimensions, and codec.
    """


def base_attributes_documentation() -> str:
    return """
        destination_path (str):
            The path where the video will be saved.
        height (int):
            The height of the video frames. Defaults to -1 (set on first frame).
        width (int):
            The width of the video frames. Defaults to -1 (set on first frame).
        fps (int):
            The frames per second for the video. Defaults to 1.
        codec (Literal["mp4v", "avc1"]):
            The codec used for video encoding. Defaults to "mp4v".
    """


class BaseVideoWriter(Template, abc.ABC):
    f"""
    Base class for video writers.

    This template allows the creation and writing of video files from frames.

    {base_documentation()}

    """
    UIProperties = UIPropertiesMetadata(output_type=OutputTypes.VIDEO)

    class AttributesBaseModel(TemplateAttributes):
        __doc__ = f"""
        Attributes for the video writer template.

        Args:
        {base_attributes_documentation()}
        """

        destination_path: str
        height: int = -1
        width: int = -1
        fps: int = 1
        codec: Literal["mp4v", "avc1", "hevc_cuvid", "h264_cuvid", "hevc", "h264_nvenc", "hevc_nvenc"]

    def __init__(self, attributes: TemplateAttributeType) -> None:
        super().__init__(attributes)
        self.video_writer = None
        self.color_space = None

        if self.attributes.codec not in self.get_supported_codecs():
            raise ValueError(
                f"Unsupported codec: {self.attributes.codec}. Supported codecs: {self.get_supported_codecs()}"
            )

    @abc.abstractmethod
    def get_supported_codecs(self) -> set[str]:
        """Returns a set of supported codecs for the subclass."""

    @abc.abstractmethod
    def make_video_writer(self) -> Any:
        """Creates a VideoWriter object based on the attributes.
        The video writer object depends on the library used to
        write the video.
        """

    @abc.abstractmethod
    def add_frame_to_video(self, image_packet: ImagePacket) -> None:
        """Adds a frame to the video writer.

        Args:
            image_packet (ImagePacket): The image packet to be added to the video.
        """

    @abc.abstractmethod
    def video_writer_is_done(self) -> None:
        """Releases the video writer resources when done writing."""

    def validate_frame_dims(self, frame: np.ndarray) -> bool:
        """Validates if the frame dimensions match the specified width and height.

        Args:
            frame (np.ndarray): The frame to validate.

        Returns:
            bool: True if dimensions match, False otherwise.
        """
        if len(frame.shape) == 2:
            height, width = frame.shape
        else:
            height, width, _ = frame.shape
        match: bool = height == self.attributes.height and width == self.attributes.width
        return match

    def init_if_needed(self, container: DataContainer) -> None:
        """Initializes the video writer if it has not been initialized.

        Args:
            container (DataContainer): The data container containing images.
        """
        if self.video_writer is None and container.images:
            first_image = container.images[0]
            if len(first_image.shape) == 2:
                height, width = first_image.shape
            else:
                height, width, _ = first_image.shape
            self.color_space = first_image.color_space
            self.attributes.height = height
            self.attributes.width = width
            self.video_writer = self.make_video_writer()

    def execute(self, container: DataContainer) -> DataContainer:
        """Executes the video writing process.

        Args:
            container (DataContainer): The data container with images.

        Returns:
            DataContainer: The processed data container.
        """
        self.init_if_needed(container)
        for image_packet in container.images:
            self.add_frame_to_video(image_packet)

        if not container.images:
            self.video_writer_is_done()

        return container
