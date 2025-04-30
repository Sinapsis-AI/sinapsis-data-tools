# -*- coding: utf-8 -*-


from sinapsis_core.template_base.base_models import UIPropertiesMetadata

from sinapsis_data_analysis.templates.sklearn_inference import SKLearnInference


class XGBoostInference(SKLearnInference):
    """Dynamic templates to perform inference using XGBoost models.
    These templates wrap the functionality of the xgb module and use the predict method on execute
    using a dataset obtained through the container.

    Usage example:
    agent:
      name: my_test_agent
    templates:
    - template_name: InputTemplate
      class_name: InputTemplate
      attributes: {}
    - template_name: XGBRFClassifierInference
      class_name: XGBRFClassifierInference
      template_input: InputTemplate
      attributes:
        model_path: 'artifacts/xgb_rf_classifier.model'
        generic_field_key: 'generic_dataset'

    """

    UIProperties = UIPropertiesMetadata(category="XGBoost")
