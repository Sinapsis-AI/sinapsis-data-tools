# -*- coding: utf-8 -*-
import re
from collections import Counter

from sinapsis_core.data_containers.data_packet import DataContainer, TextPacket
from sinapsis_core.template_base.base_models import OutputTypes, TemplateAttributes, UIPropertiesMetadata
from sinapsis_core.template_base.template import Template

STOPWORDS = {"and", "the", "or", "is", "in", "to", "of", "a"}


def is_logical(
    text: str, repeat_threshold: int = 10, unique_ratio_threshold: float = 0.1, window_size: int = 20
) -> bool:
    """Method to check whether a text string is logical, based on the number of repeated words in a
    certain window size and a certain threshold.
    Args:
            text (str): text to be evaluated
            repeat_threshold (int): The threshold for the number of repeated words
            unique_ratio_threshold (float): the ratio between the number of words and that of repeated words
            window_size (int): number of words in a single window size.
    """
    words = re.findall(r"\b\w+\b", text)
    word_count = len(words)
    unique_words = set(words)

    if word_count == 0 or len(unique_words) / word_count < unique_ratio_threshold:
        return False
    for i in range(word_count - window_size + 1):
        window = words[i : i + window_size]
        counts = Counter(window)
        for word, count in counts.items():
            if word not in STOPWORDS and count > repeat_threshold:
                return False
    return True


class TextContentFilter(Template):
    UIProperties = UIPropertiesMetadata(output_types=OutputTypes.TEXT)

    class AttributesBaseModel(TemplateAttributes):
        repeated_word_threshold: int = 10
        unique_words_ratio_threshold: float = 0.1
        window_size: int = 20

    def process_text_packet(self, packet: TextPacket) -> None:
        """Evaluate a certain packet content for its logical meaning"""
        is_text_logical = is_logical(
            packet.content,
            self.attributes.repeated_word_threshold,
            self.attributes.unique_words_ratio_threshold,
            self.attributes.window_size,
        )
        if not is_text_logical:
            packet.content = "invalid string, please try again"

    def execute(self, container: DataContainer) -> DataContainer:
        for text in container.texts:
            self.process_text_packet(text)
        return container
