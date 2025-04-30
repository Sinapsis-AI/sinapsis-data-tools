# -*- coding: utf-8 -*-
import os
from typing import Literal

import numpy as np
import soundfile
from sinapsis_core.data_containers.data_packet import AudioPacket, DataContainer
from sinapsis_core.template_base import Template
from sinapsis_core.template_base.base_models import OutputTypes, TemplateAttributes, UIPropertiesMetadata
from sinapsis_core.utils.env_var_keys import SINAPSIS_CACHE_DIR


class AudioWriterSoundfile(Template):
    """
    Template for saving audio packets to local environment
     using the SoundFile library. The template includes methods
     to extract the content of the Audio packet, and saving the audio
     with a given extension using Soundfile

     Usage example:

     agent:
      name: my_test_agent
    templates:
    - template_name: InputTemplate
      class_name: InputTemplate
      attributes: {}
    - template_name: AudioWriterSoundfile
      class_name: AudioWriterSoundfile
      template_input: InputTemplate
      attributes:
        save_dir: '/path/to/desired/destination'
        root_dir: $SINAPSIS_CACHE_DIR
        extension: wav


    """

    UIProperties = UIPropertiesMetadata(category="Sounfile", output_type=OutputTypes.AUDIO)

    class AttributesBaseModel(TemplateAttributes):
        """
        Attributes for configuring the audio saving process.

        - save_dir (str): Directory where audio files will be saved.
        - root_dir (str): Root directory for saving audio files.
        Defaults to SINAPSIS_CACHE_DIR.
        - extension (Literal["wav", "flac", "aif", "raw"]):
            File format for saving audio files.
        """

        save_dir: str
        root_dir: str = SINAPSIS_CACHE_DIR
        extension: Literal["wav", "flac", "aif", "raw"] = "wav"

    @staticmethod
    def _process_audio_packet(audio_packet: AudioPacket) -> np.ndarray:
        """
        Flattens the audio content from an AudioPacket for saving.

        Args:
            audio_packet (AudioPacket): The audio packet to process.

        Returns:
            np.ndarray: Flattened audio data.
        """
        return audio_packet.content.flatten()

    def _get_destination_dir(self) -> str:
        """
        Constructs the destination directory path and ensures it exists.

        Returns:
            str: Path to the destination directory.
        """
        destination_dir = os.path.join(self.attributes.root_dir, self.attributes.save_dir)
        os.makedirs(destination_dir, exist_ok=True)
        return destination_dir

    def _get_full_path(self, audio_packet: AudioPacket, destination_dir: str) -> str:
        """
        Generates the full file path for an audio file based on its metadata.

        Args:
            audio_packet (AudioPacket): The audio packet to save.
            destination_dir (str): Directory where the file will be saved.

        Returns:
            str: Full path to the destination file.
        """
        filename = f"{audio_packet.source}-{audio_packet.id.split('-')[0]}"
        destination_path = os.path.join(destination_dir, f"{filename}.{self.attributes.extension}")
        return destination_path

    def _save_audio(self, audio_packet: AudioPacket, destination_path: str) -> None:
        """
        Saves audio data to a file using the SoundFile library.

        Args:
            audio_packet (AudioPacket): The audio packet containing the data to save.
            destination_path (str): Full path to the destination file.
        """
        soundfile.write(
            destination_path,
            self._process_audio_packet(audio_packet),
            audio_packet.sample_rate,
            format=self.attributes.extension,
        )

    def execute(self, container: DataContainer) -> DataContainer:
        """
        Processes and saves all audio packets from a DataContainer.

        Args:
            container (DataContainer): Container holding the audio packets.

        Returns:
            DataContainer: The same container, unmodified, for chaining.
        """
        destination_dir = self._get_destination_dir()
        for audio_packet in container.audios:
            full_path = self._get_full_path(audio_packet, destination_dir)
            self._save_audio(audio_packet, full_path)
        return container
