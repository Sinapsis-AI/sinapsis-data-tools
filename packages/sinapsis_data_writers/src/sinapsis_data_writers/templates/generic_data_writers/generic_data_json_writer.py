# -*- coding: utf-8 -*-
import json
from pathlib import Path
from typing import Any

from sinapsis_core.data_containers.data_packet import DataContainer
from sinapsis_core.template_base import Template
from sinapsis_core.template_base.base_models import (
    OutputTypes,
    TemplateAttributes,
    TemplateAttributeType,
    UIPropertiesMetadata,
)
from sinapsis_core.utils.env_var_keys import WORKING_DIR
from sinapsis_data_writers.helpers.tags import Tags

FORMATTED_ANNOTATIONS = list[dict]


class GenericDataJSONWriter(Template):  # type:ignore
    """
    Base Generic Data Writer that saves generic data to a specified format.
    This template defines the base classes for storing data in a structured format
    """

    class AttributesBaseModel(TemplateAttributes):  # type:ignore
        """Attributes for the Base Generic Data Writer.

        Attributes:
            root_dir (str): Local root directory.
            save_dir (str): Local path to save the file.
            output_file (str): Name of the file.
            extension (str): extension of the file.
            generic_keys (list[str]): Optional list of keys to look for
        """

        root_dir: str = WORKING_DIR
        save_dir: str
        output_file: str = "generic_data"
        extension: str = "json"
        generic_key: str

    UIProperties = UIPropertiesMetadata(
        output_type=OutputTypes.TEXT,
        tags=[Tags.JSON, Tags.WRITERS],
    )

    def __init__(self, attributes: TemplateAttributeType) -> None:
        """Initialize the writer and prepare to accumulate data."""
        super().__init__(attributes)
        self.data: dict[str, Any] = {}

    def save_data(self, data: dict[str, Any]) -> None:
        """Saves annotations to a JSON file for a specified folder.

        Args:
            data (dict[str, Any]): the dictionary with data from the data packets
        """
        save_path = Path(self.attributes.root_dir) / self.attributes.save_dir
        save_path.mkdir(parents=True, exist_ok=True)
        output_file = save_path / f"{Path(self.attributes.output_file).stem}.{self.attributes.extension}"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, separators=(",", ":"))
            self.logger.info(f"Saved data to {output_file}")

    def execute(self, container: DataContainer) -> DataContainer:
        """Executes the annotation process by processing generic data and saving it.

        Args:
            container (DataContainer): The container holding generic data.

        Returns:
            DataContainer: The processed data container.
        """
        if not container.generic_data:
            return container

        self.data = self._get_generic_data(container, self.attributes.generic_key)

        self.save_data(self.data)

        return container
