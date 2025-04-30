# -*- coding: utf-8 -*-


import cv2
from sinapsis_core.data_containers.data_packet import ImagePacket
from sinapsis_core.template_base.base_models import OutputTypes, UIPropertiesMetadata

from sinapsis_data_readers.templates.video_readers.base_video_reader import (
    BaseVideoReader,
    NotSet,
    NotSetType,
    multi_video_wrapper,
)


class VideoReaderCV2(BaseVideoReader):
    """
    This template provides functionality to read video files using the OpenCV library.
    It supports reading video frames in specified color spaces and manages video capture
    resources appropriately.

    Usage example:
        agent:
          name: my_test_agent
        templates:
        - template_name: InputTemplate
          class_name: InputTemplate
          attributes: {}
        - template_name: VideoReaderCV2
          class_name: VideoReaderCV2
          template_input: InputTemplate
          attributes:
            video_file_path: '/path/to/video/file'
            batch_size: 1
            video_source: 4d2a355f-cda4-4742-9042-8e6ee842d1cf
            device: cpu
            loop_forever: false

    """

    UIProperties = UIPropertiesMetadata(category="OpenCV", output_type=OutputTypes.VIDEO)

    def make_video_reader(self) -> tuple[cv2.VideoCapture, int] | NotSetType:
        """Attempts to open the video file specified in `self.attributes.video_file_path`
        and retrieves the total number of frames in the video.

        Returns:
            tuple:
                - If the video cannot be opened, returns (None, num_frames),
                  where num_frames is the total number of frames in the video.
                - If successful, returns (video_reader, num_frames),
                  where video_reader is the OpenCV VideoCapture object.
        """

        video_reader = cv2.VideoCapture(self.attributes.video_file_path)
        num_frames = int(video_reader.get(cv2.CAP_PROP_FRAME_COUNT))

        if not video_reader.isOpened():
            return NotSet
        return video_reader, num_frames

    def _read_video_frames(self) -> list[ImagePacket]:
        """Reads a batch of frames from the video.

        Continuously reads frames from the video until either the specified batch size
        is reached or there are no more frames to read. The frames are converted to the
        desired color space if specified in attributes.

        Returns:
            list[ImagePacket]: A list of ImagePacket objects representing the read frames.
        """
        video_frames: list[ImagePacket] = []
        frames_range = self.attributes.batch_size if self.attributes.batch_size != -1 else self.total_frames
        for idx in range(frames_range):
            ret_status, frame = self.video_reader.read()
            if not ret_status:
                break

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            video_frames.append(self._make_image_packet(frame, frame_index=self.frame_count + idx))
        return video_frames

    def close_video_reader(self) -> None:
        """Releases the video capture resource.

        Closes the video file and releases any resources associated with the video reader.
        This method should be called when video reading is complete to avoid memory leaks.
        """
        if self.video_reader:
            self.video_reader.release()


@multi_video_wrapper
class MultiVideoReaderCV2(VideoReaderCV2):
    """
    This template provides functionality to read multiple videos, each of them assigned to
    its own DataContainer and to its own reader process.
    Similar to its base class, it supports reading in different color spaces, and distributes
    the resources properly
    """
