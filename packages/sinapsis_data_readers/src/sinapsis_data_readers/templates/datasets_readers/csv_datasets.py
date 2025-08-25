# -*- coding: utf-8 -*-
import os

from sinapsis_core.data_containers.data_packet import DataContainer, TimeSeriesPacket
from sinapsis_core.template_base.base_models import TemplateAttributes, TemplateAttributeType
from sinapsis_core.template_base.template import Template
from sinapsis_core.utils.env_var_keys import SINAPSIS_CACHE_DIR

from sinapsis_data_readers.helpers.csv_reader import read_file


class CSVDatasetReader(Template):
    class AttributesBaseModel(TemplateAttributes):
        root_dir : str | None = None
        path_to_csv: str
        store_as_time_series: bool = False

    def __init__(self, attributes: TemplateAttributeType) -> None:
        super().__init__(attributes)
        self.attributes.root_dir = self.attributes.root_dir or SINAPSIS_CACHE_DIR
        self.csv_file = read_file(os.path.join(self.attributes.root_dir, self.attributes.path_to_csv))

    def execute(self, container: DataContainer) -> DataContainer:
        if self.attributes.store_as_time_series:
            packet = TimeSeriesPacket(content=self.csv_file)
            container.time_series.append(packet)
        else:
            self._set_generic_data(container, self.csv_file)

        return container
