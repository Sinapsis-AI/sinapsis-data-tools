# -*- coding: utf-8 -*-

import io
import os
from typing import cast

import numpy as np
from pydub import AudioSegment
from sinapsis_core.data_containers.data_packet import AudioPacket, DataContainer
from sinapsis_core.template_base.base_models import OutputTypes, UIPropertiesMetadata
from sinapsis_core.template_base.multi_execute_template import (
    execute_template_n_times_wrapper,
)

from sinapsis_data_readers.templates.audio_readers.base_audio_reader import (
    _AudioBaseReader,
)


class AudioReaderPydub(_AudioBaseReader):
    """Audio reader for reading audio data directly from bytes or files using Pydub.

    This class can read audio data from either a bytes object or a file path,
    using the Pydub library.
    When reading from bytes, it retains the data in byte format.
    When reading from a file, it converts the audio data to a NumPy array.

    Usage example:

        agent:
          name: my_test_agent
        templates:
        - template_name: InputTemplate
          class_name: InputTemplate
          attributes: {}
        - template_name: AudioReaderPydub
          class_name: AudioReaderPydub
          template_input: InputTemplate
          attributes:
            audio_file_path: '/path/to/file.mp3'
            source: 'source/of/file'
            sample_rate_khz: 16
            from_bytes: false
    """

    class AttributesBaseModel(_AudioBaseReader.AttributesBaseModel):
        """Attributes for the AudioReaderAudioSegment.

        Args:
            sample_rate_khz (int):
                Sample rate in khz for the processed audio. Defaults to 16hkz.
            from_bytes (bool):
                Flag to determine if the file is in bytes. Defaults to True


        """

        sample_rate_khz: int = 16
        from_bytes: bool = True

    UIProperties = UIPropertiesMetadata(category="Pydub", output_type=OutputTypes.AUDIO)

    def read_file(self) -> AudioPacket | None:
        """Reads audio data from a file path or bytes and returns an AudioPacket.

        If reading from bytes, it returns the audio data in bytes format.
        If reading from a file, it returns audio data as a NumPy array.

        Returns:
            Optional[AudioPacket]: An AudioPacket containing the audio data,
            sample rate, and metadata, or None if there was an error.
        """

        audio_data: bytes | np.ndarray
        if self.attributes.from_bytes:
            audio_bytes: bytes = cast(bytes, self.attributes.audio_file_path)
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes))

        else:
            audio_file_path: str = cast(str, self.attributes.audio_file_path)
            if os.path.exists(audio_file_path):
                audio_segment = AudioSegment.from_file(audio_file_path, format="wav")

            else:
                self.logger.error("Invalid audio file path: %s", audio_file_path)
                return None
        audio_segment = audio_segment.set_frame_rate(self.attributes.sample_rate_khz * 1000)
        audio_segment = audio_segment.set_channels(1)

        audio_data = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)
        audio_data = audio_data / (2**15)

        audio_packet = AudioPacket(
            source=self.attributes.source,
            content=audio_data,
            sample_rate=audio_segment.frame_rate,
        )
        return audio_packet


@execute_template_n_times_wrapper
class ExecuteNTimesAudioReaderPydub(AudioReaderPydub):
    """
    This template provides functionality to read multiple audios, each of them assigned to
    its own DataContainer and to its own reader process.
    Similar to its base class, it reads the audios using the Pydub library
    """


class LazyAudioReaderPydub(AudioReaderPydub):
    """Reads an audio file using Pydub, obtaining the file path
    from the generic_field of the DataContainer and setting is as the file_path in the attributes.

    Usage example:

        agent:
          name: my_test_agent
        templates:
        - template_name: InputTemplate
          class_name: InputTemplate
          attributes: {}
        - template_name: LazyAudioReaderPydub
          class_name: LazyAudioReaderPydub
          template_input: InputTemplate
          attributes:
            sample_rate_khz: 16
            from_bytes: False
    """

    def get_file_path_from_generic_data(self, container: DataContainer) -> None:
        """Method to retrieve the file path from the genetic data field of DataContainer.
        The method extracts the file path from the generic field and sets as attribute

        Args:
            container (DataContainer): The DataContainer to extract the file path from
        """
        file_path = container.generic_data.get("audio_path", "")
        self.attributes.audio_file_path = file_path

    def execute(self, container: DataContainer) -> DataContainer:
        self.get_file_path_from_generic_data(container)
        if self.attributes.audio_file_path:
            return super().execute(container)

        return container


@execute_template_n_times_wrapper
class ExecuteNTimesLazyAudioReaderPydub(LazyAudioReaderPydub):
    """
    This template provides functionality to read multiple audios, each of them assigned to
    its own DataContainer and to its own reader process.
    Similar to its base class, it reads the file path from the generic field of the DataContainer
    """
