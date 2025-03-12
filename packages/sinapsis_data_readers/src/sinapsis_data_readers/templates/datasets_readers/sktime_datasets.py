# -*- coding: utf-8 -*-


from sinapsis_core.data_containers.data_packet import DataContainer
from sinapsis_core.template_base import Template
from sinapsis_core.template_base.dynamic_template import (
    BaseDynamicWrapperTemplate,
    WrapperEntryConfig,
)
from sinapsis_core.template_base.dynamic_template_factory import make_dynamic_template
from sinapsis_core.template_base.multi_execute_template import (
    execute_template_n_times_wrapper,
)
from sinapsis_core.utils.env_var_keys import SINAPSIS_BUILD_DOCS
from sktime import datasets

EXCLUDE_MODULES = ["load_forecastingdata", "DATASET_NAMES_FPP3"]


class SKTimeDatasets(BaseDynamicWrapperTemplate):
    """Template to process SKTime datasets module
    The DataContainer stores the Pandas Series in the generic_field_key
    defined in the attributes. To check the available datasets, refer to
    'https://www.sktime.net/en/stable/api_reference/datasets.html'

    Usage example:
        agent:
          name: my_test_agent
        templates:
        - template_name: InputTemplate
          class_name: InputTemplate
          attributes: {}
        - template_name: load_irisWrapper
          class_name: load_airplineWrapper ## Note that since this is a dynamic template
          template_input: InputTemplate         ##, the class name depends on the actual dataset being imported
          attributes:
            load_airline:
              {}


    """

    WrapperEntry = WrapperEntryConfig(
        wrapped_object=datasets, signature_from_doc_string=True, exclude_module_atts=EXCLUDE_MODULES
    )
    CATEGORY = "SKTime"

    def execute(self, container: DataContainer) -> DataContainer:
        self.logger.debug("Generating SKTime dataset...")
        dataset = self.wrapped_callable.__func__()
        self._set_generic_data(container, dataset)

        return container


@execute_template_n_times_wrapper
class ExecuteNTimesSKTimeDatasets(SKTimeDatasets):
    """This template extends the functionality of the SKTimeDatasets template
    by loading the sktime dataset n times"""

    WrapperEntry = WrapperEntryConfig(
        wrapped_object=datasets,
        signature_from_doc_string=True,
        exclude_module_atts=EXCLUDE_MODULES,
        template_name_suffix="ExecuteNTimes",
    )


def __getattr__(name: str) -> Template:
    """
    Only create a template if it's imported, this avoids creating all the base models for all templates
    and potential import errors due to not available packages.
    """
    if name in SKTimeDatasets.WrapperEntry.module_att_names:
        return make_dynamic_template(name, SKTimeDatasets)
    if name in ExecuteNTimesSKTimeDatasets.WrapperEntry.module_att_names:
        return make_dynamic_template(name, ExecuteNTimesSKTimeDatasets)
    raise AttributeError(f"template `{name}` not found in {__name__}")


__all__ = SKTimeDatasets.WrapperEntry.module_att_names + ExecuteNTimesSKTimeDatasets.WrapperEntry.module_att_names


if SINAPSIS_BUILD_DOCS:
    dynamic_templates = [__getattr__(template_name) for template_name in __all__]
    for template in dynamic_templates:
        globals()[template.__name__] = template
        del template
