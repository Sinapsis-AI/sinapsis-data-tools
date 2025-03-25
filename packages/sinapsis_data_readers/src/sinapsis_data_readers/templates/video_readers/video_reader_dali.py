# -*- coding: utf-8 -*-


from typing import Literal, cast

import nvidia.dali.fn as fn
from nvidia.dali import pipeline_def
from nvidia.dali.pipeline import DataNode, Pipeline
from nvidia.dali.plugin.pytorch import DALIGenericIterator
from sinapsis_core.data_containers.data_packet import ImagePacket
from sinapsis_core.utils.logging_utils import sinapsis_logger

from sinapsis_data_readers.templates.video_readers.base_video_reader import (
    BaseVideoReader,
    BaseVideoReaderAttributes,
    NotSet,
    NotSetType,
    multi_video_wrapper,
)


@pipeline_def
def video_pipe(filenames: list[str], device: str, random_shuffle: bool) -> DataNode:
    """Pipeline for reading video files using NVIDIA DALI.

    This pipeline reads video files from the specified list of filenames
    and returns a DataNode containing the video data.

    Args:
        filenames (list[str]): A list of file paths to the video files that
        will be read by the pipeline.
        device (str): which device to use for data reading (e.g., cpu or gpu)
        random_shuffle (bool): flag to shuffle the data frames to be read.

    Returns:
        DataNode: A DataNode containing the video frames. The output is
        suitable for further processing in a DALI pipeline.
    """
    try:
        video = fn.readers.video(
            device=device,
            filenames=filenames,
            sequence_length=1,
            random_shuffle=random_shuffle,
            initial_fill=1024 * 5,
            prefetch_queue_depth=500,
            read_ahead=True,
        )
        video = cast(DataNode, video)
    except RuntimeError as e:
        sinapsis_logger.error(f"Error opening the video using NVIDIA Dali. {e}")
        raise
    return video


class VideoReaderDali(BaseVideoReader):
    """Video input reader using NVIDIA DALI.

    This class extends the BaseVideoReader to implement video reading functionality
    using NVIDIA DALI, allowing for efficient loading and processing of video frames.

    Note:
        The fn.readers.video only supports GPU


    Usage example:
        agent:
          name: my_test_agent
        templates:
        - template_name: InputTemplate
          class_name: InputTemplate
          attributes: {}
        - template_name: VideoReaderDali
          class_name: VideoReaderDali
          template_input: InputTemplate
          attributes:
            video_file_path: '/path/to/video/file'
            batch_size: 1
            video_source: 4d2a355f-cda4-4742-9042-8e6ee842d1cf
            device: gpu
            loop_forever: false
    """

    class AttributesBaseModel(BaseVideoReaderAttributes):
        """Attributes for the VideoReaderDali
        device (Literal["gpu"]): Device to read the video. Dali only supports GPU
        num_threads (int): number of GPU threads used by the pipeline
        random_shuffle (bool): Determines whether to randomly shuffle data
        """

        device: Literal["gpu"] = "gpu"
        num_threads: int = 64
        random_shuffle: bool = False

    def make_video_reader(self) -> tuple[DALIGenericIterator | Pipeline, int] | NotSetType:
        """Creates a dali pipeline for reading video files.

        This method initializes the video reading pipeline using the provided
        attributes. If a RuntimeError is raised, it handles the error and returns None

        Returns:
            tuple[Pipeline | None, int]: A tuple containing the nvidia.dali pipeline
            and the number of frames per epoch. If the pipeline cannot be created,
            it returns None and 0.
        """

        try:
            pipe: Pipeline = video_pipe(
                batch_size=self.attributes.batch_size,
                num_threads=self.attributes.num_threads,
                device_id=0,
                filenames=self.attributes.video_file_path,
                seed=12345,
                device=self.attributes.device,
                random_shuffle=self.attributes.random_shuffle,
            )
            pipe.build()
        except RuntimeError as e:
            self.logger.warning(f"Was unable to decode video file: {e}")
            return NotSet

        return pipe, next(iter(pipe.epoch_size().values()))

    def close_video_reader(self) -> None:
        """Method to delete the Pipeline from memory"""
        if self.video_reader:
            del self.video_reader

    def _read_video_frames(self) -> list[ImagePacket]:
        """Reads video frames from the dali pipeline.

        This method runs the video reader pipeline and adds the frames to a list
        of ImagePacket objects.

        Returns:
            list[ImagePacket]: A list of ImagePacket objects representing the video frames.
        """
        video_frames: list[ImagePacket] = []
        sequences_out = self.video_reader.run()

        for idx, frame in enumerate(sequences_out[0]):
            video_frames.append(self._make_image_packet(frame, frame_index=self.frame_count + idx))
        return video_frames


@multi_video_wrapper
class MultiVideoReaderDali(VideoReaderDali):
    """
    This template provides functionality to read multiple videos, each of them assigned to
    its own DataContainer and to its own reader process.
    Similar to its base class, it supports reading in different color spaces, and distributes
    the resources properly
    """


class VideoReaderDaliPytorch(VideoReaderDali):
    """Video input reader for PyTorch using NVIDIA dali.

    This class extends VideoReaderDali to implement video reading functionality
    specifically tailored for PyTorch, utilizing the dali library for efficient
    video frame loading and processing.

    Usage example
        agent:
          name: my_test_agent
        templates:
        - template_name: InputTemplate
          class_name: InputTemplate
          attributes: {}
        - template_name: VideoReaderDali
          class_name: VideoReaderDali
          template_input: InputTemplate
          attributes:
            video_file_path: '`replace_me:str | list[str]`'
            batch_size: 1
            video_source: 33147f07-26a9-4495-b7e1-3246afe32779
            device: 'gpu'
            loop_forever: false
            num_threads: 64
            random_shuffle: false

    """

    def make_video_reader(self) -> tuple[DALIGenericIterator | Pipeline, int] | NotSetType:
        """Creates a generic  dali iterator for reading video files.

        This method calls the parent class's make_video_reader method to initialize
        the dali pipeline and returns a DALIGenericIterator to iterate over the
        video frames.

        Returns:
            tuple[DALIGenericIterator | Pipeline | int] | NotSet: A tuple containing the dali
            generic iterator and the total number of frames. If the pipeline cannot
            be created, it returns NotSet.
        """
        pipelines, num_frames = super().make_video_reader()

        if pipelines is None:
            return NotSet
        pipelines = cast(Pipeline, pipelines)
        return DALIGenericIterator([pipelines], ["data"], auto_reset=False), num_frames

    def _read_video_frames(self) -> list[ImagePacket]:
        """Reads video frames from the dali pipeline iterator.

        This method retrieves the next batch of video frames from the dali iterator
        and creates ImagePackets from the video frames

        Returns:
            list[ImagePacket]: A list of ImagePacket with the frame as content.
        """
        video_frames: list[ImagePacket] = []
        sequences_out = next(self.video_reader)
        end_index = min(self.total_frames - self.frame_count + 1, self.attributes.batch_size)
        for idx, frame in enumerate(sequences_out[0]["data"][0:end_index]):
            video_frames.append(self._make_image_packet(frame, frame_index=self.frame_count + idx))
        return video_frames


@multi_video_wrapper
class MultiVideoReaderPytorch(VideoReaderDaliPytorch):
    """
    This template provides functionality to read multiple videos, each of them assigned to
    its own DataContainer and to its own reader process.
    Similar to its base class, it supports reading in different color spaces, and distributes
    the resources properly
    """
