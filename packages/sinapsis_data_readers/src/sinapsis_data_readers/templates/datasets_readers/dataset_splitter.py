# -*- coding: utf-8 -*-

import pandas as pd
from sinapsis_core.data_containers.data_packet import DataContainer, DataFramePacket
from sinapsis_core.template_base import Template
from sinapsis_core.template_base.base_models import TemplateAttributes
from sklearn.model_selection import train_test_split


class CSVDatasetSplitter(Template):
    """
    Template to split a tabular data set into test and train samples.
    The template retrieves the dataset from the dataframe packet of the
    container and stores the features and targets as new dataframes, with source
    indicating whether train or test samples
    """

    class AttributesBaseModel(TemplateAttributes):
        target_key: str = "target"  # labels
        feature_key: str | None  = None  # arrays
        random_state: int = 42
        train_size: float = 0.2




    def extract_x_y_from_packet(self, data_frame: DataFramePacket) -> tuple[pd.DataFrame, pd.DataFrame]:


        target = data_frame.content.get(self.attributes.target_key)
        feature = data_frame.content.get(self.attributes.feature_key) \
            if self.attributes.feature_key \
            else data_frame.content.drop(columns=[self.attributes.target_key])
        return feature, target

    def split_dataset(self, x_data:pd.DataFrame, y_data:pd.DataFrame) -> dict:

        x_train, x_test, y_train, y_test = train_test_split(
            x_data,
            y_data,
            train_size=self.attributes.train_size,
            test_size=1 - self.attributes.train_size,
            random_state=self.attributes.random_state,
        )
        data_map = {
            "x_train": x_train,
            "y_train": y_train,
            "x_test": x_test,
            "y_test": y_test
        }
        return data_map
    def assign_to_dataframe_packets(self,container: DataContainer, source: str, data: pd.DataFrame) -> DataContainer:
        df_packet = DataFramePacket(content=data, source=f"{self.instance_name}_{source}")
        container.data_frames.append(df_packet)
        return container

    def execute(self, container: DataContainer) -> DataContainer:
        new_samples = []
        for df in container.data_frames:
            feature, target = self.extract_x_y_from_packet(df)

            if self.attributes.train_size:
                sample = self.split_dataset(feature, target)
                new_samples.append(sample)
        for sample in new_samples:
            for name, data_frame in sample.items():
                container = self.assign_to_dataframe_packets(container, name, data_frame)
        return container

