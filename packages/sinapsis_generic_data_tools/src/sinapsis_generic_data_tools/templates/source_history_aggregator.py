# -*- coding: utf-8 -*-
from collections import deque
from typing import Any, Literal

from sinapsis_core.data_containers.data_packet import DataContainer
from sinapsis_core.template_base import Template
from sinapsis_core.template_base.base_models import (
    TemplateAttributes,
    TemplateAttributeType,
    UIPropertiesMetadata,
)

from sinapsis_generic_data_tools.helpers.tags import Tags


class SourceHistoryAggregator(Template):
    """Template to store story or content of packets in the generic_field as a deque.
            The number of inputs in the queue is set through the attributes in the template.

            Usage example:

            agent:
      name: my_test_agent
    templates:
    - template_name: InputTemplate
      class_name: InputTemplate
      attributes: {}
    - template_name: SourceHistoryAggregator
      class_name: SourceHistoryAggregator
      template_input: InputTemplate
      attributes:
            packet_to_extract_from: texts
            context_max_length: 5
    """

    UIProperties = UIPropertiesMetadata(
        tags=[Tags.AGGREGATOR, Tags.HISTORY, Tags.QUEUE],
    )

    class AttributesBaseModel(TemplateAttributes):
        packet_to_extract_from: Literal["audios", "images", "texts", "generic_data", "time_series", "binary_data"] = (
            "texts"
        )
        context_max_length: int = 5

    def __init__(self, attributes: TemplateAttributeType) -> None:
        super().__init__(attributes)

        self.history_tracker: dict[str | int, deque] = {}

    def fetch_source_history(self, source_id: str | int) -> deque | None:
        """This method returns the source history based on the id of the history.
        Args:
                source_id (str | int): Source identification for the history
        Returns:
                the deque corresponding to the source_id
        """
        return self.history_tracker.get(source_id, None)

    def append_source_history(self, source_id: str | int, content: Any) -> None:
        """Adds a new entry to the source_id history
        Args:
                source_id (str | int): Source identification for the history
                content (Any): Content of the packet to be added to the queue
        """
        if not self.history_tracker.get(source_id, False):
            self.history_tracker[source_id] = deque(maxlen=self.attributes.context_max_length)
        self.history_tracker[source_id].append(content)

    def reset_history(self, source_id: str | int) -> None:
        """Method to reset the history of a given source"""
        self.history_tracker[source_id] = deque(maxlen=self.attributes.context_max_length)

    def execute(self, container: DataContainer) -> DataContainer:
        packets = getattr(container, self.attributes.packet_to_extract_from)
        source = ""
        for packet in packets:
            source = packet.source
            content = packet.content
            self.append_source_history(source, content)

        full_history = self.fetch_source_history(source)
        self.logger.critical(f"This is the full context: {full_history}")
        if full_history:
            self._set_generic_data(container, full_history)
        return container
