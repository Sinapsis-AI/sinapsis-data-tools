# -*- coding: utf-8 -*-
from sinapsis_core.data_containers.data_packet import DataContainer, TextPacket, TimeSeriesPacket
from sinapsis_core.template_base.base_models import TemplateAttributes, TemplateAttributeType
from sinapsis_core.template_base.template import Template

from sinapsis_data_readers.helpers.csv_reader import read_file


class CSVDatasetReader(Template):
    class AttributesBaseModel(TemplateAttributes):
        path_to_csv: str
        store_as_time_series: bool = False
        store_as_text_packet: bool = True

    def __init__(self, attributes: TemplateAttributeType) -> None:
        super().__init__(attributes)
        self.csv_file = read_file(self.attributes.path_to_csv)

    def execute(self, container: DataContainer) -> DataContainer:
        if self.attributes.store_as_time_series:
            packet = TimeSeriesPacket(content=self.csv_file)
            container.time_series.append(packet)
        if self.attributes.store_as_text_packet:
            packet = TextPacket(content=self.csv_file)
            container.texts.append(packet)
        return container
