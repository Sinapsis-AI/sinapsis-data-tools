# -*- coding: utf-8 -*-

from sinapsis_core.data_containers.data_packet import AudioPacket

from sinapsis_data_readers.templates.audio_readers.base_audio_reader import (
    _AudioBaseReader,
)


class AudioReaderToBytes(_AudioBaseReader):
    """
    AudioReader for Reading Audio Files and Converting to Bytes.
    Usage example:

        agent:
          name: my_test_agent
        templates:
        - template_name: InputTemplate
          class_name: InputTemplate
          attributes: {}
        - template_name: AudioReaderToBytes
          class_name: AudioReaderToBytes
          template_input: InputTemplate
          attributes:
            audio_file_path: '/path/to/file.mp3'
            source: 'source/of/file'
            from_bytes: true
    """

    def read_file(self) -> AudioPacket | None:
        """
        Reads an audio file from the specified path and converts it into an `AudioPacket`.
        
        Returns:
            AudioPacket: An `AudioPacket` object containing the audio data.
            
        Raises:
            FileNotFoundError: If the specified audio file does not exist.
            IOError: If there is an error reading the audio file.
        """

        try:
            with open(self.attributes.audio_file_path, "rb") as audio_file:
                audio_content = audio_file.read()

            audio_file.close()
            audio_packet = AudioPacket(
                source=self.attributes.audio_file_path,
                content=audio_content,
            )
            return audio_packet
        except FileNotFoundError:
            self.logger.error(f"Audio file not found: {self.attributes.audio_file_path}")
            return None
        except IOError as e:
            self.logger.error(f"Error reading audio file: {e}")
            return None
