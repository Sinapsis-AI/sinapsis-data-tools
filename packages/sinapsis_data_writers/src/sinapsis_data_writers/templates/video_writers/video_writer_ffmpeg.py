# -*- coding: utf-8 -*-
"""Video writer Template using ffmpeg-python binding from
https://github.com/kkroening/ffmpeg-python"""

from typing import Literal

import ffmpeg
import numpy as np
from sinapsis_core.data_containers.data_packet import ImageColor, ImagePacket
from sinapsis_core.template_base.base_models import OutputTypes, UIPropertiesMetadata
from sinapsis_generic_data_tools.helpers.image_color_space_converter import convert_color_space

from sinapsis_data_writers.templates.video_writers.base_video_writer import BaseVideoWriter


class VideoWriterFFMPEG(BaseVideoWriter):
    """
    Template to write videos in the local environment using
    the FFMPEG package

    Usage example:

    agent:
      name: my_test_agent
    templates:
    - template_name: InputTemplate
      class_name: InputTemplate
      attributes: {}
    - template_name: VideoWriterFFMPEG
      class_name: VideoWriterFFMPEG
      template_input: InputTemplate
      attributes:
        destination_path: '/path/to/video/'
        height: -1
        width: -1
        fps: 1
        codec: 'hevc_nvenc'
    """

    UIProperties = UIPropertiesMetadata(category="FFMPEG", output_type=OutputTypes.VIDEO)

    class AttributesBaseModel(BaseVideoWriter.AttributesBaseModel):
        codec: Literal["hevc_nvenc", "hevc_cuvid", "h264_cuvid", "hevc", "h264_nvenc"] = "hevc_nvenc"

    SUPPORTED_CODECS: set[str] = {"hevc_nvenc", "hevc_cuvid", "h264_cuvid", "hevc", "h264_nvenc"}  # noqa: RUF012

    def get_supported_codecs(self) -> set[str]:
        return self.SUPPORTED_CODECS

    def make_video_writer(self) -> ffmpeg.input:
        """Creates a video writer using ffmpeg.

        Returns:
            Any: The initialized ffmpeg video writer object.
        """
        video_writer = (
            ffmpeg.input(
                "pipe:",
                format="rawvideo",
                pix_fmt="rgb24" if self.color_space != ImageColor.GRAY else "gray",
                s=f"{self.attributes.width}x{self.attributes.height}",
            )
            .output(
                self.attributes.destination_path,
                pix_fmt="yuv420p",
                framerate=self.attributes.fps,
                vcodec=self.attributes.codec,
            )
            .overwrite_output()
            .run_async(pipe_stdin=True)
        )

        return video_writer

    def add_frame_to_video(self, image_packet: ImagePacket) -> None:
        """Adds a frame to the ffmpeg video object.

        Args:
            image_packet (ImagePacket): The frame to be added.
        """
        if self.video_writer is not None:
            if image_packet.color_space != ImageColor.GRAY:
                image_packet = convert_color_space(image_packet, ImageColor.RGB)
            self.video_writer.stdin.write(image_packet.content.astype(np.uint8).tobytes())
        else:
            self.logger.error("Video writer is not initialized.")

    def video_writer_is_done(self) -> None:
        """Closes the video writer and waits for it to finish."""
        if self.video_writer is not None:
            self.video_writer.stdin.close()
            self.video_writer.wait()
            self.video_writer = None  # Reset after closing
        else:
            self.logger.error("Video writer not initialized.")
