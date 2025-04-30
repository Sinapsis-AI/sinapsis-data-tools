# -*- coding: utf-8 -*-
import xgboost as xgb
from sinapsis_core.template_base import Template
from sinapsis_core.template_base.base_models import UIPropertiesMetadata
from sinapsis_core.template_base.dynamic_template import WrapperEntryConfig
from sinapsis_core.template_base.dynamic_template_factory import make_dynamic_template
from sinapsis_core.utils.env_var_keys import SINAPSIS_BUILD_DOCS

from sinapsis_data_analysis.templates.sklearn_train import SKLearnLinearModelsTrain

INCLUDED_MODELS = [
    "XGBClassifier",
    "XGBRegressor",
    "XGBRanker",
    "XGBRFClassifier",
    "XGBRFRegressor",
    "Booster",
]

EXCLUDED_MODELS = [attr for attr in dir(xgb) if attr not in INCLUDED_MODELS]


class XGBoostModelsTraining(SKLearnLinearModelsTrain):
    """Dynamic templates for XGBoost modules for classification, regression and boosting.
    These templates wrap the functionality provided by the xgb module and use the fit method
    on a dataset provided by the container.

    Usage example:

    agent:
      name: my_test_agent

    templates:
    - template_name: InputTemplate
      class_name: InputTemplate
      attributes: {}
      - template_name: XGBRankerWrapper
      class_name: XGBClassifierWrapper
      template_input: load_irisWrapper
      attributes:
        generic_field_key: load_irisWrapper
        model_save_path: "artifacts/xgb_classifier.model"
        xgbclassifier_init:
          n_estimators: 100
          max_depth: 3
          learning_rate: 0.1
    """

    WrapperEntry = WrapperEntryConfig(
        wrapped_object=xgb,
        parse_entire_mro=True,
        exclude_module_atts=EXCLUDED_MODELS,
        force_init_as_method=False,
        exclude_method_attributes=[
            "kwargs",
            "objective",
        ],
    )

    UIProperties = UIPropertiesMetadata(category="XGBoost")


def __getattr__(name: str) -> Template:
    if name in XGBoostModelsTraining.WrapperEntry.module_att_names:
        return make_dynamic_template(name, XGBoostModelsTraining)
    raise AttributeError(f"template `{name}` not found in {__name__}")


__all__ = XGBoostModelsTraining.WrapperEntry.module_att_names


if SINAPSIS_BUILD_DOCS:
    dynamic_templates = [__getattr__(template_name) for template_name in __all__]
    for template in dynamic_templates:
        globals()[template.__name__] = template
        del template
