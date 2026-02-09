# -*- coding: utf-8 -*-
import pandas as pd
from sinapsis_core.data_containers.data_packet import DataContainer
from sinapsis_core.template_base.template import Template
from sinapsis_core.template_base.base_models import TemplateAttributes



class CategoricalToNumerical(Template):
	class AttributesBaseModel(TemplateAttributes):
		generic_key: str

	@staticmethod
	def map_categorical_to_numerical(df: pd.DataFrame| pd.Series)->pd.DataFrame | pd.Series:

		if isinstance(df, pd.Series):
			categorical_cols =  [df.name] if df.dtype in ["object", "string", "category"] else []
		else:
			categorical_cols =  df.select_dtypes(include=["object", "string", "category"]).columns.tolist()


		category_maps = {}

		for col in categorical_cols:
			categories = df[col].astype("string").unique()
			category_maps[col] = {cat: idx for idx, cat in enumerate(categories)}
		for col, mapping in category_maps.items():
			df[col] = df[col].map(mapping)
		return df, category_maps
	@staticmethod
	def unmap_numerical_to_categorical(df: pd.DataFrame| pd.Series, categories: dict):
		inverse_maps = {col: {v: k for k, v in mapping.items()} for col, mapping in categories.items()}

		for col in inverse_maps:
			df[col] = df[col].map(inverse_maps[col])
		return df


	def execute(self, container: DataContainer) -> DataContainer:
		dataset = self._get_generic_data(container)
		transformed_dataset, labels = self.map_categorical_to_numerical(dataset)
		self._set_generic_data(container, transformed_dataset)
		return container


