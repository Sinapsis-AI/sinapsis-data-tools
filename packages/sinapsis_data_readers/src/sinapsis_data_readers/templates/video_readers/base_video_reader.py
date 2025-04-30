# -*- coding: utf-8 -*-


import abc
from functools import wraps
from inspect import getdoc
from pathlib import Path
from typing import Any, Literal, Type, TypeAlias, TypeVar

from numpy import ndarray
from sinapsis_core.data_containers.data_packet import (
    DataContainer,
    ImageColor,
    ImagePacket,
    get_uuid,
)
from sinapsis_core.template_base import Template
from sinapsis_core.template_base.base_models import (
    OutputTypes,
    TemplateAttributes,
    TemplateAttributeType,
    UIPropertiesMetadata,
)

from sinapsis_data_readers.helpers.file_path_helpers import parse_file_paths

NotSet = (None, 0)
NotSetType: TypeAlias = tuple[None, Literal[0]]


class BaseVideoReaderAttributes(TemplateAttributes):
    """Attributes for base class of Video Readers.

    Attributes:
        video_file_path (str | list[str]): Path or list of paths to the video(s).
        batch_size (int): Number of frames in the batch. Default is 1.
        video_source (int | str | None): Source of the video. Default is a UUID string.
        device (Literal["cpu", "gpu"]): Device to be used for loading the video. Default is "cpu".
        loop_forever (bool): Whether to loop the video indefinitely. Default is False.
    """

    video_file_path: str | list[str]
    batch_size: int = 1
    video_source: int | str | None = str(get_uuid())
    device: Literal["cpu", "gpu"] = "cpu"
    loop_forever: bool = False


class BaseVideoReader(Template):
    """Base template for Video Reader templates.
    This template already implements process_frames and make_image_packets
    methods to add the frames as ImagePacket to the DataContainer
    """

    AttributesBaseModel = BaseVideoReaderAttributes
    UIProperties = UIPropertiesMetadata(output_type=OutputTypes.VIDEO)

    def __init__(self, attributes: TemplateAttributeType) -> None:
        super().__init__(attributes)
        self.frame_count = 0
        self.video_reader: Any
        self.total_frames: int
        self.video_reader, self.total_frames = self.make_video_reader()
        self.has_reset: bool = False
        if self.video_reader is None:
            self.logger.warning("Unable to open video")

    @abc.abstractmethod
    def make_video_reader(self) -> tuple[Any, int]:
        """Method to instantiate the reader depending on the library used
        Returns:
            tuple[Any, int]: The reader object and the number of frames
            If the video can't be processed or open, the method will return NotSet type
        """

    def reset_state(self, template_name: str | None = None) -> None:
        """
        Reinitialize the video reader, by first closing any hanging processes.
        Sets the flag has_reset to True
        """
        _ = template_name
        self.close_video_reader()
        self.video_reader = None
        super().reset_state()
        self.has_reset = True

    def loop_forever(self, container: DataContainer) -> None:
        """Iterates over the video frames over and over while there is still data
        to process. This flag is set through the attributes
        """
        self.logger.debug("All frames processed. Restaring video reader...")
        self.reset_state()
        if self.has_frames():
            self.process_frames(container)
        else:
            self.logger.debug("template has no more data to load.")
            self.close_video_reader()

    @abc.abstractmethod
    def _read_video_frames(self) -> list[ImagePacket]:
        """Abstract method to read the frames of the video and assign to ImagePacket

        Returns:
            list[ImagePacket]: List of frames, each of them packed in an ImagePacket

        """

    def close_video_reader(self) -> None:
        """If necessary, close the video reader object to avoid resource wasting"""

    def num_elements(self) -> int:
        """Number of remaining frames to be read.
        If method has_frames returns False, there are no remaining frames

        Returns:
            int: the number of remaining frames.
        """
        return 0 if not self.has_frames() else self.total_frames - self.frame_count

    def has_frames(self) -> bool:
        """Determines if the reader still has frames to process

        Returns:
            bool: True if there are frames, False otherwise
        """
        video_still_has_frames_to_process: bool = self.frame_count < self.total_frames
        return video_still_has_frames_to_process

    def _make_image_packet(self, frame: ndarray, frame_index: int) -> ImagePacket:
        """Creates an ImagePacket with the frame and frame index.

        Args:
            frame (np.ndarray): processed frame to be assigned to the ImagePacket
            frame_index (int): Index of the video frame that serves as the id of the frame

        Returns:
            (ImagePacket): ImagePacket associated with the frame
        """
        return ImagePacket(
            content=frame,
            source=self.attributes.video_source,
            color_space=ImageColor.RGB,
            id=f"{self.attributes.video_source}_{frame_index}",
        )

    def process_frames(self, container: DataContainer) -> None:
        """Reads frames and adds them to DataContainer as ImagePackets
        Args:
            container (DataContainer): container to be updated
        """
        video_frames = self._read_video_frames()
        container.images += video_frames
        self.frame_count += len(video_frames)

    def execute(self, container: DataContainer) -> DataContainer:
        if self.has_frames():
            self.process_frames(container)
        elif self.attributes.loop_forever:
            self.loop_forever(container)
        else:
            self.logger.debug("template has no more data to load.")
            self.close_video_reader()

        return container


class MultiVideoReaderBase(Template):
    """Template to read multiple videos
    setting different instances of single BaseVideoReaders
    """

    class AttributesBaseModel(BaseVideoReaderAttributes):
        """Attributes for the MultiVideoReaderBase
        video_file_path (list[str] | str): path or list of paths to the video(s)
        interleaved (bool): Whether to load the videos interleaving them
        parallel_exec (bool): Whether to load the frames of the videos

        """

        interleaved: bool = False
        parallel_exec: bool = False

    def __init__(self, attributes: TemplateAttributeType) -> None:
        super().__init__(attributes)
        self.data_collection: list[BaseVideoReader] = self._make_video_readers(attributes)
        self.current_reader: BaseVideoReader | None = None
        self._num_active_readers: int = len(self.data_collection)

    def num_elements(self) -> int:
        """Returns the number of active readers from the data collection"""
        return self._num_active_readers

    @abc.abstractmethod
    def _make_video_readers(self, attributes: TemplateAttributeType) -> list[BaseVideoReader]:
        pass

    def update_video_reader(self) -> bool:
        """
        Verifies the status of the current reader. If the reader is still open, closes it and
        subtracts to the total number of active readers.
        If there are still active readers in the data collection, remove it.
        """
        if self.current_reader is not None:
            self.current_reader.close_video_reader()
            self._num_active_readers -= 1
        if len(self.data_collection) > 0:
            self.current_reader = self.data_collection.pop()
            return True
        return False

    def execute_interleaved(self, container: DataContainer) -> DataContainer:
        template_has_finished = []
        for reader in self.data_collection:
            if reader.has_frames():
                reader.process_frames(container)
            template_has_finished.append(not reader.has_frames())

        if all(template_has_finished):
            self._num_active_readers = 0

        return container

    def execute(self, container: DataContainer) -> DataContainer:
        if self.attributes.interleaved:
            return self.execute_interleaved(container)

        if (self.current_reader and self.current_reader.has_frames()) or (
            self.current_reader and self.current_reader.has_reset and self.update_video_reader()
        ):
            self.current_reader.process_frames(container)

        else:
            self.logger.debug(f"{self.class_name} has no more data to load.")
            if self.current_reader:
                self.current_reader.close_video_reader()
            self._num_active_readers = 0
        return container


MultiVideoWrapperType = TypeVar("MultiVideoWrapperType", bound="MultiVideoReaderBase")


def multi_video_wrapper(cls: Type[MultiVideoWrapperType]) -> Type[MultiVideoReaderBase]:
    """
    This decorator wraps a class in a MultiVideoWrapper, enabling it to handle
    multiple video files by creating instances of the provided class for each
    valid video file path.

        Parameters:
            cls (Type[MultiVideoWrapperType]): The class to be wrapped. It is expected
            to have a constructor that takes a TemplateAttributeType as attributes and
            provides a `video_reader` attribute.

        Returns:
            Type[MultiVideoReaderBase]: A new class that extends MultiVideoReaderBase,
            capable of creating video readers for multiple video file paths.
    """

    @wraps(cls, updated=())
    class MultiVideoWrapper(MultiVideoReaderBase):
        """
        Wrapper for MultiVideoReader template.
        """

        def _make_video_readers(self, attributes: TemplateAttributeType) -> list[BaseVideoReader]:
            """Creates video readers for each valid video file path.

            This method parses the video file paths, verifies their existence,
            and initializes a video reader for each valid path.

            Parameters:
                attributes (TemplateAttributeType): A dictionary of attributes that contains
                the 'video_file_path' key. This dictionary is modified to include
                the current video path during processing.

            Returns:
                List[BaseVideoReader]: A list of initialized BaseVideoReader instances
                corresponding to the valid video file paths. If a path is invalid or
                results in a None video reader, it is skipped and a logging warning message
                is displayed.
            """
            video_readers = []
            for vid_path in parse_file_paths(self.attributes.video_file_path):
                if not Path(vid_path).is_file():
                    self.logger.warning(f"{vid_path} is not a valid file path, will skip")
                    continue

                attributes["video_file_path"] = vid_path
                template_cls = cls(attributes)
                if template_cls.video_reader is None:
                    self.logger.warning(f"skipping video reader for {vid_path}, please verify path")
                    continue
                video_readers.append(template_cls)

            return video_readers

    MultiVideoWrapper.__doc__ = f"{getdoc(cls)}, \n{getdoc(MultiVideoWrapper.AttributesBaseModel)}"
    return MultiVideoWrapper
