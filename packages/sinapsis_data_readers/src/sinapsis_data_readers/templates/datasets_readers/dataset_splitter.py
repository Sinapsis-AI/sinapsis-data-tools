# -*- coding: utf-8 -*-
from abc import abstractmethod
from typing import Union, cast

import numpy as np
import pandas as pd
from pydantic import BaseModel
from sinapsis_core.data_containers.data_packet import DataContainer, ImagePacket, Packet
from sinapsis_core.template_base import Template
from sinapsis_core.template_base.base_models import TemplateAttributes
from sklearn.model_selection import train_test_split

ArrayDataFrameType = Union[list[np.ndarray], pd.DataFrame]
StringDataFrameType = Union[list[str], pd.DataFrame]
OptionalArrayDataFrameType = Union[ArrayDataFrameType, None]

OptionalStringDataFrameType = Union[StringDataFrameType, None]


class ImageDatasetSplit(BaseModel):
    """BaseModel to store the content of the data packets as a list
    x_train (list): Contains the x values for the train set.
        If there is no split, contains the x values for the whole set
    y_train (list): Contains the y values for the train set.
        If there is no split, contains the x values for the whole set
    x_test (list | None): Contains the x values for the test set.
        If there is no split, is set to None
    y_test (list | None): Contains the y values for the test set.
        If there is no split, is set to None
    """

    x_train: list[np.ndarray] = []
    y_train: list[str] = []
    x_test: list[np.ndarray] | None = None
    y_test: list[str] | None = None

    class Config:
        """allow arbitrary types"""

        arbitrary_types_allowed = True


class TabularDatasetSplit(BaseModel):
    """BaseModel to store the content of the data packets as a list
    x_train (pd.DataFrame) :  Contains the x values for the train set.
        If there is no split, contains the x values for the whole set
    y_train (pd.DataFrame) :  Contains the y values for the train set.
        If there is no split, contains the x values for the whole set
    x_test (pd.DataFrame | None) :  Contains the x values for the test set.
        If there is no split, is set to None
    y_test (pd.DataFrame | None) :  Contains the y values for the test set.
        If there is no split, is set to None
    """

    x_train: pd.DataFrame
    y_train: pd.DataFrame
    x_test: pd.DataFrame | None = None
    y_test: pd.DataFrame | None = None

    class Config:
        """allow arbitrary types"""

        arbitrary_types_allowed = True


class DatasetSplitterBase(Template):
    """Base Template to split data sets into train and test samples
    The Template splits the datasets and stores them in a BaseModel containing
    entries for x_train, y_train, x_test and y_yest
    """

    PACKET: str

    class AttributesBaseModel(TemplateAttributes):
        train_size: float = 0.5

    @staticmethod
    @abstractmethod
    def return_data_splitter_object(
        x_train: ArrayDataFrameType,
        y_train: StringDataFrameType,
        x_test: OptionalArrayDataFrameType,
        y_test: OptionalStringDataFrameType,
    ) -> BaseModel:
        """Store the x and y values in the DatasetSplit BaseModel"""

    def store_data_in_data_splitter(self, x_data: ArrayDataFrameType, y_data: StringDataFrameType) -> BaseModel:
        """
        This method performs the split using the train_test_split from
        sklearn and calls the return_data_splitter_object to return the BaseModel
        with the x and y train and test samples
        """
        x_train, x_test, y_train, y_test = x_data, None, y_data, None
        if self.attributes.train_size:
            x_train, x_test, y_train, y_test = train_test_split(
                x_data, y_data, train_size=self.attributes.train_size, random_state=0
            )
        split_dataset = self.return_data_splitter_object(x_train=x_train, y_train=y_train, x_test=x_test, y_test=y_test)
        return split_dataset

    @abstractmethod
    def extract_x_y_from_packet(self, packets: list[Packet] | dict) -> tuple[ArrayDataFrameType, StringDataFrameType]:
        """
        Method to extract the x and y values from a given list of data packets

        Returns:
            tuple[ArrayDataFrameType, StringDataFrameType]: A tuple with the x and y values.

        Note:
            x can be of type array or pd.DataFrame
            y can be of type str or pd.DataFrame
        """

    def execute(self, container: DataContainer) -> DataContainer:
        """Executes the template

        Args:
            container (DataContainer): incoming container,
            with the data to be split in a packet
        Returns:
            DataContainer: Modified container
        """

        packet = getattr(container, self.PACKET)

        if not packet:
            self.logger.debug("No data to be processed by dataset splitter")
            return container

        x_data, y_data = self.extract_x_y_from_packet(packet)

        custom_dataset = self.store_data_in_data_splitter(x_data, y_data)
        self._set_generic_data(container, custom_dataset)
        return container


class ImageDatasetSplitter(DatasetSplitterBase):
    """
    Template to split an Image data set into test and train samples.
    The template retrieves the image packets from the container and
    stores the image arrays and labels in the ImageDatasetSplit BaseModel

    Usage example:
        agent:
          name: my_test_agent
        templates:
        - template_name: InputTemplate
          class_name: InputTemplate
          attributes: {}
        - template_name: ImageDatasetSplitter
          class_name: ImageDatasetSplitter
          template_input: InputTemplate
          attributes:
            train_size: 0.5
            generic_field_key: SPLIT_DATASET

    """

    PACKET = "images"

    def extract_x_y_from_packet(self, packets: list[Packet] | dict) -> tuple[ArrayDataFrameType, StringDataFrameType]:
        packets = cast(list, packets)
        x, y = self.process_images_packet(packets)
        return x, y

    @staticmethod
    def process_images_packet(
        packets: list[ImagePacket],
    ) -> tuple[ArrayDataFrameType, StringDataFrameType]:
        """Processes an 'images' type packet."""
        arrays, labels = [], []
        for pck in packets:
            if pck.annotations:
                arrays.append(pck.content)
                labels.append(pck.annotations[0].label)
        return arrays, labels

    @staticmethod
    def return_data_splitter_object(
        x_train: ArrayDataFrameType,
        y_train: StringDataFrameType,
        x_test: OptionalArrayDataFrameType,
        y_test: OptionalStringDataFrameType,
    ) -> ImageDatasetSplit:
        return ImageDatasetSplit(x_train=x_train, y_train=y_train, x_test=x_test, y_test=y_test)


class TabularDatasetSplitter(DatasetSplitterBase):
    """
    Template to split a tabular data set into test and train samples.
    The template retrieves the dataset from the generic field of the
    container and stores the features and targets in the ImageDatasetSplit BaseModel

    Usage example:
        agent:
          name: my_test_agent
        templates:
        - template_name: InputTemplate
          class_name: InputTemplate
          attributes: {}
        - template_name: TabularDatasetSplitter
          class_name: TabularDatasetSplitter
          template_input: InputTemplate
          attributes:
            train_size: 0.5
            generic_field_key: SPLIT_DATASET
    """

    PACKET = "generic_data"

    class AttributesBaseModel(DatasetSplitterBase.AttributesBaseModel):
        generic_data_extract_key: str = "SKLearn-Datasets"
        generic_data_target_key: str = "target"  # labels
        generic_data_feature_key: str = "data"  # arrays

    def extract_x_y_from_packet(self, packets: list[Packet] | dict) -> tuple[StringDataFrameType, ArrayDataFrameType]:
        packet = cast(dict, packets)
        dataframe: pd.DataFrame | None = packet.get(self.attributes.generic_data_extract_key, None)
        target: pd.DataFrame = pd.DataFrame()
        feature: pd.DataFrame = pd.DataFrame()
        if isinstance(dataframe, pd.DataFrame):
            target = dataframe.get(self.attributes.generic_data_target_key)
            feature = dataframe.get(self.attributes.generic_data_feature_key)

        return feature, target

    @staticmethod
    def return_data_splitter_object(
        x_train: ArrayDataFrameType,
        y_train: StringDataFrameType,
        x_test: OptionalArrayDataFrameType,
        y_test: OptionalStringDataFrameType,
    ) -> TabularDatasetSplit:
        return TabularDatasetSplit(x_train=x_train, y_train=y_train, x_test=x_test, y_test=y_test)
