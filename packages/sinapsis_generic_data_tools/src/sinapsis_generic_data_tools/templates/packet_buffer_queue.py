# -*- coding: utf-8 -*-
from collections import deque
from copy import deepcopy
from functools import wraps
from inspect import getdoc
from typing import Literal, Type

from pydantic.dataclasses import dataclass
from sinapsis_core.data_containers.data_packet import DataContainer, Packet
from sinapsis_core.template_base import Template
from sinapsis_core.template_base.base_models import (
    TemplateAttributes,
    TemplateAttributeType,
)


@dataclass
class PacketBuffer:
    """PacketBuffer dataclass. Contains the queues for
    both the tail and from buffers
    """

    front_q: deque
    tail_q: deque


class PacketBufferQueue(Template):
    """Template to perform buffering of a data packet
    Data is stored in a front buffer unless a trigger is set
    in which case, a PacketBuffer is generated, and data is stored in the
    tail buffer. Once the tail buffer is full, it is appended to the generic_data
    field in DataContainer

    Usage example:
    agent:
      name: my_test_agent
    templates:
    - template_name: InputTemplate
      class_name: InputTemplate
      attributes: {}
    - template_name: BufferTemplate
      class_name: BufferTemplate
      template_input: InputTemplate
      attributes:
        buffer_name: 'name_of_buffer'
        front_size: '10'
        tail_size: '10'
        packet_to_store: 'texts'

    """

    class AttributesBaseModel(TemplateAttributes):
        """Attributes of the template

        Args:
            buffer_name (str): name of the buffer
            front_size (int): size of the front queue
            tail_size(int): size of the tail queue
            packet_to_store(Literal["audios", "images", "texts",
                "time_series", "binary_data"]): type of packet to be buffered.
        """

        buffer_name: str
        front_size: int
        tail_size: int
        packet_to_store: Literal["audios", "images", "texts", "time_series", "binary_data"]

    def __init__(self, attributes: TemplateAttributeType) -> None:
        super().__init__(attributes)

        self.general_front_q: deque = deque(maxlen=self.attributes.front_size)
        self.buffer_queues: deque[PacketBuffer] = deque()

    def execute(self, container: DataContainer) -> DataContainer:
        if container.is_empty:
            return container

        packet_to_store: Packet = getattr(container, self.attributes.packet_to_store)

        if container.generic_data.get("trigger_buffer", False):
            self.logger.debug("Trigger has been set, initializing buffer...")
            initial_buffer = PacketBuffer(
                front_q=deepcopy(self.general_front_q),
                tail_q=deque(maxlen=self.attributes.tail_size),
            )
            self.buffer_queues.append(initial_buffer)
        else:
            self.general_front_q.append(packet_to_store)

        if len(self.buffer_queues[0].tail_q) == self.attributes.tail_size:
            self.logger.debug(f"{self.attributes.buffer_name} is full... adding to container")
            container.generic_data[self.attributes.buffer_name] = self.buffer_queues.popleft()

        for buffer_entry in self.buffer_queues:
            buffer_entry.tail_q.append(packet_to_store)

        return container


def multi_source_template(cls: Type[Template]) -> Type[Template]:
    """
    This decorator wraps the MultiSourceReader template, enabling to handle
    different sources, assigning an entry to each of them, such that the data
    from the same source are grouped together.

    Args:

        Parameters:
            cls (Type[Template]): The class to be wrapped. It is expected
            to have a constructor that takes a TemplateAttruteType as attributes and
            provides a `source` attribute.

        Returns:
            Type[Template]: A new class that extends Template,
            capable of creating video readers for multiple video file paths.
    """

    @wraps(cls, updated=())
    class MultiSourceReader(cls):
        """Wrapper for Templates that read from multiple sources"""

        def __init__(self, attributes: TemplateAttributeType) -> None:
            super().__init__(attributes)
            self.source_instances: dict = {}

    MultiSourceReader.__doc__ = f"{getdoc(cls)}, \n{getdoc(MultiSourceReader.AttributesBaseModel)}"
    return MultiSourceReader
