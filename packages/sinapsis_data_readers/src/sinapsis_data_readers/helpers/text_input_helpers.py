# -*- coding: utf-8 -*-
"""Module for processing text input from TextPacket objects."""

from sinapsis_core.data_containers.data_packet import TextPacket


def load_input_text(input_data: list[TextPacket]) -> str:
    """Loads and concatenates the text content of all TextPacket objects into a single string.

    Args:
        input_data (list[TextPacket]): A list of TextPacket objects containing text content.

    Returns:
        str: A single string containing the concatenated text from all TextPacket objects.
    """
    return "".join(t.content for t in input_data)
