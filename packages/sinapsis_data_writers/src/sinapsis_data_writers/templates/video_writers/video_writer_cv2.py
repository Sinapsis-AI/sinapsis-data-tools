# -*- coding: utf-8 -*-

from typing import Literal

import cv2
from sinapsis_core.data_containers.data_packet import ImageColor, ImagePacket
from sinapsis_core.template_base.base_models import OutputTypes, UIPropertiesMetadata
from sinapsis_generic_data_tools.helpers.image_color_space_converter import convert_color_space

from sinapsis_data_writers.templates.video_writers.base_video_writer import BaseVideoWriter


class VideoWriterCV2(BaseVideoWriter):
    """
    Video writer Template that uses the OpenCV library
    to write the frames in the local environment.

    Usage example:

    agent:
      name: my_test_agent
    templates:
    - template_name: InputTemplate
      class_name: InputTemplate
      attributes: {}
    - template_name: VideoWriterCV2
      class_name: VideoWriterCV2
      template_input: InputTemplate
      attributes:
        destination_path: '/path/to/video/file'
        height: -1
        width: -1
        fps: 1
        codec: 'mp4v'


    """

    UIProperties = UIPropertiesMetadata(category="OpenCV", output_type=OutputTypes.VIDEO)

    class AttributesBaseModel(BaseVideoWriter.AttributesBaseModel):
        codec: Literal["mp4v", "avc1"] = "mp4v"

    SUPPORTED_CODECS: set[str] = {"mp4v", "avc1"}  # noqa: RUF012

    def get_supported_codecs(self) -> set[str]:
        return self.SUPPORTED_CODECS

    def make_video_writer(self) -> cv2.VideoWriter:
        """Creates a VideoWriter object with OpenCV settings.

        Returns:
            cv2.VideoWriter: The initialized OpenCV video writer object.
        """
        fourcc = cv2.VideoWriter_fourcc(*self.attributes.codec)
        return cv2.VideoWriter(
            self.attributes.destination_path,
            fourcc,
            self.attributes.fps,
            (self.attributes.width, self.attributes.height),
            self.color_space != ImageColor.GRAY,
        )

    def add_frame_to_video(self, image_packet: ImagePacket) -> None:
        """Adds a frame to the OpenCV video writer.
        Args:
            image_packet (ImagePacket): The frame to be added.

        Raises:
            ValueError: If the frame dimensions do not match the expected dimensions.
        """
        if self.video_writer is not None:
            if self.validate_frame_dims(image_packet.content):
                if image_packet.color_space != ImageColor.GRAY:
                    image_packet = convert_color_space(image_packet, ImageColor.BGR)
                self.video_writer.write(image_packet.content)
            else:
                self.logger.warning(
                    f"""Dimensions provided ({self.attributes.height}, {self.attributes.width})
                do not correspond to those of the video frames"""
                )
        else:
            self.logger.error("Video writer not initialized.")

    def video_writer_is_done(self) -> None:
        """Releases the video writer resources when done writing."""
        if self.video_writer:
            self.video_writer.release()
