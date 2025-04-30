# -*- coding: utf-8 -*-
import joblib
from sinapsis_core.template_base import Template
from sinapsis_core.template_base.base_models import UIPropertiesMetadata
from sinapsis_core.template_base.dynamic_template import WrapperEntryConfig
from sinapsis_core.template_base.dynamic_template_factory import make_dynamic_template
from sinapsis_core.utils.env_var_keys import SINAPSIS_BUILD_DOCS
from sklearn import linear_model, neighbors, neural_network, tree

from sinapsis_data_analysis.helpers.excluded_models import (
    excluded_linear_models,
    excluded_neighbors_models,
    excluded_tree_models,
)
from sinapsis_data_analysis.templates.ml_base_training import MLBaseTraining


class SKLearnLinearModelsTrain(MLBaseTraining):
    """
    This template dynamically wraps sklearn linear_model module,
    to train a dataset using linear models.

    Usage example:

        agent:
          name: my_test_agent
        templates:
        - template_name: InputTemplate
          class_name: InputTemplate
          attributes: {}
          template_name: LarsWrapper
          class_name: LinearRegressionWrapper
          template_input: load_diabetesWrapper
          attributes:
            generic_field_key: InputTemplate
            model_save_path: "artifacts/linear_regression.joblib"
            linearregression_init:
              fit_intercept: true
              copy_X: true
              n_jobs: 8
              positive: false
    """

    WrapperEntry = WrapperEntryConfig(
        wrapped_object=linear_model,
        signature_from_doc_string=True,
        exclude_module_atts=excluded_linear_models,
        force_init_as_method=False,
    )

    UIProperties = UIPropertiesMetadata(category="SKLearn")

    def _save_model_implementation(self) -> None:
        """
        Implements the abstract method from the base class to
        save the model to the path specified in attributes.
        """
        joblib.dump(self.trained_model, self.attributes.model_save_path)


class SKLearnNeighborsModelsTrain(SKLearnLinearModelsTrain):
    """
    This template dynamically wraps sklearn neighbors module,
    providing access to models like KNeighborsClassifier,
    KNeighborsRegressor, etc.

    Usage example:

      agent:
          name: my_test_agent
        templates:
        - template_name: InputTemplate
          class_name: InputTemplate
          attributes: {}
        - template_name: KNeighborsClassifierWrapper
          class_name: KNeighborsClassifierWrapper
          template_input: InputTemplate
          attributes:
            generic_field_key: 'input_template'
            model_save_path: 'kneighbors.joblib'
            kneighborsclassifier_init:
              n_neighbors: 5
              weights: uniform
              algorithm: auto
              leaf_size: 30
              p: 2
              metric: minkowski
              n_jobs: 2
    """

    WrapperEntry = WrapperEntryConfig(
        wrapped_object=neighbors,
        signature_from_doc_string=True,
        exclude_module_atts=excluded_neighbors_models,
        force_init_as_method=False,
    )


class SKLearnNNModelsTrain(SKLearnLinearModelsTrain):
    """
    This template dynamically wraps sklearn's neural_network module,
    providing access to models like MLPClassifier, MLPRegressor, etc.

    Usage example:

    agent:
      name: my_test_agent
    templates:
    - template_name: InputTemplate
      class_name: InputTemplate
      attributes: {}
    - template_name: BernoulliRBMWrapper
      class_name: BernoulliRBMWrapper
      template_input: InputTemplate
      attributes:
        generic_field_key: 'input_template'
        model_save_path: 'artifacts/bernoulli.joblib'
        bernoullirbm_init:
          n_components: 256
          learning_rate: 0.1
          batch_size: 10
          n_iter: 10
          verbose: 0
          random_state: null

    """

    WrapperEntry = WrapperEntryConfig(
        wrapped_object=neural_network, signature_from_doc_string=True, force_init_as_method=False
    )


class SKLearnTreeModelsTrain(SKLearnLinearModelsTrain):
    """
    This template dynamically wraps sklearn's tree module,
    providing access to models like DecisionTreeClassifier,
    DecisionTreeRegressor, etc.

    Usage example:

    agent:
      name: my_test_agent
    templates:
    - template_name: InputTemplate
      class_name: InputTemplate
      attributes: {}
    - template_name: DecisionTreeClassifierWrapper
      class_name: DecisionTreeClassifierWrapper
      template_input: InputTemplate
      attributes:
        generic_field_key: 'input_template'
        model_save_path: 'artifacts/decision_tree.joblib'
        decisiontreeclassifier_init:
          criterion: gini
          splitter: best
          max_depth: null
          min_samples_split: 2
          min_samples_leaf: 1
          min_weight_fraction_leaf: 0.0
          max_features: sqrt
          random_state: 1
          max_leaf_nodes: 2
          min_impurity_decrease: 0.0
          class_weight: balanced
          ccp_alpha: 0.0

    """

    WrapperEntry = WrapperEntryConfig(
        wrapped_object=tree,
        signature_from_doc_string=True,
        exclude_module_atts=excluded_tree_models,
        force_init_as_method=False,
    )


def __getattr__(name: str) -> Template:
    """
    Only create a template if it's imported, this avoids creating all the base models for all templates
    and potential import errors due to not available packages.
    """
    if name in SKLearnLinearModelsTrain.WrapperEntry.module_att_names:
        return make_dynamic_template(name, SKLearnLinearModelsTrain)
    if name in SKLearnNeighborsModelsTrain.WrapperEntry.module_att_names:
        return make_dynamic_template(name, SKLearnNeighborsModelsTrain)
    if name in SKLearnNNModelsTrain.WrapperEntry.module_att_names:
        return make_dynamic_template(name, SKLearnNNModelsTrain)
    if name in SKLearnTreeModelsTrain.WrapperEntry.module_att_names:
        return make_dynamic_template(name, SKLearnTreeModelsTrain)
    raise AttributeError(f"template `{name}` not found in {__name__}")


__all__ = (
    SKLearnLinearModelsTrain.WrapperEntry.module_att_names
    + SKLearnNeighborsModelsTrain.WrapperEntry.module_att_names
    + SKLearnNNModelsTrain.WrapperEntry.module_att_names
    + SKLearnTreeModelsTrain.WrapperEntry.module_att_names
)


if SINAPSIS_BUILD_DOCS:
    dynamic_templates = [__getattr__(template_name) for template_name in __all__]
    for template in dynamic_templates:
        globals()[template.__name__] = template
        del template
