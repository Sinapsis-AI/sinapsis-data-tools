# -*- coding: utf-8 -*-

import subprocess

import ffmpeg
import numpy as np
from sinapsis_core.data_containers.data_packet import ImagePacket
from sinapsis_core.template_base.base_models import OutputTypes, TemplateAttributeType, UIPropertiesMetadata

from sinapsis_data_readers.templates.video_readers.base_video_reader import (
    BaseVideoReader,
    NotSetType,
    multi_video_wrapper,
)


class VideoReaderFFMPEG(BaseVideoReader):
    """This template provides functionality to read video files using the FFMPEG library.
    The video frames are read asynchronously, and the resources are cleaned after all
    the frames have been processed

    Usage example:
        agent:
          name: my_test_agent
        templates:
        - template_name: InputTemplate
          class_name: InputTemplate
          attributes: {}
        - template_name: VideoReaderFFMPEG
          class_name: VideoReaderFFMPEG
          template_input: InputTemplate
          attributes:
            video_file_path: '/path/to/video/file'
            batch_size: 1
            video_source: 4d2a355f-cda4-4742-9042-8e6ee842d1cf
            device: cpu
            loop_forever: false
    """

    UIProperties = UIPropertiesMetadata(category="FFMPEG", output_type=OutputTypes.VIDEO)

    def __init__(self, attributes: TemplateAttributeType) -> None:
        super().__init__(attributes)
        self.height, self.width, _ = self.get_count_height_width()

    def get_count_height_width(self) -> tuple[int, int, int]:
        """Method to extract the size of the frames and the number of frames
        The method checks for the metadata in each of the fames and calculates the
        width, height and the number of frames

        Returns:
            tuple[int, int, int]: the values for height, width and frames as integers
        """
        try:
            probe = ffmpeg.probe(self.attributes.video_file_path)
        except ffmpeg.Error as e:
            self.logger.warning("ffmpeg error: %s", str(e))
            return (0, 0, 0)
        video_stream = next(
            (stream for stream in probe["streams"] if stream["codec_type"] == "video"),
            None,
        )
        if video_stream is not None:
            width = int(video_stream["width"])
            height = int(video_stream["height"])
            total_frames = int(video_stream["nb_frames"])
            return height, width, total_frames
        return 0, 0, 0

    def make_video_reader(self) -> tuple[subprocess.Popen, int] | NotSetType:
        """This method asynchronously runs a subprocess to stream the video frames"""
        video_reader = (
            ffmpeg.input(self.attributes.video_file_path)
            .output(
                "pipe:",
                format="rawvideo",
                pix_fmt="rgb24",
            )
            .run_async(pipe_stdout=True)
        )
        _, _, total_frames = self.get_count_height_width()
        return video_reader, total_frames

    def close_video_reader(self) -> None:
        """Clean up resources and terminate the video reading process.

        This method ensures that any resources associated with the video reader are
        properly released. It waits for the underlying subprocess to finish executing
        before returning, ensuring that no processes are left hanging.

        """
        if self.video_reader:
            self.video_reader.wait()

    def _read_video_frames(self) -> list[ImagePacket]:
        """Read a batch of video frames from the video reader.

        This method reads raw video data from the video reader's standard output,
        processes it into individual frames, and stores them as ImagePacket objects.

        Returns:
            list[ImagePacket]: A list of ImagePacket objects representing the video
            frames read from the video stream.

        Raises:
            RuntimeError: If the video data cannot be read or processed correctly.
        """

        video_frames: list[ImagePacket] = []
        frames_range = self.attributes.batch_size if self.attributes.batch_size != -1 else self.total_frames
        video_bytes = self.video_reader.stdout.read(frames_range * self.width * self.height * 3)
        for idx, frame in enumerate(np.frombuffer(video_bytes, np.uint8).reshape([-1, self.height, self.width, 3])):
            video_frames.append(self._make_image_packet(frame, frame_index=self.frame_count + idx))
        return video_frames


@multi_video_wrapper
class MultiVideoReaderFFMPEG(VideoReaderFFMPEG):
    """Template to read multiple videos using the FFMPEG library,
    This template expands the functionality of VideoReaderFFMPEG
    where video_file_path is a list of paths instead of a single string.
    For each of the video_file_path it creates a new instance of the video
    reader and appends each frame to the ImagePacket list in DataContainer
    """
