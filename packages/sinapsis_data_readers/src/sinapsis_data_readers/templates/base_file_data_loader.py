# -*- coding: utf-8 -*-
import abc
from typing import Generator

from sinapsis_core.data_containers.data_packet import DataContainer, Packet
from sinapsis_core.template_base import Template
from sinapsis_core.template_base.base_models import (
    TemplateAttributes,
    TemplateAttributeType,
)


def base_documentation() -> str:
    return """ The template implements __iter__ and __next__ methods so that it can be used
    as an iterator if desired. See examples below. Otherwise, it behaves as a normal
    template.  These two methods always return the data in batches, even if batch_size == 1.
    """


def example_documentation() -> str:
    return """ usage in a for loop:

            for data_batch in my_data_loader:
                for single_data_packet in data_batch:
                    my_data = single_data_packet.source

        usage in a while loop with next:

            while my_data_loader.has_elements():
                for data_batch in next(my_data_loader):
                    for single_data_packet in data_batch:
                        my_data = single_data_packet.source

        if you just want the next item in line:
            data_batch = list(next(my_data_loader))"""


def base_attributes_documentation() -> str:
    return """
        data_dir (str):
                root path to the data
        pattern (str) = "**/*":
                regex to be used with Path.glob. By default, we find recursively.
        batch_size (int) = 1:
                if batch size is set to a number >= len(self.data_collection), or batch_size ==-1, the entire
                set of data will be returned at once.

        shuffle_data (bool) = False:
                flag to indicate whether to shuffle the list of datafiles.
        samples_to_load (int) = -1:
                by default, load all the data unless samples_to_load is set to >= 0. If 0, the
                list of data files will be empty and no data will be loaded.
        load_on_init: bool = False
                flag to indicate if data should be loaded in the __init__ or during execution. Note
                that for large data sets with large files, it is recommended to set this flag to
                false in order to avoid long initialization times of the template.

    """


class ContentNotSetException(Exception):
    pass


class _BaseDataReader(Template, abc.ABC):
    __doc__ = f"""
    This template serves as a base class for file data loaders. It relies on 'PACKET_ATT_NAME'
    to read and append data Packets to a DataContainer.

    {base_documentation()}

    Example:

        my_data_loader = MySubClassDataLoader({{'data_dir': 'some/path', 'batch_size': 2}})

         {example_documentation()}
    """

    class AttributesBaseModel(TemplateAttributes):
        __doc__ = f"""
        {base_attributes_documentation()}
        """

        data_dir: str
        pattern: str = "**/*"
        batch_size: int = 1
        shuffle_data: bool = False
        samples_to_load: int = -1
        load_on_init: bool = False

    PACKET_ATT_NAME: str

    def __init__(self, attributes: TemplateAttributeType) -> None:
        super().__init__(attributes)
        self.counter = 0
        self.data_collection = self.make_data_entries()

    @abc.abstractmethod
    def make_data_entries(self) -> list[Packet]:
        """
        This method creates the data entries for this template. Each data entry
        consists of a `Packet` type.
        This method is called in the constructor and values are stored in data_collection.

        Returns:
            list[Packet]: list of ImagePacket
        """

    def read_packet_content(self, data_packet: Packet) -> None:
        """
        Sets the value for data_packet.content where data packets can be ImagePacket|TextPacket...

        Args:
            data_packet (Packet): Packet for content to be read from

        """

    def _retrieve_packets(self, packets: list[Packet]) -> list[Packet]:
        """This method retrieves the Packets from the batch after they have been processed

        Args:
            packets (list[Packet]): list of Packets. These can be of type ImagePacket|TextPacket...

        Returns:
            packets (list[Packet]): The retrieved list of Packets.
        """
        if not self.attributes.load_on_init:
            for data_packet in packets:
                self.read_packet_content(data_packet)
        return packets

    def __iter__(self) -> Generator:
        if self.attributes.batch_size == -1:
            yield self._retrieve_packets(self.data_collection)
        else:
            for batch_start_index in range(0, len(self.data_collection), self.attributes.batch_size):
                image_packets = self._retrieve_packets(
                    self.data_collection[batch_start_index : batch_start_index + self.attributes.batch_size]
                )
                yield image_packets

    def __next__(self) -> StopIteration | Generator:  # type:ignore #the yield method returns the Generator object
        if not self.has_elements():
            raise StopIteration("No more data to load")
        if self.attributes.batch_size == -1:
            yield self._retrieve_packets(self.data_collection)
            self.counter = len(self.data_collection)
        else:
            start_idx = self.counter * self.attributes.batch_size
            yield self._retrieve_packets(self.data_collection[start_idx : start_idx + self.attributes.batch_size])
            self.counter += 1

    def has_elements(self) -> bool:
        """Method to determine whether there are still data to be loaded
        If True, the data collection still has elements to be passed,
        If False, there are no more elements to be passed
        """
        data_collection_has_elements: bool = self.counter < abs(
            (len(self.data_collection) / self.attributes.batch_size)
        )
        return data_collection_has_elements

    def append_packets_to_container(self, container: DataContainer) -> None:
        """Method to add an extra data packet to the container

        Args:
            container (DataContainer): container where data is to be appended
        """
        data_packets_to_add = list(next(self))[0]  # noqa: RUF015  # avoid nested lists
        data_packets_to_add += getattr(container, self.PACKET_ATT_NAME)
        setattr(container, self.PACKET_ATT_NAME, data_packets_to_add)

    def num_elements(self) -> int:
        """Checks the number of remaining elements from the data collection.
        If the method has_elements returns True, then the number of remaining elements is 0
        """
        return 0 if not self.has_elements() else len(self.data_collection)

    def execute(self, container: DataContainer) -> DataContainer:
        if self.has_elements():
            self.append_packets_to_container(container)
        else:
            self.logger.debug(f"{self.class_name} has no more data to load.")
        return container
