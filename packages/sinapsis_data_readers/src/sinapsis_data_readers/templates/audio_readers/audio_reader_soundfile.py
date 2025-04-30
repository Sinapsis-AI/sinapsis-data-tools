# -*- coding: utf-8 -*-

import os
from typing import cast

import soundfile as sf
from sinapsis_core.data_containers.data_packet import AudioPacket, DataContainer
from sinapsis_core.template_base.base_models import OutputTypes, UIPropertiesMetadata
from sinapsis_core.template_base.multi_execute_template import (
    execute_template_n_times_wrapper,
)

from sinapsis_data_readers.templates.audio_readers.base_audio_reader import (
    _AudioBaseReader,
)


class AudioReaderSoundfile(_AudioBaseReader):
    """Reads audio data from a file path using Soundfile.

    This class utilizes the Soundfile library to read audio data from a specified file path.
    It returns the audio data wrapped in an AudioPacket, which includes additional metadata
    such as sample rate and source information.


    Usage example:

        agent:
          name: my_test_agent
        templates:
        - template_name: InputTemplate
          class_name: InputTemplate
          attributes: {}
        - template_name: AudioReaderSoundfile
          class_name: AudioReaderSoundfile
          template_input: InputTemplate
          attributes:
            audio_file_path: '/path/to/file.mp3'
            source: 'source/of/file'
            sample_rate_khz: 16
            from_bytes: true

    """

    AttributesBaseModel = _AudioBaseReader.AttributesBaseModel
    UIProperties = UIPropertiesMetadata(category="Soundfile", output_type=OutputTypes.AUDIO)

    def read_file(self) -> AudioPacket | None:
        """Reads audio data from a file path and returns an AudioPacket.

        This method checks if the specified audio file exists and attempts to read
        the audio data using the Soundfile library. If successful, it wraps the audio
        data in an AudioPacket and returns it. If the file does not exist or if there
        is an error during reading, it logs the error and returns None.

        Returns:
            AudioPacket|None: An AudioPacket containing the audio data and
            sample rate, or None if the file could not be read or was invalid.
        """
        audio_path = cast(str, self.attributes.audio_file_path)
        if os.path.exists(audio_path):
            try:
                audio_content, sample_rate = sf.read(audio_path)
                audio_packet = AudioPacket(
                    source=self.attributes.source,
                    content=audio_content,
                    sample_rate=sample_rate,
                )
                return audio_packet
            except (ValueError, TypeError) as e:
                self.logger.error("Error reading audio file: %s", e)
                return None
        else:
            self.logger.error("Invalid audio file path: %s", audio_path)
            return None


@execute_template_n_times_wrapper
class ExecuteNTimesAudioReaderSoundfile(AudioReaderSoundfile):
    """
    This template provides functionality to read multiple audios, each of them assigned to
    its own DataContainer and to its own reader process.
        Similar to its base class, it reads the audio using the Soundfile library
    """


class LazyAudioReaderSoundfile(AudioReaderSoundfile):
    """Reads audio data from a file path using Soundfile.

    This class uses the Soundfile library to read audio data from a specified file path.
    It returns the audio data wrapped in an AudioPacket, which includes additional metadata
    such as sample rate and source information.

    Usage example:

        agent:
          name: my_test_agent
        templates:
        - template_name: InputTemplate
          class_name: InputTemplate
          attributes: {}
        - template_name: LazyAudioReaderSoundfile
          class_name: LazyAudioReaderSoundfile
          template_input: InputTemplate
          attributes:
            sample_rate_khz: 16
            from_bytes: true
    """

    def get_file_path_from_generic_data(self, container: DataContainer) -> None:
        """Method to retrieve the file path from the genetic data field of DataContainer.
        The method extracts the file path from the generic field and sets as attribute

        Args:
            container (DataContainer): The DataContainer to extract the file path from
        """
        file_path = container.generic_data["audio_path"]
        self.attributes.audio_file_path = file_path

    def execute(self, container: DataContainer) -> DataContainer:
        self.get_file_path_from_generic_data(container)
        return super().execute(container)


@execute_template_n_times_wrapper
class ExecuteNTimesLazyAudioReaderSoundfile(LazyAudioReaderSoundfile):
    """
    This template provides functionality to read multiple audios, each of them assigned to
    its own DataContainer and to its own reader process.
    Similar to its base class, it reads the audio using the Soundfile library
    """
