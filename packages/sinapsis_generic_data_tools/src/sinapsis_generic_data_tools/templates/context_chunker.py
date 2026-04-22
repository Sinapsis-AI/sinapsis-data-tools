# -*- coding: utf-8 -*-
from typing import Any

from sinapsis_core.data_containers.data_packet import DataContainer, TextPacket
from sinapsis_core.template_base.template import Template, TemplateAttributes


class ContextChunker(Template):
    """Template to chunk a list of sentences keeping a context window
    Attributes:
        window_size (int): Total sentences per chunk
        overlap (int): Sentences to carry over to the next chunk
        override_text (bool): Whether to override the text packets in the container
    """

    class AttributesBaseModel(TemplateAttributes):
        window_size: int = 5
        overlap: int = 2
        override_text: bool = False

    attributes: AttributesBaseModel

    @staticmethod
    def get_conversation_chunks(transcript: list[str], window_size: int, overlap: int) -> list[dict[str, Any]]:
        """
        Splits a list of strings into overlapping chunks.
        Args:

            transcript: List of sentences  to be chunked
            window_size: Total sentences per chunk
            overlap: Sentences to carry over to the next chunk
        """
        stride = window_size - overlap
        chunks = []
        for i in range(0, len(transcript), stride):
            # Slice the list from current index to index + 5
            window = transcript[i : i + window_size]

            if window:
                chunks.append(
                    {
                        "chunk_id": len(chunks),
                        "text": "\n".join(window),
                    }
                )

        return chunks

    def execute(self, container: DataContainer) -> DataContainer:
        sentence_list = [text.content for text in container.texts]

        chunks = self.get_conversation_chunks(sentence_list, self.attributes.window_size, self.attributes.overlap)
        new_texts = [TextPacket(content=chunk.get("text"), source=str(chunk.get("chunk_id"))) for chunk in chunks]
        if self.attributes.override_text:
            container.texts = new_texts
        else:
            container.texts.extend(new_texts)
        return container
