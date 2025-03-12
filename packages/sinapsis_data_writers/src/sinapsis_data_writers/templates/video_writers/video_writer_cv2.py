# -*- coding: utf-8 -*-

from typing import Literal

import cv2
import numpy as np

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
        )

    def add_frame_to_video(self, frame: np.ndarray) -> None:
        """Adds a frame to the OpenCV video writer.
        Args:
            frame (np.ndarray): The frame to be added.

        Raises:
            ValueError: If the frame dimensions do not match the expected dimensions.
        """
        if self.video_writer is not None:
            if self.validate_frame_dims(frame):
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                self.video_writer.write(frame)
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
