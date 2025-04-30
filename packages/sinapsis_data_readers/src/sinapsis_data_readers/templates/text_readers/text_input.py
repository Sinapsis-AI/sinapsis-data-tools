# -*- coding: utf-8 -*-

from sinapsis_core.data_containers.data_packet import DataContainer, TextPacket
from sinapsis_core.template_base import Template
from sinapsis_core.template_base.base_models import OutputTypes, TemplateAttributes, UIPropertiesMetadata


class TextInputAttributes(TemplateAttributes):
    """
    Attributes:
        source (str | None): The source identifier for the text input. If provided,
            it will be used to set the `source` attribute of the created `TextPacket`.
        text (str): The text content to be added to the data container.
    """

    source: str | None = None
    text: str


class TextInput(Template):
    """
    A template for adding text content to a data container.

    This class uses the provided attributes to create a `TextPacket`
    and appends it to the container's text data.

    Usage example:

    agent:
      name: my_test_agent
    templates:
    - template_name: InputTemplate
      class_name: InputTemplate
      attributes: {}
    - template_name: TextInput
      class_name: TextInput
      template_input: InputTemplate
      attributes:
        source: local
        text: 'text to be added to the TextPacket'


    """

    PACKET_ATT_NAME = "texts"
    AttributesBaseModel = TextInputAttributes
    UIProperties = UIPropertiesMetadata(output_type=OutputTypes.TEXT)

    def execute(self, container: DataContainer) -> DataContainer:
        """
        Creates a TextPacket with the user's input and appends it to the container.

        Args:
            container (DataContainer): The container to which the text packet will be added.

        Returns:
            DataContainer: The updated container with the newly added text packet.
        """
        text_packet = TextPacket(content=self.attributes.text)
        text_packet.source = self.attributes.source if self.attributes.source is not None else self.instance_name
        texts = getattr(container, self.PACKET_ATT_NAME)
        texts.append(text_packet)

        return container
